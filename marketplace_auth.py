from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


EMAIL_PATTERN = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,63}$")
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
NAME_MAX_LENGTH = 120
PHONE_MAX_LENGTH = 24
ADDRESS_MAX_LENGTH = 300
LOCATION_MAX_LENGTH = 100
POSTAL_CODE_MAX_LENGTH = 12
COMPANY_MAX_LENGTH = 120
JOB_TITLE_MAX_LENGTH = 120
BIO_MAX_LENGTH = 600
PHONE_PATTERN = re.compile(r"^[0-9+().\-\s]*$")
POSTAL_CODE_PATTERN = re.compile(r"^[A-Za-z0-9\-\s]*$")
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_MAXMEM = 64 * 1024 * 1024


class AuthValidationError(ValueError):
    def __init__(self, message: str, errors: dict[str, str] | None = None):
        super().__init__(message)
        self.errors = errors or {}


class DuplicateEmailError(ValueError):
    pass


@dataclass(frozen=True)
class MemberSession:
    user: dict
    csrf_token: str
    expires_at: int


class AuthStore:
    def __init__(
        self,
        database_path: Path,
        idle_ttl: int = 8 * 60 * 60,
        absolute_ttl: int = 7 * 24 * 60 * 60,
    ):
        self.database_path = database_path
        self.idle_ttl = idle_ttl
        self.absolute_ttl = absolute_ttl

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    @contextmanager
    def connection(self):
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
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
            migrations = {
                1: """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'member'
                        CHECK (role IN ('member', 'admin', 'super_admin')),
                    status TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'inactive', 'suspended')),
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS member_sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    csrf_token TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    last_seen_at INTEGER NOT NULL,
                    idle_expires_at INTEGER NOT NULL,
                    absolute_expires_at INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_member_sessions_user
                    ON member_sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_member_sessions_expiry
                    ON member_sessions(idle_expires_at, absolute_expires_at);
                """,
                2: """
                CREATE TABLE IF NOT EXISTS member_profiles (
                    user_id TEXT PRIMARY KEY,
                    phone TEXT NOT NULL DEFAULT '',
                    address TEXT NOT NULL DEFAULT '',
                    city TEXT NOT NULL DEFAULT '',
                    province TEXT NOT NULL DEFAULT '',
                    postal_code TEXT NOT NULL DEFAULT '',
                    company_name TEXT NOT NULL DEFAULT '',
                    job_title TEXT NOT NULL DEFAULT '',
                    bio TEXT NOT NULL DEFAULT '',
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """,
            }
            for version, statement in migrations.items():
                if version in applied:
                    continue
                connection.executescript(statement)
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                    (version, int(time.time())),
                )

    @staticmethod
    def normalize_email(value: object) -> str:
        return str(value or "").strip().lower()

    @staticmethod
    def normalize_name(value: object) -> str:
        return " ".join(str(value or "").strip().split())

    @staticmethod
    def validate_registration(name: object, email: object, password: object) -> tuple[str, str, str]:
        clean_name = AuthStore.normalize_name(name)
        clean_email = AuthStore.normalize_email(email)
        clean_password = str(password or "")
        errors: dict[str, str] = {}

        if len(clean_name) < 2 or len(clean_name) > NAME_MAX_LENGTH:
            errors["name"] = f"Nama harus 2-{NAME_MAX_LENGTH} karakter."
        if len(clean_email) > 254 or not EMAIL_PATTERN.fullmatch(clean_email):
            errors["email"] = "Format email tidak valid."
        if not PASSWORD_MIN_LENGTH <= len(clean_password) <= PASSWORD_MAX_LENGTH:
            errors["password"] = (
                f"Password harus {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} karakter."
            )

        if errors:
            raise AuthValidationError("Data registrasi belum valid.", errors)
        return clean_name, clean_email, clean_password

    @staticmethod
    def validate_login(email: object, password: object) -> tuple[str, str]:
        clean_email = AuthStore.normalize_email(email)
        clean_password = str(password or "")
        if len(clean_email) > 254 or not EMAIL_PATTERN.fullmatch(clean_email):
            raise AuthValidationError("Email atau password tidak valid.")
        if not clean_password or len(clean_password) > PASSWORD_MAX_LENGTH:
            raise AuthValidationError("Email atau password tidak valid.")
        return clean_email, clean_password

    @staticmethod
    def normalize_profile_text(value: object) -> str:
        return " ".join(str(value or "").strip().split())

    @staticmethod
    def validate_profile(payload: object) -> dict[str, str]:
        if not isinstance(payload, dict):
            raise AuthValidationError("Data profile tidak valid.")

        fields = {
            "name": AuthStore.normalize_name(payload.get("name")),
            "phone": AuthStore.normalize_profile_text(payload.get("phone")),
            "address": str(payload.get("address") or "").strip(),
            "city": AuthStore.normalize_profile_text(payload.get("city")),
            "province": AuthStore.normalize_profile_text(payload.get("province")),
            "postalCode": AuthStore.normalize_profile_text(payload.get("postalCode")),
            "companyName": AuthStore.normalize_profile_text(payload.get("companyName")),
            "jobTitle": AuthStore.normalize_profile_text(payload.get("jobTitle")),
            "bio": str(payload.get("bio") or "").strip(),
        }
        errors: dict[str, str] = {}

        if len(fields["name"]) < 2 or len(fields["name"]) > NAME_MAX_LENGTH:
            errors["name"] = f"Nama harus 2-{NAME_MAX_LENGTH} karakter."
        if len(fields["phone"]) > PHONE_MAX_LENGTH or not PHONE_PATTERN.fullmatch(
            fields["phone"]
        ):
            errors["phone"] = "Nomor telepon tidak valid."
        if len(fields["address"]) > ADDRESS_MAX_LENGTH:
            errors["address"] = f"Alamat maksimal {ADDRESS_MAX_LENGTH} karakter."
        for field, label in (("city", "Kota"), ("province", "Provinsi")):
            if len(fields[field]) > LOCATION_MAX_LENGTH:
                errors[field] = f"{label} maksimal {LOCATION_MAX_LENGTH} karakter."
        if len(fields["postalCode"]) > POSTAL_CODE_MAX_LENGTH or not POSTAL_CODE_PATTERN.fullmatch(
            fields["postalCode"]
        ):
            errors["postalCode"] = "Kode pos tidak valid."
        if len(fields["companyName"]) > COMPANY_MAX_LENGTH:
            errors["companyName"] = f"Nama perusahaan maksimal {COMPANY_MAX_LENGTH} karakter."
        if len(fields["jobTitle"]) > JOB_TITLE_MAX_LENGTH:
            errors["jobTitle"] = f"Jabatan maksimal {JOB_TITLE_MAX_LENGTH} karakter."
        if len(fields["bio"]) > BIO_MAX_LENGTH:
            errors["bio"] = f"Bio maksimal {BIO_MAX_LENGTH} karakter."

        if errors:
            raise AuthValidationError("Data profile belum valid.", errors)
        return fields

    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=SCRYPT_N,
            r=SCRYPT_R,
            p=SCRYPT_P,
            maxmem=SCRYPT_MAXMEM,
        )
        salt_value = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
        hash_value = base64.urlsafe_b64encode(derived).decode("ascii").rstrip("=")
        return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt_value}${hash_value}"

    @staticmethod
    def verify_password(password: str, encoded: str) -> bool:
        try:
            algorithm, raw_n, raw_r, raw_p, salt_value, hash_value = encoded.split("$", 5)
            if algorithm != "scrypt":
                return False
            salt = base64.urlsafe_b64decode(salt_value + "=" * (-len(salt_value) % 4))
            expected = base64.urlsafe_b64decode(hash_value + "=" * (-len(hash_value) % 4))
            candidate = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt,
                n=int(raw_n),
                r=int(raw_r),
                p=int(raw_p),
                maxmem=SCRYPT_MAXMEM,
                dklen=len(expected),
            )
            return hmac.compare_digest(candidate, expected)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def public_user(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "role": row["role"],
        }

    def register(self, name: object, email: object, password: object) -> dict:
        clean_name, clean_email, clean_password = self.validate_registration(
            name, email, password
        )
        now = int(time.time())
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(clean_password)

        try:
            with self.connection() as connection:
                connection.execute(
                    """
                    INSERT INTO users (
                        id, name, email, password_hash, role, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 'member', 'active', ?, ?)
                    """,
                    (user_id, clean_name, clean_email, password_hash, now, now),
                )
        except sqlite3.IntegrityError as error:
            if "users.email" in str(error):
                raise DuplicateEmailError("Email sudah terdaftar.") from error
            raise

        return {
            "id": user_id,
            "name": clean_name,
            "email": clean_email,
            "role": "member",
        }

    def authenticate(self, email: object, password: object) -> dict | None:
        clean_email, clean_password = self.validate_login(email, password)
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT id, name, email, password_hash, role, status
                FROM users
                WHERE email = ?
                """,
                (clean_email,),
            ).fetchone()

        if not row or row["status"] != "active":
            return None
        if not self.verify_password(clean_password, row["password_hash"]):
            return None
        return self.public_user(row)

    def create_session(self, user_id: str) -> tuple[str, MemberSession]:
        now = int(time.time())
        token = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(24)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        idle_expires_at = now + self.idle_ttl
        absolute_expires_at = now + self.absolute_ttl

        with self.connection() as connection:
            connection.execute("DELETE FROM member_sessions WHERE user_id = ?", (user_id,))
            connection.execute(
                """
                INSERT INTO member_sessions (
                    token_hash, user_id, csrf_token, created_at, last_seen_at,
                    idle_expires_at, absolute_expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    token_hash,
                    user_id,
                    csrf_token,
                    now,
                    now,
                    idle_expires_at,
                    absolute_expires_at,
                ),
            )
            user = connection.execute(
                "SELECT id, name, email, role FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

        if not user:
            raise LookupError("User session tidak ditemukan.")
        return token, MemberSession(
            user=self.public_user(user),
            csrf_token=csrf_token,
            expires_at=idle_expires_at,
        )

    def get_session(self, token: str, refresh: bool = True) -> MemberSession | None:
        if not token:
            return None
        now = int(time.time())
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    s.csrf_token,
                    s.idle_expires_at,
                    s.absolute_expires_at,
                    u.id,
                    u.name,
                    u.email,
                    u.role,
                    u.status
                FROM member_sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token_hash = ?
                """,
                (token_hash,),
            ).fetchone()

            if (
                not row
                or row["status"] != "active"
                or row["idle_expires_at"] <= now
                or row["absolute_expires_at"] <= now
            ):
                connection.execute(
                    "DELETE FROM member_sessions WHERE token_hash = ?",
                    (token_hash,),
                )
                return None

            expires_at = row["idle_expires_at"]
            if refresh:
                expires_at = min(now + self.idle_ttl, row["absolute_expires_at"])
                connection.execute(
                    """
                    UPDATE member_sessions
                    SET last_seen_at = ?, idle_expires_at = ?
                    WHERE token_hash = ?
                    """,
                    (now, expires_at, token_hash),
                )

        return MemberSession(
            user=self.public_user(row),
            csrf_token=row["csrf_token"],
            expires_at=expires_at,
        )

    def revoke_session(self, token: str) -> None:
        if not token:
            return
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with self.connection() as connection:
            connection.execute(
                "DELETE FROM member_sessions WHERE token_hash = ?",
                (token_hash,),
            )

    def get_profile(self, user_id: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    u.id,
                    u.name,
                    u.email,
                    u.role,
                    COALESCE(p.phone, '') AS phone,
                    COALESCE(p.address, '') AS address,
                    COALESCE(p.city, '') AS city,
                    COALESCE(p.province, '') AS province,
                    COALESCE(p.postal_code, '') AS postal_code,
                    COALESCE(p.company_name, '') AS company_name,
                    COALESCE(p.job_title, '') AS job_title,
                    COALESCE(p.bio, '') AS bio
                FROM users u
                LEFT JOIN member_profiles p ON p.user_id = u.id
                WHERE u.id = ? AND u.status = 'active'
                """,
                (user_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "role": row["role"],
            "phone": row["phone"],
            "address": row["address"],
            "city": row["city"],
            "province": row["province"],
            "postalCode": row["postal_code"],
            "companyName": row["company_name"],
            "jobTitle": row["job_title"],
            "bio": row["bio"],
        }

    def update_profile(self, user_id: str, payload: object) -> dict:
        fields = self.validate_profile(payload)
        now = int(time.time())
        with self.connection() as connection:
            updated = connection.execute(
                """
                UPDATE users
                SET name = ?, updated_at = ?
                WHERE id = ? AND status = 'active'
                """,
                (fields["name"], now, user_id),
            )
            if updated.rowcount != 1:
                raise LookupError("Member tidak ditemukan.")
            connection.execute(
                """
                INSERT INTO member_profiles (
                    user_id, phone, address, city, province, postal_code,
                    company_name, job_title, bio, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    phone = excluded.phone,
                    address = excluded.address,
                    city = excluded.city,
                    province = excluded.province,
                    postal_code = excluded.postal_code,
                    company_name = excluded.company_name,
                    job_title = excluded.job_title,
                    bio = excluded.bio,
                    updated_at = excluded.updated_at
                """,
                (
                    user_id,
                    fields["phone"],
                    fields["address"],
                    fields["city"],
                    fields["province"],
                    fields["postalCode"],
                    fields["companyName"],
                    fields["jobTitle"],
                    fields["bio"],
                    now,
                    now,
                ),
            )
        profile = self.get_profile(user_id)
        if not profile:
            raise LookupError("Member tidak ditemukan.")
        return profile

    def cleanup_expired_sessions(self) -> None:
        now = int(time.time())
        with self.connection() as connection:
            connection.execute(
                """
                DELETE FROM member_sessions
                WHERE idle_expires_at <= ? OR absolute_expires_at <= ?
                """,
                (now, now),
            )
