#!/usr/bin/env python3
"""Verify exact source inventory, public-only payload and deployment assets."""
from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_pages import published_records


def verify(html: str, raw_manifest: str, revision: str) -> int:
    manifest = json.loads(raw_manifest)
    if manifest.get("revision") != revision:
        raise ValueError("Published revision does not match the workflow SHA")
    if manifest.get("site_kind") != "source_desk" or manifest.get("schema_version") != 2:
        raise ValueError("Expected the new source desk, not the former settings page")
    if manifest.get("validation") != "configuration_passed":
        raise ValueError("Missing configuration validation result")
    registry = json.loads((ROOT / "config/domain_registry.json").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))
    domains = manifest.get("domains")
    expected_ids = [x["id"] for x in registry["domains"]]
    if not isinstance(domains, list) or manifest.get("domain_count") != len(expected_ids):
        raise ValueError("Invalid domain inventory")
    if [x.get("id") for x in domains] != expected_ids:
        raise ValueError("Domain inventory differs from the canonical registry")
    for name, key in [("source_count", "sources"), ("candidate_count", "candidates"), ("feed_count", "feeds")]:
        if manifest.get(name) != len(catalog[key]):
            raise ValueError(f"{name} differs from the canonical registry")
    records = manifest.get("records")
    if not isinstance(records, list) or records != published_records(catalog):
        raise ValueError("Published source records differ from the canonical registry")
    if set(manifest) != {
        "schema_version", "site_kind", "project", "revision", "validation",
        "domain_count", "source_count", "candidate_count", "feed_count",
        "domains", "records", "assets"
    }:
        raise ValueError("Unexpected data in public manifest")
    if 'lang="ja"' not in html or 'data-theme="paper"' not in html:
        raise ValueError("Missing language or non-navy canonical paper theme")
    if "id=\"search\"" not in html or "id=\"records\"" not in html:
        raise ValueError("Searchable source desk was not rendered")
    if f'data-revision="{escape(revision, quote=True)}"' not in html:
        raise ValueError("HTML revision does not match workflow SHA")
    for x in records:
        if escape(x["url"], quote=True) not in html or escape(x["title"]) not in html:
            raise ValueError(f"Missing published source record: {x['id']}")
    for x in expected_ids:
        if f'data-domain="{escape(x, quote=True)}"' not in html:
            raise ValueError(f"Missing domain filter: {x}")
    assets = manifest.get("assets")
    if not isinstance(assets, dict) or set(assets) != {"site.css", "site.js"}:
        raise ValueError("Unexpected assets manifest")
    if any(not isinstance(x, str) or not re.fullmatch(r"[a-f0-9]{64}", x) for x in assets.values()):
        raise ValueError("Invalid assets hash")
    if any(key in raw_manifest for key in ('"guardrails"', '"routes"', '"public_repos"')):
        raise ValueError("Private or policy metadata exposed in public artifact")
    return len(domains)


def verify_assets(manifest_text: str, assets: dict[str, bytes]) -> None:
    expected = json.loads(manifest_text)["assets"]
    for filename in ("site.css", "site.js"):
        payload = assets.get(filename)
        if payload is None or sha256(payload).hexdigest() != expected[filename]:
            raise ValueError(f"Published asset content differs from exact revision: {filename}")
    if b"source-desk" not in assets["site.js"] and b"Progressive enhancement" not in assets["site.js"]:
        raise ValueError("Unexpected site JavaScript")


def download(url: str) -> bytes:
    req = Request(url, headers={
        "User-Agent": "universal-knowledge-pages-validation/2",
        "Cache-Control": "no-cache",
    })
    with urlopen(req, timeout=15) as response:
        if response.status != 200:
            raise ValueError(f"HTTP {response.status}: {url}")
        data = response.read(1_000_001)
        if len(data) > 1_000_000:
            raise ValueError("Published asset exceeds bounded verification size")
        return data


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--local", type=Path)
    source.add_argument("--url")
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    if args.local:
        html = (args.local / "index.html").read_text(encoding="utf-8")
        raw = (args.local / "manifest.json").read_text(encoding="utf-8")
        count = verify(html, raw, args.revision)
        verify_assets(raw, {
            key: (args.local / "assets" / key).read_bytes()
            for key in ("site.css", "site.js")
        })
    else:
        parsed = urlsplit(args.url)
        if parsed.scheme != "https" or not parsed.netloc:
            parser.error("--url must be a deployed HTTPS site")
        base = args.url.rstrip("/") + "/"
        error = None
        for attempt in range(8):
            try:
                suffix = "?revision=" + args.revision
                html = download(urljoin(base, "index.html") + suffix).decode("utf-8")
                raw = download(urljoin(base, "manifest.json") + suffix).decode("utf-8")
                count = verify(html, raw, args.revision)
                verify_assets(raw, {
                    key: download(urljoin(base, "assets/" + key) + suffix)
                    for key in ("site.css", "site.js")
                })
                break
            except (ValueError, OSError, KeyError, json.JSONDecodeError, UnicodeError) as exc:
                error = exc
                if attempt == 7:
                    raise RuntimeError(f"Production verification failed: {error}") from error
                time.sleep(5)
    print(f"PASS: source desk revision={args.revision} domains={count}")


if __name__ == "__main__":
    main()
