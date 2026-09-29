import unittest
import json
from pathlib import Path

from dedupe import canonical_url, dedupe, match


def item(identifier, title, url, when="2026-01-08T09:00:00Z", region="demo"):
    return {"id": identifier, "title": title, "url": url, "published_at": when, "region": region}


class DedupeTests(unittest.TestCase):
    def test_canonical_url_drops_tracking_but_preserves_content_query(self):
        self.assertEqual(
            canonical_url("HTTPS://EXAMPLE.ORG/story/?id=7&utm_source=x#top"),
            "https://example.org/story?id=7",
        )

    def test_same_url_is_reported_without_deleting_record(self):
        a = item("a", "示例港口增长12%", "https://example.org/story?utm_medium=x")
        b = item("b", "示例港口增长12%", "https://example.org/story#top")
        result = dedupe([a, b])
        self.assertEqual(len(result["unique"]), 1)
        self.assertEqual(result["duplicates"][0]["duplicate_of"], "a")
        self.assertEqual(result["duplicates"][0]["item"], b)

    def test_conflicting_numbers_are_kept_even_on_same_url(self):
        a = item("a", "港口增长12%", "https://example.org/story")
        b = item("b", "港口增长15%", "https://example.org/story")
        self.assertEqual(len(dedupe([a, b])["unique"]), 2)

    def test_time_and_region_guard_approximate_matches(self):
        a = item("a", "Example City opens new library", "https://example.org/a")
        late = item("b", "Example City opens new library", "https://example.org/b", "2026-01-15T09:00:00Z")
        elsewhere = item("c", "Example City opens new library", "https://example.org/c", region="other")
        self.assertIsNone(match(a, late))
        self.assertIsNone(match(a, elsewhere))

    def test_duplicate_ids_fail(self):
        a = item("a", "First story", "https://example.org/a")
        with self.assertRaisesRegex(ValueError, "duplicate id"):
            dedupe([a, a])

    def test_fictional_bilingual_sample_runs_on_supported_python(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "news.jsonl"
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        result = dedupe(records)
        self.assertEqual(result["input_count"], 5)
        self.assertEqual(len(result["duplicates"]), 2)


if __name__ == "__main__":
    unittest.main()
