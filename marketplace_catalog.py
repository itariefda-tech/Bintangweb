from __future__ import annotations

import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path


DEFAULT_CATEGORIES = [
    {
        "name": "Workstation",
        "slug": "workstation",
        "description": "Perangkat kerja untuk produktivitas, kolaborasi, dan operasional.",
        "icon": "Laptop",
    },
    {
        "name": "Network",
        "slug": "network",
        "description": "Pondasi konektivitas kantor yang terukur dan aman.",
        "icon": "Network",
    },
    {
        "name": "Security",
        "slug": "security",
        "description": "Perangkat monitoring dan keamanan untuk area penting.",
        "icon": "Shield",
    },
    {
        "name": "Digital Solution",
        "slug": "digital-solution",
        "description": "Paket implementasi website dan aplikasi untuk proses bisnis.",
        "icon": "Code",
    },
]

DEFAULT_PRODUCTS = [
    {
        "category": "workstation",
        "name": "Business Laptop Foundation",
        "slug": "business-laptop-foundation",
        "short_description": "Perangkat kerja ringkas untuk operasional harian dan kolaborasi.",
        "description": "Paket laptop bisnis terkurasi untuk pekerjaan administrasi, meeting, kolaborasi cloud, dan mobilitas tim. Konsultasi spesifikasi dan garansi disertakan sebelum pemesanan.",
        "price": 8999000,
        "stock": 12,
        "thumbnail": "/assets/images/service-procurement.webp",
        "featured": 1,
        "badge": "Business ready",
        "images": [
            "/assets/images/service-procurement.webp",
            "/assets/images/about-tailored-solution.webp",
            "/assets/images/about-end-to-end-service.webp",
        ],
    },
    {
        "category": "network",
        "name": "Secure Office Network",
        "slug": "secure-office-network",
        "short_description": "Pondasi jaringan kantor dengan ruang tumbuh yang terukur.",
        "description": "Paket awal router, switching, access point, konfigurasi, dan dokumentasi implementasi untuk kantor kecil hingga menengah.",
        "price": 4750000,
        "stock": 7,
        "thumbnail": "/assets/images/service-network.webp",
        "featured": 1,
        "badge": "Consulted setup",
        "images": [
            "/assets/images/service-network.webp",
            "/assets/images/futuristic_netcloud.webp",
            "/assets/images/futuristic_netcloud02.webp",
        ],
    },
    {
        "category": "security",
        "name": "Smart Surveillance Kit",
        "slug": "smart-surveillance-kit",
        "short_description": "Monitoring area penting dengan akses yang lebih sederhana.",
        "description": "Paket CCTV untuk kebutuhan kantor dan usaha, mencakup estimasi kamera, storage, instalasi dasar, dan remote monitoring.",
        "price": 6250000,
        "stock": 0,
        "thumbnail": "/assets/images/service-cctv.webp",
        "featured": 1,
        "badge": "Security pick",
        "images": [
            "/assets/images/service-cctv.webp",
            "/assets/images/about-modern-system.webp",
        ],
    },
    {
        "category": "digital-solution",
        "name": "Company Website Launch",
        "slug": "company-website-launch",
        "short_description": "Website company profile modern yang siap membangun kepercayaan.",
        "description": "Paket discovery, desain responsif, pengembangan, optimasi dasar, dan pendampingan peluncuran website perusahaan.",
        "price": 7500000,
        "stock": 4,
        "thumbnail": "/assets/images/service-website.webp",
        "featured": 0,
        "badge": "Digital growth",
        "images": [
            "/assets/images/service-website.webp",
            "/assets/images/brand-hero01.webp",
            "/assets/images/brand-hero02.webp",
        ],
    },
    {
        "category": "digital-solution",
        "name": "Custom App Discovery",
        "slug": "custom-app-discovery",
        "short_description": "Workshop teknis untuk memetakan aplikasi yang benar-benar dibutuhkan.",
        "description": "Sesi discovery terstruktur untuk proses bisnis, user flow, integrasi, scope, risiko, dan estimasi pengembangan aplikasi custom.",
        "price": 2500000,
        "stock": 9,
        "thumbnail": "/assets/images/service-application.webp",
        "featured": 0,
        "badge": "Discovery first",
        "images": [
            "/assets/images/service-application.webp",
            "/assets/images/about-operational-problems.webp",
        ],
    },
]


class CatalogStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path

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
            if 4 not in applied:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS product_categories (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        slug TEXT NOT NULL UNIQUE,
                        icon TEXT NOT NULL DEFAULT '',
                        description TEXT NOT NULL DEFAULT '',
                        status TEXT NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'inactive'))
                    );

                    CREATE TABLE IF NOT EXISTS products (
                        id TEXT PRIMARY KEY,
                        category_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        slug TEXT NOT NULL UNIQUE,
                        short_description TEXT NOT NULL,
                        description TEXT NOT NULL,
                        price INTEGER NOT NULL CHECK (price >= 0),
                        stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
                        thumbnail TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'inactive', 'out_of_stock', 'archived')),
                        featured INTEGER NOT NULL DEFAULT 0 CHECK (featured IN (0, 1)),
                        badge TEXT NOT NULL DEFAULT '',
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL,
                        FOREIGN KEY (category_id) REFERENCES product_categories(id)
                    );

                    CREATE TABLE IF NOT EXISTS product_images (
                        id TEXT PRIMARY KEY,
                        product_id TEXT NOT NULL,
                        image_path TEXT NOT NULL,
                        sort_order INTEGER NOT NULL DEFAULT 0,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_products_public
                        ON products(status, featured, category_id);
                    CREATE INDEX IF NOT EXISTS idx_product_images_product
                        ON product_images(product_id, sort_order);
                    """
                )
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (4, ?)",
                    (int(time.time()),),
                )
            self._seed(connection)

    def _seed(self, connection: sqlite3.Connection) -> None:
        now = int(time.time())
        category_ids = {}
        for category in DEFAULT_CATEGORIES:
            existing = connection.execute(
                "SELECT id FROM product_categories WHERE slug = ?",
                (category["slug"],),
            ).fetchone()
            category_id = existing["id"] if existing else str(uuid.uuid4())
            category_ids[category["slug"]] = category_id
            connection.execute(
                """
                INSERT INTO product_categories (id, name, slug, icon, description, status)
                VALUES (?, ?, ?, ?, ?, 'active')
                ON CONFLICT(slug) DO NOTHING
                """,
                (
                    category_id,
                    category["name"],
                    category["slug"],
                    category["icon"],
                    category["description"],
                ),
            )

        for product in DEFAULT_PRODUCTS:
            existing = connection.execute(
                "SELECT id FROM products WHERE slug = ?",
                (product["slug"],),
            ).fetchone()
            if existing:
                continue
            product_id = str(uuid.uuid4())
            status = "out_of_stock" if product["stock"] == 0 else "active"
            connection.execute(
                """
                INSERT INTO products (
                    id, category_id, name, slug, short_description, description,
                    price, stock, thumbnail, status, featured, badge, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    category_ids[product["category"]],
                    product["name"],
                    product["slug"],
                    product["short_description"],
                    product["description"],
                    product["price"],
                    product["stock"],
                    product["thumbnail"],
                    status,
                    product["featured"],
                    product["badge"],
                    now,
                    now,
                ),
            )
            for index, image in enumerate(product["images"]):
                connection.execute(
                    """
                    INSERT INTO product_images (id, product_id, image_path, sort_order)
                    VALUES (?, ?, ?, ?)
                    """,
                    (str(uuid.uuid4()), product_id, image, index),
                )

    @staticmethod
    def _public_product(row: sqlite3.Row) -> dict:
        stock = row["stock"]
        return {
            "slug": row["slug"],
            "name": row["name"],
            "shortDescription": row["short_description"],
            "description": row["description"],
            "price": row["price"],
            "stock": stock,
            "stockStatus": (
                "out_of_stock"
                if stock <= 0 or row["status"] == "out_of_stock"
                else "low_stock" if stock <= 5 else "in_stock"
            ),
            "image": row["thumbnail"],
            "featured": bool(row["featured"]),
            "badge": row["badge"],
            "category": {
                "name": row["category_name"],
                "slug": row["category_slug"],
            },
        }

    def list_categories(self) -> list[dict]:
        with self.connection() as connection:
            rows = connection.execute(
                """
                SELECT c.name, c.slug, c.icon, c.description, COUNT(p.id) AS product_count
                FROM product_categories c
                LEFT JOIN products p
                    ON p.category_id = c.id
                    AND p.status IN ('active', 'out_of_stock')
                WHERE c.status = 'active'
                GROUP BY c.id
                ORDER BY c.name
                """
            ).fetchall()
        return [
            {
                "name": row["name"],
                "slug": row["slug"],
                "icon": row["icon"],
                "description": row["description"],
                "productCount": row["product_count"],
            }
            for row in rows
        ]

    def list_products(
        self,
        search: str = "",
        category: str = "",
        featured: bool = False,
        sort: str = "featured",
    ) -> list[dict]:
        conditions = ["p.status IN ('active', 'out_of_stock')", "c.status = 'active'"]
        parameters: list[object] = []
        clean_search = " ".join(str(search or "").strip().split())[:120]
        clean_category = str(category or "").strip().lower()[:120]
        if clean_search:
            conditions.append(
                "(p.name LIKE ? OR p.short_description LIKE ? OR p.description LIKE ?)"
            )
            pattern = f"%{clean_search}%"
            parameters.extend([pattern, pattern, pattern])
        if clean_category:
            conditions.append("c.slug = ?")
            parameters.append(clean_category)
        if featured:
            conditions.append("p.featured = 1")

        ordering = {
            "price_asc": "p.price ASC, p.name ASC",
            "price_desc": "p.price DESC, p.name ASC",
            "name": "p.name ASC",
            "newest": "p.created_at DESC, p.name ASC",
            "featured": "p.featured DESC, p.created_at DESC, p.name ASC",
        }.get(sort, "p.featured DESC, p.created_at DESC, p.name ASC")
        query = f"""
            SELECT p.*, c.name AS category_name, c.slug AS category_slug
            FROM products p
            JOIN product_categories c ON c.id = p.category_id
            WHERE {' AND '.join(conditions)}
            ORDER BY {ordering}
        """
        with self.connection() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._public_product(row) for row in rows]

    def get_product(self, slug: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT p.*, c.name AS category_name, c.slug AS category_slug
                FROM products p
                JOIN product_categories c ON c.id = p.category_id
                WHERE p.slug = ?
                    AND p.status IN ('active', 'out_of_stock')
                    AND c.status = 'active'
                """,
                (str(slug or "").strip().lower()[:160],),
            ).fetchone()
            if not row:
                return None
            images = [
                image["image_path"]
                for image in connection.execute(
                    """
                    SELECT image_path
                    FROM product_images
                    WHERE product_id = ?
                    ORDER BY sort_order, id
                    """,
                    (row["id"],),
                ).fetchall()
            ]
            related_rows = connection.execute(
                """
                SELECT p.*, c.name AS category_name, c.slug AS category_slug
                FROM products p
                JOIN product_categories c ON c.id = p.category_id
                WHERE p.category_id = ?
                    AND p.id != ?
                    AND p.status IN ('active', 'out_of_stock')
                ORDER BY p.featured DESC, p.created_at DESC
                LIMIT 3
                """,
                (row["category_id"], row["id"]),
            ).fetchall()
        product = self._public_product(row)
        product["images"] = images or [product["image"]]
        product["related"] = [self._public_product(item) for item in related_rows]
        return product
