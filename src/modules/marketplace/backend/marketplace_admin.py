from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path

from .marketplace_auth import AuthStore
from .marketplace_catalog import CatalogStore


PAYMENT_STATUS_VALUES = {"unpaid", "pending", "paid", "failed", "expired", "cancelled"}
ORDER_STATUS_VALUES = {
    "pending",
    "waiting_payment",
    "paid",
    "processing",
    "shipped",
    "completed",
    "cancelled",
}
FULFILLMENT_TRANSITIONS = {
    "paid": "processing",
    "processing": "shipped",
    "shipped": "completed",
}


class AdminValidationError(ValueError):
    def __init__(self, message: str, errors: dict[str, str] | None = None):
        super().__init__(message)
        self.errors = errors or {}


class AdminStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.auth = AuthStore(database_path)
        self.catalog = CatalogStore(database_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = self.connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at INTEGER NOT NULL
                )
                """
            )
            applied = {
                row["version"]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations"
                ).fetchall()
            }
            if 9 not in applied:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS admin_audit_logs (
                        id TEXT PRIMARY KEY,
                        actor_id TEXT NOT NULL,
                        actor_email TEXT NOT NULL,
                        actor_role TEXT NOT NULL,
                        action TEXT NOT NULL,
                        target_type TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        details TEXT NOT NULL DEFAULT '{}',
                        created_at INTEGER NOT NULL,
                        FOREIGN KEY (actor_id) REFERENCES users(id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_created
                        ON admin_audit_logs(created_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_actor
                        ON admin_audit_logs(actor_id, created_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_target
                        ON admin_audit_logs(target_type, target_id, created_at DESC);
                    """
                )
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (9, ?)",
                    (int(time.time()),),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _require_admin(actor: dict) -> None:
        if actor.get("role") not in {"admin", "super_admin"}:
            raise PermissionError("Hanya admin yang dapat membuka dashboard admin.")

    def dashboard_kpis(self, actor: dict) -> dict:
        self._require_admin(actor)
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM users) AS total_members,
                    (SELECT COUNT(*) FROM users WHERE status = 'active') AS active_members,
                    (SELECT COUNT(*) FROM orders) AS total_orders,
                    (
                        SELECT COALESCE(SUM(grand_total), 0)
                        FROM orders
                        WHERE payment_status = 'paid'
                    ) AS paid_revenue,
                    (
                        SELECT COUNT(*)
                        FROM orders
                        WHERE payment_status IN ('unpaid', 'pending')
                    ) AS pending_payments,
                    (
                        SELECT COUNT(*)
                        FROM consultation_tickets
                        WHERE status NOT IN ('resolved', 'closed')
                    ) AS active_tickets,
                    (
                        SELECT COUNT(*)
                        FROM consultation_tickets
                        WHERE priority = 'urgent'
                            AND status NOT IN ('resolved', 'closed')
                    ) AS urgent_tickets
                """
            ).fetchone()
            return {
                "totalMembers": row["total_members"],
                "activeMembers": row["active_members"],
                "totalOrders": row["total_orders"],
                "paidRevenue": row["paid_revenue"],
                "pendingPayments": row["pending_payments"],
                "activeTickets": row["active_tickets"],
                "urgentTickets": row["urgent_tickets"],
            }
        finally:
            connection.close()

    @staticmethod
    def _clean(value: object) -> str:
        return " ".join(str(value or "").strip().split())

    @staticmethod
    def _audit_payload(row: sqlite3.Row) -> dict:
        try:
            details = json.loads(row["details"] or "{}")
        except json.JSONDecodeError:
            details = {}
        return {
            "id": row["id"],
            "actor": {
                "id": row["actor_id"],
                "email": row["actor_email"],
                "role": row["actor_role"],
            },
            "action": row["action"],
            "targetType": row["target_type"],
            "targetId": row["target_id"],
            "details": details,
            "createdAt": row["created_at"],
        }

    def _record_action(
        self,
        connection: sqlite3.Connection,
        actor: dict,
        action: str,
        target_type: str,
        target_id: object,
        details: dict | None = None,
    ) -> None:
        connection.execute(
            """
            INSERT INTO admin_audit_logs (
                id, actor_id, actor_email, actor_role, action, target_type,
                target_id, details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                actor.get("id", ""),
                actor.get("email", ""),
                actor.get("role", ""),
                action,
                target_type,
                self._clean(target_id),
                json.dumps(details or {}, separators=(",", ":"), sort_keys=True),
                int(time.time()),
            ),
        )

    def record_action(
        self,
        actor: dict,
        action: str,
        target_type: str,
        target_id: object,
        details: dict | None = None,
    ) -> None:
        self._require_admin(actor)
        connection = self.connect()
        try:
            self._record_action(connection, actor, action, target_type, target_id, details)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_audit_logs(self, actor: dict, limit: int = 50) -> list[dict]:
        self._require_admin(actor)
        clean_limit = max(1, min(int(limit or 50), 100))
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT id, actor_id, actor_email, actor_role, action, target_type,
                    target_id, details, created_at
                FROM admin_audit_logs
                ORDER BY created_at DESC, rowid DESC
                LIMIT ?
                """,
                (clean_limit,),
            ).fetchall()
            return [self._audit_payload(row) for row in rows]
        finally:
            connection.close()

    @staticmethod
    def _public_order(row: sqlite3.Row, items: list[dict] | None = None) -> dict:
        current_status = row["order_status"]
        next_status = FULFILLMENT_TRANSITIONS.get(current_status)
        return {
            "id": row["id"],
            "invoiceNumber": row["invoice_number"],
            "customer": {
                "id": row["user_id"],
                "name": row["member_name"],
                "email": row["member_email"],
                "recipientName": row["recipient_name"],
                "phone": row["phone"],
            },
            "shipping": {
                "address": row["shipping_address"],
                "city": row["city"],
                "province": row["province"],
                "postalCode": row["postal_code"],
                "method": row["shipping_method"],
            },
            "subtotal": row["subtotal"],
            "shippingCost": row["shipping_cost"],
            "grandTotal": row["grand_total"],
            "paymentStatus": row["payment_status"],
            "orderStatus": current_status,
            "nextFulfillmentStatus": next_status,
            "createdAt": row["created_at"],
            "items": items or [],
        }

    def list_orders(
        self,
        actor: dict,
        payment_status: object = "",
        order_status: object = "",
    ) -> list[dict]:
        self._require_admin(actor)
        clean_payment = self._clean(payment_status)
        clean_order = self._clean(order_status)
        if clean_payment and clean_payment not in PAYMENT_STATUS_VALUES:
            raise AdminValidationError(
                "Filter payment tidak valid.",
                {"paymentStatus": "Filter payment tidak valid."},
            )
        if clean_order and clean_order not in ORDER_STATUS_VALUES:
            raise AdminValidationError(
                "Filter order tidak valid.",
                {"orderStatus": "Filter order tidak valid."},
            )
        conditions = ["1=1"]
        params: list[object] = []
        if clean_payment:
            conditions.append("o.payment_status = ?")
            params.append(clean_payment)
        if clean_order:
            conditions.append("o.order_status = ?")
            params.append(clean_order)
        connection = self.connect()
        try:
            rows = connection.execute(
                f"""
                SELECT o.*, u.name AS member_name, u.email AS member_email
                FROM orders o
                JOIN users u ON u.id = o.user_id
                WHERE {' AND '.join(conditions)}
                ORDER BY o.created_at DESC, o.invoice_number DESC
                """,
                params,
            ).fetchall()
            return [self._public_order(row) for row in rows]
        finally:
            connection.close()

    def get_order(self, actor: dict, order_id: object) -> dict:
        self._require_admin(actor)
        clean_id = self._clean(order_id)
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT o.*, u.name AS member_name, u.email AS member_email
                FROM orders o
                JOIN users u ON u.id = o.user_id
                WHERE o.id = ?
                """,
                (clean_id,),
            ).fetchone()
            if not row:
                raise LookupError("Order tidak ditemukan.")
            items = [
                {
                    "id": item["id"],
                    "name": item["product_name"],
                    "slug": item["product_slug"],
                    "qty": item["qty"],
                    "price": item["price"],
                    "subtotal": item["subtotal"],
                }
                for item in connection.execute(
                    """
                    SELECT id, product_name, product_slug, qty, price, subtotal
                    FROM order_items
                    WHERE order_id = ?
                    ORDER BY rowid
                    """,
                    (clean_id,),
                ).fetchall()
            ]
            return self._public_order(row, items)
        finally:
            connection.close()

    def update_fulfillment(
        self,
        actor: dict,
        order_id: object,
        status: object,
    ) -> dict:
        self._require_admin(actor)
        clean_id = self._clean(order_id)
        clean_status = self._clean(status)
        now = int(time.time())
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            order = connection.execute(
                """
                SELECT id, user_id, invoice_number, payment_status, order_status
                FROM orders
                WHERE id = ?
                """,
                (clean_id,),
            ).fetchone()
            if not order:
                raise LookupError("Order tidak ditemukan.")
            expected = FULFILLMENT_TRANSITIONS.get(order["order_status"])
            if order["payment_status"] != "paid":
                raise AdminValidationError(
                    "Order belum dibayar dan tidak dapat diproses.",
                    {"status": "Fulfillment hanya tersedia untuk order paid."},
                )
            if not expected or clean_status != expected:
                raise AdminValidationError(
                    "Transisi fulfillment tidak valid.",
                    {
                        "status": (
                            f"Status berikutnya harus {expected}."
                            if expected
                            else "Order tidak memiliki transisi fulfillment berikutnya."
                        )
                    },
                )
            connection.execute(
                "UPDATE orders SET order_status = ? WHERE id = ?",
                (clean_status, clean_id),
            )
            connection.execute(
                """
                INSERT INTO member_notifications (
                    id, user_id, title, message, kind, action_url, created_at
                ) VALUES (?, ?, ?, ?, 'order', '/member/orders', ?)
                """,
                (
                    str(uuid.uuid4()),
                    order["user_id"],
                    "Status order diperbarui",
                    f"Invoice {order['invoice_number']} sekarang berstatus {clean_status}.",
                    now,
                ),
            )
            self._record_action(
                connection,
                actor,
                "order.fulfillment_update",
                "order",
                clean_id,
                {
                    "invoiceNumber": order["invoice_number"],
                    "fromStatus": order["order_status"],
                    "toStatus": clean_status,
                },
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.get_order(actor, clean_id)

    def list_products(self, actor: dict) -> list[dict]:
        self._require_admin(actor)
        return self.catalog.list_admin_products()

    def save_product(
        self,
        actor: dict,
        payload: object,
        product_id: str | None = None,
    ) -> dict:
        self._require_admin(actor)
        product = self.catalog.save_product(payload, product_id)
        self.record_action(
            actor,
            "product.updated" if product_id else "product.created",
            "product",
            product["id"],
            {
                "slug": product["slug"],
                "status": product["status"],
                "stock": product["stock"],
            },
        )
        return product

    def archive_product(self, actor: dict, product_id: object) -> dict:
        self._require_admin(actor)
        product = self.catalog.archive_product(self._clean(product_id))
        self.record_action(
            actor,
            "product.archived",
            "product",
            product["id"],
            {"slug": product["slug"], "status": product["status"]},
        )
        return product

    def update_member_status(
        self,
        actor: dict,
        target_user_id: object,
        status: object,
    ) -> dict:
        self._require_admin(actor)
        clean_id = self._clean(target_user_id)
        connection = self.connect()
        try:
            before = connection.execute(
                "SELECT id, email, role, status FROM users WHERE id = ?",
                (clean_id,),
            ).fetchone()
        finally:
            connection.close()
        member = self.auth.update_member_status(clean_id, status)
        self.record_action(
            actor,
            "member.status_updated",
            "member",
            member["id"],
            {
                "email": member["email"],
                "role": member["role"],
                "fromStatus": before["status"] if before else None,
                "toStatus": member["status"],
            },
        )
        return member

    def update_member_role(
        self,
        actor: dict,
        target_user_id: object,
        role: object,
    ) -> dict:
        self._require_admin(actor)
        clean_id = self._clean(target_user_id)
        connection = self.connect()
        try:
            before = connection.execute(
                "SELECT id, email, role, status FROM users WHERE id = ?",
                (clean_id,),
            ).fetchone()
        finally:
            connection.close()
        member = self.auth.update_user_role(actor["id"], clean_id, role)
        self.record_action(
            actor,
            "member.role_updated",
            "member",
            member["id"],
            {
                "email": member["email"],
                "fromRole": before["role"] if before else None,
                "toRole": member["role"],
                "status": before["status"] if before else None,
            },
        )
        return member
