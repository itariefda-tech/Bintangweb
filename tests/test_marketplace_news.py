import tempfile
import unittest
from pathlib import Path

from marketplace_news import NewsStore, NewsValidationError


class NewsStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "marketplace.sqlite3"
        self.store = NewsStore(self.database)
        self.store.initialize()

    def tearDown(self):
        self.temporary.cleanup()

    def test_seed_is_idempotent_and_categories_have_counts(self):
        first = self.store.list_articles()
        self.store.initialize()
        second = self.store.list_articles()
        categories = self.store.list_categories()

        self.assertEqual(4, len(first))
        self.assertEqual(4, len(second))
        self.assertEqual(3, len(categories))
        self.assertEqual(4, sum(category["articleCount"] for category in categories))

    def test_articles_support_search_category_featured_and_trending(self):
        searched = self.store.list_articles(search="CCTV")
        category = self.store.list_articles(category="digital-workflow")
        featured = self.store.list_articles(featured=True)
        trending = self.store.list_articles(trending=True)

        self.assertEqual(
            ["checklist-cctv-sebelum-bisnis-membuka-cabang-baru"],
            [item["slug"] for item in searched],
        )
        self.assertEqual(2, len(category))
        self.assertTrue(all(item["featured"] for item in featured))
        self.assertGreaterEqual(trending[0]["trendingScore"], trending[-1]["trendingScore"])

    def test_article_detail_contains_related_articles(self):
        article = self.store.get_article("kapan-bisnis-perlu-aplikasi-custom-bukan-spreadsheet-lagi")

        self.assertEqual("Digital Workflow", article["category"]["name"])
        self.assertEqual(
            ["website-company-profile-yang-membantu-sales-bekerja"],
            [item["slug"] for item in article["related"]],
        )

    def test_archived_article_is_not_public(self):
        connection = self.store.connect()
        try:
            connection.execute(
                "UPDATE news_articles SET status = 'archived' WHERE slug = ?",
                ("tanda-jaringan-kantor-mulai-butuh-ditata-ulang",),
            )
            connection.commit()
        finally:
            connection.close()

        self.assertIsNone(
            self.store.get_article("tanda-jaringan-kantor-mulai-butuh-ditata-ulang")
        )

    def test_owner_can_manage_categories_and_articles(self):
        category = self.store.save_category(
            {
                "name": "Cloud Operations",
                "slug": "cloud-operations",
                "description": "Cloud, observability, dan operasi layanan.",
                "status": "active",
            }
        )
        article = self.store.save_article(
            {
                "title": "Checklist operasional cloud untuk tim kecil",
                "slug": "checklist-operasional-cloud-untuk-tim-kecil",
                "category": category["slug"],
                "excerpt": "Checklist praktis agar layanan cloud tetap terpantau dan biaya lebih terkendali.",
                "body": "Mulailah dari ownership layanan, alert yang benar-benar actionable, backup teruji, pengelolaan akses, dan review biaya secara berkala.",
                "image": "/assets/images/futuristic_netcloud.webp",
                "status": "published",
                "featured": True,
                "trendingScore": 95,
                "readingTime": "6 min read",
            }
        )
        self.assertEqual("published", article["status"])
        self.assertIsNotNone(self.store.get_article(article["slug"]))

        updated = self.store.save_article(
            {
                **article,
                "category": category["slug"],
                "image": article["image"],
                "readingTime": article["readingTime"],
                "trendingScore": 99,
            },
            article["id"],
        )
        self.assertEqual(99, updated["trendingScore"])

        archived = self.store.archive_article(article["id"])
        self.assertEqual("archived", archived["status"])
        self.assertIsNone(self.store.get_article(article["slug"]))

    def test_owner_news_validation_rejects_duplicate_slug(self):
        with self.assertRaises(NewsValidationError) as context:
            self.store.save_article(
                {
                    "title": "Artikel duplikat infrastructure",
                    "slug": "tanda-jaringan-kantor-mulai-butuh-ditata-ulang",
                    "category": "infrastructure",
                    "excerpt": "Excerpt artikel duplikat yang cukup panjang untuk melewati validasi.",
                    "body": "Isi artikel duplikat yang cukup panjang untuk memastikan validasi slug menjadi sumber kegagalan utama.",
                    "image": "/assets/images/service-network.webp",
                    "status": "draft",
                }
            )
        self.assertIn("slug", context.exception.errors)


if __name__ == "__main__":
    unittest.main()
