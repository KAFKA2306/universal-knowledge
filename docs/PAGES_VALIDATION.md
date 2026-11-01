# GitHub Pagesで確認できること

[公開ページ](https://kafka2306.github.io/universal-knowledge/)は、`config/`と`domain_packs/`から生成した設定一覧です。正本はGitHubのソースであり、PagesのHTMLとJSONは直接編集しません。

## PRとmainで実行する検証

- **PR:** 分野設定の構造と参照関係、架空例による動作テスト、生成したHTMLと`manifest.json`のコミットSHA・分野一覧を確認する。PRでは公開しない。
- **main:** 同じ検証を通過した後、Pagesへ公開する。公開URLからHTMLとJSONを再取得し、公開時のコミットSHAと分野一覧が一致するか確認する。

公開ページには、分野ID、優先度、設定版、操作数、レビュー指定の有無だけを表示します。引用原文、モデル出力、個人の予定、内部資料、情報源のヒントは出力しません。

**検証の範囲:** 設定の構造、生成物の整合性、公開後のリビジョン一致です。JSON Schemaの完全適合、実モデルの抽出精度、抽出内容の意味や実運用の安全性は測定していません。レビュー指定は設定項目であり、人間の承認が完了したことを示しません。

## 手元で確認する

```bash
python scripts/validate_project.py
python -m unittest discover -s tests -v
GITHUB_SHA=local python scripts/build_pages.py --output _site
python scripts/verify_pages.py --local _site --revision local
```

公開結果は[GitHub Actions](https://github.com/KAFKA2306/universal-knowledge/actions/workflows/pages.yml)の`Verify live HTML and manifest for exact commit`で確認します。この処理が失敗した場合は、公開先URL、SHA、`manifest.json`の分野一覧を調べます。ローカル検証が成功しても、公開後の検証が終わるまで公開完了とは判定しません。

Pagesを初めて有効にする場合は、GitHubの**Settings → Pages → Build and deployment → Source**で**GitHub Actions**を選びます。[公式手順](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
