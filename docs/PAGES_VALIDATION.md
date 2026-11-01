# GitHub Pagesでの公開検証

このリポジトリはGitHub Pagesを公開成果物の検証対象にします。正式な設定の正本は`config/`と`domain_packs/`です。Pagesは生成物で、直接編集しません。

## PRとmainの違い

- PR: 設定検証、架空データのテスト、ページ生成、生成したHTML/JSONとコミットSHAの一致を検証します。公開しません。
- main: 同じ検証を通過した場合だけGitHub Pagesへ公開し、実際の公開URLからHTMLと`manifest.json`を取得します。GitHub ActionsのコミットSHAが一致しなければ失敗します。
- 公開ページには11分野のID、区分、設定版、操作数、レビュー要否だけを掲載します。個人の予定、抽出した原文、内部資料、モデル出力、情報源のヒントは公開しません。

## 初回セットアップ

リポジトリの **Settings → Pages → Build and deployment → Source** で **GitHub Actions** を選択してください。GitHub連携から設定変更できない場合は、管理者がこの操作を行います。未設定ではmainでの公開ジョブが失敗する可能性があります。

GitHubの公式手順: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## ローカル検証

```bash
python scripts/validate_project.py
python -m unittest discover -s tests -v
GITHUB_SHA=local python scripts/build_pages.py --output _site
python scripts/verify_pages.py --local _site --revision local
```

公開URLの確認は、デプロイ完了後にワークフローの`Verify live HTML and manifest for exact commit`を確認します。GitHub Actionsの緑色チェックだけでは、公開URLの更新を証明できません。公開結果の検証まで成功してはじめて完了とします。

公開ページは設定形式の整合性を示すだけです。実モデルの抽出精度、引用内容の意味的正しさ、セキュリティの安全性は保証しません。
