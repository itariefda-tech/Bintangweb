import tempfile
import unittest
import base64
from pathlib import Path

from marketplace_auth import AuthStore
from marketplace_consultation import ConsultationStore, ConsultationValidationError


class ConsultationStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "marketplace.sqlite3"
        self.auth = AuthStore(self.database)
        self.auth.initialize()
        self.store = ConsultationStore(
            self.database,
            Path(self.temporary.name) / "consultation-media",
        )
        self.store.initialize()
        self.member = self.auth.register("Member User", "member@example.com", "password123")
        self.admin = self.auth.register("Admin User", "admin@example.com", "password123")
        with self.auth.connection() as connection:
            connection.execute("UPDATE users SET role = 'admin' WHERE id = ?", (self.admin["id"],))
        self.admin["role"] = "admin"

    def tearDown(self):
        self.temporary.cleanup()

    def test_member_can_create_ticket_and_reply(self):
        ticket = self.store.create_ticket(
            self.member["id"],
            {
                "subject": "Audit jaringan kantor",
                "category": "Network",
                "priority": "high",
                "message": "Jaringan kantor sering lambat saat meeting online.",
            },
        )

        self.assertTrue(ticket["number"].startswith("CS-"))
        self.assertEqual("open", ticket["status"])
        self.assertEqual(1, len(ticket["replies"]))

        replied = self.store.add_reply(
            {**self.member, "role": "member"},
            ticket["id"],
            "Saya tambahkan denah kantor pada sesi berikutnya.",
        )

        self.assertEqual("in_review", replied["status"])
        self.assertEqual(2, len(replied["replies"]))
        self.assertEqual(1, len(self.store.list_tickets(self.member["id"])))

    def test_admin_queue_and_status_update(self):
        ticket = self.store.create_ticket(
            self.member["id"],
            {
                "subject": "CCTV gudang offline",
                "category": "CCTV",
                "priority": "urgent",
                "message": "Dua kamera gudang tidak dapat dipantau dari aplikasi.",
            },
        )

        queue = self.store.admin_queue(self.admin)
        self.assertEqual([ticket["id"]], [item["id"] for item in queue])
        self.assertEqual(1, len(queue[0]["replies"]))
        self.assertEqual(self.member["email"], queue[0]["member"]["email"])

        updated = self.store.update_status(self.admin, ticket["id"], "resolved")
        self.assertEqual("resolved", updated["status"])

        with self.assertRaises(PermissionError):
            self.store.admin_queue({**self.member, "role": "member"})

    def test_admin_can_reply_and_attachment_download_is_private(self):
        other_member = self.auth.register(
            "Other Member",
            "other@example.com",
            "password123",
        )
        attachment_data = base64.b64encode(b"%PDF-1.4\nprivate consultation").decode("ascii")
        ticket = self.store.create_ticket(
            self.member["id"],
            {
                "subject": "Review dokumen infrastruktur",
                "category": "Network",
                "priority": "normal",
                "message": "Mohon review rancangan infrastruktur terlampir.",
                "attachment": {
                    "filename": "rancangan.pdf",
                    "data": f"data:application/pdf;base64,{attachment_data}",
                },
            },
        )

        attachment = ticket["attachments"][0]
        self.assertEqual(
            f"/api/v1/consultation/attachments/{attachment['id']}",
            attachment["downloadUrl"],
        )
        download = self.store.get_attachment(self.member, attachment["id"])
        self.assertEqual(b"%PDF-1.4\nprivate consultation", download["path"].read_bytes())
        self.assertEqual("rancangan.pdf", download["filename"])

        with self.assertRaises(LookupError):
            self.store.get_attachment(other_member, attachment["id"])

        admin_download = self.store.get_attachment(self.admin, attachment["id"])
        self.assertEqual(download["path"], admin_download["path"])

        replied = self.store.add_reply(
            self.admin,
            ticket["id"],
            "Dokumen sudah diterima dan sedang kami review.",
        )
        self.assertEqual("waiting_member", replied["status"])
        self.assertEqual("admin", replied["replies"][-1]["authorRole"])

    def test_validation_rejects_short_ticket(self):
        with self.assertRaises(ConsultationValidationError) as context:
            self.store.create_ticket(
                self.member["id"],
                {"subject": "IT", "message": "pendek"},
            )

        self.assertIn("subject", context.exception.errors)
        self.assertIn("message", context.exception.errors)


if __name__ == "__main__":
    unittest.main()
