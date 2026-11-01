# v0.2からv0.3への分野移行

2026年10月31日、汎用の10分野を継続的に扱う11分野へ再編した。旧版と新版では操作名だけでなく対象も変わったため、**IDを置換するだけでは意味を維持できない**。旧JSONの自動変換は行わない。

| 旧ID | 新しい受け皿 | 主な変更 |
| --- | --- | --- |
| `manufacturing` | `manufacturing_process` | 一般的な処理操作から、SPC・試作・異常分析へ変更 |
| `finance` | `equity_research`、`semiconductor_capex` | 投資仮説と設備投資の発表を分離 |
| `software` | `software_factory`、`local_ai_agents` | 開発・リリースとモデル運用を分離 |
| `research` | `scientific_intelligence` | 論文の版、方法、再現性を中心に再定義 |
| `game` | `game_systems` | 推理上の確度とVRChatの状態も扱う |
| `operations` | `life_logistics`、`security_posture` | 予定管理と認証・権限管理を分離 |
| `cooking` | 対象外 | 必要になった時点で独立したパックを作る |
| `education` | 対象外 | 同上 |
| `medicine` | 対象外 | 再追加する場合は専門家の確認を必須とする |
| `legal` | 対象外 | 再追加する場合は専門家の確認を必須とする |

`career_intelligence` と `creative_production` は新設した。共通の `kind`、`status`、出力形式は維持しているが、各分野の `actions` は互換ではない。

既存の抽出結果を保存する場合は、元の分野ID、パックのバージョン、原文の識別子とSHA-256を残す。新しい操作定義で結果が必要なら、アクセス権のある環境で元の文章から再抽出して評価する。新しい架空例は `examples/domain_samples/` に置いた。
