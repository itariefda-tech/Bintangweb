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

        self.assertEqual([1, 2], versions)
        self.assertEqual(1, user_count)


if __name__ == "__main__":
    unittest.main()
