from __future__ import annotations

import base64
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import threading
import time
from http import cookies
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

from marketplace_auth import (
    AuthStore,
    AuthValidationError,
    DuplicateEmailError,
)


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"


def normalize_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_env_file() -> None:
    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), normalize_env_value(value))


load_env_file()

PUBLIC_ROOT = Path(os.environ.get("PUBLIC_ROOT") or PROJECT_ROOT).resolve()
DATA_ROOT = Path(os.environ.get("DATA_ROOT") or PROJECT_ROOT / "data").resolve()
UPLOAD_ROOT = DATA_ROOT / "owner-media"
SETTINGS_FILE = DATA_ROOT / "owner-settings.json"
MARKETPLACE_DATABASE = DATA_ROOT / "marketplace.sqlite3"
MARKETPLACE_SHELL = "/src/pages/marketplace-shell.html"

MARKETPLACE_ROUTES = {
    "/marketplace",
    "/login",
    "/register",
    "/member",
    "/member/profile",
    "/member/orders",
    "/member/consultation",
    "/news",
    "/checkout",
}
PROTECTED_MEMBER_ROUTES = {
    "/member",
    "/member/profile",
    "/member/orders",
    "/member/consultation",
    "/checkout",
}

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
SESSION_TTL = 8 * 60 * 60
SESSION_COOKIE = "bcf_owner_session"
MEMBER_SESSION_TTL = int(os.environ.get("MEMBER_SESSION_TTL", str(8 * 60 * 60)))
MEMBER_SESSION_ABSOLUTE_TTL = int(
    os.environ.get("MEMBER_SESSION_ABSOLUTE_TTL", str(7 * 24 * 60 * 60))
)
MEMBER_SESSION_COOKIE = "feira_member_session"
MAX_JSON_BODY = 140 * 1024 * 1024
MAX_AUTH_JSON_BODY = 16 * 1024

DEFAULT_SETTINGS = {
    "processAudioAutoplay": True,
    "workVideo": "",
    "clients": [],
    "backgrounds": {
        "header": "",
        "hero": "",
        "about": "",
        "solutions": "",
        "process": "",
        "contact": "",
        "footer": "",
    },
    "testimonials": {
        "office": {"quote": "", "name": "", "role": "", "company": ""},
        "security": {"quote": "", "name": "", "role": "", "company": ""},
        "digital": {"quote": "", "name": "", "role": "", "company": ""},
    },
}

ALLOWED_UPLOADS = {
    "background": {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    },
    "video": {
        "video/mp4": ".mp4",
        "video/webm": ".webm",
        "video/quicktime": ".mov",
    },
}

SESSIONS: dict[str, float] = {}
AUTH_RATE_LIMITS: dict[str, list[float]] = {}
AUTH_RATE_LIMIT_LOCK = threading.Lock()
AUTH_STORE = AuthStore(
    MARKETPLACE_DATABASE,
    idle_ttl=MEMBER_SESSION_TTL,
    absolute_ttl=MEMBER_SESSION_ABSOLUTE_TTL,
)


def deep_copy_default() -> dict:
    return json.loads(json.dumps(DEFAULT_SETTINGS))


def merge_settings(candidate: object) -> dict:
    result = deep_copy_default()
    if not isinstance(candidate, dict):
        return result

    result["processAudioAutoplay"] = bool(
        candidate.get("processAudioAutoplay", result["processAudioAutoplay"])
    )
    work_video = candidate.get("workVideo")
    if isinstance(work_video, str):
        result["workVideo"] = work_video[:500]

    clients = candidate.get("clients")
    if isinstance(clients, list):
        result["clients"] = [
            value.strip()[:120]
            for value in clients[:100]
            if isinstance(value, str) and value.strip()
        ]

    backgrounds = candidate.get("backgrounds")
    if isinstance(backgrounds, dict):
        for key in result["backgrounds"]:
            value = backgrounds.get(key)
            if isinstance(value, str):
                result["backgrounds"][key] = value[:500]

    testimonials = candidate.get("testimonials")
    if isinstance(testimonials, dict):
        for case_id in result["testimonials"]:
            entry = testimonials.get(case_id)
            if not isinstance(entry, dict):
                continue
            for field in result["testimonials"][case_id]:
                value = entry.get(field)
                if isinstance(value, str):
                    result["testimonials"][case_id][field] = value.strip()[:600]

    return result


def read_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return deep_copy_default()
    try:
        return merge_settings(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return deep_copy_default()


def write_settings(settings: object) -> dict:
    cleaned = merge_settings(settings)
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    temporary = SETTINGS_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(cleaned, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    temporary.replace(SETTINGS_FILE)
    return cleaned


def cleanup_sessions() -> None:
    now = time.time()
    expired = [token for token, expires_at in SESSIONS.items() if expires_at <= now]
    for token in expired:
        SESSIONS.pop(token, None)


OWNER_PASSWORD = normalize_env_value(os.environ.get("OWNER_PASSWORD", ""))


class BintangHandler(SimpleHTTPRequestHandler):
    server_version = "BintangWeb/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        if (
            self.path.startswith("/api/")
            or self.path.startswith("/owner-builder")
            or self.path.startswith("/src/")
        ):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status: int, payload: object, extra_headers=None) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for key, value in extra_headers or []:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def read_json(self, max_bytes: int = MAX_JSON_BODY) -> object:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > max_bytes:
            raise ValueError("Ukuran request tidak valid.")
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def cookie_value(self, name: str) -> str:
        raw_cookie = self.headers.get("Cookie", "")
        jar = cookies.SimpleCookie()
        try:
            jar.load(raw_cookie)
        except cookies.CookieError:
            return ""
        morsel = jar.get(name)
        return morsel.value if morsel else ""

    def session_token(self) -> str:
        return self.cookie_value(SESSION_COOKIE)

    def member_session_token(self) -> str:
        return self.cookie_value(MEMBER_SESSION_COOKIE)

    def member_session(self, refresh: bool = True):
        return AUTH_STORE.get_session(self.member_session_token(), refresh=refresh)

    def auth_response(
        self,
        status: int,
        success: bool,
        message: str,
        data: object | None = None,
        errors: dict | None = None,
        extra_headers=None,
    ) -> None:
        payload = {"success": success, "message": message}
        if data is not None:
            payload["data"] = data
        if errors:
            payload["errors"] = errors
        self.send_json(status, payload, extra_headers)

    def is_same_origin_request(self) -> bool:
        fetch_site = self.headers.get("Sec-Fetch-Site", "")
        if fetch_site == "cross-site":
            return False
        origin = self.headers.get("Origin")
        if not origin:
            return True
        expected_scheme = (
            "https" if self.headers.get("X-Forwarded-Proto") == "https" else "http"
        )
        return origin == f"{expected_scheme}://{self.headers.get('Host', '')}"

    def auth_rate_limited(self, action: str, limit: int, window: int) -> bool:
        client_ip = self.client_address[0]
        key = f"{action}:{client_ip}"
        now = time.time()
        with AUTH_RATE_LIMIT_LOCK:
            attempts = [
                timestamp
                for timestamp in AUTH_RATE_LIMITS.get(key, [])
                if timestamp > now - window
            ]
            if len(attempts) >= limit:
                AUTH_RATE_LIMITS[key] = attempts
                return True
            attempts.append(now)
            AUTH_RATE_LIMITS[key] = attempts
        return False

    def member_cookie(self, token: str, max_age: int) -> str:
        secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
        return (
            f"{MEMBER_SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; "
            f"Max-Age={max_age}{secure}"
        )

    def valid_member_csrf(self, session) -> bool:
        submitted = self.headers.get("X-CSRF-Token", "")
        return bool(
            session
            and submitted
            and hmac.compare_digest(submitted, session.csrf_token)
        )

    def is_owner(self) -> bool:
        cleanup_sessions()
        token = self.session_token()
        expires_at = SESSIONS.get(token, 0)
        if expires_at <= time.time():
            return False
        SESSIONS[token] = time.time() + SESSION_TTL
        return True

    def require_owner(self) -> bool:
        if self.is_owner():
            return True
        self.send_json(401, {"ok": False, "error": "Sesi owner tidak valid."})
        return False

    @staticmethod
    def is_private_static_path(path: str) -> bool:
        parts = [part for part in Path(path).parts if part not in {"/", "\\"}]
        return (
            path == "/owner-builder.html"
            or path == "/data"
            or path.startswith("/data/")
            or any(part.startswith(".") for part in parts)
        )

    def do_GET(self):
        path = unquote(urlparse(self.path).path)

        if path == "/api/v1/auth/me":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Sesi member aktif.",
                {"user": session.user, "csrfToken": session.csrf_token},
            )
            return

        if path == "/api/v1/member/profile":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            profile = AUTH_STORE.get_profile(session.user["id"])
            if not profile:
                self.auth_response(404, False, "Profile member tidak ditemukan.")
                return
            self.auth_response(
                200,
                True,
                "Profile member tersedia.",
                {"profile": profile},
            )
            return

        normalized_path = path.rstrip("/") or "/"
        if normalized_path in PROTECTED_MEMBER_ROUTES and not self.member_session():
            target = quote(normalized_path, safe="/")
            self.send_response(303)
            self.send_header("Location", f"/login?next={target}")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return

        if path.rstrip("/") in MARKETPLACE_ROUTES or path.startswith("/marketplace/product/"):
            self.path = MARKETPLACE_SHELL
            super().do_GET()
            return

        if path == "/api/public-settings":
            self.send_json(200, read_settings())
            return

        if path == "/api/owner/session":
            self.send_json(200, {"authenticated": self.is_owner()})
            return

        if path in {"/owner-builder", "/owner-builder/"}:
            if not self.is_owner():
                self.send_error(404)
                return
            self.path = "/owner-builder.html"
            super().do_GET()
            return

        if path == "/health":
            body = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.is_private_static_path(path):
            self.send_error(404)
            return

        if path.startswith("/owner-media/"):
            self.serve_owner_media(path)
            return

        super().do_GET()

    def do_HEAD(self):
        path = unquote(urlparse(self.path).path)

        normalized_path = path.rstrip("/") or "/"
        if normalized_path in PROTECTED_MEMBER_ROUTES and not self.member_session():
            target = quote(normalized_path, safe="/")
            self.send_response(303)
            self.send_header("Location", f"/login?next={target}")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return

        if path.rstrip("/") in MARKETPLACE_ROUTES or path.startswith("/marketplace/product/"):
            self.path = MARKETPLACE_SHELL
            super().do_HEAD()
            return

        if path in {"/owner-builder", "/owner-builder/"}:
            if not self.is_owner():
                self.send_error(404)
                return
            self.path = "/owner-builder.html"
            super().do_HEAD()
            return

        if self.is_private_static_path(path):
            self.send_error(404)
            return

        if path.startswith("/owner-media/"):
            self.serve_owner_media(path, head_only=True)
            return
        super().do_HEAD()

    def serve_owner_media(self, path: str, head_only: bool = False) -> None:
        relative = Path(path.removeprefix("/owner-media/")).name
        target = UPLOAD_ROOT / relative
        if not target.is_file():
            self.send_error(404)
            return

        file_size = target.stat().st_size
        start = 0
        end = max(0, file_size - 1)
        status = 200
        range_header = self.headers.get("Range", "")

        if range_header.startswith("bytes="):
            try:
                requested = range_header.removeprefix("bytes=").split(",", 1)[0]
                raw_start, raw_end = requested.split("-", 1)
                if raw_start:
                    start = int(raw_start)
                    end = min(int(raw_end), end) if raw_end else end
                elif raw_end:
                    suffix_length = int(raw_end)
                    start = max(0, file_size - suffix_length)
                if start < 0 or start > end or start >= file_size:
                    raise ValueError
                status = 206
            except (ValueError, TypeError):
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{file_size}")
                self.end_headers()
                return

        content_length = end - start + 1
        mime_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(status)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "public, max-age=86400")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.end_headers()

        if head_only:
            return

        with target.open("rb") as media:
            media.seek(start)
            remaining = content_length
            while remaining > 0:
                chunk = media.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_POST(self):
        path = unquote(urlparse(self.path).path)

        if path == "/api/v1/auth/register":
            if not self.is_same_origin_request():
                self.auth_response(403, False, "Origin request tidak diizinkan.")
                return
            if self.auth_rate_limited("register", 5, 60 * 60):
                self.auth_response(429, False, "Terlalu banyak percobaan registrasi.")
                return
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                if not isinstance(payload, dict):
                    raise AuthValidationError("Data registrasi tidak valid.")
                user = AUTH_STORE.register(
                    payload.get("name"),
                    payload.get("email"),
                    payload.get("password"),
                )
                token, session = AUTH_STORE.create_session(user["id"])
            except AuthValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except DuplicateEmailError as error:
                self.auth_response(409, False, str(error), errors={"email": str(error)})
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request registrasi tidak valid.")
                return
            self.auth_response(
                201,
                True,
                "Akun member berhasil dibuat.",
                {"user": session.user, "csrfToken": session.csrf_token},
                extra_headers=[
                    ("Set-Cookie", self.member_cookie(token, MEMBER_SESSION_ABSOLUTE_TTL))
                ],
            )
            return

        if path == "/api/v1/auth/login":
            if not self.is_same_origin_request():
                self.auth_response(403, False, "Origin request tidak diizinkan.")
                return
            if self.auth_rate_limited("login", 10, 15 * 60):
                self.auth_response(429, False, "Terlalu banyak percobaan login.")
                return
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                if not isinstance(payload, dict):
                    raise AuthValidationError("Email atau password tidak valid.")
                user = AUTH_STORE.authenticate(
                    payload.get("email"),
                    payload.get("password"),
                )
            except AuthValidationError:
                user = None
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request login tidak valid.")
                return
            if not user:
                time.sleep(0.25)
                self.auth_response(401, False, "Email atau password tidak valid.")
                return
            token, session = AUTH_STORE.create_session(user["id"])
            self.auth_response(
                200,
                True,
                "Login berhasil.",
                {"user": session.user, "csrfToken": session.csrf_token},
                extra_headers=[
                    ("Set-Cookie", self.member_cookie(token, MEMBER_SESSION_ABSOLUTE_TTL))
                ],
            )
            return

        if path == "/api/v1/auth/logout":
            if not self.is_same_origin_request():
                self.auth_response(403, False, "Origin request tidak diizinkan.")
                return
            token = self.member_session_token()
            session = AUTH_STORE.get_session(token, refresh=False)
            if not self.valid_member_csrf(session):
                self.auth_response(403, False, "CSRF token tidak valid.")
                return
            AUTH_STORE.revoke_session(token)
            self.auth_response(
                200,
                True,
                "Logout berhasil.",
                extra_headers=[("Set-Cookie", self.member_cookie("", 0))],
            )
            return

        if path == "/api/owner/login":
            try:
                payload = self.read_json()
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.send_json(400, {"ok": False, "error": "Request login tidak valid."})
                return

            submitted = payload.get("password", "") if isinstance(payload, dict) else ""
            if not OWNER_PASSWORD or not hmac.compare_digest(str(submitted), OWNER_PASSWORD):
                time.sleep(0.35)
                self.send_json(401, {"ok": False, "error": "Password owner salah."})
                return

            token = secrets.token_urlsafe(32)
            SESSIONS[token] = time.time() + SESSION_TTL
            secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
            cookie = (
                f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict; "
                f"Max-Age={SESSION_TTL}{secure}"
            )
            self.send_json(200, {"ok": True}, [("Set-Cookie", cookie)])
            return

        if path == "/api/owner/logout":
            token = self.session_token()
            SESSIONS.pop(token, None)
            expired = f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0"
            self.send_json(200, {"ok": True}, [("Set-Cookie", expired)])
            return

        if path == "/api/owner/settings":
            if not self.require_owner():
                return
            try:
                payload = self.read_json()
                saved = write_settings(payload)
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError):
                self.send_json(400, {"ok": False, "error": "Setting tidak dapat disimpan."})
                return
            self.send_json(200, {"ok": True, "settings": saved})
            return

        if path == "/api/owner/upload":
            if not self.require_owner():
                return
            try:
                payload = self.read_json()
                public_url = self.save_upload(payload)
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError) as error:
                self.send_json(400, {"ok": False, "error": str(error)})
                return
            self.send_json(200, {"ok": True, "url": public_url})
            return

        self.send_error(404)

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)

        if path == "/api/v1/member/profile":
            if not self.is_same_origin_request():
                self.auth_response(403, False, "Origin request tidak diizinkan.")
                return
            session = self.member_session(refresh=False)
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            if not self.valid_member_csrf(session):
                self.auth_response(403, False, "CSRF token tidak valid.")
                return
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                profile = AUTH_STORE.update_profile(session.user["id"], payload)
            except AuthValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request profile tidak valid.")
                return
            except LookupError:
                self.auth_response(404, False, "Profile member tidak ditemukan.")
                return
            self.auth_response(
                200,
                True,
                "Profile berhasil diperbarui.",
                {"profile": profile},
            )
            return

        self.send_error(404)

    def save_upload(self, payload: object) -> str:
        if not isinstance(payload, dict):
            raise ValueError("Data upload tidak valid.")

        kind = payload.get("kind")
        data_url = payload.get("data")
        if kind not in ALLOWED_UPLOADS or not isinstance(data_url, str):
            raise ValueError("Jenis upload tidak didukung.")

        try:
            metadata, encoded = data_url.split(",", 1)
            mime_type = metadata.removeprefix("data:").split(";", 1)[0].lower()
            binary = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error):
            raise ValueError("File upload rusak atau tidak valid.")

        extension = ALLOWED_UPLOADS[kind].get(mime_type)
        if not extension:
            raise ValueError("Format file tidak didukung.")

        limit = 100 * 1024 * 1024 if kind == "video" else 10 * 1024 * 1024
        if len(binary) > limit:
            raise ValueError("Ukuran file melebihi batas.")

        digest = hashlib.sha256(binary).hexdigest()[:16]
        filename = f"{kind}-{digest}{extension}"
        UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        (UPLOAD_ROOT / filename).write_bytes(binary)
        return f"/owner-media/{filename}"


def main():
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    AUTH_STORE.initialize()
    AUTH_STORE.cleanup_expired_sessions()
    server = ThreadingHTTPServer((HOST, PORT), BintangHandler)
    print(f"Bintang Computer Feira server: http://{HOST}:{PORT}")
    if not OWNER_PASSWORD:
        print("WARNING: OWNER_PASSWORD belum diatur. Owner login dinonaktifkan.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
