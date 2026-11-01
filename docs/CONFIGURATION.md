# 分野の追加と設定の変更

操作名とその意味は `domain_packs/<id>.json`、分野の目的と情報源は `config/domain_registry.json`、推論サーバーの初期値は `config/pipeline.json` が正本となる。設定値は説明文書へ転記せず、正本を参照する。

## 新しい分野を追加する

1. 既存分野と役割が重ならないか、[`DOMAIN_SCOPE.md`](DOMAIN_SCOPE.md) で確かめる。
2. `domain_packs/<id>.json` を作る。IDは `snake_case`、バージョンは `X.Y.Z`。各操作を `actions` に定義する。共通操作の `read`、`record`、`check`、`approve`、`reject`、`notify`、`wait` は再定義しない。
3. `config/domain_registry.json` に同じIDを一度だけ登録し、`tier`、`goal`、`routes`、`sources`、`public_repos`、`links`、`guardrails` を記す。`links` は登録済みの分野IDを指定する。現段階の `routes`、`sources`、`public_repos`、`links`、`guardrails` は管理用のメタデータであり、抽出処理による自動判定・自動取得・アクセス制御は実装していない。
4. `requires_review` を設定する。高リスク分野では `true` が必須。ただし、この値は抽出結果の確認を促す印であり、人間の承認や実行権限を管理する機能ではない。
5. `examples/domain_samples/` に架空の原文と、正しい操作名・状態を記した模擬LLM応答を用意する。操作名の違いや引用の欠落を検出するテストを追加する。
6. 操作定義の意味を変えた場合はバージョンを更新し、旧出力との互換性をPRに記録する。

## 確認する

```bash
python scripts/validate_project.py
python -m unittest discover -s tests -v
```

最初のコマンドは設定の構造、分野間参照、模擬データの存在などを確認する。JSON Schemaへの完全な適合、外部GitHubリポジトリの存在、分野固有の意味の正しさは検査しない。次のコマンドは模擬データに対する動作テストを実行する。両方とも実モデルの精度を測るものではない。

## 推論とデータの取り扱い

初期の推論先はローカルのOpenAI互換HTTPサーバーで、`config/pipeline.json` に記載する。CLIでモデルと接続先を変更できるが、接続先はループバックアドレスに制限する。引用を必須とする設定と、意味の正確さを保証しない設定は変更できない。

公開リポジトリには、架空データと公開可能な設定だけを保存する。実際の工程記録、口座情報、個人の予定、認証情報は追加しない。抽出結果には引用として元の文が含まれるため、ローカルの出力も適切に管理する。
