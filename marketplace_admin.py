from __future__ import annotations

import sqlite3
import time
import uuid
from pathlib import Path

from marketplace_catalog import CatalogStore


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
        self.catalog = CatalogStore(database_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

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
        return self.catalog.save_product(payload, product_id)

    def archive_product(self, actor: dict, product_id: object) -> dict:
        self._require_admin(actor)
        return self.catalog.archive_product(self._clean(product_id))
