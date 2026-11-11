# ADR-0003：抽出実行のモデル・設定・出典追跡

**状態：** 採用（2026-11-11）。関連Issue：#3

## 背景

従来の出力には、引用と原文SHA-256、分野パックのバージョンがあったが、使用したモデル、プロンプト、分野パックそのもの、実効設定の同一性を各レコードから追跡できなかった。

## 決定

抽出結果の最上位と各採用レコードに `provenance` を追加する。`source_sha256` はUTF-8原文、`domain_pack_sha256` はパックJSONの実ファイル、`prompt_sha256` はcanonical JSON化した実行対象メッセージ、`runtime_config_sha256` は設定ファイルのハッシュとモデル・接続先・タイムアウトの実効値から計算する。`prompt_version` はコード側の固定版番号とする。モデルの名前は呼び出しに指定した値を記録する。

モデル実体のrevisionはAPI呼び出し名から推測できない。`--model-revision` は取得・確認できた場合にだけ指定し、ユーザー申告のrevisionは `DECLARED_NOT_VERIFIED` と記録する。指定がなければnull、状態は `UNVERIFIED_MODEL_REVISION` とする。オフラインfixtureは `model_id=null`、`prompt_executed=false`、`FIXTURE_NOT_MODEL` として実モデル実行を装わない。

## 移行と互換性

既存の `normalize(prediction, source, pack, id)` 呼び出しは互換とし、明示的な実行情報がなければ不明を記録する。旧JSONは `read_output(path)` で読み込み、欠けた `provenance` に `LEGACY_UNVERIFIED` だけを付与する。過去のモデル名・版・ハッシュは推測して埋めない。採用済み原文・文字位置・引用・判断を変更しない。グラフのrecord nodeにも同じ出典情報を引き継ぐ。

ハッシュの一致は入力の同一性を検証するものであり、抽出内容の意味的な正確さ、モデルの実体revision、推論の再現可能性を保証しない。実モデル精度の評価は別Issueで扱う。
