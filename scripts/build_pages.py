#!/usr/bin/env python3
"""Build a public, searchable source desk from the reviewed URL registry."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate_project import validate as validate_project
from scripts.source_intake import validate as validate_sources

DESIGN_SHA = "08d91bb9faa6805852502812bc4575f328d62ec3"
DESIGN_URL = "https://cdn.jsdelivr.net/gh/KAFKA2306/design@" + DESIGN_SHA + "/styles/"
DOMAIN_NAMES = {
    "manufacturing_process": "製造・品質",
    "semiconductor_capex": "半導体・設備投資",
    "equity_research": "企業財務・投資",
    "scientific_intelligence": "科学・論文",
    "software_factory": "開発・自動化",
    "local_ai_agents": "ローカルAI",
    "security_posture": "セキュリティ",
    "career_intelligence": "転職・キャリア",
    "game_systems": "ゲーム・VR",
    "life_logistics": "旅行・暮らし",
    "creative_production": "制作・デザイン",
}
TYPE_NAMES = {
    "official_portal": "公式ポータル",
    "official_financial_results": "企業決算",
    "official_press_release": "公式発表",
    "regulatory_filing": "提出書類",
    "official_releases": "公式リリース",
    "official_docs": "公式文書",
    "official_careers": "採用ページ",
    "repository": "リポジトリ",
    "paper": "研究論文",
    "preprint": "プレプリント",
}


def published_records(catalog: dict) -> list[dict]:
    """Publish explicitly allowed metadata only; never copy routing hints or bodies."""
    records = []
    for entry in catalog["candidates"]:
        records.append({
            "id": entry["id"], "domain": entry["domain"],
            "title": entry["title"], "url": entry["url"],
            "record_type": "release_candidate", "published": entry["published"],
            "stage": "candidate",
        })
    for entry in catalog["sources"]:
        records.append({
            "id": entry["id"], "domain": entry["domain"],
            "title": entry["title"], "url": entry["url"],
            "record_type": entry["type"], "published": "",
            "stage": "source",
        })
    records.sort(key=lambda x: (
        x["stage"] != "candidate", -(int(x["published"][:4]) if x["published"][:4].isdigit() else 0),
        x["domain"], x["title"],
    ))
    return records


def build_site(output: Path, *, root: Path = ROOT, revision: str = "local") -> dict:
    if root != ROOT:
        raise ValueError("Pages builder only accepts its own repository root")
    errors = validate_project()
    if errors:
        raise ValueError("Project validation failed: " + "; ".join(errors))
    registry = json.loads((root / "config/domain_registry.json").read_text(encoding="utf-8"))
    domain_ids = [d["id"] for d in registry["domains"]]
    catalog = json.loads((root / "config/source_registry.json").read_text(encoding="utf-8"))
    validate_sources(catalog, set(domain_ids))
    records = published_records(catalog)
    domains = []
    for entry in registry["domains"]:
        pack = json.loads((root / "domain_packs" / (entry["id"] + ".json")).read_text(encoding="utf-8"))
        domains.append({
            "id": entry["id"], "tier": entry["tier"], "version": pack["version"],
            "operations": len(pack["actions"]), "requires_review": pack["requires_review"]
        })
    output.mkdir(parents=True, exist_ok=True)
    (output / "assets").mkdir(exist_ok=True)
    assets = {}
    for key, filename in [("site.css", "source-desk.css"), ("site.js", "source-desk.js")]:
        data = (root / "site" / filename).read_bytes()
        (output / "assets" / key).write_bytes(data)
        assets[key] = sha256(data).hexdigest()
    manifest = {
        "schema_version": 2, "site_kind": "source_desk", "project": "Universal Knowledge Lab",
        "revision": revision, "validation": "configuration_passed",
        "domain_count": len(domains), "source_count": len(catalog["sources"]),
        "candidate_count": len(catalog["candidates"]), "feed_count": len(catalog["feeds"]),
        "domains": domains, "records": records, "assets": assets,
    }
    counts = Counter(x["domain"] for x in records)
    buttons = ['<button type="button" class="domain-btn" data-domain="all" aria-pressed="true"><span>すべての分野</span><span>' + str(len(records)) + '</span></button>']
    for domain in domain_ids:
        label = DOMAIN_NAMES.get(domain, domain.replace("_", " "))
        buttons.append(
            '<button type="button" class="domain-btn" data-domain="' + escape(domain, quote=True) +
            '" aria-pressed="false"><span>' + escape(label) + '</span><span>' +
            str(counts[domain]) + '</span></button>'
        )
    cards = []
    for index, item in enumerate(records):
        domain = item["domain"]
        label = DOMAIN_NAMES.get(domain, domain.replace("_", " "))
        stage = item["stage"]
        status = "未審査候補" if stage == "candidate" else "出典入口確認"
        date = item["published"][:10] if item["published"] else "公開日未登録"
        type_label = TYPE_NAMES.get(item["record_type"], "公式リリース候補" if stage == "candidate" else item["record_type"])
        url = escape(item["url"], quote=True)
        title = escape(item["title"])
        search_text = " ".join((item["title"], label, domain, item["url"], type_label))
        cards.append(
            '<article class="record" data-index="' + str(index) +
            '" data-search="' + escape(search_text, quote=True) +
            '" data-domain="' + escape(domain, quote=True) +
            '" data-stage="' + escape(stage, quote=True) +
            '" data-published="' + escape(item["published"], quote=True) + '">' +
            '<div><div class="record-top"><span class="state-tag" data-state="' + stage + '">' + status +
            '</span><span>' + escape(label) + '</span><span>' + escape(type_label) +
            '</span></div><h3><a href="' + url + '" target="_blank" rel="noopener noreferrer">' +
            title + '</a></h3><p class="record-url">' + escape(item["url"]) +
            '</p><p class="record-meta">' + date + ' ・ 内容の正しさは未検証</p></div>' +
            '<a class="record-open" href="' + url +
            '" target="_blank" rel="noopener noreferrer" aria-label="' +
            escape(item["title"] + " の公式URLを開く", quote=True) + '">↗</a></article>'
        )

    page = """<!doctype html>
<html lang="ja" data-theme="paper">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' https://cdn.jsdelivr.net; script-src 'self'; img-src 'self' data:; base-uri 'none'; object-src 'none'; form-action 'none'">
<meta name="description" content="11分野の一次資料と公式更新情報を、出典・審査状態・日付から探せる公開資料台帳。">
<title>資料を探す | Universal Knowledge Lab</title>
<link rel="stylesheet" href="__DESIGN_URL__tokens.css">
<link rel="stylesheet" href="__DESIGN_URL__globals.css">
<link rel="stylesheet" href="__DESIGN_URL__components.css">
<link rel="stylesheet" href="assets/site.css">
<script defer src="assets/site.js"></script>
</head>
<body>
<div class="page-shell">
<header class="masthead">
<a class="identity" href="./" aria-label="Universal Knowledge Lab ホーム"><span class="identity-mark" aria-hidden="true">U</span><span class="identity-copy"><span class="identity-name">UNIVERSAL KNOWLEDGE</span><span class="identity-kicker">source desk / public edition</span></span></a>
<nav class="mast-links" aria-label="関連リンク"><a href="manifest.json">公開データ</a><a href="https://github.com/KAFKA2306/universal-knowledge" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav>
</header>
<main data-revision="__REVISION__">
<section class="hero" aria-labelledby="hero-title">
<div><p class="eyebrow">Evidence, not assumptions · 11 domains</p>
<h1 id="hero-title">資料を集める。<br>根拠をたどる。</h1>
<p class="hero-lead">半導体・投資・AI・製造・ゲームなど、11分野の一次資料と公式更新情報を一か所から探せます。URLの確認状況と未審査の候補を分けて表示します。</p></div>
<aside class="note" aria-label="検証状態について"><p class="note-head">確認できた範囲</p><p>「出典入口確認」は公開先URLを登録した状態です。資料の内容や主張を検証した意味ではありません。「未審査候補」は公開日や関連性の確認が残っています。</p></aside>
</section>
<section class="stats" aria-label="収集状況">
<div class="stat"><span class="stat-number">__SOURCE_COUNT__</span><span class="stat-label">登録した資料・情報源</span></div>
<div class="stat"><span class="stat-number">__CANDIDATE_COUNT__</span><span class="stat-label">未審査の更新候補</span></div>
<div class="stat"><span class="stat-number">__DOMAIN_COUNT__</span><span class="stat-label">対象分野</span></div>
<div class="stat"><span class="stat-number">__FEED_COUNT__</span><span class="stat-label">自動収集フィード</span></div>
</section>
<div class="section-head"><div><p class="eyebrow">Source inventory</p><h2 id="records-title">資料一覧</h2></div><p>公式URLのみを掲載。本文・個人情報は保存しません。</p></div>
<div class="workspace">
<aside class="domain-panel" aria-label="分野を選択"><p class="panel-label">分野フィルター</p><div class="domain-list">__DOMAIN_BUTTONS__</div></aside>
<section aria-labelledby="records-title">
<div class="toolbar" role="search" aria-label="資料を検索・絞り込み">
<label class="search-field"><span class="tool-label">キーワード</span><input id="search" type="search" placeholder="企業・技術・資料名で検索" autocomplete="off"></label>
<label><span class="tool-label">審査状態</span><select id="stage"><option value="all">すべて</option><option value="source">出典入口確認</option><option value="candidate">未審査候補</option></select></label>
<label><span class="tool-label">並び替え</span><select id="order"><option value="default">候補を優先</option><option value="newest">公開日が新しい</option><option value="oldest">公開日が古い</option></select></label>
</div>
<div class="search-status"><output id="result-count" aria-live="polite">__RECORD_COUNT__件 / 全__RECORD_COUNT__件</output><button id="clear-filters" type="button" class="clear-button">条件をクリア</button></div>
<div id="records" class="records">__CARDS__</div>
<div id="empty" class="empty" hidden><h3>該当する資料がありません</h3><p>検索語や分野、審査状態を変えてください。</p></div>
</section>
</div>
</main>
<footer class="footer"><div>Universal Knowledge Lab · 公開メタデータのみ。モデルの抽出精度は未評価です。</div><div>Commit <span class="commit">__SHORT_REVISION__</span> · <a href="manifest.json">JSON</a> · <a href="https://github.com/KAFKA2306/design">Design authority</a></div></footer>
</div>
</body>
</html>
"""
    replacements = {
        "__DESIGN_URL__": DESIGN_URL, "__REVISION__": escape(revision, quote=True),
        "__SHORT_REVISION__": escape(revision[:9]),
        "__SOURCE_COUNT__": str(len(catalog["sources"])),
        "__CANDIDATE_COUNT__": str(len(catalog["candidates"])),
        "__DOMAIN_COUNT__": str(len(domains)),
        "__FEED_COUNT__": str(len(catalog["feeds"])),
        "__DOMAIN_BUTTONS__": "\n".join(buttons),
        "__RECORD_COUNT__": str(len(records)),
        "__CARDS__": "\n".join(cards),
    }
    for before, after in replacements.items():
        page = page.replace(before, after)
    (output / "index.html").write_text(page, encoding="utf-8")
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("_site"))
    args = parser.parse_args()
    result = build_site(args.output, revision=os.environ.get("GITHUB_SHA", "local"))
    print(f"PASS: source desk with {result['source_count']} verified URLs, "
          f"{result['candidate_count']} unreviewed candidates -> {args.output}")
