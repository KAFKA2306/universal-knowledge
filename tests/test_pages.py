"""Source-desk publication contract: correct content, provenance and safe output."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.build_pages import build_site, published_records
from scripts.verify_pages import verify, verify_assets


class PagesTests(unittest.TestCase):
    def make_site(self, revision="test-sha"):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        out = Path(temp.name)
        manifest = build_site(out, revision=revision)
        html = (out / "index.html").read_text(encoding="utf-8")
        raw = (out / "manifest.json").read_text(encoding="utf-8")
        assets = {name: (out / "assets" / name).read_bytes()
                  for name in ("site.css", "site.js")}
        return manifest, html, raw, assets

    def test_every_public_record_is_rendered_and_matches_canonical_registry(self):
        manifest, html, raw, assets = self.make_site()
        expected = json.loads((Path(__file__).resolve().parents[1] /
                               "config/source_registry.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["records"], published_records(expected))
        self.assertEqual(len(manifest["domains"]), verify(html, raw, "test-sha"))
        self.assertEqual(manifest["source_count"], len(expected["sources"]))
        self.assertEqual(manifest["candidate_count"], len(expected["candidates"]))
        self.assertEqual(manifest["feed_count"], len(expected["feeds"]))
        self.assertEqual(manifest["schema_version"], 2)
        self.assertIn('data-theme="paper"', html)
        self.assertIn('id="search"', html)
        self.assertIn('id="stage"', html)
        self.assertIn('id="order"', html)
        verify_assets(raw, assets)

    def test_no_private_hints_or_raw_documents_in_public_artifact(self):
        manifest, html, raw, assets = self.make_site()
        for forbidden in ['"guardrails"', '"routes"', '"public_repos"',
                          '"source_document"', '"full_text"', '"summary"']:
            self.assertNotIn(forbidden, raw)
        self.assertNotIn("github_pat_", html)
        self.assertEqual({"id", "tier", "version", "operations", "requires_review"},
                         set(manifest["domains"][0]))
        self.assertEqual({"id", "domain", "title", "url", "record_type",
                          "published", "stage"}, set(manifest["records"][0]))

    def test_stale_revision_fails(self):
        manifest, html, raw, assets = self.make_site("old-sha")
        with self.assertRaisesRegex(ValueError, "revision"):
            verify(html, raw, "new-sha")

    def test_mismatched_record_is_rejected(self):
        manifest, html, raw, assets = self.make_site()
        damaged = json.loads(raw)
        damaged["records"][0]["title"] = "invented evidence"
        with self.assertRaisesRegex(ValueError, "source records"):
            verify(html, json.dumps(damaged), "test-sha")

    def test_css_or_javascript_tampering_is_rejected(self):
        manifest, html, raw, assets = self.make_site()
        assets["site.js"] += b"// modified after deployment"
        with self.assertRaisesRegex(ValueError, "site.js"):
            verify_assets(raw, assets)


if __name__ == "__main__":
    unittest.main()
