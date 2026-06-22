import tempfile
import unittest
from pathlib import Path

from src.modules.marketplace.backend.marketplace_admin import (
    AdminStore,
    AdminValidationError,
)
from src.modules.marketplace.backend.marketplace_auth import AuthStore
from src.modules.marketplace.backend.marketplace_catalog import CatalogStore
from src.modules.marketplace.backend.marketplace_checkout import CartStore
from src.modules.marketplace.backend.marketplace_consultation import ConsultationStore


class AdminStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "marketplace.sqlite3"
        self.auth = AuthStore(self.database)
        self.catalog = CatalogStore(self.database)
        self.cart = CartStore(self.database)
        self.consultation = ConsultationStore(
            self.database,
            Path(self.temporary.name) / "consultation-media",
        )
        self.auth.initialize()
        self.catalog.initialize()
        self.cart.initialize()
        self.consultation.initialize()
        self.store = AdminStore(self.database)
        self.store.initialize()
        self.member = self.auth.register(
            "Member User",
            "member@example.com",
            "password123",
        )
        self.admin = self.auth.register(
            "Admin User",
            "admin@example.com",
            "password123",
        )
        with self.auth.connection() as connection:
            connection.execute(
                "UPDATE users SET role = 'admin' WHERE id = ?",
                (self.admin["id"],),
            )
        self.admin["role"] = "admin"
        self.super_admin = self.auth.register(
            "Super Admin",
            "super@example.com",
            "password123",
        )
        with self.auth.connection() as connection:
            connection.execute(
                "UPDATE users SET role = 'super_admin' WHERE id = ?",
                (self.super_admin["id"],),
            )
        self.super_admin["role"] = "super_admin"

    def tearDown(self):
        self.temporary.cleanup()

    def test_dashboard_kpis_summarize_existing_data(self):
        self.consultation.create_ticket(
            self.member["id"],
            {
                "subject": "Server kantor tidak stabil",
                "category": "Infrastructure",
                "priority": "urgent",
                "message": "Server kantor restart sendiri beberapa kali hari ini.",
            },
        )

        kpis = self.store.dashboard_kpis(self.admin)

        self.assertEqual(3, kpis["totalMembers"])
        self.assertEqual(3, kpis["activeMembers"])
        self.assertEqual(0, kpis["totalOrders"])
        self.assertEqual(0, kpis["paidRevenue"])
        self.assertEqual(0, kpis["pendingPayments"])
        self.assertEqual(1, kpis["activeTickets"])
        self.assertEqual(1, kpis["urgentTickets"])

    def test_dashboard_kpis_reject_member_role(self):
        with self.assertRaises(PermissionError):
            self.store.dashboard_kpis(self.member)

    def _create_paid_order(self):
        self.cart.add_item(self.member["id"], "company-website-launch", 1)
        order = self.cart.checkout(
            self.member["id"],
            {
                "address": {
                    "label": "Kantor",
                    "recipientName": "Member User",
                    "phone": "+62 812-3456-7890",
                    "address": "Jl. Teknologi No. 1",
                    "city": "Jakarta",
                    "province": "DKI Jakarta",
                    "postalCode": "12345",
                },
                "shippingMethod": "standard",
            },
        )
        connection = self.cart.connect()
        try:
            connection.execute(
                """
                UPDATE orders
                SET payment_status = 'paid', order_status = 'paid'
                WHERE id = ?
                """,
                (order["id"],),
            )
            connection.commit()
        finally:
            connection.close()
        return order

    def test_order_monitoring_filters_and_returns_invoice_detail(self):
        order = self._create_paid_order()

        listed = self.store.list_orders(
            self.admin,
            payment_status="paid",
            order_status="paid",
        )
        detail = self.store.get_order(self.admin, order["id"])

        self.assertEqual([order["id"]], [item["id"] for item in listed])
        self.assertEqual("Member User", detail["customer"]["name"])
        self.assertEqual("Jakarta", detail["shipping"]["city"])
        self.assertEqual("company-website-launch", detail["items"][0]["slug"])
        self.assertEqual("processing", detail["nextFulfillmentStatus"])

    def test_fulfillment_transition_is_sequential_and_notifies_member(self):
        order = self._create_paid_order()

        processing = self.store.update_fulfillment(
            self.admin,
            order["id"],
            "processing",
        )
        shipped = self.store.update_fulfillment(
            self.admin,
            order["id"],
            "shipped",
        )
        completed = self.store.update_fulfillment(
            self.admin,
            order["id"],
            "completed",
        )

        self.assertEqual("processing", processing["orderStatus"])
        self.assertEqual("shipped", shipped["orderStatus"])
        self.assertEqual("completed", completed["orderStatus"])
        self.assertIsNone(completed["nextFulfillmentStatus"])
        notifications = self.auth.list_notifications(self.member["id"])
        self.assertTrue(
            any(
                order["invoiceNumber"] in item["message"]
                and "completed" in item["message"]
                for item in notifications["items"]
            )
        )
        logs = self.store.list_audit_logs(self.admin)
        fulfillment_logs = [
            item for item in logs if item["action"] == "order.fulfillment_update"
        ]
        self.assertEqual(3, len(fulfillment_logs))
        self.assertEqual(order["id"], fulfillment_logs[0]["targetId"])
        self.assertEqual("completed", fulfillment_logs[0]["details"]["toStatus"])

    def test_fulfillment_rejects_unpaid_and_status_jump(self):
        self.cart.add_item(self.member["id"], "company-website-launch", 1)
        unpaid = self.cart.checkout(
            self.member["id"],
            {
                "address": {
                    "label": "Kantor",
                    "recipientName": "Member User",
                    "phone": "+62 812-3456-7890",
                    "address": "Jl. Teknologi No. 1",
                    "city": "Jakarta",
                    "province": "DKI Jakarta",
                    "postalCode": "12345",
                },
                "shippingMethod": "standard",
            },
        )
        with self.assertRaises(AdminValidationError):
            self.store.update_fulfillment(self.admin, unpaid["id"], "processing")

        connection = self.cart.connect()
        try:
            connection.execute(
                """
                UPDATE orders
                SET payment_status = 'paid', order_status = 'paid'
                WHERE id = ?
                """,
                (unpaid["id"],),
            )
            connection.commit()
        finally:
            connection.close()
        with self.assertRaises(AdminValidationError):
            self.store.update_fulfillment(self.admin, unpaid["id"], "shipped")

    def test_admin_can_create_update_and_archive_product(self):
        created = self.store.save_product(
            self.admin,
            {
                "name": "Admin Managed Switch",
                "slug": "admin-managed-switch",
                "category": "network",
                "shortDescription": "Switch managed untuk operasional kantor.",
                "description": "Switch managed dengan konfigurasi VLAN dan dokumentasi.",
                "price": 2800000,
                "stock": 6,
                "thumbnail": "/assets/images/service-network.webp",
                "images": ["/assets/images/service-network.webp"],
                "status": "active",
                "featured": True,
                "badge": "Admin managed",
            },
        )
        self.assertIn(
            created["id"],
            [product["id"] for product in self.store.list_products(self.admin)],
        )

        updated = self.store.save_product(
            self.admin,
            {
                **created,
                "category": created["category"]["slug"],
                "thumbnail": created["image"],
                "price": 3000000,
            },
            created["id"],
        )
        self.assertEqual(3000000, updated["price"])

        archived = self.store.archive_product(self.admin, created["id"])
        self.assertEqual("archived", archived["status"])
        logs = self.store.list_audit_logs(self.admin)
        self.assertEqual(
            ["product.archived", "product.updated", "product.created"],
            [item["action"] for item in logs[:3]],
        )
        self.assertEqual(created["id"], logs[0]["targetId"])
        self.assertEqual("admin@example.com", logs[0]["actor"]["email"])

    def test_member_cannot_manage_products(self):
        with self.assertRaises(PermissionError):
            self.store.list_products(self.member)
        with self.assertRaises(PermissionError):
            self.store.save_product(self.member, {})
        with self.assertRaises(PermissionError):
            self.store.archive_product(self.member, "missing")
        with self.assertRaises(PermissionError):
            self.store.list_audit_logs(self.member)

    def test_member_status_and_role_updates_are_audited(self):
        suspended = self.store.update_member_status(
            self.admin,
            self.member["id"],
            "suspended",
        )
        promoted = self.store.update_member_role(
            self.super_admin,
            self.member["id"],
            "admin",
        )

        self.assertEqual("suspended", suspended["status"])
        self.assertEqual("admin", promoted["role"])
        logs = self.store.list_audit_logs(self.admin)
        self.assertEqual(
            ["member.role_updated", "member.status_updated"],
            [item["action"] for item in logs[:2]],
        )
        self.assertEqual("member", logs[0]["targetType"])
        self.assertEqual(self.member["id"], logs[0]["targetId"])
        self.assertEqual("member", logs[0]["details"]["fromRole"])
        self.assertEqual("admin", logs[0]["details"]["toRole"])
        self.assertEqual("active", logs[1]["details"]["fromStatus"])
        self.assertEqual("suspended", logs[1]["details"]["toStatus"])


if __name__ == "__main__":
    unittest.main()
