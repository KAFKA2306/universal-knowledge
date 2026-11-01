# Universal Knowledge Lab

製造技術、半導体投資、研究、ソフトウェア開発などの文章から、操作・観測・主張・判断・規則を取り出し、出典とともに記録する試作です。11分野の操作定義を差し替えられるため、抽出処理の基本部分を変更せずに分野を追加できます。

**現在の状態（2026-11-01）:** 11分野の設定、模擬LLM応答による動作テスト、GitHub Actionsでの設定検証とPages公開を実装しています。公開ページでは設定一覧とコミットSHAを照合できます。実モデルの抽出精度は未測定です。また、引用文字列が原文と一致しても、解釈が正しいとは限りません。分野横断の自動推論と外部サービスの操作は未実装です。

## 対応する11分野

分野ID、優先度、情報源、禁止事項の正本は [`config/domain_registry.json`](config/domain_registry.json) です。操作名とその意味は [`domain_packs/`](domain_packs/) に定義します。`routes`、`sources`、`guardrails` は現段階では参照用の設定で、自動選別やアクセス制御には使いません。

| 優先度 | 分野ID | 主な対象 |
| --- | --- | --- |
| core | `manufacturing_process` | 製造条件、SPC、試作、不具合分析 |
| core | `semiconductor_capex` | 設備投資、工場、受注残、生産能力 |
| core | `equity_research` | 決算、財務、投資仮説、反証条件 |
| core | `scientific_intelligence` | 論文、特許、実験方法、再現結果 |
| core | `software_factory` | Issue、PR、CI、デプロイ、復旧 |
| core | `local_ai_agents` | ローカルLLM、検索、グラフ探索、監視 |
| active | `security_posture` | 認証、漏えい、OAuth、権限 |
| active | `career_intelligence` | 技術リード求人、応募条件、待遇 |
| active | `game_systems` | ボードゲーム、推理、VRChat |
| active | `life_logistics` | 体験イベント、旅行、交通、予定 |
| active | `creative_production` | 画像、動画、プロンプト、公開作業 |

`core` は精度評価を先に行う6分野、`active` は継続して扱う5分野です。どちらも実データでの精度検証を終えていません。旧10分野からの変更は [`docs/DOMAIN_MIGRATION.md`](docs/DOMAIN_MIGRATION.md) に記録しています。

## 試作でできること

UTF-8の文書と分野定義を入力し、抽出結果をJSONで保存します。抽出対象は `action`（操作）、`observation`（観測）、`claim`（主張）、`decision`（判断）、`rule`（規則）の5種類。`performed`（実施済み）、`planned`（予定）、`hypothetical`（仮定）など6つの状態も区別します。

抽出結果には、引用文、文字位置、入力文書のSHA-256、出典識別子を残します。引用が原文にない候補や未登録の操作名は拒否します。引用が複数箇所にある場合や、確認が必要な分野の結果にはレビューの印を付けます。出力されるグラフは言及関係の記録であり、因果関係や同一人物・同一企業の確定ではありません。

## 実行方法

Python 3.11以上を想定しています。次の例は人が作成した模擬LLM応答を読み込むため、LLMサーバーは不要です。

```bash
python scripts/validate_project.py
python -m unittest discover -s tests -v
python ukl.py --domain manufacturing_process \
  --input examples/domain_samples/manufacturing_process.txt \
  --fixture examples/domain_samples/manufacturing_process.model.json \
  --output output/manufacturing_process.json \
  --graph-output output/manufacturing_process_graph.json
```

最後のコマンドで `Accepted 1; rejected 0` が表示され、指定したJSONファイルが保存されれば、模擬データを使った抽出処理は成功です。実際のローカルLLMを使う場合は `--fixture` を外し、実行可能なモデル名を `--model`、ローカルサーバーのURLを `--base-url` に指定します。既定のモデル名 `local` は仮置きです。HTTPでの接続先はループバックアドレスに限定されます。

入力文書や抽出結果には機密情報が含まれる場合があります。原文が再掲されるため、アクセス制御された保存先を使ってください。公開リポジトリに含めるのは設定、設計、架空データだけです。

## 設定を育てる手順

1. [`docs/DOMAIN_SCOPE.md`](docs/DOMAIN_SCOPE.md) で追加する分野の役割と既存分野との境界を確認する。
2. `domain_packs/<id>.json` に操作名と説明を定義し、`config/domain_registry.json` に用途と禁止事項を記載する。
3. 架空例と境界を確かめるテストを追加する。定義の意味を変える場合はパックのバージョンを更新する。
4. 上記の検証コマンドを実行し、PRで変更理由と互換性を確認する。
5. 実際の文章に対する精度は、出典を確認した正解データを別途用意して評価する。

設計の詳細は [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)、評価項目は [`docs/EVALUATION.md`](docs/EVALUATION.md)、日本語の文書規約は [`docs/WRITING_GUIDE.md`](docs/WRITING_GUIDE.md) にまとめています。`KAFKA2306/design` はUI、`KAFKA2306/prompt-vault` は共通プロンプトの正本です。ここでは両者の内容を複製しません。

## 参考研究

- [Costaら（2026年）](https://doi.org/10.1038/s41467-026-78605-7)：研究室の調製手順を、分野別の操作定義とLLMで抽出する研究。
- [Prospector（2026年）](https://arxiv.org/abs/2610.37121)：学習した探索方針で知識グラフをたどり、回答の根拠を収集する研究。

本リポジトリはこれらを参考に設計した**独立した試作**です。論文の方式を再実装したものではなく、論文が報告した精度も本プロジェクトの性能ではありません。

## GitHub Pagesによる公開検証

PRでは設定とテストを確認し、公開用HTMLとJSONを照合します。mainへ統合した後はPagesへ公開し、公開URLから再取得した内容のコミットSHAと分野一覧を確認します。この検証の対象は設定と公開成果物です。実モデルによる抽出の正しさは測定していません。

- [公開設定一覧（GitHub Pages）](https://kafka2306.github.io/universal-knowledge/)
- [検証内容と失敗時の確認方法](docs/PAGES_VALIDATION.md)

## 一次資料の収集

11分野の公式情報源12件を [`config/source_registry.json`](config/source_registry.json) に登録しました。**情報源の所在を確認した**段階であり、各ページの主張や、データ利用条件を検証したという意味ではありません。

[`scripts/source_intake.py`](scripts/source_intake.py) はURL・分野ID・重複を検査します。週次の [Source intake proposals](.github/workflows/source-intake.yml) は、現在llama.cppのAtomフィードから公開タイトル・URL・日付のみ取得し、差分がある場合に未審査候補のPRを作成します。自動マージは行いません。全文や個人情報は収集しません。

対象、審査方法、運用上の制約は [`docs/SOURCE_COLLECTION.md`](docs/SOURCE_COLLECTION.md) に記載しています。**11分野すべての自動収集が実装されたわけではありません。**
