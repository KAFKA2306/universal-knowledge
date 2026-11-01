#!/usr/bin/env python3
"""Build a public, offline GitHub Pages validation summary from canonical configuration."""
from __future__ import annotations

import argparse
from html import escape
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate_project import validate


def build_site(output: Path, *, root: Path = ROOT, revision: str = "local") -> dict:
    if root != ROOT:
        raise ValueError("Pages builder only accepts its own repository root")
    errors = validate()
    if errors:
        raise ValueError("Project validation failed: " + "; ".join(errors))
    registry = json.loads((root / "config/domain_registry.json").read_text(encoding="utf-8"))
    domains = []
    for entry in registry["domains"]:
        pack = json.loads((root / "domain_packs" / (entry["id"] + ".json")).read_text(encoding="utf-8"))
        domains.append({
            "id": entry["id"],
            "tier": entry["tier"],
            "version": pack["version"],
            "operations": len(pack["actions"]),
            "requires_review": pack["requires_review"],
        })
    manifest = {
        "schema_version": 1,
        "project": "Universal Knowledge Lab",
        "revision": revision,
        "validation": "configuration_passed",
        "domain_count": len(domains),
        "domains": domains,
    }
    rows = "\n".join(
        "<tr><th scope='row'><code>{}</code></th><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            escape(item["id"]), escape(item["tier"]), escape(item["version"]),
            item["operations"], "必要" if item["requires_review"] else "任意"
        ) for item in domains
    )
    page = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Universal Knowledge Lab | 設定検証</title>
</head>
<body>
<main data-revision="{escape(revision, quote=True)}">
<h1>Universal Knowledge Lab</h1>
<p>公開設定から生成した検証用ページです。設定の形式検証は成功しています。実LLMの抽出精度を保証するものではありません。</p>
<p>対象分野: {len(domains)}件 / ソースリビジョン: <code>{escape(revision)}</code></p>
<table>
<caption>分野設定の一覧</caption>
<thead><tr><th scope="col">分野ID</th><th scope="col">区分</th><th scope="col">設定版</th><th scope="col">操作数</th><th scope="col">確認</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p><a href="manifest.json">機械検証用JSON</a> / <a href="https://github.com/KAFKA2306/universal-knowledge">GitHubで正本を確認</a></p>
<p>ここには原文、LLM出力、個人情報、内部資料を公開しません。</p>
</main>
</body>
</html>
"""
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.html").write_text(page, encoding="utf-8")
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("_site"))
    args = parser.parse_args()
    result = build_site(args.output, revision=os.environ.get("GITHUB_SHA", "local"))
    print(f"PASS: {result['domain_count']} domains -> {args.output}")
