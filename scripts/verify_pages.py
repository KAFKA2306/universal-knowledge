#!/usr/bin/env python3
"""Fail if a local Pages artifact or deployed site doesn't match the intended commit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


def verify(html: str, raw_manifest: str, revision: str) -> int:
    manifest = json.loads(raw_manifest)
    if manifest.get("revision") != revision:
        raise ValueError("Published revision does not match the workflow SHA")
    domains = manifest.get("domains")
    if manifest.get("validation") != "configuration_passed" or not isinstance(domains, list):
        raise ValueError("Missing configuration validation result")
    registry = json.loads((Path(__file__).resolve().parents[1] / "config/domain_registry.json").read_text(encoding="utf-8"))
    expected_ids = [item["id"] for item in registry["domains"]]
    if manifest.get("domain_count") != len(domains) or [item.get("id") for item in domains] != expected_ids:
        raise ValueError("Domain inventory differs from the checked-out registry")
    if 'lang="ja"' not in html or "Universal Knowledge Lab" not in html:
        raise ValueError("Unexpected HTML page")
    if f'data-revision="{revision}"' not in html:
        raise ValueError("HTML revision does not match workflow SHA")
    for domain in domains:
        if domain["id"] not in html:
            raise ValueError(f"Domain is missing from HTML: {domain['id']}")
    return len(domains)


def download(url: str) -> str:
    req = Request(url, headers={"User-Agent": "universal-knowledge-pages-validation/1", "Cache-Control": "no-cache"})
    with urlopen(req, timeout=15) as response:
        if response.status != 200:
            raise ValueError(f"HTTP {response.status}: {url}")
        return response.read().decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--local", type=Path)
    source.add_argument("--url")
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    if args.local:
        html = (args.local / "index.html").read_text(encoding="utf-8")
        manifest = (args.local / "manifest.json").read_text(encoding="utf-8")
        count = verify(html, manifest, args.revision)
    else:
        parsed = urlsplit(args.url)
        if parsed.scheme != "https" or not parsed.netloc:
            parser.error("--url must be a published HTTPS site")
        base = args.url.rstrip("/") + "/"
        error = None
        for attempt in range(8):
            try:
                html = download(urljoin(base, "index.html") + "?revision=" + args.revision)
                manifest = download(urljoin(base, "manifest.json") + "?revision=" + args.revision)
                count = verify(html, manifest, args.revision)
                break
            except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
                error = exc
                if attempt == 7:
                    raise RuntimeError(f"Production verification failed: {error}") from error
                time.sleep(5)
    print(f"PASS: revision={args.revision} domains={count}")


if __name__ == "__main__":
    main()
