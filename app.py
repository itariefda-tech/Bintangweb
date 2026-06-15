from __future__ import annotations

import base64
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import smtplib
import threading
import time
from email.message import EmailMessage
from http import cookies
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from marketplace_auth import (
    AuthAccountStatusError,
    AuthStore,
    AuthValidationError,
    DuplicateEmailError,
)
from marketplace_admin import AdminStore, AdminValidationError
from marketplace_catalog import CatalogStore, CatalogValidationError
from marketplace_checkout import (
    CartStore,
    CheckoutValidationError,
    StockConflictError,
)
from marketplace_consultation import (
    ConsultationStore,
    ConsultationValidationError,
)
from marketplace_news import NewsStore, NewsValidationError
from marketplace_payment import (
    MidtransClient,
    PaymentGatewayError,
    PaymentStore,
    PaymentValidationError,
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
MEMBER_MEDIA_ROOT = DATA_ROOT / "member-media"
CONSULTATION_MEDIA_ROOT = DATA_ROOT / "consultation-media"
SETTINGS_FILE = DATA_ROOT / "owner-settings.json"
MARKETPLACE_DATABASE = DATA_ROOT / "marketplace.sqlite3"
MARKETPLACE_SHELL = "/src/pages/marketplace-shell.html"

MARKETPLACE_ROUTES = {
    "/marketplace",
    "/login",
    "/register",
    "/forgot-password",
    "/reset-password",
    "/member",
    "/member/profile",
    "/member/notifications",
    "/member/orders",
    "/member/consultation",
    "/news",
    "/checkout",
    "/admin",
    "/admin/consultation",
    "/admin/orders",
    "/admin/products",
}
PROTECTED_MEMBER_ROUTES = {
    "/member",
    "/member/profile",
    "/member/notifications",
    "/member/orders",
    "/member/consultation",
    "/checkout",
}
PROTECTED_ADMIN_ROUTES = {
    "/admin",
    "/admin/consultation",
    "/admin/orders",
    "/admin/products",
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
MAX_AVATAR_JSON_BODY = 3 * 1024 * 1024
MAX_CONSULTATION_JSON_BODY = 8 * 1024 * 1024
PASSWORD_RESET_DEBUG = os.environ.get("PASSWORD_RESET_DEBUG", "0") == "1"
SMTP_HOST = os.environ.get("SMTP_HOST", "").strip()
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USERNAME).strip()
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "1") == "1"
SUPER_ADMIN_EMAILS = {
    email.strip().lower()
    for email in os.environ.get("MARKETPLACE_SUPER_ADMIN_EMAILS", "").split(",")
    if email.strip()
}
MIDTRANS_SERVER_KEY = os.environ.get("MIDTRANS_SERVER_KEY", "").strip()
MIDTRANS_PRODUCTION = os.environ.get("MIDTRANS_PRODUCTION", "0") == "1"
MIDTRANS_MOCK = os.environ.get(
    "MIDTRANS_MOCK", "0" if MIDTRANS_SERVER_KEY else "1"
) == "1"

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
    "product": {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    },
    "news": {
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
    super_admin_emails=SUPER_ADMIN_EMAILS,
)
ADMIN_STORE = AdminStore(MARKETPLACE_DATABASE)
CATALOG_STORE = CatalogStore(MARKETPLACE_DATABASE)
CART_STORE = CartStore(MARKETPLACE_DATABASE)
CONSULTATION_STORE = ConsultationStore(MARKETPLACE_DATABASE, CONSULTATION_MEDIA_ROOT)
NEWS_STORE = NewsStore(MARKETPLACE_DATABASE)
MIDTRANS_CLIENT = MidtransClient(
    server_key=MIDTRANS_SERVER_KEY,
    production=MIDTRANS_PRODUCTION,
    mock=MIDTRANS_MOCK,
)
PAYMENT_STORE = PaymentStore(MARKETPLACE_DATABASE, MIDTRANS_CLIENT)


def send_password_reset_email(user: dict, reset_url: str) -> bool:
    if not SMTP_HOST or not SMTP_FROM:
        return False
    message = EmailMessage()
    message["Subject"] = "Reset password Feira"
    message["From"] = SMTP_FROM
    message["To"] = user["email"]
    message.set_content(
        "\n".join(
            [
                f"Halo {user['name']},",
                "",
                "Gunakan link berikut untuk mengatur ulang password Feira Anda:",
                reset_url,
                "",
                "Link berlaku selama 30 menit. Abaikan email ini jika Anda tidak memintanya.",
            ]
        )
    )
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            if SMTP_USE_TLS:
                smtp.starttls()
            if SMTP_USERNAME:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(message)
        return True
    except (OSError, smtplib.SMTPException) as error:
        print(f"WARNING: password reset email gagal dikirim: {error}")
        return False


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

    @staticmethod
    def is_admin_user(user: dict | None) -> bool:
        return bool(user and user.get("role") in {"admin", "super_admin"})

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
        parsed_url = urlparse(self.path)
        path = unquote(parsed_url.path)
        query = parse_qs(parsed_url.query)

        if path == "/api/v1/categories":
            self.auth_response(
                200,
                True,
                "Kategori produk tersedia.",
                {"categories": CATALOG_STORE.list_categories()},
            )
            return

        if path == "/api/v1/products":
            featured_value = str(query.get("featured", [""])[0]).lower()
            products = CATALOG_STORE.list_products(
                search=query.get("search", [""])[0],
                category=query.get("category", [""])[0],
                featured=featured_value in {"1", "true", "yes"},
                sort=query.get("sort", ["featured"])[0],
            )
            self.auth_response(
                200,
                True,
                "Produk tersedia.",
                {"products": products, "count": len(products)},
            )
            return

        if path == "/api/v1/news/categories":
            self.auth_response(
                200,
                True,
                "Kategori news tersedia.",
                {"categories": NEWS_STORE.list_categories()},
            )
            return

        if path == "/api/v1/news":
            featured_value = str(query.get("featured", [""])[0]).lower()
            trending_value = str(query.get("trending", [""])[0]).lower()
            articles = NEWS_STORE.list_articles(
                search=query.get("search", query.get("q", [""]))[0],
                category=query.get("category", [""])[0],
                featured=featured_value in {"1", "true", "yes"},
                trending=trending_value in {"1", "true", "yes"},
            )
            self.auth_response(
                200,
                True,
                "Artikel news tersedia.",
                {"articles": articles, "count": len(articles)},
            )
            return

        if path == "/api/v1/news/featured":
            articles = NEWS_STORE.list_articles(featured=True)
            self.auth_response(
                200,
                True,
                "Artikel featured tersedia.",
                {"articles": articles, "count": len(articles)},
            )
            return

        if path == "/api/v1/news/trending":
            articles = NEWS_STORE.list_articles(trending=True)
            self.auth_response(
                200,
                True,
                "Artikel trending tersedia.",
                {"articles": articles, "count": len(articles)},
            )
            return

        if path.startswith("/api/v1/news/"):
            slug = path.removeprefix("/api/v1/news/").strip("/")
            article = NEWS_STORE.get_article(slug)
            if not article:
                self.auth_response(404, False, "Artikel tidak ditemukan.")
                return
            self.auth_response(
                200,
                True,
                "Detail artikel tersedia.",
                {"article": article},
            )
            return

        if path == "/api/v1/products/featured":
            products = CATALOG_STORE.list_products(featured=True)
            self.auth_response(
                200,
                True,
                "Produk featured tersedia.",
                {"products": products, "count": len(products)},
            )
            return

        if path == "/api/v1/products/search":
            products = CATALOG_STORE.list_products(
                search=query.get("q", query.get("search", [""]))[0],
                sort=query.get("sort", ["featured"])[0],
            )
            self.auth_response(
                200,
                True,
                "Hasil pencarian produk tersedia.",
                {"products": products, "count": len(products)},
            )
            return

        if path.startswith("/api/v1/products/category/"):
            category_slug = path.removeprefix("/api/v1/products/category/").strip("/")
            products = CATALOG_STORE.list_products(
                category=category_slug,
                sort=query.get("sort", ["featured"])[0],
            )
            self.auth_response(
                200,
                True,
                "Produk kategori tersedia.",
                {"products": products, "count": len(products)},
            )
            return

        if path.startswith("/api/v1/products/"):
            slug = path.removeprefix("/api/v1/products/").strip("/")
            product = CATALOG_STORE.get_product(slug)
            if not product:
                self.auth_response(404, False, "Produk tidak ditemukan.")
                return
            self.auth_response(
                200,
                True,
                "Detail produk tersedia.",
                {"product": product},
            )
            return

        if path.startswith("/api/v1/categories/"):
            category_slug = path.removeprefix("/api/v1/categories/").strip("/")
            category = next(
                (
                    item
                    for item in CATALOG_STORE.list_categories()
                    if item["slug"] == category_slug
                ),
                None,
            )
            if not category:
                self.auth_response(404, False, "Kategori tidak ditemukan.")
                return
            category["products"] = CATALOG_STORE.list_products(category=category_slug)
            self.auth_response(
                200,
                True,
                "Detail kategori tersedia.",
                {"category": category},
            )
            return

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

        if path == "/api/v1/member/notifications":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            notifications = AUTH_STORE.list_notifications(session.user["id"])
            self.auth_response(
                200,
                True,
                "Notifikasi member tersedia.",
                {"notifications": notifications},
            )
            return

        if path == "/api/v1/cart":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Cart tersedia.",
                {"cart": CART_STORE.get_cart(session.user["id"])},
            )
            return

        if path == "/api/v1/member/addresses":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Alamat member tersedia.",
                {"addresses": CART_STORE.list_addresses(session.user["id"])},
            )
            return

        if path == "/api/v1/member/orders":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Order member tersedia.",
                {"orders": CART_STORE.list_orders(session.user["id"])},
            )
            return

        if path == "/api/v1/member/consultation":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Ticket konsultasi tersedia.",
                {"tickets": CONSULTATION_STORE.list_tickets(session.user["id"])},
            )
            return

        if path.startswith("/api/v1/consultation/attachments/"):
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            attachment_id = path.removeprefix(
                "/api/v1/consultation/attachments/"
            ).strip("/")
            try:
                attachment = CONSULTATION_STORE.get_attachment(
                    session.user,
                    attachment_id,
                )
            except LookupError:
                self.auth_response(404, False, "Attachment konsultasi tidak ditemukan.")
                return
            self.serve_consultation_attachment(attachment)
            return

        if path.startswith("/api/v1/member/consultation/"):
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            ticket_id = path.removeprefix("/api/v1/member/consultation/").strip("/")
            try:
                ticket = CONSULTATION_STORE.get_ticket(session.user["id"], ticket_id)
            except LookupError:
                self.auth_response(404, False, "Ticket konsultasi tidak ditemukan.")
                return
            self.auth_response(
                200,
                True,
                "Detail ticket konsultasi tersedia.",
                {"ticket": ticket},
            )
            return

        if path == "/api/v1/admin/consultation":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            try:
                tickets = CONSULTATION_STORE.admin_queue(
                    session.user,
                    status=query.get("status", [""])[0],
                )
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            self.auth_response(
                200,
                True,
                "Queue konsultasi tersedia.",
                {"tickets": tickets},
            )
            return

        if path == "/api/v1/admin/kpis":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            try:
                kpis = ADMIN_STORE.dashboard_kpis(session.user)
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            self.auth_response(
                200,
                True,
                "KPI dashboard admin tersedia.",
                {"kpis": kpis},
            )
            return

        if path == "/api/v1/admin/orders":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            try:
                orders = ADMIN_STORE.list_orders(
                    session.user,
                    payment_status=query.get("paymentStatus", [""])[0],
                    order_status=query.get("orderStatus", [""])[0],
                )
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except AdminValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            self.auth_response(
                200,
                True,
                "Order admin tersedia.",
                {"orders": orders, "count": len(orders)},
            )
            return

        if path == "/api/v1/admin/products":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            try:
                products = ADMIN_STORE.list_products(session.user)
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            self.auth_response(
                200,
                True,
                "Produk admin tersedia.",
                {"products": products, "count": len(products)},
            )
            return

        if path.startswith("/api/v1/admin/orders/"):
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            order_id = path.removeprefix("/api/v1/admin/orders/").strip("/")
            try:
                order = ADMIN_STORE.get_order(session.user, order_id)
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except LookupError:
                self.auth_response(404, False, "Order tidak ditemukan.")
                return
            self.auth_response(
                200,
                True,
                "Detail invoice tersedia.",
                {"order": order},
            )
            return

        if path == "/api/v1/payments":
            session = self.member_session()
            if not session:
                self.auth_response(401, False, "Sesi member tidak valid.")
                return
            order_id = str(query.get("orderId", [""])[0]).strip()
            if not order_id:
                self.auth_response(422, False, "Order wajib dipilih.")
                return
            self.auth_response(
                200,
                True,
                "Payment order tersedia.",
                {
                    "payments": PAYMENT_STORE.list_order_payments(
                        session.user["id"], order_id
                    )
                },
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
        if normalized_path in PROTECTED_ADMIN_ROUTES:
            session = self.member_session()
            if not session:
                target = quote(normalized_path, safe="/")
                self.send_response(303)
                self.send_header("Location", f"/login?next={target}")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            if not self.is_admin_user(session.user):
                self.send_error(403)
                return

        if (
            path.rstrip("/") in MARKETPLACE_ROUTES
            or path.startswith("/marketplace/product/")
            or path.startswith("/news/")
        ):
            self.path = MARKETPLACE_SHELL
            super().do_GET()
            return

        if path == "/api/public-settings":
            self.send_json(200, read_settings())
            return

        if path == "/api/owner/session":
            self.send_json(200, {"authenticated": self.is_owner()})
            return

        if path == "/api/owner/catalog":
            if not self.require_owner():
                return
            self.send_json(
                200,
                {
                    "ok": True,
                    "products": CATALOG_STORE.list_admin_products(),
                    "categories": CATALOG_STORE.list_categories(),
                },
            )
            return

        if path == "/api/owner/members":
            if not self.require_owner():
                return
            self.send_json(200, {"ok": True, "members": AUTH_STORE.list_members()})
            return

        if path == "/api/owner/news":
            if not self.require_owner():
                return
            self.send_json(
                200,
                {
                    "ok": True,
                    "articles": NEWS_STORE.list_admin_articles(),
                    "categories": NEWS_STORE.list_admin_categories(),
                },
            )
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

        if path.startswith("/member-media/"):
            self.serve_member_media(path)
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
        if normalized_path in PROTECTED_ADMIN_ROUTES:
            session = self.member_session()
            if not session:
                target = quote(normalized_path, safe="/")
                self.send_response(303)
                self.send_header("Location", f"/login?next={target}")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            if not self.is_admin_user(session.user):
                self.send_error(403)
                return

        if (
            path.rstrip("/") in MARKETPLACE_ROUTES
            or path.startswith("/marketplace/product/")
            or path.startswith("/news/")
        ):
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
        if path.startswith("/member-media/"):
            self.serve_member_media(path, head_only=True)
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

    def serve_member_media(self, path: str, head_only: bool = False) -> None:
        filename = Path(path.removeprefix("/member-media/")).name
        target = MEMBER_MEDIA_ROOT / filename
        if not target.is_file():
            self.send_error(404)
            return
        mime_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=86400, immutable")
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def serve_consultation_attachment(
        self,
        attachment: dict,
        head_only: bool = False,
    ) -> None:
        target = attachment["path"]
        body = target.read_bytes()
        safe_filename = str(attachment["filename"]).replace('"', "")
        self.send_response(200)
        self.send_header("Content-Type", attachment["mimeType"])
        self.send_header("Content-Length", str(len(body)))
        self.send_header(
            "Content-Disposition",
            f'attachment; filename="{safe_filename}"',
        )
        self.send_header("Cache-Control", "private, no-store")
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

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
                    pending_approval=True,
                )
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
                "Registrasi berhasil. Akun menunggu persetujuan owner.",
                {"user": user, "approvalRequired": user["status"] != "active"},
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
            except AuthAccountStatusError as error:
                self.auth_response(403, False, str(error))
                return
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

        if path == "/api/v1/auth/forgot-password":
            if not self.is_same_origin_request():
                self.auth_response(403, False, "Origin request tidak diizinkan.")
                return
            if self.auth_rate_limited("forgot-password", 5, 60 * 60):
                self.auth_response(429, False, "Terlalu banyak permintaan reset password.")
                return
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                email = payload.get("email") if isinstance(payload, dict) else ""
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request reset password tidak valid.")
                return
            reset = AUTH_STORE.create_password_reset(email)
            response_data = None
            if reset:
                token, user = reset
                scheme = (
                    "https"
                    if self.headers.get("X-Forwarded-Proto") == "https"
                    else "http"
                )
                reset_url = (
                    f"{scheme}://{self.headers.get('Host', '')}"
                    f"/reset-password?token={quote(token, safe='')}"
                )
                send_password_reset_email(user, reset_url)
                if PASSWORD_RESET_DEBUG:
                    response_data = {"resetUrl": reset_url}
            self.auth_response(
                200,
                True,
                "Jika email terdaftar, instruksi reset password telah dikirim.",
                response_data,
            )
            return

        if path == "/api/v1/auth/reset-password":
            if not self.is_same_origin_request():
                self.auth_response(403, False, "Origin request tidak diizinkan.")
                return
            if self.auth_rate_limited("reset-password", 10, 60 * 60):
                self.auth_response(429, False, "Terlalu banyak percobaan reset password.")
                return
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                if not isinstance(payload, dict):
                    raise AuthValidationError("Request reset password tidak valid.")
                AUTH_STORE.reset_password(payload.get("token"), payload.get("password"))
            except AuthValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request reset password tidak valid.")
                return
            self.auth_response(200, True, "Password berhasil diperbarui. Silakan login.")
            return

        if path == "/api/v1/member/avatar":
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
                payload = self.read_json(MAX_AVATAR_JSON_BODY)
                avatar_url = self.save_member_avatar(session.user["id"], payload)
                profile = AUTH_STORE.update_avatar(session.user["id"], avatar_url)
            except AuthValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError) as error:
                self.auth_response(400, False, str(error))
                return
            self.auth_response(
                200,
                True,
                "Avatar berhasil diperbarui.",
                {"profile": profile},
            )
            return

        if path == "/api/v1/cart/add":
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
                if not isinstance(payload, dict):
                    raise CheckoutValidationError("Data cart tidak valid.")
                cart = CART_STORE.add_item(
                    session.user["id"], payload.get("productSlug"), payload.get("qty", 1)
                )
            except CheckoutValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except StockConflictError as error:
                self.auth_response(409, False, str(error))
                return
            except LookupError:
                self.auth_response(404, False, "Produk tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request cart tidak valid.")
                return
            self.auth_response(200, True, "Produk ditambahkan ke cart.", {"cart": cart})
            return

        if path == "/api/v1/member/addresses":
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
                address = CART_STORE.save_address(session.user["id"], payload)
            except CheckoutValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request alamat tidak valid.")
                return
            self.auth_response(201, True, "Alamat berhasil disimpan.", {"address": address})
            return

        if path == "/api/v1/checkout":
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
                order = CART_STORE.checkout(session.user["id"], payload)
            except CheckoutValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except StockConflictError as error:
                self.auth_response(409, False, str(error))
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request checkout tidak valid.")
                return
            self.auth_response(201, True, "Order berhasil dibuat.", {"order": order})
            return

        if path == "/api/v1/payment/create":
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
            if self.auth_rate_limited("payment-create", 20, 60 * 60):
                self.auth_response(429, False, "Terlalu banyak percobaan pembayaran.")
                return
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                if not isinstance(payload, dict):
                    raise PaymentValidationError("Data payment tidak valid.")
                payment = PAYMENT_STORE.create_payment(
                    session.user["id"],
                    payload.get("orderId"),
                    payload.get("method"),
                    payload.get("bank"),
                )
            except PaymentValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except PaymentGatewayError as error:
                self.auth_response(502, False, str(error))
                return
            except LookupError:
                self.auth_response(404, False, "Order tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request payment tidak valid.")
                return
            self.auth_response(
                201,
                True,
                "Instruksi pembayaran berhasil dibuat.",
                {"payment": payment, "mock": MIDTRANS_CLIENT.mock},
            )
            return

        if path == "/api/v1/payment/callback/midtrans":
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                result = PAYMENT_STORE.handle_notification(payload)
            except PermissionError:
                self.auth_response(403, False, "Signature callback tidak valid.")
                return
            except PaymentValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except LookupError:
                self.auth_response(404, False, "Payment tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Callback payment tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Callback payment diproses.",
                result,
            )
            return

        if path == "/api/v1/member/consultation":
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
                payload = self.read_json(MAX_CONSULTATION_JSON_BODY)
                ticket = CONSULTATION_STORE.create_ticket(session.user["id"], payload)
            except ConsultationValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request konsultasi tidak valid.")
                return
            self.auth_response(
                201,
                True,
                "Ticket konsultasi berhasil dibuat.",
                {"ticket": ticket},
            )
            return

        if path == "/api/v1/admin/products":
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
                product = ADMIN_STORE.save_product(session.user, payload)
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except CatalogValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request produk tidak valid.")
                return
            self.auth_response(
                201,
                True,
                "Produk berhasil ditambahkan.",
                {"product": product},
            )
            return

        if path == "/api/v1/admin/products/upload":
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
            if not self.is_admin_user(session.user):
                self.auth_response(403, False, "Hanya admin yang dapat upload produk.")
                return
            try:
                payload = self.read_json(12 * 1024 * 1024)
                if not isinstance(payload, dict):
                    raise ValueError("Data upload tidak valid.")
                public_url = self.save_upload({**payload, "kind": "product"})
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError) as error:
                self.auth_response(422, False, str(error))
                return
            self.auth_response(
                201,
                True,
                "Gambar produk berhasil diupload.",
                {"url": public_url},
            )
            return

        if path.startswith("/api/v1/member/consultation/") and path.endswith("/replies"):
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
            ticket_id = (
                path.removeprefix("/api/v1/member/consultation/")
                .removesuffix("/replies")
                .strip("/")
            )
            try:
                payload = self.read_json(MAX_CONSULTATION_JSON_BODY)
                if not isinstance(payload, dict):
                    raise ConsultationValidationError("Reply tidak valid.")
                ticket = CONSULTATION_STORE.add_reply(
                    session.user,
                    ticket_id,
                    payload.get("message"),
                    payload.get("attachment"),
                )
            except ConsultationValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except LookupError:
                self.auth_response(404, False, "Ticket konsultasi tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request reply tidak valid.")
                return
            self.auth_response(
                201,
                True,
                "Reply konsultasi berhasil dikirim.",
                {"ticket": ticket},
            )
            return

        if path.startswith("/api/v1/admin/consultation/") and path.endswith("/replies"):
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
            ticket_id = (
                path.removeprefix("/api/v1/admin/consultation/")
                .removesuffix("/replies")
                .strip("/")
            )
            try:
                if session.user.get("role") not in {"admin", "super_admin"}:
                    raise PermissionError("Hanya admin yang dapat membalas ticket.")
                payload = self.read_json(MAX_CONSULTATION_JSON_BODY)
                if not isinstance(payload, dict):
                    raise ConsultationValidationError("Reply tidak valid.")
                ticket = CONSULTATION_STORE.add_reply(
                    session.user,
                    ticket_id,
                    payload.get("message"),
                    payload.get("attachment"),
                )
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except ConsultationValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except LookupError:
                self.auth_response(404, False, "Ticket konsultasi tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request reply tidak valid.")
                return
            self.auth_response(
                201,
                True,
                "Reply admin berhasil dikirim.",
                {"ticket": ticket},
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

        if path == "/api/owner/products":
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            try:
                product = CATALOG_STORE.save_product(self.read_json(MAX_AUTH_JSON_BODY))
            except CatalogValidationError as error:
                self.send_json(
                    422,
                    {"ok": False, "error": str(error), "errors": error.errors},
                )
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.send_json(400, {"ok": False, "error": "Request produk tidak valid."})
                return
            self.send_json(201, {"ok": True, "product": product})
            return

        if path == "/api/owner/news/categories":
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            try:
                category = NEWS_STORE.save_category(self.read_json(MAX_AUTH_JSON_BODY))
            except NewsValidationError as error:
                self.send_json(
                    422,
                    {"ok": False, "error": str(error), "errors": error.errors},
                )
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.send_json(400, {"ok": False, "error": "Request kategori tidak valid."})
                return
            self.send_json(201, {"ok": True, "category": category})
            return

        if path == "/api/owner/news/articles":
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            try:
                article = NEWS_STORE.save_article(self.read_json(MAX_JSON_BODY))
            except NewsValidationError as error:
                self.send_json(
                    422,
                    {"ok": False, "error": str(error), "errors": error.errors},
                )
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.send_json(400, {"ok": False, "error": "Request artikel tidak valid."})
                return
            self.send_json(201, {"ok": True, "article": article})
            return

        self.send_error(404)

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)

        if path.startswith("/api/owner/news/categories/"):
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            category_id = path.removeprefix("/api/owner/news/categories/").strip("/")
            try:
                category = NEWS_STORE.save_category(
                    self.read_json(MAX_AUTH_JSON_BODY),
                    category_id,
                )
            except NewsValidationError as error:
                self.send_json(
                    422,
                    {"ok": False, "error": str(error), "errors": error.errors},
                )
                return
            except LookupError:
                self.send_json(404, {"ok": False, "error": "Kategori tidak ditemukan."})
                return
            self.send_json(200, {"ok": True, "category": category})
            return

        if path.startswith("/api/owner/news/articles/"):
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            article_id = path.removeprefix("/api/owner/news/articles/").strip("/")
            try:
                article = NEWS_STORE.save_article(
                    self.read_json(MAX_JSON_BODY),
                    article_id,
                )
            except NewsValidationError as error:
                self.send_json(
                    422,
                    {"ok": False, "error": str(error), "errors": error.errors},
                )
                return
            except LookupError:
                self.send_json(404, {"ok": False, "error": "Artikel tidak ditemukan."})
                return
            self.send_json(200, {"ok": True, "article": article})
            return

        if path.startswith("/api/v1/admin/products/"):
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
            product_id = path.removeprefix("/api/v1/admin/products/").strip("/")
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                product = ADMIN_STORE.save_product(
                    session.user,
                    payload,
                    product_id,
                )
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except CatalogValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except LookupError:
                self.auth_response(404, False, "Produk tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request produk tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Produk berhasil diperbarui.",
                {"product": product},
            )
            return

        if path.startswith("/api/owner/products/"):
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            product_id = path.removeprefix("/api/owner/products/").strip("/")
            try:
                product = CATALOG_STORE.save_product(
                    self.read_json(MAX_AUTH_JSON_BODY), product_id
                )
            except CatalogValidationError as error:
                self.send_json(
                    422,
                    {"ok": False, "error": str(error), "errors": error.errors},
                )
                return
            except LookupError as error:
                self.send_json(404, {"ok": False, "error": str(error)})
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.send_json(400, {"ok": False, "error": "Request produk tidak valid."})
                return
            self.send_json(200, {"ok": True, "product": product})
            return

        if path.startswith("/api/owner/members/") and path.endswith("/status"):
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            member_id = (
                path.removeprefix("/api/owner/members/")
                .removesuffix("/status")
                .strip("/")
            )
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                member = AUTH_STORE.update_member_status(
                    member_id, payload.get("status") if isinstance(payload, dict) else ""
                )
            except AuthValidationError as error:
                self.send_json(
                    422,
                    {"ok": False, "error": str(error), "errors": error.errors},
                )
                return
            except LookupError as error:
                self.send_json(404, {"ok": False, "error": str(error)})
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.send_json(400, {"ok": False, "error": "Request member tidak valid."})
                return
            self.send_json(200, {"ok": True, "member": member})
            return

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

        if path == "/api/v1/member/notifications/read":
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
                notification_id = (
                    str(payload.get("notificationId") or "").strip()
                    if isinstance(payload, dict)
                    else ""
                )
                notifications = AUTH_STORE.mark_notifications_read(
                    session.user["id"], notification_id or None
                )
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request notifikasi tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Status notifikasi diperbarui.",
                {"notifications": notifications},
            )
            return

        if path.startswith("/api/v1/cart/items/"):
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
            item_id = path.removeprefix("/api/v1/cart/items/").strip("/")
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                qty = payload.get("qty") if isinstance(payload, dict) else None
                cart = CART_STORE.update_item(session.user["id"], item_id, qty)
            except CheckoutValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except StockConflictError as error:
                self.auth_response(409, False, str(error))
                return
            except LookupError:
                self.auth_response(404, False, "Item cart tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request cart tidak valid.")
                return
            self.auth_response(200, True, "Jumlah cart diperbarui.", {"cart": cart})
            return

        if path.startswith("/api/v1/admin/members/") and path.endswith("/role"):
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
            target_id = path.removeprefix("/api/v1/admin/members/").removesuffix("/role")
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                role = payload.get("role") if isinstance(payload, dict) else ""
                user = AUTH_STORE.update_user_role(
                    session.user["id"], target_id.strip("/"), role
                )
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except AuthValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except LookupError:
                self.auth_response(404, False, "Member tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request role tidak valid.")
                return
            self.auth_response(200, True, "Role member berhasil diperbarui.", {"user": user})
            return

        if path.startswith("/api/v1/admin/consultation/") and path.endswith("/status"):
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
            ticket_id = (
                path.removeprefix("/api/v1/admin/consultation/")
                .removesuffix("/status")
                .strip("/")
            )
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                status = payload.get("status") if isinstance(payload, dict) else ""
                ticket = CONSULTATION_STORE.update_status(
                    session.user,
                    ticket_id,
                    status,
                )
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except ConsultationValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except LookupError:
                self.auth_response(404, False, "Ticket konsultasi tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request status konsultasi tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Status konsultasi berhasil diperbarui.",
                {"ticket": ticket},
            )
            return

        if path.startswith("/api/v1/admin/orders/") and path.endswith("/fulfillment"):
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
            order_id = (
                path.removeprefix("/api/v1/admin/orders/")
                .removesuffix("/fulfillment")
                .strip("/")
            )
            try:
                payload = self.read_json(MAX_AUTH_JSON_BODY)
                status = payload.get("status") if isinstance(payload, dict) else ""
                order = ADMIN_STORE.update_fulfillment(
                    session.user,
                    order_id,
                    status,
                )
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except AdminValidationError as error:
                self.auth_response(422, False, str(error), errors=error.errors)
                return
            except LookupError:
                self.auth_response(404, False, "Order tidak ditemukan.")
                return
            except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                self.auth_response(400, False, "Request fulfillment tidak valid.")
                return
            self.auth_response(
                200,
                True,
                "Status fulfillment berhasil diperbarui.",
                {"order": order},
            )
            return

        self.send_error(404)

    def do_DELETE(self):
        path = unquote(urlparse(self.path).path)
        if path.startswith("/api/owner/news/articles/"):
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            try:
                article = NEWS_STORE.archive_article(
                    path.removeprefix("/api/owner/news/articles/").strip("/")
                )
            except LookupError:
                self.send_json(404, {"ok": False, "error": "Artikel tidak ditemukan."})
                return
            self.send_json(200, {"ok": True, "article": article})
            return
        if path.startswith("/api/v1/admin/products/"):
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
                product = ADMIN_STORE.archive_product(
                    session.user,
                    path.removeprefix("/api/v1/admin/products/").strip("/"),
                )
            except PermissionError as error:
                self.auth_response(403, False, str(error))
                return
            except LookupError:
                self.auth_response(404, False, "Produk tidak ditemukan.")
                return
            self.auth_response(
                200,
                True,
                "Produk berhasil diarsipkan.",
                {"product": product},
            )
            return
        if path.startswith("/api/owner/products/"):
            if not self.require_owner():
                return
            if not self.is_same_origin_request():
                self.send_json(403, {"ok": False, "error": "Origin request tidak diizinkan."})
                return
            try:
                product = CATALOG_STORE.archive_product(
                    path.removeprefix("/api/owner/products/").strip("/")
                )
            except LookupError as error:
                self.send_json(404, {"ok": False, "error": str(error)})
                return
            self.send_json(200, {"ok": True, "product": product})
            return
        if path.startswith("/api/v1/cart/items/"):
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
            item_id = path.removeprefix("/api/v1/cart/items/").strip("/")
            try:
                cart = CART_STORE.remove_item(session.user["id"], item_id)
            except LookupError:
                self.auth_response(404, False, "Item cart tidak ditemukan.")
                return
            self.auth_response(200, True, "Item dihapus dari cart.", {"cart": cart})
            return
        self.send_error(404)

    def save_member_avatar(self, user_id: str, payload: object) -> str:
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), str):
            raise ValueError("Data avatar tidak valid.")
        try:
            metadata, encoded = payload["data"].split(",", 1)
            declared_mime = metadata.removeprefix("data:").split(";", 1)[0].lower()
            binary = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error):
            raise ValueError("File avatar rusak atau tidak valid.")
        if not binary or len(binary) > 2 * 1024 * 1024:
            raise ValueError("Ukuran avatar maksimal 2MB.")

        detected = ""
        extension = ""
        if binary.startswith(b"\x89PNG\r\n\x1a\n"):
            detected, extension = "image/png", ".png"
        elif binary.startswith(b"\xff\xd8\xff"):
            detected, extension = "image/jpeg", ".jpg"
        elif len(binary) >= 12 and binary[:4] == b"RIFF" and binary[8:12] == b"WEBP":
            detected, extension = "image/webp", ".webp"
        if not detected or detected != declared_mime:
            raise ValueError("Format avatar harus JPG, PNG, atau WebP.")

        digest = hashlib.sha256(binary).hexdigest()[:20]
        safe_user_id = "".join(character for character in user_id if character.isalnum())
        filename = f"avatar-{safe_user_id}-{digest}{extension}"
        MEMBER_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        (MEMBER_MEDIA_ROOT / filename).write_bytes(binary)
        return f"/member-media/{filename}"

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

        if kind in {"background", "product", "news"}:
            valid_signature = (
                (mime_type == "image/jpeg" and binary.startswith(b"\xff\xd8\xff"))
                or (
                    mime_type == "image/png"
                    and binary.startswith(b"\x89PNG\r\n\x1a\n")
                )
                or (
                    mime_type == "image/webp"
                    and len(binary) >= 12
                    and binary[:4] == b"RIFF"
                    and binary[8:12] == b"WEBP"
                )
                or (
                    mime_type == "image/gif"
                    and binary.startswith((b"GIF87a", b"GIF89a"))
                )
            )
            if not valid_signature:
                raise ValueError("Isi file tidak sesuai format gambar.")

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
    CATALOG_STORE.initialize()
    CART_STORE.initialize()
    PAYMENT_STORE.initialize()
    CONSULTATION_STORE.initialize()
    NEWS_STORE.initialize()
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
