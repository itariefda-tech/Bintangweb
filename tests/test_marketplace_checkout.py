import tempfile
import unittest
from pathlib import Path

from marketplace_auth import AuthStore
from marketplace_catalog import CatalogStore
from marketplace_checkout import (
    CartStore,
    CheckoutValidationError,
    StockConflictError,
)


ADDRESS = {
    "label": "Kantor",
    "recipientName": "Feira Member",
    "phone": "+62 812-3456-7890",
    "address": "Jl. Teknologi No. 1",
    "city": "Jakarta",
    "province": "DKI Jakarta",
    "postalCode": "12345",
    "isDefault": True,
}


class CartCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "marketplace.sqlite3"
        self.auth = AuthStore(self.database)
        self.catalog = CatalogStore(self.database)
        self.cart = CartStore(self.database)
        self.auth.initialize()
        self.catalog.initialize()
        self.cart.initialize()
        self.user = self.auth.register(
            "Feira Member", "member@example.com", "securepass123"
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_cart_add_update_remove_and_persistence(self):
        added = self.cart.add_item(
            self.user["id"], "business-laptop-foundation", 2
        )
        self.assertEqual(2, added["itemCount"])
        self.assertEqual(2 * 8999000, added["subtotal"])

        reloaded = CartStore(self.database)
        persisted = reloaded.get_cart(self.user["id"])
        self.assertEqual(2, persisted["items"][0]["qty"])

        updated = reloaded.update_item(
            self.user["id"], persisted["items"][0]["id"], 3
        )
        self.assertEqual(3, updated["itemCount"])

        removed = reloaded.remove_item(
            self.user["id"], updated["items"][0]["id"]
        )
        self.assertEqual(0, removed["itemCount"])

    def test_add_and_update_validate_server_stock(self):
        with self.assertRaises(StockConflictError):
            self.cart.add_item(self.user["id"], "smart-surveillance-kit", 1)
        with self.assertRaises(StockConflictError):
            self.cart.add_item(self.user["id"], "company-website-launch", 5)

        cart = self.cart.add_item(self.user["id"], "company-website-launch", 1)
        with self.assertRaises(StockConflictError):
            self.cart.update_item(
                self.user["id"], cart["items"][0]["id"], 5
            )

    def test_address_management_and_validation(self):
        saved = self.cart.save_address(self.user["id"], ADDRESS)
        self.assertTrue(saved["isDefault"])
        self.assertEqual("Jakarta", saved["city"])
        self.assertEqual(saved["id"], self.cart.list_addresses(self.user["id"])[0]["id"])

        with self.assertRaises(CheckoutValidationError):
            self.cart.save_address(
                self.user["id"], {**ADDRESS, "phone": "invalid"}
            )

    def test_checkout_creates_invoice_decrements_stock_and_converts_cart(self):
        self.cart.add_item(self.user["id"], "company-website-launch", 2)
        address = self.cart.save_address(self.user["id"], ADDRESS)
        before = self.catalog.get_product("company-website-launch")

        order = self.cart.checkout(
            self.user["id"],
            {"addressId": address["id"], "shippingMethod": "standard"},
        )

        after = self.catalog.get_product("company-website-launch")
        self.assertTrue(order["invoiceNumber"].startswith("FRA-"))
        self.assertEqual(2, before["stock"] - after["stock"])
        self.assertEqual(25000, order["shippingCost"])
        self.assertEqual(order["subtotal"] + 25000, order["grandTotal"])
        self.assertEqual(0, self.cart.get_cart(self.user["id"])["itemCount"])
        self.assertEqual(
            order["invoiceNumber"],
            self.cart.list_orders(self.user["id"])[0]["invoiceNumber"],
        )

    def test_checkout_is_atomic_when_stock_changes(self):
        second = self.auth.register(
            "Second Member", "second@example.com", "securepass123"
        )
        first_cart = self.cart.add_item(
            self.user["id"], "company-website-launch", 3
        )
        second_cart = self.cart.add_item(
            second["id"], "company-website-launch", 2
        )
        self.assertEqual(3, first_cart["itemCount"])
        self.assertEqual(2, second_cart["itemCount"])

        self.cart.checkout(
            self.user["id"],
            {"address": ADDRESS, "shippingMethod": "standard"},
        )
        with self.assertRaises(StockConflictError):
            self.cart.checkout(
                second["id"],
                {"address": {**ADDRESS, "recipientName": "Second Member"}, "shippingMethod": "standard"},
            )

        product = self.catalog.get_product("company-website-launch")
        self.assertEqual(1, product["stock"])
        self.assertEqual(2, self.cart.get_cart(second["id"])["itemCount"])
        self.assertEqual([], self.cart.list_orders(second["id"]))

    def test_schema_migration_is_idempotent(self):
        self.cart.initialize()
        connection = self.cart.connect()
        try:
            versions = [
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                ).fetchall()
            ]
        finally:
            connection.close()
        self.assertEqual([1, 2, 3, 4, 5], versions)


if __name__ == "__main__":
    unittest.main()
