"""Verify the generated site is a public summary, not an export of private input hints."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.build_pages import build_site
from scripts.verify_pages import verify


class PagesTests(unittest.TestCase):
    def test_public_artifact_is_consistent_and_excludes_routing_hints(self):
        with TemporaryDirectory() as d:
            out = Path(d)
            manifest = build_site(out, revision="test-sha")
            html = (out / "index.html").read_text(encoding="utf-8")
            raw = (out / "manifest.json").read_text(encoding="utf-8")
            self.assertEqual(len(manifest["domains"]), verify(html, raw, "test-sha"))
            self.assertEqual(len(manifest["domains"]), manifest["domain_count"])
            self.assertEqual(
                {"id", "tier", "version", "operations", "requires_review"},
                set(manifest["domains"][0]),
            )
            self.assertNotIn('"guardrails"', raw)
            self.assertNotIn('"sources"', raw)
            self.assertNotIn('"routes"', raw)

    def test_stale_revision_fails(self):
        with TemporaryDirectory() as d:
            out = Path(d)
            build_site(out, revision="old-sha")
            with self.assertRaisesRegex(ValueError, "revision"):
                verify((out / "index.html").read_text(encoding="utf-8"),
                       (out / "manifest.json").read_text(encoding="utf-8"), "new-sha")


if __name__ == "__main__":
    unittest.main()
