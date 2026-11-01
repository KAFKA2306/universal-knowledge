# GitHubでの更新と検証

**正本:** [KAFKA2306/universal-knowledge](https://github.com/KAFKA2306/universal-knowledge)（公開リポジトリ）。設計と設定はGitHubの`main`で管理し、[GitHub Pages](https://kafka2306.github.io/universal-knowledge/)に公開用の設定一覧を生成します。

## 変更を反映する手順

1. `main`を取得し、変更する設定・コード・文書の最新版を確認する。
2. 作業ブランチで変更し、必要なら架空例とテストを更新する。機密情報は含めない。
3. 次のコマンドを実行し、失敗を解消する。

   ```bash
   python scripts/validate_project.py
   python -m unittest discover -s tests -v
   GITHUB_SHA=local python scripts/build_pages.py --output _site
   python scripts/verify_pages.py --local _site --revision local
   ```

4. PRに変更理由、設定の互換性、確認した結果と未検証事項を書く。GitHub Actionsの結果を確認する。
5. リポジトリの保護ルールと必要な承認を満たした後に`main`へ統合する。不要な作業ブランチは削除する。
6. Pagesを変更した場合は、[公開URL](https://kafka2306.github.io/universal-knowledge/)とActionsの公開後検証結果を確認する。

## GitHub側で確認する設定

- `main`のブランチ保護、必須チェック、force pushの制限。
- マージ後のブランチ自動削除。
- secret scanningとpush protection（利用可能な場合）。
- Actionsの権限。通常のCIは`contents: read`、Pages公開ジョブだけが`pages: write`と`id-token: write`を要求する。

**これらのGitHub設定がすべて有効かは未確認です。** ワークフローファイルがあることと、ブランチ保護が有効なことは別です。

開発課題の下書きは`planning/issue-seeds.json`、優先順は[`ROADMAP.md`](ROADMAP.md)を参照してください。
