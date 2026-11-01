# GitHub運用

**正本リポジトリ:** [KAFKA2306/universal-knowledge-lab-](https://github.com/KAFKA2306/universal-knowledge-lab-)（末尾のハイフンを含む）。

このリポジトリは2026-11-01にGitHub上で確認した。公開範囲はPublic。初回確認時にはファイルがなく、v0.3.2の内容はまだ反映されていなかった。

## 更新手順

1. `main` と手元の変更を比較する。
2. 仕様・設定・実装・架空の検証データを同じ変更で更新する。機密情報は含めない。
3. `python scripts/validate_project.py` と `python -m unittest discover -s tests -v` を実行する。
4. PRに目的、変更対象、互換性、未検証事項を書く。CIの結果を確認する。
5. 保護ルールを満たしたPRを`main`へマージし、不要な作業ブランチを削除する。

## GitHub設定の確認

- `main` に対するPRとCIの必須チェック（GitHubで実際に有効か確認する）。
- force pushの禁止、マージ後のブランチ自動削除。
- シークレットスキャンとpush protection（利用可能な場合）。
- Actionsの最小権限。CIは `contents: read` のみを要求する。

CI定義が存在するだけでは保護機能を有効化できない。保護ルールはGitHub側で別途確認・設定する。

実装課題の下書きは `planning/issue-seeds.json`、優先順は [`ROADMAP.md`](ROADMAP.md) にある。
