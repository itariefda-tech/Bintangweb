from __future__ import annotations

import base64
import hashlib
import re
import sqlite3
import time
import uuid
from pathlib import Path


TICKET_SUBJECT_MAX = 160
TICKET_MESSAGE_MAX = 4000
TICKET_REPLY_MAX = 3000
TICKET_CATEGORY_MAX = 80
TICKET_PRIORITY_VALUES = {"low", "normal", "high", "urgent"}
TICKET_STATUS_VALUES = {"open", "in_review", "waiting_member", "resolved", "closed"}
ATTACHMENT_LIMIT = 5 * 1024 * 1024
ALLOWED_ATTACHMENT_SIGNATURES = {
    "image/png": (b"\x89PNG\r\n\x1a\n", ".png"),
    "image/jpeg": (b"\xff\xd8\xff", ".jpg"),
    "application/pdf": (b"%PDF-", ".pdf"),
}


class ConsultationValidationError(ValueError):
    def __init__(self, message: str, errors: dict[str, str] | None = None):
        super().__init__(message)
        self.errors = errors or {}


class ConsultationStore:
    def __init__(self, database_path: Path, attachment_root: Path | None = None):
        self.database_path = database_path
        self.attachment_root = attachment_root or database_path.parent / "consultation-media"

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
                for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
            }
            if 7 not in applied:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS consultation_tickets (
                        id TEXT PRIMARY KEY,
                        ticket_number TEXT NOT NULL UNIQUE,
                        user_id TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        category TEXT NOT NULL,
                        priority TEXT NOT NULL DEFAULT 'normal'
                            CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
                        status TEXT NOT NULL DEFAULT 'open'
                            CHECK (status IN ('open', 'in_review', 'waiting_member', 'resolved', 'closed')),
                        summary TEXT NOT NULL DEFAULT '',
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_consultation_user
                        ON consultation_tickets(user_id, updated_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_consultation_queue
                        ON consultation_tickets(status, priority, updated_at DESC);

                    CREATE TABLE IF NOT EXISTS consultation_replies (
                        id TEXT PRIMARY KEY,
                        ticket_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        author_role TEXT NOT NULL
                            CHECK (author_role IN ('member', 'admin', 'super_admin')),
                        message TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        FOREIGN KEY (ticket_id) REFERENCES consultation_tickets(id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_consultation_replies_ticket
                        ON consultation_replies(ticket_id, created_at);

                    CREATE TABLE IF NOT EXISTS consultation_attachments (
                        id TEXT PRIMARY KEY,
                        ticket_id TEXT NOT NULL,
                        reply_id TEXT,
                        user_id TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        mime_type TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        size INTEGER NOT NULL CHECK (size > 0),
                        created_at INTEGER NOT NULL,
                        FOREIGN KEY (ticket_id) REFERENCES consultation_tickets(id) ON DELETE CASCADE,
                        FOREIGN KEY (reply_id) REFERENCES consultation_replies(id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_consultation_attachments_ticket
                        ON consultation_attachments(ticket_id, created_at);
                    """
                )
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (7, ?)",
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

    @staticmethod
    def _ticket_number(now: int) -> str:
        return f"CS-{time.strftime('%Y%m%d', time.gmtime(now))}-{uuid.uuid4().hex[:6].upper()}"

    @classmethod
    def _validate_ticket_payload(cls, payload: object) -> dict:
        if not isinstance(payload, dict):
            raise ConsultationValidationError("Data konsultasi tidak valid.")
        fields = {
            "subject": cls._normalize(payload.get("subject")),
            "category": cls._normalize(payload.get("category")) or "General IT",
            "priority": cls._normalize(payload.get("priority")) or "normal",
            "message": str(payload.get("message") or "").strip(),
        }
        errors = {}
        if not 5 <= len(fields["subject"]) <= TICKET_SUBJECT_MAX:
            errors["subject"] = "Subject harus 5-160 karakter."
        if not 2 <= len(fields["category"]) <= TICKET_CATEGORY_MAX:
            errors["category"] = "Kategori harus 2-80 karakter."
        if fields["priority"] not in TICKET_PRIORITY_VALUES:
            errors["priority"] = "Prioritas tidak valid."
        if not 12 <= len(fields["message"]) <= TICKET_MESSAGE_MAX:
            errors["message"] = "Pesan harus 12-4000 karakter."
        if errors:
            raise ConsultationValidationError("Data konsultasi belum valid.", errors)
        return fields

    @staticmethod
    def _validate_reply_message(message: object) -> str:
        clean = str(message or "").strip()
        if not 2 <= len(clean) <= TICKET_REPLY_MAX:
            raise ConsultationValidationError(
                "Reply belum valid.",
                {"message": "Reply harus 2-3000 karakter."},
            )
        return clean

    @staticmethod
    def _public_attachment(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "filename": row["filename"],
            "mimeType": row["mime_type"],
            "size": row["size"],
            "createdAt": row["created_at"],
            "downloadUrl": f"/api/v1/consultation/attachments/{row['id']}",
        }

    @staticmethod
    def _public_ticket(row: sqlite3.Row, replies: list[dict] | None = None, attachments: list[dict] | None = None) -> dict:
        return {
            "id": row["id"],
            "number": row["ticket_number"],
            "subject": row["subject"],
            "category": row["category"],
            "priority": row["priority"],
            "status": row["status"],
            "summary": row["summary"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "member": {
                "id": row["user_id"],
                "name": row["member_name"],
                "email": row["member_email"],
            } if "member_name" in row.keys() else None,
            "replies": replies or [],
            "attachments": attachments or [],
        }

    def _save_attachment(
        self,
        connection: sqlite3.Connection,
        ticket_id: str,
        user_id: str,
        attachment: object,
        reply_id: str | None = None,
    ) -> None:
        if not isinstance(attachment, dict) or not attachment.get("data"):
            return
        try:
            metadata, encoded = str(attachment["data"]).split(",", 1)
            declared_mime = metadata.removeprefix("data:").split(";", 1)[0].lower()
            binary = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error) as error:
            raise ConsultationValidationError("Attachment tidak valid.") from error
        signature = ALLOWED_ATTACHMENT_SIGNATURES.get(declared_mime)
        if not signature or not binary.startswith(signature[0]):
            raise ConsultationValidationError(
                "Attachment tidak valid.",
                {"attachment": "Format harus JPG, PNG, atau PDF."},
            )
        if len(binary) > ATTACHMENT_LIMIT:
            raise ConsultationValidationError(
                "Attachment terlalu besar.",
                {"attachment": "Attachment maksimal 5MB."},
            )
        clean_name = self._normalize(attachment.get("filename"))[:120] or f"attachment{signature[1]}"
        safe_stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(clean_name).stem).strip("-") or "attachment"
        digest = hashlib.sha256(binary).hexdigest()[:20]
        filename = f"{safe_stem}-{digest}{signature[1]}"
        self.attachment_root.mkdir(parents=True, exist_ok=True)
        (self.attachment_root / filename).write_bytes(binary)
        now = int(time.time())
        connection.execute(
            """
            INSERT INTO consultation_attachments (
                id, ticket_id, reply_id, user_id, filename, mime_type, file_path, size, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                ticket_id,
                reply_id,
                user_id,
                clean_name,
                declared_mime,
                filename,
                len(binary),
                now,
            ),
        )

    def create_ticket(self, user_id: str, payload: object) -> dict:
        fields = self._validate_ticket_payload(payload)
        attachment = payload.get("attachment") if isinstance(payload, dict) else None
        now = int(time.time())
        ticket_id = str(uuid.uuid4())
        reply_id = str(uuid.uuid4())
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            ticket_number = self._ticket_number(now)
            connection.execute(
                """
                INSERT INTO consultation_tickets (
                    id, ticket_number, user_id, subject, category, priority, status,
                    summary, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
                """,
                (
                    ticket_id,
                    ticket_number,
                    user_id,
                    fields["subject"],
                    fields["category"],
                    fields["priority"],
                    fields["message"][:220],
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO consultation_replies (
                    id, ticket_id, user_id, author_role, message, created_at
                ) VALUES (?, ?, ?, 'member', ?, ?)
                """,
                (reply_id, ticket_id, user_id, fields["message"], now),
            )
            self._save_attachment(connection, ticket_id, user_id, attachment, reply_id)
            connection.execute(
                """
                INSERT INTO member_notifications (
                    id, user_id, title, message, kind, action_url, created_at
                ) VALUES (?, ?, ?, ?, 'consultation', '/member/consultation', ?)
                """,
                (
                    str(uuid.uuid4()),
                    user_id,
                    "Ticket konsultasi dibuat",
                    f"Ticket {ticket_number} berhasil masuk queue konsultasi.",
                    now,
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.get_ticket(user_id, ticket_id)

    def list_tickets(self, user_id: str) -> list[dict]:
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT t.*, u.name AS member_name, u.email AS member_email
                FROM consultation_tickets t
                JOIN users u ON u.id = t.user_id
                WHERE t.user_id = ?
                ORDER BY t.updated_at DESC
                """,
                (user_id,),
            ).fetchall()
            tickets = []
            for row in rows:
                replies = [
                    {
                        "id": reply["id"],
                        "authorRole": reply["author_role"],
                        "message": reply["message"],
                        "createdAt": reply["created_at"],
                    }
                    for reply in connection.execute(
                        """
                        SELECT id, author_role, message, created_at
                        FROM consultation_replies
                        WHERE ticket_id = ?
                        ORDER BY created_at, rowid
                        """,
                        (row["id"],),
                    ).fetchall()
                ]
                attachments = [
                    self._public_attachment(item)
                    for item in connection.execute(
                        """
                        SELECT id, filename, mime_type, size, created_at
                        FROM consultation_attachments
                        WHERE ticket_id = ?
                        ORDER BY created_at, id
                        """,
                        (row["id"],),
                    ).fetchall()
                ]
                tickets.append(self._public_ticket(row, replies, attachments))
            return tickets
        finally:
            connection.close()

    def get_ticket(self, user_id: str, ticket_id: str, include_all: bool = False) -> dict:
        connection = self.connect()
        try:
            condition = "t.id = ?" if include_all else "t.id = ? AND t.user_id = ?"
            params: tuple[object, ...] = (ticket_id,) if include_all else (ticket_id, user_id)
            row = connection.execute(
                f"""
                SELECT t.*, u.name AS member_name, u.email AS member_email
                FROM consultation_tickets t
                JOIN users u ON u.id = t.user_id
                WHERE {condition}
                """,
                params,
            ).fetchone()
            if not row:
                raise LookupError("Ticket konsultasi tidak ditemukan.")
            replies = [
                {
                    "id": reply["id"],
                    "authorRole": reply["author_role"],
                    "message": reply["message"],
                    "createdAt": reply["created_at"],
                }
                for reply in connection.execute(
                    """
                    SELECT id, author_role, message, created_at
                    FROM consultation_replies
                    WHERE ticket_id = ?
                    ORDER BY created_at, rowid
                    """,
                    (row["id"],),
                ).fetchall()
            ]
            attachments = [
                self._public_attachment(item)
                for item in connection.execute(
                    """
                    SELECT id, filename, mime_type, size, created_at
                    FROM consultation_attachments
                    WHERE ticket_id = ?
                    ORDER BY created_at, id
                    """,
                    (row["id"],),
                ).fetchall()
            ]
            return self._public_ticket(row, replies, attachments)
        finally:
            connection.close()

    def get_attachment(self, actor: dict, attachment_id: str) -> dict:
        is_admin = actor.get("role") in {"admin", "super_admin"}
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT a.id, a.filename, a.mime_type, a.file_path, a.size, t.user_id
                FROM consultation_attachments a
                JOIN consultation_tickets t ON t.id = a.ticket_id
                WHERE a.id = ?
                """,
                (attachment_id,),
            ).fetchone()
            if not row or (not is_admin and row["user_id"] != actor.get("id")):
                raise LookupError("Attachment konsultasi tidak ditemukan.")
            target = (self.attachment_root / row["file_path"]).resolve()
            attachment_root = self.attachment_root.resolve()
            if target.parent != attachment_root or not target.is_file():
                raise LookupError("Attachment konsultasi tidak ditemukan.")
            return {
                "path": target,
                "filename": row["filename"],
                "mimeType": row["mime_type"],
                "size": row["size"],
            }
        finally:
            connection.close()

    def add_reply(self, actor: dict, ticket_id: str, message: object, attachment: object = None) -> dict:
        clean_message = self._validate_reply_message(message)
        is_admin = actor.get("role") in {"admin", "super_admin"}
        now = int(time.time())
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            ticket = connection.execute(
                "SELECT id, user_id, ticket_number FROM consultation_tickets WHERE id = ?",
                (ticket_id,),
            ).fetchone()
            if not ticket or (not is_admin and ticket["user_id"] != actor["id"]):
                raise LookupError("Ticket konsultasi tidak ditemukan.")
            reply_id = str(uuid.uuid4())
            connection.execute(
                """
                INSERT INTO consultation_replies (
                    id, ticket_id, user_id, author_role, message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (reply_id, ticket_id, actor["id"], actor["role"], clean_message, now),
            )
            next_status = "waiting_member" if is_admin else "in_review"
            connection.execute(
                "UPDATE consultation_tickets SET status = ?, updated_at = ? WHERE id = ?",
                (next_status, now, ticket_id),
            )
            self._save_attachment(connection, ticket_id, actor["id"], attachment, reply_id)
            notified_user = ticket["user_id"]
            if is_admin or actor["id"] == notified_user:
                title = "Reply konsultasi diterima" if is_admin else "Reply konsultasi terkirim"
                message_text = (
                    f"Ticket {ticket['ticket_number']} mendapat balasan dari tim Feira."
                    if is_admin
                    else f"Reply ticket {ticket['ticket_number']} berhasil dikirim."
                )
                connection.execute(
                    """
                    INSERT INTO member_notifications (
                        id, user_id, title, message, kind, action_url, created_at
                    ) VALUES (?, ?, ?, ?, 'consultation', '/member/consultation', ?)
                    """,
                    (str(uuid.uuid4()), notified_user, title, message_text, now),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.get_ticket(actor["id"], ticket_id, include_all=is_admin)

    def update_status(self, actor: dict, ticket_id: str, status: object) -> dict:
        if actor.get("role") not in {"admin", "super_admin"}:
            raise PermissionError("Hanya admin yang dapat mengubah status ticket.")
        clean_status = self._normalize(status)
        if clean_status not in TICKET_STATUS_VALUES:
            raise ConsultationValidationError(
                "Status ticket tidak valid.",
                {"status": "Status ticket tidak valid."},
            )
        now = int(time.time())
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            ticket = connection.execute(
                "SELECT id, user_id, ticket_number FROM consultation_tickets WHERE id = ?",
                (ticket_id,),
            ).fetchone()
            if not ticket:
                raise LookupError("Ticket konsultasi tidak ditemukan.")
            connection.execute(
                "UPDATE consultation_tickets SET status = ?, updated_at = ? WHERE id = ?",
                (clean_status, now, ticket_id),
            )
            connection.execute(
                """
                INSERT INTO member_notifications (
                    id, user_id, title, message, kind, action_url, created_at
                ) VALUES (?, ?, ?, ?, 'consultation', '/member/consultation', ?)
                """,
                (
                    str(uuid.uuid4()),
                    ticket["user_id"],
                    "Status konsultasi diperbarui",
                    f"Ticket {ticket['ticket_number']} sekarang berstatus {clean_status}.",
                    now,
                ),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.get_ticket(actor["id"], ticket_id, include_all=True)

    def admin_queue(self, actor: dict, status: str = "") -> list[dict]:
        if actor.get("role") not in {"admin", "super_admin"}:
            raise PermissionError("Hanya admin yang dapat membuka queue konsultasi.")
        clean_status = self._normalize(status)
        conditions = ["1=1"]
        params: list[object] = []
        if clean_status:
            conditions.append("t.status = ?")
            params.append(clean_status)
        connection = self.connect()
        try:
            rows = connection.execute(
                f"""
                SELECT t.*, u.name AS member_name, u.email AS member_email
                FROM consultation_tickets t
                JOIN users u ON u.id = t.user_id
                WHERE {' AND '.join(conditions)}
                ORDER BY
                    CASE t.priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
                    t.updated_at DESC
                """,
                params,
            ).fetchall()
            tickets = []
            for row in rows:
                replies = [
                    {
                        "id": reply["id"],
                        "authorRole": reply["author_role"],
                        "message": reply["message"],
                        "createdAt": reply["created_at"],
                    }
                    for reply in connection.execute(
                        """
                        SELECT id, author_role, message, created_at
                        FROM consultation_replies
                        WHERE ticket_id = ?
                        ORDER BY created_at, rowid
                        """,
                        (row["id"],),
                    ).fetchall()
                ]
                attachments = [
                    self._public_attachment(item)
                    for item in connection.execute(
                        """
                        SELECT id, filename, mime_type, size, created_at
                        FROM consultation_attachments
                        WHERE ticket_id = ?
                        ORDER BY created_at, rowid
                        """,
                        (row["id"],),
                    ).fetchall()
                ]
                tickets.append(self._public_ticket(row, replies, attachments))
            return tickets
        finally:
            connection.close()
