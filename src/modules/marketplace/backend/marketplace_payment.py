from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path


PAYMENT_METHODS = {"qris", "bank_transfer"}
SUPPORTED_BANKS = {"bca", "bni", "bri", "permata"}


class PaymentValidationError(ValueError):
    def __init__(self, message: str, errors: dict[str, str] | None = None):
        super().__init__(message)
        self.errors = errors or {}


class PaymentGatewayError(RuntimeError):
    pass


class MidtransClient:
    def __init__(
        self,
        server_key: str = "",
        production: bool = False,
        mock: bool = True,
        timeout: int = 15,
    ):
        self.server_key = server_key.strip()
        self.production = production
        self.mock = mock
        self.timeout = timeout
        self.base_url = (
            "https://api.midtrans.com"
            if production
            else "https://api.sandbox.midtrans.com"
        )

    @property
    def configured(self) -> bool:
        return self.mock or bool(self.server_key)

    def _request(self, path: str, method: str = "GET", payload: dict | None = None) -> dict:
        if not self.server_key:
            raise PaymentGatewayError("MIDTRANS_SERVER_KEY belum dikonfigurasi.")
        token = base64.b64encode(f"{self.server_key}:".encode("utf-8")).decode("ascii")
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Basic {token}",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            try:
                detail = json.loads(error.read().decode("utf-8"))
                message = detail.get("status_message") or detail.get("message")
            except (json.JSONDecodeError, UnicodeDecodeError):
                message = None
            raise PaymentGatewayError(
                message or f"Midtrans mengembalikan HTTP {error.code}."
            ) from error
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
            raise PaymentGatewayError("Midtrans tidak dapat dihubungi.") from error

    def charge(self, order: dict, method: str, bank: str = "") -> dict:
        provider_order_id = order["providerOrderId"]
        if self.mock:
            transaction_id = f"mock-{uuid.uuid4()}"
            if method == "qris":
                return {
                    "transaction_id": transaction_id,
                    "order_id": provider_order_id,
                    "gross_amount": f"{order['grandTotal']:.2f}",
                    "payment_type": "qris",
                    "transaction_status": "pending",
                    "status_code": "201",
                    "actions": [
                        {
                            "name": "generate-qr-code",
                            "method": "GET",
                            "url": "/assets/branding/favicon.svg",
                        }
                    ],
                    "expiry_time": int(time.time()) + 24 * 60 * 60,
                }
            virtual_account = f"8808{str(order['grandTotal'])[-8:].zfill(8)}"
            return {
                "transaction_id": transaction_id,
                "order_id": provider_order_id,
                "gross_amount": f"{order['grandTotal']:.2f}",
                "payment_type": "bank_transfer",
                "transaction_status": "pending",
                "status_code": "201",
                "va_numbers": [{"bank": bank, "va_number": virtual_account}],
                "expiry_time": int(time.time()) + 24 * 60 * 60,
            }

        payload = {
            "payment_type": method,
            "transaction_details": {
                "order_id": provider_order_id,
                "gross_amount": order["grandTotal"],
            },
            "item_details": [
                {
                    "id": item["slug"][:50],
                    "price": item["price"],
                    "quantity": item["qty"],
                    "name": item["name"][:50],
                }
                for item in order["items"]
            ]
            + (
                [
                    {
                        "id": "shipping",
                        "price": order["shippingCost"],
                        "quantity": 1,
                        "name": "Shipping",
                    }
                ]
                if order["shippingCost"]
                else []
            ),
            "customer_details": {
                "first_name": order["customer"]["name"][:50],
                "email": order["customer"]["email"],
                "phone": order["customer"]["phone"],
            },
        }
        if method == "qris":
            payload["qris"] = {"acquirer": "gopay"}
        else:
            payload["bank_transfer"] = {"bank": bank}
        return self._request("/v2/charge", method="POST", payload=payload)

    def status(self, provider_order_id: str) -> dict:
        if self.mock:
            raise PaymentGatewayError("Status mock diperbarui melalui callback test.")
        safe_id = urllib.parse.quote(provider_order_id, safe="")
        return self._request(f"/v2/{safe_id}/status")


class PaymentStore:
    def __init__(self, database_path: Path, client: MidtransClient):
        self.database_path = database_path
        self.client = client

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def initialize(self) -> None:
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
            if 6 not in applied:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS payments (
                        id TEXT PRIMARY KEY,
                        order_id TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        provider_order_id TEXT NOT NULL UNIQUE,
                        provider_transaction_id TEXT,
                        method TEXT NOT NULL,
                        bank TEXT NOT NULL DEFAULT '',
                        amount INTEGER NOT NULL CHECK (amount >= 0),
                        status TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'paid', 'failed', 'expired', 'cancelled')),
                        qr_url TEXT NOT NULL DEFAULT '',
                        va_number TEXT NOT NULL DEFAULT '',
                        raw_response TEXT NOT NULL DEFAULT '{}',
                        expires_at INTEGER,
                        paid_at INTEGER,
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        FOREIGN KEY (order_id) REFERENCES orders(id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_payments_order
                        ON payments(order_id, created_at DESC);

                    CREATE TABLE IF NOT EXISTS payment_events (
                        id TEXT PRIMARY KEY,
                        payment_id TEXT NOT NULL,
                        event_key TEXT NOT NULL UNIQUE,
                        transaction_status TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE
                    );
                    """
                )
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (6, ?)",
                    (int(time.time()),),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _payment_payload(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "invoiceNumber": row["invoice_number"],
            "provider": row["provider"],
            "providerOrderId": row["provider_order_id"],
            "transactionId": row["provider_transaction_id"] or "",
            "method": row["method"],
            "bank": row["bank"],
            "amount": row["amount"],
            "status": row["status"],
            "qrUrl": row["qr_url"],
            "vaNumber": row["va_number"],
            "expiresAt": row["expires_at"],
            "paidAt": row["paid_at"],
        }

    def _order_for_charge(self, connection: sqlite3.Connection, user_id: str, order_id: str) -> dict:
        order = connection.execute(
            """
            SELECT
                o.id, o.invoice_number, o.grand_total, o.shipping_cost,
                o.payment_status, o.phone, u.name, u.email
            FROM orders o
            JOIN users u ON u.id = o.user_id
            WHERE o.id = ? AND o.user_id = ?
            """,
            (order_id, user_id),
        ).fetchone()
        if not order:
            raise LookupError("Order tidak ditemukan.")
        if order["payment_status"] == "paid":
            raise PaymentValidationError("Order sudah dibayar.")
        items = connection.execute(
            """
            SELECT product_name, product_slug, qty, price
            FROM order_items
            WHERE order_id = ?
            ORDER BY id
            """,
            (order_id,),
        ).fetchall()
        attempt = connection.execute(
            "SELECT COUNT(*) FROM payments WHERE order_id = ?",
            (order_id,),
        ).fetchone()[0] + 1
        return {
            "id": order["id"],
            "invoiceNumber": order["invoice_number"],
            "providerOrderId": f"{order['invoice_number']}-P{attempt}",
            "grandTotal": order["grand_total"],
            "shippingCost": order["shipping_cost"],
            "customer": {
                "name": order["name"],
                "email": order["email"],
                "phone": order["phone"],
            },
            "items": [
                {
                    "name": item["product_name"],
                    "slug": item["product_slug"],
                    "qty": item["qty"],
                    "price": item["price"],
                }
                for item in items
            ],
        }

    def create_payment(
        self, user_id: str, order_id: object, method: object, bank: object = ""
    ) -> dict:
        clean_method = str(method or "").strip()
        clean_bank = str(bank or "").strip().lower()
        if clean_method not in PAYMENT_METHODS:
            raise PaymentValidationError(
                "Metode pembayaran tidak valid.",
                {"method": "Pilih QRIS atau bank transfer."},
            )
        if clean_method == "bank_transfer" and clean_bank not in SUPPORTED_BANKS:
            raise PaymentValidationError(
                "Bank tidak valid.",
                {"bank": "Pilih BCA, BNI, BRI, atau Permata."},
            )
        connection = self.connect()
        try:
            order = self._order_for_charge(connection, user_id, str(order_id or ""))
            existing = connection.execute(
                """
                SELECT p.*, o.invoice_number
                FROM payments p
                JOIN orders o ON o.id = p.order_id
                WHERE p.order_id = ? AND p.status = 'pending'
                    AND p.method = ? AND p.bank = ?
                ORDER BY p.created_at DESC
                LIMIT 1
                """,
                (order["id"], clean_method, clean_bank),
            ).fetchone()
            if existing:
                return self._payment_payload(existing)
        finally:
            connection.close()

        response = self.client.charge(order, clean_method, clean_bank)
        transaction_id = str(response.get("transaction_id") or "")
        provider_order_id = str(response.get("order_id") or order["providerOrderId"])
        qr_url = ""
        for action in response.get("actions") or []:
            if action.get("name") in {"generate-qr-code", "generate-qr-code-v2"}:
                qr_url = str(action.get("url") or "")
        va_number = ""
        va_numbers = response.get("va_numbers") or []
        if va_numbers:
            clean_bank = str(va_numbers[0].get("bank") or clean_bank)
            va_number = str(va_numbers[0].get("va_number") or "")
        if not va_number:
            va_number = str(response.get("permata_va_number") or "")
        expires_at = response.get("expiry_time")
        if not isinstance(expires_at, int):
            expires_at = int(time.time()) + 24 * 60 * 60

        now = int(time.time())
        payment_id = str(uuid.uuid4())
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                INSERT INTO payments (
                    id, order_id, provider, provider_order_id,
                    provider_transaction_id, method, bank, amount, status,
                    qr_url, va_number, raw_response, expires_at, created_at, updated_at
                ) VALUES (?, ?, 'midtrans', ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?)
                """,
                (
                    payment_id,
                    order["id"],
                    provider_order_id,
                    transaction_id,
                    clean_method,
                    clean_bank,
                    order["grandTotal"],
                    qr_url,
                    va_number,
                    json.dumps(response, ensure_ascii=True),
                    expires_at,
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                UPDATE orders
                SET payment_status = 'pending', order_status = 'waiting_payment'
                WHERE id = ?
                """,
                (order["id"],),
            )
            row = connection.execute(
                """
                SELECT p.*, o.invoice_number
                FROM payments p JOIN orders o ON o.id = p.order_id
                WHERE p.id = ?
                """,
                (payment_id,),
            ).fetchone()
            connection.commit()
            return self._payment_payload(row)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_order_payments(self, user_id: str, order_id: str) -> list[dict]:
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT p.*, o.invoice_number
                FROM payments p
                JOIN orders o ON o.id = p.order_id
                WHERE p.order_id = ? AND o.user_id = ?
                ORDER BY p.created_at DESC
                """,
                (order_id, user_id),
            ).fetchall()
            return [self._payment_payload(row) for row in rows]
        finally:
            connection.close()

    def verify_signature(self, payload: dict) -> bool:
        if self.client.mock:
            return hmac.compare_digest(
                str(payload.get("signature_key") or ""), "mock-signature"
            )
        raw = "".join(
            [
                str(payload.get("order_id") or ""),
                str(payload.get("status_code") or ""),
                str(payload.get("gross_amount") or ""),
                self.client.server_key,
            ]
        )
        expected = hashlib.sha512(raw.encode("utf-8")).hexdigest()
        return hmac.compare_digest(
            str(payload.get("signature_key") or "").lower(), expected.lower()
        )

    @staticmethod
    def _mapped_status(
        transaction_status: str, fraud_status: str, status_code: str
    ) -> str:
        status = transaction_status.lower()
        fraud = fraud_status.lower()
        if status_code == "200" and fraud == "accept" and status in {
            "settlement",
            "capture",
        }:
            return "paid"
        if status in {"expire"}:
            return "expired"
        if status in {"cancel"}:
            return "cancelled"
        if status in {"deny", "failure"} or (status == "capture" and fraud != "accept"):
            return "failed"
        return "pending"

    def handle_notification(self, payload: object) -> dict:
        if not isinstance(payload, dict):
            raise PaymentValidationError("Payload callback tidak valid.")
        if not self.verify_signature(payload):
            raise PermissionError("Signature callback tidak valid.")
        provider_order_id = str(payload.get("order_id") or "")
        transaction_status = str(payload.get("transaction_status") or "").lower()
        fraud_status = str(payload.get("fraud_status") or "")
        status_code = str(payload.get("status_code") or "")
        try:
            gross_amount = Decimal(str(payload.get("gross_amount") or ""))
        except InvalidOperation as error:
            raise PaymentValidationError("Nominal callback tidak valid.") from error
        event_identity = "|".join(
            [
                provider_order_id,
                str(payload.get("transaction_id") or ""),
                transaction_status,
                str(payload.get("gross_amount") or ""),
            ]
        )
        event_key = hashlib.sha256(event_identity.encode("utf-8")).hexdigest()
        now = int(time.time())
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            payment = connection.execute(
                """
                SELECT p.*, o.user_id, o.invoice_number
                FROM payments p
                JOIN orders o ON o.id = p.order_id
                WHERE p.provider_order_id = ?
                """,
                (provider_order_id,),
            ).fetchone()
            if not payment:
                raise LookupError("Payment tidak ditemukan.")
            if gross_amount != Decimal(payment["amount"]):
                raise PaymentValidationError("Nominal callback tidak sesuai.")
            duplicate = connection.execute(
                "SELECT 1 FROM payment_events WHERE event_key = ?",
                (event_key,),
            ).fetchone()
            if duplicate:
                connection.rollback()
                return {"duplicate": True, "status": payment["status"]}

            mapped = self._mapped_status(
                transaction_status, fraud_status, status_code
            )
            paid_at = now if mapped == "paid" else payment["paid_at"]
            connection.execute(
                """
                UPDATE payments
                SET provider_transaction_id = COALESCE(NULLIF(?, ''), provider_transaction_id),
                    status = ?, paid_at = ?, raw_response = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    str(payload.get("transaction_id") or ""),
                    mapped,
                    paid_at,
                    json.dumps(payload, ensure_ascii=True),
                    now,
                    payment["id"],
                ),
            )
            connection.execute(
                """
                INSERT INTO payment_events (
                    id, payment_id, event_key, transaction_status, payload, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    payment["id"],
                    event_key,
                    transaction_status,
                    json.dumps(payload, ensure_ascii=True),
                    now,
                ),
            )
            order_payment_status = mapped
            order_status = {
                "paid": "paid",
                "pending": "waiting_payment",
                "expired": "cancelled",
                "cancelled": "cancelled",
                "failed": "cancelled",
            }[mapped]
            connection.execute(
                """
                UPDATE orders
                SET payment_status = ?, order_status = ?
                WHERE id = ?
                """,
                (order_payment_status, order_status, payment["order_id"]),
            )
            title = {
                "paid": "Pembayaran berhasil",
                "pending": "Pembayaran menunggu penyelesaian",
                "expired": "Pembayaran kedaluwarsa",
                "cancelled": "Pembayaran dibatalkan",
                "failed": "Pembayaran gagal",
            }[mapped]
            connection.execute(
                """
                INSERT INTO member_notifications (
                    id, user_id, title, message, kind, action_url, created_at
                ) VALUES (?, ?, ?, ?, 'payment', '/member/orders', ?)
                """,
                (
                    str(uuid.uuid4()),
                    payment["user_id"],
                    title,
                    f"Status invoice {payment['invoice_number']}: {mapped}.",
                    now,
                ),
            )
            connection.commit()
            return {"duplicate": False, "status": mapped}
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
