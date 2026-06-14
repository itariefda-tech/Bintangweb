import tempfile
import unittest
from pathlib import Path

from marketplace_catalog import CatalogStore


class CatalogStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "marketplace.sqlite3"
        self.store = CatalogStore(self.database)
        self.store.initialize()

    def tearDown(self):
        self.temporary.cleanup()

    def test_seed_is_idempotent_and_categories_have_counts(self):
        first_products = self.store.list_products()
        self.store.initialize()
        second_products = self.store.list_products()
        categories = self.store.list_categories()

        self.assertEqual(5, len(first_products))
        self.assertEqual(5, len(second_products))
        self.assertEqual(4, len(categories))
        self.assertEqual(
            5,
            sum(category["productCount"] for category in categories),
        )

    def test_listing_supports_search_category_featured_and_sort(self):
        searched = self.store.list_products(search="network")
        category = self.store.list_products(category="digital-solution")
        featured = self.store.list_products(featured=True)
        sorted_products = self.store.list_products(sort="price_asc")

        self.assertEqual(["secure-office-network"], [item["slug"] for item in searched])
        self.assertEqual(2, len(category))
        self.assertTrue(all(item["featured"] for item in featured))
        self.assertEqual(
            sorted(item["price"] for item in sorted_products),
            [item["price"] for item in sorted_products],
        )

    def test_product_detail_contains_gallery_stock_and_related_products(self):
        product = self.store.get_product("company-website-launch")

        self.assertEqual("Digital Solution", product["category"]["name"])
        self.assertGreaterEqual(len(product["images"]), 2)
        self.assertEqual("low_stock", product["stockStatus"])
        self.assertEqual(
            ["custom-app-discovery"],
            [item["slug"] for item in product["related"]],
        )

        out_of_stock = self.store.get_product("smart-surveillance-kit")
        self.assertEqual("out_of_stock", out_of_stock["stockStatus"])

    def test_inactive_and_archived_products_are_not_public(self):
        product = self.store.get_product("business-laptop-foundation")
        self.assertIsNotNone(product)
        with self.store.connection() as connection:
            connection.execute(
                "UPDATE products SET status = 'archived' WHERE slug = ?",
                ("business-laptop-foundation",),
            )

        self.assertIsNone(self.store.get_product("business-laptop-foundation"))
        self.assertNotIn(
            "business-laptop-foundation",
            [item["slug"] for item in self.store.list_products()],
        )


if __name__ == "__main__":
    unittest.main()
