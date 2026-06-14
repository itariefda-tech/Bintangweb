import hashlib
import tempfile
import unittest
from pathlib import Path

from marketplace_auth import AuthStore
from marketplace_catalog import CatalogStore
from marketplace_checkout import CartStore
from marketplace_payment import (
    MidtransClient,
    PaymentStore,
    PaymentValidationError,
)


ADDRESS = {
    "recipientName": "Payment Member",
    "phone": "+62 812-3456-7890",
    "address": "Jl. Payment No. 1",
    "city": "Jakarta",
    "province": "DKI Jakarta",
    "postalCode": "12345",
}


class PaymentStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "marketplace.sqlite3"
        self.auth = AuthStore(self.database)
        self.catalog = CatalogStore(self.database)
        self.cart = CartStore(self.database)
        self.client = MidtransClient(mock=True)
        self.payments = PaymentStore(self.database, self.client)
        self.auth.initialize()
        self.catalog.initialize()
        self.cart.initialize()
        self.payments.initialize()
        self.user = self.auth.register(
            "Payment Member", "payment@example.com", "securepass123"
        )
        self.cart.add_item(self.user["id"], "custom-app-discovery", 1)
        self.order = self.cart.checkout(
            self.user["id"],
            {"address": ADDRESS, "shippingMethod": "digital"},
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_qris_and_bank_transfer_payment_instructions(self):
        qris = self.payments.create_payment(
            self.user["id"], self.order["id"], "qris"
        )
        self.assertEqual("pending", qris["status"])
        self.assertTrue(qris["qrUrl"])

        bank = self.payments.create_payment(
            self.user["id"], self.order["id"], "bank_transfer", "bni"
        )
        self.assertEqual("bni", bank["bank"])
        self.assertTrue(bank["vaNumber"])
        self.assertEqual(
            2,
            len(self.payments.list_order_payments(self.user["id"], self.order["id"])),
        )

    def test_pending_payment_creation_is_idempotent_per_method(self):
        first = self.payments.create_payment(
            self.user["id"], self.order["id"], "qris"
        )
        second = self.payments.create_payment(
            self.user["id"], self.order["id"], "qris"
        )
        self.assertEqual(first["id"], second["id"])

    def test_callback_validates_signature_amount_and_is_idempotent(self):
        payment = self.payments.create_payment(
            self.user["id"], self.order["id"], "qris"
        )
        payload = {
            "order_id": payment["providerOrderId"],
            "status_code": "200",
            "gross_amount": f"{payment['amount']:.2f}",
            "transaction_id": "mock-settlement-1",
            "transaction_status": "settlement",
            "fraud_status": "accept",
            "signature_key": "mock-signature",
        }
        result = self.payments.handle_notification(payload)
        duplicate = self.payments.handle_notification(
            {**payload, "status_message": "Duplicate delivery"}
        )

        self.assertEqual("paid", result["status"])
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(
            "paid", self.cart.list_orders(self.user["id"])[0]["paymentStatus"]
        )
        self.assertGreaterEqual(
            self.auth.list_notifications(self.user["id"])["unreadCount"], 2
        )

        invalid_amount = {**payload, "gross_amount": "1.00"}
        with self.assertRaises(PaymentValidationError):
            self.payments.handle_notification(invalid_amount)

    def test_paid_status_requires_success_code_and_accepted_fraud(self):
        payment = self.payments.create_payment(
            self.user["id"], self.order["id"], "qris"
        )
        result = self.payments.handle_notification(
            {
                "order_id": payment["providerOrderId"],
                "status_code": "202",
                "gross_amount": f"{payment['amount']:.2f}",
                "transaction_id": "mock-review-1",
                "transaction_status": "settlement",
                "fraud_status": "challenge",
                "signature_key": "mock-signature",
            }
        )
        self.assertNotEqual("paid", result["status"])

    def test_invalid_signature_is_rejected(self):
        payment = self.payments.create_payment(
            self.user["id"], self.order["id"], "qris"
        )
        with self.assertRaises(PermissionError):
            self.payments.handle_notification(
                {
                    "order_id": payment["providerOrderId"],
                    "status_code": "200",
                    "gross_amount": f"{payment['amount']:.2f}",
                    "transaction_status": "settlement",
                    "fraud_status": "accept",
                    "signature_key": "wrong",
                }
            )

    def test_real_midtrans_signature_formula(self):
        client = MidtransClient(server_key="server-key", mock=False)
        store = PaymentStore(self.database, client)
        payload = {
            "order_id": "ORDER-1",
            "status_code": "200",
            "gross_amount": "2500000.00",
        }
        raw = "ORDER-1" + "200" + "2500000.00" + "server-key"
        payload["signature_key"] = hashlib.sha512(raw.encode()).hexdigest()
        self.assertTrue(store.verify_signature(payload))

    def test_payment_validation_and_schema_migration(self):
        with self.assertRaises(PaymentValidationError):
            self.payments.create_payment(
                self.user["id"], self.order["id"], "bank_transfer", "invalid"
            )
        connection = self.payments.connect()
        try:
            versions = [
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                ).fetchall()
            ]
        finally:
            connection.close()
        self.assertEqual([1, 2, 3, 4, 5, 6], versions)


if __name__ == "__main__":
    unittest.main()
