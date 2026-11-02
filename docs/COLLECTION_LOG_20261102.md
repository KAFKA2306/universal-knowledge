# 2026年11月2日：一次資料の初回収集

**収集範囲:** 公開情報源18件、Atomフィード4件、個別リリース候補5件。情報源の入口は11分野すべてに登録済みですが、自動収集は3分野に限ります。

「公開先URLを確認した」ことと、「資料の内容を検証した」ことは別です。以下の数値は各発行元が公表したもので、独立した追試ではありません。

## 決算・半導体の一次資料

| 発行日 | 分野 | 一次資料と確認できる内容 | 扱い |
| --- | --- | --- | --- |
| 2026-10-15 | `semiconductor_capex` | [TSMC 2026年第3四半期決算](https://pr.tsmc.com/english/news/3346)：連結売上高 NT$1,494.24 billion、希薄化後EPS NT$29.43。対象は2026年7～9月期、TIFRSに基づく公表実績。 | 企業公表実績。外部監査や独立検証を実施したという意味ではない。 |
| 2026-10-15 | `semiconductor_capex` | [TSMC四半期決算資料](https://investor.tsmc.com/english/quarterly-results/2026/q3)：2026年第4四半期の売上高ガイダンス US$52.3–54.3 billion。 | **会社予測**。実績として扱わない。 |
| 2026-10-15 | `equity_research` | [TSMCのSEC提出資料](https://www.sec.gov/Archives/edgar/data/1046179/000104617926000726/a3q26e_withguidancexfinal.htm)：同社の第3四半期決算公表内容を米SEC上の提出資料と照合できる。 | 一次資料の複数経路。重複する業績数値を別実績として二重計上しない。 |

## 公式ソフトウェアリリース：未審査候補

| 公開日時（UTC） | 分野 | 公式リリース | 状態 |
| --- | --- | --- | --- |
| 2026-11-01 09:00:59 | `local_ai_agents` | [llama.cpp b12032](https://github.com/ggml-org/llama.cpp/releases/tag/b12032) | プレリリース。GPU互換性や性能は未検証。 |
| 2026-10-27 00:47:49 | `software_factory` | [uv 0.13.6](https://github.com/astral-sh/uv/releases/tag/0.13.6) | リリース掲載を確認。導入の必要性は未評価。 |
| 2026-10-22 01:35:54 | `software_factory` | [uv 0.13.5](https://github.com/astral-sh/uv/releases/tag/0.13.5) | リリース掲載を確認。影響範囲は未評価。 |
| 2026-10-23 18:47:17 | `software_factory` | [FastAPI 0.162.0](https://github.com/fastapi/fastapi/releases/tag/0.162.0) | リリース掲載を確認。互換性は未評価。 |
| 2026-06-25 19:55:44 | `game_systems` | [VRChat Creator Companion 2.5.0 Beta 2](https://github.com/vrchat-community/creator-companion/releases/tag/2.5.0-beta.2) | **参考（過去資料）**。新着とは呼ばない。ベータ版。 |

日時は発行元のGitHub Releases APIで確認しました。これら5件はフィード由来の型に揃えて手動登録した初回候補であり、`review: unreviewed` のまま保管します。自動収集が実ネットワーク上で成功した証拠ではありません。

## 収集処理と次の確認

- [情報源の正本](../config/source_registry.json)に、発行元の公式ページ、登録済みAtomフィード、未審査候補を分離しました。URLをSHA-256の先頭16文字で識別し、既登録URLを重複追加しません。
- [収集スクリプト](../scripts/source_intake.py)は、各フィードに紐付けたGitHubリポジトリのリリースURLだけを採用します。本文・要約や私的なデータは保存しません。
- [収集ワークフロー](../.github/workflows/source-intake.yml)が次回ネットワーク取得した候補はPRへ提案し、承認前に自動マージしません。
- 製造、金融、科学論文、セキュリティ、キャリア、生活、制作など、残る分野の自動収集は**未実装**です。今回の初回登録を実モデルの抽出精度検証とみなさないでください。
