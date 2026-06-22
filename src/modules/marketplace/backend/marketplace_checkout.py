from __future__ import annotations

import re
import secrets
import sqlite3
import time
import uuid
from pathlib import Path


MAX_CART_QTY = 99
NAME_MAX_LENGTH = 120
PHONE_MAX_LENGTH = 24
ADDRESS_MAX_LENGTH = 300
LOCATION_MAX_LENGTH = 100
POSTAL_CODE_MAX_LENGTH = 12
PHONE_PATTERN = re.compile(r"^[0-9+().\-\s]{6,24}$")
POSTAL_CODE_PATTERN = re.compile(r"^[A-Za-z0-9\-\s]{3,12}$")


class CheckoutValidationError(ValueError):
    def __init__(self, message: str, errors: dict[str, str] | None = None):
        super().__init__(message)
        self.errors = errors or {}


class StockConflictError(ValueError):
    pass


class CartStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path

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
            if 5 not in applied:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS carts (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'converted', 'abandoned')),
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );

                    CREATE UNIQUE INDEX IF NOT EXISTS idx_carts_active_user
                        ON carts(user_id) WHERE status = 'active';

                    CREATE TABLE IF NOT EXISTS cart_items (
                        id TEXT PRIMARY KEY,
                        cart_id TEXT NOT NULL,
                        product_id TEXT NOT NULL,
                        qty INTEGER NOT NULL CHECK (qty BETWEEN 1 AND 99),
                        price INTEGER NOT NULL CHECK (price >= 0),
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        UNIQUE(cart_id, product_id),
                        FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
                        FOREIGN KEY (product_id) REFERENCES products(id)
                    );

                    CREATE TABLE IF NOT EXISTS member_addresses (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        label TEXT NOT NULL,
                        recipient_name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        address TEXT NOT NULL,
                        city TEXT NOT NULL,
                        province TEXT NOT NULL,
                        postal_code TEXT NOT NULL,
                        is_default INTEGER NOT NULL DEFAULT 0 CHECK (is_default IN (0, 1)),
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_member_addresses_user
                        ON member_addresses(user_id, is_default DESC, created_at DESC);

                    CREATE TABLE IF NOT EXISTS orders (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        invoice_number TEXT NOT NULL UNIQUE,
                        address_id TEXT,
                        recipient_name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        shipping_address TEXT NOT NULL,
                        city TEXT NOT NULL,
                        province TEXT NOT NULL,
                        postal_code TEXT NOT NULL,
                        shipping_method TEXT NOT NULL,
                        subtotal INTEGER NOT NULL CHECK (subtotal >= 0),
                        shipping_cost INTEGER NOT NULL CHECK (shipping_cost >= 0),
                        grand_total INTEGER NOT NULL CHECK (grand_total >= 0),
                        payment_status TEXT NOT NULL DEFAULT 'unpaid',
                        order_status TEXT NOT NULL DEFAULT 'pending',
                        created_at INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (address_id) REFERENCES member_addresses(id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_orders_user
                        ON orders(user_id, created_at DESC);

                    CREATE TABLE IF NOT EXISTS order_items (
                        id TEXT PRIMARY KEY,
                        order_id TEXT NOT NULL,
                        product_id TEXT NOT NULL,
                        product_name TEXT NOT NULL,
                        product_slug TEXT NOT NULL,
                        qty INTEGER NOT NULL CHECK (qty > 0),
                        price INTEGER NOT NULL CHECK (price >= 0),
                        subtotal INTEGER NOT NULL CHECK (subtotal >= 0),
                        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                        FOREIGN KEY (product_id) REFERENCES products(id)
                    );
                    """
                )
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (5, ?)",
                    (int(time.time()),),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _normalize(value: object) -> str:
        return " ".join(str(value or "").strip().split())

    @classmethod
    def validate_address(cls, payload: object) -> dict:
        if not isinstance(payload, dict):
            raise CheckoutValidationError("Data alamat tidak valid.")
        fields = {
            "label": cls._normalize(payload.get("label")) or "Alamat utama",
            "recipientName": cls._normalize(payload.get("recipientName")),
            "phone": cls._normalize(payload.get("phone")),
            "address": str(payload.get("address") or "").strip(),
            "city": cls._normalize(payload.get("city")),
            "province": cls._normalize(payload.get("province")),
            "postalCode": cls._normalize(payload.get("postalCode")),
            "isDefault": bool(payload.get("isDefault")),
        }
        errors = {}
        if not 2 <= len(fields["recipientName"]) <= NAME_MAX_LENGTH:
            errors["recipientName"] = "Nama penerima harus 2-120 karakter."
        if not PHONE_PATTERN.fullmatch(fields["phone"]):
            errors["phone"] = "Nomor telepon tidak valid."
        if not 8 <= len(fields["address"]) <= ADDRESS_MAX_LENGTH:
            errors["address"] = "Alamat harus 8-300 karakter."
        for key, label in (("city", "Kota"), ("province", "Provinsi")):
            if not 2 <= len(fields[key]) <= LOCATION_MAX_LENGTH:
                errors[key] = f"{label} harus 2-100 karakter."
        if not POSTAL_CODE_PATTERN.fullmatch(fields["postalCode"]):
            errors["postalCode"] = "Kode pos tidak valid."
        if len(fields["label"]) > 50:
            errors["label"] = "Label maksimal 50 karakter."
        if errors:
            raise CheckoutValidationError("Data alamat belum valid.", errors)
        return fields

    @staticmethod
    def _validate_qty(qty: object) -> int:
        try:
            clean_qty = int(qty)
        except (TypeError, ValueError):
            raise CheckoutValidationError("Jumlah produk tidak valid.", {"qty": "Jumlah tidak valid."})
        if not 1 <= clean_qty <= MAX_CART_QTY:
            raise CheckoutValidationError(
                "Jumlah produk tidak valid.",
                {"qty": f"Jumlah harus 1-{MAX_CART_QTY}."},
            )
        return clean_qty

    @staticmethod
    def _cart_id(connection: sqlite3.Connection, user_id: str, create: bool = True) -> str | None:
        row = connection.execute(
            "SELECT id FROM carts WHERE user_id = ? AND status = 'active'",
            (user_id,),
        ).fetchone()
        if row:
            return row["id"]
        if not create:
            return None
        now = int(time.time())
        cart_id = str(uuid.uuid4())
        connection.execute(
            """
            INSERT INTO carts (id, user_id, status, created_at, updated_at)
            VALUES (?, ?, 'active', ?, ?)
            """,
            (cart_id, user_id, now, now),
        )
        return cart_id

    @staticmethod
    def _cart_payload(connection: sqlite3.Connection, user_id: str) -> dict:
        cart_id = CartStore._cart_id(connection, user_id, create=False)
        if not cart_id:
            return {"id": None, "items": [], "itemCount": 0, "subtotal": 0}
        rows = connection.execute(
            """
            SELECT
                ci.id,
                ci.qty,
                ci.price,
                p.slug,
                p.name,
                p.thumbnail,
                p.stock,
                p.status
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.cart_id = ?
            ORDER BY ci.created_at, ci.id
            """,
            (cart_id,),
        ).fetchall()
        items = []
        for row in rows:
            available = row["status"] == "active" and row["stock"] > 0
            items.append(
                {
                    "id": row["id"],
                    "slug": row["slug"],
                    "name": row["name"],
                    "image": row["thumbnail"],
                    "qty": row["qty"],
                    "price": row["price"],
                    "subtotal": row["qty"] * row["price"],
                    "stock": row["stock"],
                    "available": available,
                }
            )
        return {
            "id": cart_id,
            "items": items,
            "itemCount": sum(item["qty"] for item in items),
            "subtotal": sum(item["subtotal"] for item in items),
        }

    def get_cart(self, user_id: str) -> dict:
        connection = self.connect()
        try:
            return self._cart_payload(connection, user_id)
        finally:
            connection.close()

    def add_item(self, user_id: str, product_slug: object, qty: object = 1) -> dict:
        clean_qty = self._validate_qty(qty)
        slug = str(product_slug or "").strip().lower()[:160]
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            product = connection.execute(
                """
                SELECT id, price, stock, status
                FROM products
                WHERE slug = ?
                """,
                (slug,),
            ).fetchone()
            if not product or product["status"] not in {"active", "out_of_stock"}:
                raise LookupError("Produk tidak ditemukan.")
            if product["status"] != "active" or product["stock"] <= 0:
                raise StockConflictError("Stok produk sedang habis.")
            cart_id = self._cart_id(connection, user_id)
            existing = connection.execute(
                "SELECT id, qty FROM cart_items WHERE cart_id = ? AND product_id = ?",
                (cart_id, product["id"]),
            ).fetchone()
            total_qty = clean_qty + (existing["qty"] if existing else 0)
            if total_qty > product["stock"]:
                raise StockConflictError(
                    f"Stok hanya tersedia {product['stock']} unit."
                )
            now = int(time.time())
            if existing:
                connection.execute(
                    """
                    UPDATE cart_items
                    SET qty = ?, price = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (total_qty, product["price"], now, existing["id"]),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO cart_items (
                        id, cart_id, product_id, qty, price, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        cart_id,
                        product["id"],
                        clean_qty,
                        product["price"],
                        now,
                        now,
                    ),
                )
            connection.execute(
                "UPDATE carts SET updated_at = ? WHERE id = ?",
                (now, cart_id),
            )
            cart = self._cart_payload(connection, user_id)
            connection.commit()
            return cart
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def update_item(self, user_id: str, item_id: str, qty: object) -> dict:
        clean_qty = self._validate_qty(qty)
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT ci.id, ci.cart_id, p.stock, p.status, p.price
                FROM cart_items ci
                JOIN carts c ON c.id = ci.cart_id
                JOIN products p ON p.id = ci.product_id
                WHERE ci.id = ? AND c.user_id = ? AND c.status = 'active'
                """,
                (item_id, user_id),
            ).fetchone()
            if not row:
                raise LookupError("Item cart tidak ditemukan.")
            if row["status"] != "active" or clean_qty > row["stock"]:
                raise StockConflictError(f"Stok hanya tersedia {row['stock']} unit.")
            now = int(time.time())
            connection.execute(
                "UPDATE cart_items SET qty = ?, price = ?, updated_at = ? WHERE id = ?",
                (clean_qty, row["price"], now, item_id),
            )
            connection.execute(
                "UPDATE carts SET updated_at = ? WHERE id = ?",
                (now, row["cart_id"]),
            )
            cart = self._cart_payload(connection, user_id)
            connection.commit()
            return cart
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def remove_item(self, user_id: str, item_id: str) -> dict:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            deleted = connection.execute(
                """
                DELETE FROM cart_items
                WHERE id = ?
                    AND cart_id IN (
                        SELECT id FROM carts WHERE user_id = ? AND status = 'active'
                    )
                """,
                (item_id, user_id),
            )
            if deleted.rowcount != 1:
                raise LookupError("Item cart tidak ditemukan.")
            cart = self._cart_payload(connection, user_id)
            connection.commit()
            return cart
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _public_address(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "label": row["label"],
            "recipientName": row["recipient_name"],
            "phone": row["phone"],
            "address": row["address"],
            "city": row["city"],
            "province": row["province"],
            "postalCode": row["postal_code"],
            "isDefault": bool(row["is_default"]),
        }

    def list_addresses(self, user_id: str) -> list[dict]:
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT *
                FROM member_addresses
                WHERE user_id = ?
                ORDER BY is_default DESC, created_at DESC
                """,
                (user_id,),
            ).fetchall()
            return [self._public_address(row) for row in rows]
        finally:
            connection.close()

    def save_address(self, user_id: str, payload: object) -> dict:
        fields = self.validate_address(payload)
        address_id = str(payload.get("id") or "").strip() if isinstance(payload, dict) else ""
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            now = int(time.time())
            if fields["isDefault"]:
                connection.execute(
                    "UPDATE member_addresses SET is_default = 0 WHERE user_id = ?",
                    (user_id,),
                )
            if address_id:
                updated = connection.execute(
                    """
                    UPDATE member_addresses
                    SET label = ?, recipient_name = ?, phone = ?, address = ?,
                        city = ?, province = ?, postal_code = ?, is_default = ?,
                        updated_at = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (
                        fields["label"],
                        fields["recipientName"],
                        fields["phone"],
                        fields["address"],
                        fields["city"],
                        fields["province"],
                        fields["postalCode"],
                        int(fields["isDefault"]),
                        now,
                        address_id,
                        user_id,
                    ),
                )
                if updated.rowcount != 1:
                    raise LookupError("Alamat tidak ditemukan.")
            else:
                address_id = str(uuid.uuid4())
                connection.execute(
                    """
                    INSERT INTO member_addresses (
                        id, user_id, label, recipient_name, phone, address, city,
                        province, postal_code, is_default, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        address_id,
                        user_id,
                        fields["label"],
                        fields["recipientName"],
                        fields["phone"],
                        fields["address"],
                        fields["city"],
                        fields["province"],
                        fields["postalCode"],
                        int(fields["isDefault"]),
                        now,
                        now,
                    ),
                )
            row = connection.execute(
                "SELECT * FROM member_addresses WHERE id = ?",
                (address_id,),
            ).fetchone()
            connection.commit()
            return self._public_address(row)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _invoice_number(now: int) -> str:
        stamp = time.strftime("%Y%m%d", time.gmtime(now))
        return f"FRA-{stamp}-{secrets.token_hex(3).upper()}"

    @staticmethod
    def _shipping_cost(method: str) -> int:
        costs = {"standard": 25000, "priority": 75000, "digital": 0}
        if method not in costs:
            raise CheckoutValidationError(
                "Metode pengiriman tidak valid.",
                {"shippingMethod": "Pilih metode pengiriman yang tersedia."},
            )
        return costs[method]

    def checkout(self, user_id: str, payload: object) -> dict:
        if not isinstance(payload, dict):
            raise CheckoutValidationError("Data checkout tidak valid.")
        shipping_method = str(payload.get("shippingMethod") or "standard").strip()
        shipping_cost = self._shipping_cost(shipping_method)
        address_id = str(payload.get("addressId") or "").strip()
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            cart_id = self._cart_id(connection, user_id, create=False)
            if not cart_id:
                raise CheckoutValidationError("Cart masih kosong.")
            rows = connection.execute(
                """
                SELECT
                    ci.id AS cart_item_id,
                    ci.product_id,
                    ci.qty,
                    p.name,
                    p.slug,
                    p.price,
                    p.stock,
                    p.status
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                WHERE ci.cart_id = ?
                ORDER BY ci.created_at
                """,
                (cart_id,),
            ).fetchall()
            if not rows:
                raise CheckoutValidationError("Cart masih kosong.")

            if address_id:
                address = connection.execute(
                    "SELECT * FROM member_addresses WHERE id = ? AND user_id = ?",
                    (address_id, user_id),
                ).fetchone()
                if not address:
                    raise CheckoutValidationError(
                        "Alamat tidak ditemukan.", {"addressId": "Alamat tidak ditemukan."}
                    )
                fields = {
                    "recipientName": address["recipient_name"],
                    "phone": address["phone"],
                    "address": address["address"],
                    "city": address["city"],
                    "province": address["province"],
                    "postalCode": address["postal_code"],
                }
            else:
                fields = self.validate_address(payload.get("address"))

            subtotal = 0
            for row in rows:
                if row["status"] != "active" or row["stock"] < row["qty"]:
                    raise StockConflictError(
                        f"Stok {row['name']} berubah. Tersedia {row['stock']} unit."
                    )
                subtotal += row["price"] * row["qty"]

            now = int(time.time())
            order_id = str(uuid.uuid4())
            invoice = self._invoice_number(now)
            grand_total = subtotal + shipping_cost
            connection.execute(
                """
                INSERT INTO orders (
                    id, user_id, invoice_number, address_id, recipient_name, phone,
                    shipping_address, city, province, postal_code, shipping_method,
                    subtotal, shipping_cost, grand_total, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    user_id,
                    invoice,
                    address_id or None,
                    fields["recipientName"],
                    fields["phone"],
                    fields["address"],
                    fields["city"],
                    fields["province"],
                    fields["postalCode"],
                    shipping_method,
                    subtotal,
                    shipping_cost,
                    grand_total,
                    now,
                ),
            )
            order_items = []
            for row in rows:
                reduced = connection.execute(
                    """
                    UPDATE products
                    SET stock = stock - ?,
                        status = CASE WHEN stock - ? = 0 THEN 'out_of_stock' ELSE status END,
                        updated_at = ?
                    WHERE id = ? AND status = 'active' AND stock >= ?
                    """,
                    (row["qty"], row["qty"], now, row["product_id"], row["qty"]),
                )
                if reduced.rowcount != 1:
                    raise StockConflictError(f"Stok {row['name']} tidak lagi tersedia.")
                item_subtotal = row["price"] * row["qty"]
                connection.execute(
                    """
                    INSERT INTO order_items (
                        id, order_id, product_id, product_name, product_slug,
                        qty, price, subtotal
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        order_id,
                        row["product_id"],
                        row["name"],
                        row["slug"],
                        row["qty"],
                        row["price"],
                        item_subtotal,
                    ),
                )
                order_items.append(
                    {
                        "name": row["name"],
                        "slug": row["slug"],
                        "qty": row["qty"],
                        "price": row["price"],
                        "subtotal": item_subtotal,
                    }
                )
            connection.execute(
                "UPDATE carts SET status = 'converted', updated_at = ? WHERE id = ?",
                (now, cart_id),
            )
            connection.execute(
                """
                INSERT INTO member_notifications (
                    id, user_id, title, message, kind, action_url, created_at
                ) VALUES (?, ?, ?, ?, 'order', '/member/orders', ?)
                """,
                (
                    str(uuid.uuid4()),
                    user_id,
                    "Order berhasil dibuat",
                    f"Invoice {invoice} menunggu proses pembayaran.",
                    now,
                ),
            )
            connection.commit()
            return {
                "id": order_id,
                "invoiceNumber": invoice,
                "items": order_items,
                "subtotal": subtotal,
                "shippingCost": shipping_cost,
                "grandTotal": grand_total,
                "paymentStatus": "unpaid",
                "orderStatus": "pending",
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_orders(self, user_id: str) -> list[dict]:
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT id, invoice_number, subtotal, shipping_cost, grand_total,
                       payment_status, order_status, created_at
                FROM orders
                WHERE user_id = ?
                ORDER BY created_at DESC, invoice_number DESC
                """,
                (user_id,),
            ).fetchall()
            return [
                {
                    "id": row["id"],
                    "invoiceNumber": row["invoice_number"],
                    "subtotal": row["subtotal"],
                    "shippingCost": row["shipping_cost"],
                    "grandTotal": row["grand_total"],
                    "paymentStatus": row["payment_status"],
                    "orderStatus": row["order_status"],
                    "createdAt": row["created_at"],
                }
                for row in rows
            ]
        finally:
            connection.close()
