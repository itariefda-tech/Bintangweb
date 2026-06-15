from __future__ import annotations

import re
import sqlite3
import time
import uuid
from pathlib import Path


DEFAULT_NEWS_CATEGORIES = [
    {
        "name": "Infrastructure",
        "slug": "infrastructure",
        "description": "Jaringan, server, backup, dan fondasi operasional IT.",
    },
    {
        "name": "Security",
        "slug": "security",
        "description": "Monitoring, akses, dan kebiasaan keamanan digital.",
    },
    {
        "name": "Digital Workflow",
        "slug": "digital-workflow",
        "description": "Aplikasi, website, otomasi, dan sistem kerja modern.",
    },
]

DEFAULT_ARTICLES = [
    {
        "category": "infrastructure",
        "title": "Tanda jaringan kantor mulai butuh ditata ulang",
        "slug": "tanda-jaringan-kantor-mulai-butuh-ditata-ulang",
        "excerpt": "Koneksi lambat bukan selalu masalah provider. Topologi, perangkat, dan dokumentasi sering menjadi akar masalah operasional.",
        "body": "Jaringan kantor yang tumbuh tanpa dokumentasi biasanya mulai terasa lambat saat jumlah perangkat meningkat. Audit sederhana pada router, switch, access point, IP plan, dan kabel dapat membantu menemukan titik lemah sebelum operasional terganggu.",
        "image": "/assets/images/service-network.webp",
        "featured": 1,
        "trending_score": 92,
        "reading_time": "4 min read",
    },
    {
        "category": "security",
        "title": "Checklist CCTV sebelum bisnis membuka cabang baru",
        "slug": "checklist-cctv-sebelum-bisnis-membuka-cabang-baru",
        "excerpt": "Penempatan kamera, storage, akses remote, dan policy pengguna perlu diputuskan sebelum instalasi dimulai.",
        "body": "CCTV yang baik tidak hanya soal jumlah kamera. Tentukan area prioritas, sudut pandang, lama penyimpanan rekaman, akses user, dan prosedur backup agar monitoring tetap berguna setelah sistem berjalan.",
        "image": "/assets/images/service-cctv.webp",
        "featured": 1,
        "trending_score": 87,
        "reading_time": "3 min read",
    },
    {
        "category": "digital-workflow",
        "title": "Kapan bisnis perlu aplikasi custom, bukan spreadsheet lagi",
        "slug": "kapan-bisnis-perlu-aplikasi-custom-bukan-spreadsheet-lagi",
        "excerpt": "Spreadsheet tetap berguna, tetapi workflow yang melibatkan banyak role dan approval butuh sistem yang lebih terstruktur.",
        "body": "Aplikasi custom mulai relevan saat data sering duplikat, approval sulit dilacak, report dikerjakan manual, dan akses antar role perlu dibatasi. Mulailah dari discovery kecil agar sistem dibuat sesuai proses bisnis nyata.",
        "image": "/assets/images/service-application.webp",
        "featured": 0,
        "trending_score": 76,
        "reading_time": "5 min read",
    },
    {
        "category": "digital-workflow",
        "title": "Website company profile yang membantu sales bekerja",
        "slug": "website-company-profile-yang-membantu-sales-bekerja",
        "excerpt": "Website modern harus menjelaskan layanan, membangun trust, dan memberi jalur konsultasi yang jelas.",
        "body": "Company profile yang efektif bukan hanya tampil rapi. Struktur informasi, bukti kerja, CTA, halaman layanan, dan performa mobile menentukan apakah calon customer mudah mengambil keputusan berikutnya.",
        "image": "/assets/images/service-website.webp",
        "featured": 0,
        "trending_score": 68,
        "reading_time": "4 min read",
    },
]


class NewsValidationError(ValueError):
    def __init__(self, message: str, errors: dict[str, str] | None = None):
        super().__init__(message)
        self.errors = errors or {}


class NewsStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path

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
            if 8 not in applied:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS news_categories (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        slug TEXT NOT NULL UNIQUE,
                        description TEXT NOT NULL DEFAULT '',
                        status TEXT NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'inactive'))
                    );

                    CREATE TABLE IF NOT EXISTS news_articles (
                        id TEXT PRIMARY KEY,
                        category_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        slug TEXT NOT NULL UNIQUE,
                        excerpt TEXT NOT NULL,
                        body TEXT NOT NULL,
                        image TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'published'
                            CHECK (status IN ('draft', 'published', 'archived')),
                        featured INTEGER NOT NULL DEFAULT 0 CHECK (featured IN (0, 1)),
                        trending_score INTEGER NOT NULL DEFAULT 0 CHECK (trending_score >= 0),
                        reading_time TEXT NOT NULL DEFAULT '3 min read',
                        published_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        FOREIGN KEY (category_id) REFERENCES news_categories(id)
                    );

                    CREATE INDEX IF NOT EXISTS idx_news_public
                        ON news_articles(status, featured, trending_score, published_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_news_category
                        ON news_articles(category_id, status, published_at DESC);
                    """
                )
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (8, ?)",
                    (int(time.time()),),
                )
            self._seed(connection)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _seed(self, connection: sqlite3.Connection) -> None:
        now = int(time.time())
        category_ids = {}
        for category in DEFAULT_NEWS_CATEGORIES:
            row = connection.execute(
                "SELECT id FROM news_categories WHERE slug = ?",
                (category["slug"],),
            ).fetchone()
            category_id = row["id"] if row else str(uuid.uuid4())
            category_ids[category["slug"]] = category_id
            connection.execute(
                """
                INSERT INTO news_categories (id, name, slug, description, status)
                VALUES (?, ?, ?, ?, 'active')
                ON CONFLICT(slug) DO NOTHING
                """,
                (category_id, category["name"], category["slug"], category["description"]),
            )
        for offset, article in enumerate(DEFAULT_ARTICLES):
            exists = connection.execute(
                "SELECT id FROM news_articles WHERE slug = ?",
                (article["slug"],),
            ).fetchone()
            if exists:
                continue
            published_at = now - (offset * 86400)
            connection.execute(
                """
                INSERT INTO news_articles (
                    id, category_id, title, slug, excerpt, body, image, status,
                    featured, trending_score, reading_time, published_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'published', ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    category_ids[article["category"]],
                    article["title"],
                    article["slug"],
                    article["excerpt"],
                    article["body"],
                    article["image"],
                    article["featured"],
                    article["trending_score"],
                    article["reading_time"],
                    published_at,
                    published_at,
                ),
            )

    @staticmethod
    def _public_article(row: sqlite3.Row) -> dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "slug": row["slug"],
            "excerpt": row["excerpt"],
            "body": row["body"],
            "image": row["image"],
            "featured": bool(row["featured"]),
            "trendingScore": row["trending_score"],
            "readingTime": row["reading_time"],
            "publishedAt": row["published_at"],
            "category": {
                "name": row["category_name"],
                "slug": row["category_slug"],
            },
        }

    @staticmethod
    def _admin_article(row: sqlite3.Row) -> dict:
        article = NewsStore._public_article(row)
        article["status"] = row["status"]
        article["updatedAt"] = row["updated_at"]
        return article

    @staticmethod
    def _clean(value: object, limit: int = 120) -> str:
        return " ".join(str(value or "").strip().split())[:limit]

    def list_categories(self) -> list[dict]:
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT c.name, c.slug, c.description, COUNT(a.id) AS article_count
                FROM news_categories c
                LEFT JOIN news_articles a
                    ON a.category_id = c.id
                    AND a.status = 'published'
                WHERE c.status = 'active'
                GROUP BY c.id
                ORDER BY c.name
                """
            ).fetchall()
            return [
                {
                    "name": row["name"],
                    "slug": row["slug"],
                    "description": row["description"],
                    "articleCount": row["article_count"],
                }
                for row in rows
            ]
        finally:
            connection.close()

    def list_admin_categories(self) -> list[dict]:
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT c.id, c.name, c.slug, c.description, c.status,
                       COUNT(a.id) AS article_count
                FROM news_categories c
                LEFT JOIN news_articles a ON a.category_id = c.id
                GROUP BY c.id
                ORDER BY c.name
                """
            ).fetchall()
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "slug": row["slug"],
                    "description": row["description"],
                    "status": row["status"],
                    "articleCount": row["article_count"],
                }
                for row in rows
            ]
        finally:
            connection.close()

    def list_admin_articles(self) -> list[dict]:
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT a.*, c.name AS category_name, c.slug AS category_slug
                FROM news_articles a
                JOIN news_categories c ON c.id = a.category_id
                ORDER BY a.updated_at DESC, a.title
                """
            ).fetchall()
            return [self._admin_article(row) for row in rows]
        finally:
            connection.close()

    def save_category(
        self,
        payload: object,
        category_id: str | None = None,
    ) -> dict:
        if not isinstance(payload, dict):
            raise NewsValidationError("Data kategori news tidak valid.")
        name = self._clean(payload.get("name"), 120)
        slug = self._clean(payload.get("slug"), 120).lower() or self.slugify(name)
        description = str(payload.get("description") or "").strip()[:500]
        status = self._clean(payload.get("status"), 20) or "active"
        errors = {}
        if not 2 <= len(name) <= 120:
            errors["name"] = "Nama kategori harus 2-120 karakter."
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            errors["slug"] = "Slug kategori tidak valid."
        if status not in {"active", "inactive"}:
            errors["status"] = "Status kategori tidak valid."
        if errors:
            raise NewsValidationError("Kategori news belum valid.", errors)
        clean_id = self._clean(category_id, 80)
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            duplicate = connection.execute(
                "SELECT id FROM news_categories WHERE slug = ? AND id != ?",
                (slug, clean_id),
            ).fetchone()
            if duplicate:
                raise NewsValidationError(
                    "Slug kategori sudah digunakan.",
                    {"slug": "Slug kategori sudah digunakan."},
                )
            if clean_id:
                updated = connection.execute(
                    """
                    UPDATE news_categories
                    SET name = ?, slug = ?, description = ?, status = ?
                    WHERE id = ?
                    """,
                    (name, slug, description, status, clean_id),
                )
                if updated.rowcount != 1:
                    raise LookupError("Kategori news tidak ditemukan.")
                saved_id = clean_id
            else:
                saved_id = str(uuid.uuid4())
                connection.execute(
                    """
                    INSERT INTO news_categories (id, name, slug, description, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (saved_id, name, slug, description, status),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return next(
            item for item in self.list_admin_categories() if item["id"] == saved_id
        )

    def save_article(
        self,
        payload: object,
        article_id: str | None = None,
    ) -> dict:
        if not isinstance(payload, dict):
            raise NewsValidationError("Data artikel tidak valid.")
        title = self._clean(payload.get("title"), 180)
        slug = self._clean(payload.get("slug"), 180).lower() or self.slugify(title)
        category = self._clean(payload.get("category"), 120).lower()
        excerpt = str(payload.get("excerpt") or "").strip()
        body = str(payload.get("body") or "").strip()
        image = self._clean(payload.get("image"), 500)
        status = self._clean(payload.get("status"), 20) or "draft"
        reading_time = self._clean(payload.get("readingTime"), 40) or "3 min read"
        errors = {}
        if not 5 <= len(title) <= 180:
            errors["title"] = "Judul harus 5-180 karakter."
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            errors["slug"] = "Slug artikel tidak valid."
        if not category:
            errors["category"] = "Kategori wajib dipilih."
        if not 20 <= len(excerpt) <= 500:
            errors["excerpt"] = "Excerpt harus 20-500 karakter."
        if not 40 <= len(body) <= 20000:
            errors["body"] = "Isi artikel harus 40-20000 karakter."
        if not image:
            errors["image"] = "Cover artikel wajib diisi."
        if status not in {"draft", "published", "archived"}:
            errors["status"] = "Status artikel tidak valid."
        try:
            trending_score = int(payload.get("trendingScore") or 0)
            if not 0 <= trending_score <= 100000:
                raise ValueError
        except (TypeError, ValueError):
            trending_score = 0
            errors["trendingScore"] = "Trending score harus 0-100000."
        if errors:
            raise NewsValidationError("Artikel belum valid.", errors)

        clean_id = self._clean(article_id, 80)
        now = int(time.time())
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            category_row = connection.execute(
                "SELECT id FROM news_categories WHERE slug = ?",
                (category,),
            ).fetchone()
            if not category_row:
                raise NewsValidationError(
                    "Kategori news tidak ditemukan.",
                    {"category": "Kategori news tidak ditemukan."},
                )
            duplicate = connection.execute(
                "SELECT id FROM news_articles WHERE slug = ? AND id != ?",
                (slug, clean_id),
            ).fetchone()
            if duplicate:
                raise NewsValidationError(
                    "Slug artikel sudah digunakan.",
                    {"slug": "Slug artikel sudah digunakan."},
                )
            if clean_id:
                existing = connection.execute(
                    "SELECT published_at FROM news_articles WHERE id = ?",
                    (clean_id,),
                ).fetchone()
                if not existing:
                    raise LookupError("Artikel tidak ditemukan.")
                connection.execute(
                    """
                    UPDATE news_articles
                    SET category_id = ?, title = ?, slug = ?, excerpt = ?, body = ?,
                        image = ?, status = ?, featured = ?, trending_score = ?,
                        reading_time = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        category_row["id"],
                        title,
                        slug,
                        excerpt,
                        body,
                        image,
                        status,
                        1 if bool(payload.get("featured")) else 0,
                        trending_score,
                        reading_time,
                        now,
                        clean_id,
                    ),
                )
                saved_id = clean_id
            else:
                saved_id = str(uuid.uuid4())
                connection.execute(
                    """
                    INSERT INTO news_articles (
                        id, category_id, title, slug, excerpt, body, image, status,
                        featured, trending_score, reading_time, published_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        saved_id,
                        category_row["id"],
                        title,
                        slug,
                        excerpt,
                        body,
                        image,
                        status,
                        1 if bool(payload.get("featured")) else 0,
                        trending_score,
                        reading_time,
                        now,
                        now,
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return next(
            item for item in self.list_admin_articles() if item["id"] == saved_id
        )

    def archive_article(self, article_id: object) -> dict:
        clean_id = self._clean(article_id, 80)
        connection = self.connect()
        try:
            updated = connection.execute(
                """
                UPDATE news_articles
                SET status = 'archived', featured = 0, updated_at = ?
                WHERE id = ?
                """,
                (int(time.time()), clean_id),
            )
            if updated.rowcount != 1:
                raise LookupError("Artikel tidak ditemukan.")
            connection.commit()
        finally:
            connection.close()
        return next(
            item for item in self.list_admin_articles() if item["id"] == clean_id
        )

    def list_articles(
        self,
        search: object = "",
        category: object = "",
        featured: bool = False,
        trending: bool = False,
    ) -> list[dict]:
        conditions = ["a.status = 'published'", "c.status = 'active'"]
        params: list[object] = []
        clean_search = self._clean(search)
        clean_category = self._clean(category)
        if clean_search:
            conditions.append("(a.title LIKE ? OR a.excerpt LIKE ? OR a.body LIKE ?)")
            pattern = f"%{clean_search}%"
            params.extend([pattern, pattern, pattern])
        if clean_category:
            conditions.append("c.slug = ?")
            params.append(clean_category)
        if featured:
            conditions.append("a.featured = 1")
        ordering = (
            "a.trending_score DESC, a.published_at DESC"
            if trending
            else "a.featured DESC, a.published_at DESC"
        )
        connection = self.connect()
        try:
            rows = connection.execute(
                f"""
                SELECT a.*, c.name AS category_name, c.slug AS category_slug
                FROM news_articles a
                JOIN news_categories c ON c.id = a.category_id
                WHERE {' AND '.join(conditions)}
                ORDER BY {ordering}
                """,
                params,
            ).fetchall()
            return [self._public_article(row) for row in rows]
        finally:
            connection.close()

    def get_article(self, slug: object) -> dict | None:
        clean_slug = self._clean(slug, 160).lower()
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT a.*, c.name AS category_name, c.slug AS category_slug
                FROM news_articles a
                JOIN news_categories c ON c.id = a.category_id
                WHERE a.slug = ?
                    AND a.status = 'published'
                    AND c.status = 'active'
                """,
                (clean_slug,),
            ).fetchone()
            if not row:
                return None
            related_rows = connection.execute(
                """
                SELECT a.*, c.name AS category_name, c.slug AS category_slug
                FROM news_articles a
                JOIN news_categories c ON c.id = a.category_id
                WHERE a.category_id = ?
                    AND a.id != ?
                    AND a.status = 'published'
                ORDER BY a.featured DESC, a.published_at DESC
                LIMIT 3
                """,
                (row["category_id"], row["id"]),
            ).fetchall()
            article = self._public_article(row)
            article["related"] = [self._public_article(item) for item in related_rows]
            return article
        finally:
            connection.close()

    @staticmethod
    def slugify(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
