import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from marketplace_auth import AuthStore, AuthValidationError, DuplicateEmailError


class AuthStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "marketplace.sqlite3"
        self.store = AuthStore(self.database, idle_ttl=3600, absolute_ttl=7200)
        self.store.initialize()

    def tearDown(self):
        self.temporary.cleanup()

    def test_register_hashes_password_and_authenticates(self):
        user = self.store.register("Feira Member", "MEMBER@example.com", "securepass123")
        authenticated = self.store.authenticate("member@example.com", "securepass123")

        self.assertEqual("member@example.com", user["email"])
        self.assertEqual(user["id"], authenticated["id"])

        with closing(sqlite3.connect(self.database)) as connection:
            stored = connection.execute(
                "SELECT password_hash FROM users WHERE id = ?",
                (user["id"],),
            ).fetchone()[0]
        self.assertTrue(stored.startswith("scrypt$"))
        self.assertNotIn("securepass123", stored)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.store.register("First Member", "member@example.com", "securepass123")
        with self.assertRaises(DuplicateEmailError):
            self.store.register("Second Member", "MEMBER@example.com", "securepass456")

    def test_registration_validation_returns_field_errors(self):
        with self.assertRaises(AuthValidationError) as context:
            self.store.register("A", "invalid", "short")
        self.assertEqual({"name", "email", "password"}, set(context.exception.errors))

    def test_session_token_is_hashed_and_can_be_revoked(self):
        user = self.store.register("Feira Member", "member@example.com", "securepass123")
        token, session = self.store.create_session(user["id"])

        self.assertEqual(user["id"], self.store.get_session(token).user["id"])
        with closing(sqlite3.connect(self.database)) as connection:
            stored_token = connection.execute(
                "SELECT token_hash FROM member_sessions"
            ).fetchone()[0]
        self.assertNotEqual(token, stored_token)
        self.assertEqual(64, len(stored_token))
        self.assertTrue(session.csrf_token)

        self.store.revoke_session(token)
        self.assertIsNone(self.store.get_session(token))

    def test_profile_defaults_update_and_session_name_refresh(self):
        user = self.store.register("Feira Member", "member@example.com", "securepass123")
        token, _session = self.store.create_session(user["id"])

        default_profile = self.store.get_profile(user["id"])
        self.assertEqual("", default_profile["phone"])
        self.assertEqual("", default_profile["companyName"])

        updated = self.store.update_profile(
            user["id"],
            {
                "name": "Feira Business Member",
                "phone": "+62 812-3456-7890",
                "address": "Jl. Teknologi No. 1",
                "city": "Jakarta",
                "province": "DKI Jakarta",
                "postalCode": "12345",
                "companyName": "PT Feira Digital",
                "jobTitle": "IT Manager",
                "bio": "Mengelola infrastruktur dan transformasi digital.",
            },
        )

        self.assertEqual("PT Feira Digital", updated["companyName"])
        self.assertEqual("Feira Business Member", self.store.get_session(token).user["name"])

        reloaded_store = AuthStore(self.database, idle_ttl=3600, absolute_ttl=7200)
        reloaded_store.initialize()
        persisted = reloaded_store.get_profile(user["id"])
        self.assertEqual("Jakarta", persisted["city"])
        self.assertEqual("IT Manager", persisted["jobTitle"])

    def test_profile_validation_returns_field_errors(self):
        user = self.store.register("Feira Member", "member@example.com", "securepass123")
        with self.assertRaises(AuthValidationError) as context:
            self.store.update_profile(
                user["id"],
                {
                    "name": "A",
                    "phone": "phone<script>",
                    "postalCode": "12345<script>",
                    "bio": "x" * 601,
                },
            )
        self.assertEqual(
            {"name", "phone", "postalCode", "bio"},
            set(context.exception.errors),
        )

    def test_password_reset_is_single_use_and_revokes_sessions(self):
        user = self.store.register("Feira Member", "member@example.com", "securepass123")
        session_token, _session = self.store.create_session(user["id"])
        token, reset_user = self.store.create_password_reset("MEMBER@example.com")

        self.assertEqual(user["id"], reset_user["id"])
        self.store.reset_password(token, "new-secure-pass456")

        self.assertIsNone(self.store.get_session(session_token))
        self.assertIsNone(self.store.authenticate("member@example.com", "securepass123"))
        self.assertEqual(
            user["id"],
            self.store.authenticate("member@example.com", "new-secure-pass456")["id"],
        )
        with self.assertRaises(AuthValidationError):
            self.store.reset_password(token, "another-secure-pass789")

    def test_notifications_are_private_and_can_be_marked_read(self):
        first = self.store.register("First Member", "first@example.com", "securepass123")
        second = self.store.register("Second Member", "second@example.com", "securepass123")

        first_notifications = self.store.list_notifications(first["id"])
        second_notifications = self.store.list_notifications(second["id"])
        self.assertEqual(1, first_notifications["unreadCount"])
        self.assertEqual(1, second_notifications["unreadCount"])
        self.assertNotEqual(
            first_notifications["items"][0]["id"],
            second_notifications["items"][0]["id"],
        )

        updated = self.store.mark_notifications_read(
            first["id"], first_notifications["items"][0]["id"]
        )
        self.assertEqual(0, updated["unreadCount"])
        self.assertEqual(1, self.store.list_notifications(second["id"])["unreadCount"])

    def test_avatar_url_is_validated_and_persisted(self):
        user = self.store.register("Feira Member", "member@example.com", "securepass123")
        profile = self.store.update_avatar(
            user["id"], "/member-media/avatar-member-example.png"
        )
        self.assertEqual(
            "/member-media/avatar-member-example.png", profile["avatarUrl"]
        )
        with self.assertRaises(AuthValidationError):
            self.store.update_avatar(user["id"], "https://example.com/avatar.png")

    def test_only_super_admin_can_update_roles(self):
        store = AuthStore(
            self.database,
            idle_ttl=3600,
            absolute_ttl=7200,
            super_admin_emails={"owner@example.com"},
        )
        store.initialize()
        owner = store.register("Owner Feira", "owner@example.com", "securepass123")
        member = store.register("Feira Member", "member@example.com", "securepass123")
        other = store.register("Other Member", "other@example.com", "securepass123")

        updated = store.update_user_role(owner["id"], member["id"], "admin")
        self.assertEqual("admin", updated["role"])
        with self.assertRaises(PermissionError):
            store.update_user_role(other["id"], member["id"], "member")
        with self.assertRaises(AuthValidationError):
            store.update_user_role(owner["id"], owner["id"], "admin")

    def test_schema_migrations_are_versioned_and_idempotent(self):
        user = self.store.register("Feira Member", "member@example.com", "securepass123")
        self.store.initialize()

        with closing(sqlite3.connect(self.database)) as connection:
            versions = [
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                ).fetchall()
            ]
            user_count = connection.execute(
                "SELECT COUNT(*) FROM users WHERE id = ?",
                (user["id"],),
            ).fetchone()[0]

        self.assertEqual([1, 2, 3], versions)
        self.assertEqual(1, user_count)


if __name__ == "__main__":
    unittest.main()
