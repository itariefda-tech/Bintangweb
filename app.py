from __future__ import annotations

import base64
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import time
from http import cookies
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env_file() -> None:
    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file()

PUBLIC_ROOT = Path(os.environ.get("PUBLIC_ROOT") or PROJECT_ROOT).resolve()
DATA_ROOT = Path(os.environ.get("DATA_ROOT") or PROJECT_ROOT / "data").resolve()
UPLOAD_ROOT = DATA_ROOT / "owner-media"
SETTINGS_FILE = DATA_ROOT / "owner-settings.json"

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
SESSION_TTL = 8 * 60 * 60
SESSION_COOKIE = "bcf_owner_session"
MAX_JSON_BODY = 140 * 1024 * 1024

DEFAULT_SETTINGS = {
    "processAudioAutoplay": True,
    "workVideo": "",
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


OWNER_PASSWORD = os.environ.get("OWNER_PASSWORD", "")


class BintangHandler(SimpleHTTPRequestHandler):
    server_version = "BintangWeb/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        if self.path.startswith("/api/") or self.path.startswith("/owner-builder"):
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

    def read_json(self) -> object:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_JSON_BODY:
            raise ValueError("Ukuran request tidak valid.")
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def session_token(self) -> str:
        raw_cookie = self.headers.get("Cookie", "")
        jar = cookies.SimpleCookie()
        try:
            jar.load(raw_cookie)
        except cookies.CookieError:
            return ""
        morsel = jar.get(SESSION_COOKIE)
        return morsel.value if morsel else ""

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
