# GitHub Pages：公開資料デスク

[公開サイト](https://kafka2306.github.io/universal-knowledge/)は、旧「設定検証表」を**全面的に置き換えた**、一次資料の閲覧・検索画面です。登録した情報源と未審査候補をまとめて探せます。元の`config/`、`domain_packs/`、資料URLの履歴は削除しません。

## 表示内容と状態

- **出典入口確認：** `config/source_registry.json` の`sources`。URLを登録した段階で、原文の記述が正しいと確認した意味ではありません。
- **未審査候補：** 同ファイルの`candidates`。公式リリースなどの候補URL・題名・日時のみ。人手での採否を終えていません。
- **分野と件数：** `config/domain_registry.json` に登録された分野名・優先度をもとに表示する。ユーザーはキーワード、分野、審査状態で絞り込み、日付順に並べ替えられます。
- 公開日が`source`にない場合は「公開日未登録」と表示し、架空の日付を補いません。公開日時のある`candidate`のみで日付順を評価できます。

**公開しないもの：** 収集した本文、要約、認証情報、個人の予定、内部資料、分野ごとの入力ヒント・禁止事項。ページは資料へのリンクであって、全文データベースではありません。

## GitHubとデザインの正本

- 情報源：[`config/source_registry.json`](../config/source_registry.json)
- 分野：[`config/domain_registry.json`](../config/domain_registry.json)
- 画面生成：[`scripts/build_pages.py`](../scripts/build_pages.py)
- レイアウト・検索：[`site/source-desk.css`](../site/source-desk.css)、[`site/source-desk.js`](../site/source-desk.js)
- 色、文字、余白、操作部品：[`KAFKA2306/design`](https://github.com/KAFKA2306/design)を正本とし、指定のGitコミット`08d91bb9faa6805852502812bc4575f328d62ec3`の公開CSSをCDNで参照します。紙色テーマ`data-theme="paper"`を使用します。CDN障害時に装飾が適用されないことがありますが、資料リンクはHTMLとして残ります。

## 自動検証

PRでは設定検証・単体テスト・ページ生成・HTML/JSON・CSS/JSのSHA-256照合を実行し、公開しません。mainにマージすると公開し、公開URLから`index.html`、`manifest.json`、`assets/site.css`、`assets/site.js`を再取得します。

検証は次を確認します。

1. `manifest.json`の仕様が**v2/source_desk**であり、以前の設定一覧には戻っていない。
2. 掲載する資料ID・題名・URL・審査状態が正本と一致し、11分野を欠落なく表示する。
3. 公開したコミットSHAがGitHub Actionsの対象SHAと一致する。
4. HTML・JSON以外のCSS/JSも、ビルド済みハッシュと一致する。
5. 機密入力情報やルーティングヒントがページに含まれない。

手元では次を実行します。

```bash
python scripts/validate_project.py
python scripts/source_intake.py
python -m unittest discover -s tests -v
GITHUB_SHA=local python scripts/build_pages.py --output _site
python scripts/verify_pages.py --local _site --revision local
```

[GitHub Actions](https://github.com/KAFKA2306/universal-knowledge/actions/workflows/pages.yml)で`Verify live HTML and manifest for exact commit`まで成功すれば、公開内容が対象コミットと一致したと判断できます。サイト上での検索操作の実機使用感、CDN接続、実LLMの抽出精度、資料内容の正しさは、この自動検証だけでは証明できません。

過去の設定一覧画面は置き換えますが、以前のコミットへGitHubから戻せます。
