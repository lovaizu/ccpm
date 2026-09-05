Rn version: 0.8.0
Design: .rn/hposal-plugin/design.md

# Goal

`corporate-site-kit`（HP＝コーポレートサイトの見積・提案書を作る、日本語の「読み物キット」：README＋
唯一の手順書 `workflow.md`＋記入用 `templates/` 5本）を、Claude Code から `/コマンド` で呼び出せる
プラグイン **`hposal`**（HP proposal）に作り変え、この `ccpm` マーケットプレイスに `rn` と並べて
`/plugin install` で導入できるようにする。

お手本は完成済みの `rn` プラグイン（`rn/` 配下の構成をそのまま型として踏襲する）。言語は読者層で分岐させ、
利用者が読む成果物（README・テンプレ本文・提案書の可視コピー）は日本語、AI 向け SKILL.md と機械/マーケット
向けメタは英語にする（design.md 4.2 / D-6）。着手の前に、元キット一式を本セッションのステアリングと同じ
フォルダにベース素材としてコピーしておく（原本は Google Drive にあり、リポジトリ内に変換のたたき台と
「変換前」の比較対象を持つため）。

# Acceptance criteria

**ゴール適合**

- `hposal/` がリポジトリ直下に存在し、`rn` と同じプラグイン構成を持つ：`.claude-plugin/plugin.json` /
  `skills/<name>/SKILL.md` / `references/`（テンプレ） / `README.md` / `CHANGELOG.md`。
- `workflow.md` の4フェーズ（要件整理→提案整理→作業リスト→提案書）が、スキルの挙動として欠落なく
  保たれている — フェーズ・共通ルール・各 ⚠️ 落とし穴・★人間ゲートが一つも失われていない。
- スキルが `/hposal:<name>` として呼び出せ、呼ぶとそのフェーズ手順が動く（frontmatter を持つ正しい
  SKILL.md である）。
- 元の `templates/` 5本（01_requirements / 02_proposal-design / 03_work-breakdown / 04_proposal /
  site-inventory）が `hposal/references/` 配下に置かれ、スキル本文から参照されている。
- `hposal/README.md` が冒頭で一度だけ「HP（corporate site）」と補い、キットが何をするかと、導入手順
  （marketplace add → plugin install）・始め方を `rn` の README と同じ流儀で説明している。
- `hposal/.claude-plugin/plugin.json` が `name: hposal` / 英語の description（corporate-site-proposal
  系） / `version: 0.1.0` / `author: lovaizu` を持つ。
- `.claude-plugin/marketplace.json` に `hposal` のエントリ（`name`/`description`(英語)/`source: ./hposal`/
  `category`）があり、かつ root `README.md` の Plugins 一覧にも `hposal` がリンク付きで載っている
  （両者が同期している）。

**品質**

- 言語は D-6 に従う（hposal＝日本限定）：利用者が読む成果物＝日本語、AI/メタ＝英語。日本語＝README・
  テンプレ本文（01-03・site-inventory・04_proposal.md）・`04_proposal.html` の記入ガイド/コメント＋
  クライアント可視コピー＋`{{}}`（提出物）＋実行時生成物/コンソール。英語＝SKILL.md・plugin.json・
  marketplace.json・CHANGELOG・root README 一覧行・コミット/PR。
- `claude plugin validate hposal --strict` と `claude plugin validate .`（マーケットルート）の両方が
  通る。
- ヘッドレス確認 `claude -p "/hposal:<name>" --plugin-dir hposal` でスキルが読み込まれて起動する。
- 内容ドリフトがない：変換後のスキル/テンプレが元キットの意図と一致し、ルールの取りこぼしや、参照の
  受け渡し点に挿入された要約が無い（`.rn/hposal-plugin/` のベースコピーと差分照合できる）。
- リポジトリのルールに沿う：plugin.md（version は plugin.json のみ・CHANGELOG を置く）／marketplace.md
  （2か所に登録）／language.md（読者層が一言語に限定されるプラグインの例外に従い、利用者が読む成果物は
  日本語＝D-6）。

# Assumptions

（`D-n` は本セッションの決定。実体は `design.md`（Design: 行の指す先）に置いてある。）

- 〔事実・確認済〕元キット＝`README.md`＋`workflow.md`（128行）＋`templates/` 5本、すべて日本語。
- 〔事実・確認済〕`rn` がプラグインの型：`.claude-plugin/plugin.json`／`skills/<name>/SKILL.md`／
  `references/`／`README.md`／`CHANGELOG.md`。`skills/<フォルダ名>` がコマンド名になる。
- 〔事実・確認済〕現状 `marketplace.json` と root `README.md` は `rn` のみを載せている。
- 〔事実・確認済〕Google Drive 上の元キットパスは読み取り可能（コピー可能）。
- 〔事実・ユーザー確認済〕名前は `hposal`。言語は D-6（読者層＝日本限定／利用者が読む成果物＝日本語・AI/メタ＝英語）。
  README 冒頭で一度だけ「HP（corporate site）」を補う。
- 〔判断・要レビュー〕1スキルで4フェーズ全体を駆動する（フェーズごとに別スキルへ割らない）。workflow は
  ★ゲートで区切られた一続きの工程だから（D-1）。
- 〔判断・要レビュー〕スキル名＝コマンド名は `up`（`/hposal:up`）。「提案を起こす」を表す短い合図で、
  `rn` の `gm`/`bb`/`hi` の流儀に揃える（D-1）。
- 〔判断・方針〕初期 version は `0.1.0`。タグ付け／GitHub Release は別の明示指示で行う作業で、本セッションの
  スコープ外（D-3、plugin.md の「リリース指示があるときだけ昇格」に従う）。

# Rules

- 変更のたびに commit & push する。完了マーカー（`complete task #{id}`）は1タスクにつき1つ。
- 言語は D-6（hposal＝日本限定）：利用者が読む成果物（README・テンプレ本文・`04_proposal.html` の記入
  ガイド/可視コピー）＝日本語、AI向け SKILL.md とメタ（plugin.json/marketplace.json/CHANGELOG/root README）＝英語。
- version は `plugin.json` の1か所だけ（marketplace.json には書かない）。
- `marketplace.json` と root `README.md` は同じ変更内で同期させる。
- 内容ドリフト禁止：`workflow.md` の全フェーズ・全ルール・全 ⚠️・★ゲートを保つ。参照の受け渡し点
  （SKILL.md → references）に要約を置かない（ペイロードのみ渡す）。

# Tasks

### #1: 元キットをベースとしてセッションフォルダにコピーする

**Purpose**: 変換のたたき台と「変換前」の比較基準として、Google Drive 上の元キット一式をリポジトリ内の
`.rn/hposal-plugin/corporate-site-kit/` に丸ごとコピーする。

**Prerequisites**: none

**Steps**:

- [x] Google Drive の `corporate-site-kit`（README.md / workflow.md / templates/ 5本）を
      `.rn/hposal-plugin/corporate-site-kit/` に再帰コピーする
- [x] コピー後のファイル数・相対構成が元と一致することを確認する
- [x] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/1.md` に記録）
- [x] QA engineer review（subagent）
- [x] user review

**Completion criteria**:

- `.rn/hposal-plugin/corporate-site-kit/` に `README.md`・`workflow.md`・`templates/` の5本が存在する。
- コピー先の各ファイルの内容が Google Drive 上の原本とバイト一致している。

### #2: workflow.md をスキル `hposal/skills/up/SKILL.md` に変換する

**Purpose**: 唯一の手順書 `workflow.md` を、frontmatter を備え `${CLAUDE_PLUGIN_ROOT}/references/` を指す
正しい SKILL.md に作り変える。フェーズ・ルール・⚠️・★ゲートは欠落なく保つ。

**Prerequisites**: #1

**Steps**:

- [x] `hposal/skills/up/SKILL.md` を作成し、`name: up` と description を持つ frontmatter を付ける
- [x] `workflow.md` の本文（4フェーズ・共通ルール・たどれるようにする・全 ⚠️・★ゲート）を本体に移し、
      テンプレ参照箇所を `${CLAUDE_PLUGIN_ROOT}/references/templates/...` の実パスに置き換える
- [x] 元 `workflow.md` のフェーズ/ルール/⚠️ を1件ずつ突き合わせ、取りこぼしゼロを数えて確認する
- [x] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/2.md` に記録）
- [x] QA engineer review（subagent）
- [x] user review

**Completion criteria**:

- `hposal/skills/up/SKILL.md` が存在し、`name` と `description` を含む有効な frontmatter を持つ。
- 元 `workflow.md` の4フェーズ・各フェーズの完了条件・全 ⚠️ 落とし穴・★人間ゲートが SKILL.md に
  すべて含まれている（`.rn/hposal-plugin/corporate-site-kit/workflow.md` との項目突き合わせで漏れゼロ）。
- テンプレへの参照が `${CLAUDE_PLUGIN_ROOT}/references/templates/` 配下の実在パスを指している。

### #3: templates を references に配置しスキルから参照させる

**Purpose**: 記入用テンプレ5本を `hposal/references/templates/` に置き、SKILL.md がそこを指すようにする。

**Prerequisites**: #2

**Steps**:

- [x] `templates/` の5本を `hposal/references/templates/` にコピーする（内容は日本語のまま不変）
- [x] SKILL.md のテンプレ参照パスが実在ファイルを指していることを確認する
- [x] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/3.md` に記録）
- [x] QA engineer review（subagent）（機械的タスクのため coordinator 網羅検証で代替）
- [x] user review

**Completion criteria**:

- `hposal/references/templates/` に元の5本（01_requirements / 02_proposal-design / 03_work-breakdown /
  04_proposal / site-inventory）が存在し、内容が元キットと一致している。
- SKILL.md 内のテンプレ参照パスがすべて `hposal/references/templates/` 配下の実在ファイルに解決する。

### #4: プラグインの自前メタ・ドキュメントを書く（plugin.json / CHANGELOG / README）

**Purpose**: `hposal` の名札・変更履歴・人が読む入口を用意する。README は冒頭で一度だけ
「HP（corporate site）」と補い、導入・始め方を `rn` の流儀で書く。

**Prerequisites**: #2, #3

**Steps**:

- [x] `hposal/.claude-plugin/plugin.json` を作成（`name: hposal` / 英語 description / `version: 0.1.0` /
      `author: lovaizu`）
- [x] `hposal/CHANGELOG.md` を Keep a Changelog 形式で作成（`## [Unreleased]` に初期内容）
- [x] `hposal/README.md` を作成（冒頭で一度だけ「HP（corporate site）」、何をするか、marketplace add →
      plugin install、始め方）
- [x] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/4.md` に記録）
- [x] QA engineer review（subagent）
- [x] user review

**Completion criteria**:

- `hposal/.claude-plugin/plugin.json` が `name: hposal`・英語の description・`version: 0.1.0`・
  `author` を持ち、JSON として妥当である。
- `hposal/CHANGELOG.md` が `## [Unreleased]` セクションを持ち、Keep a Changelog 形式に従う。
- `hposal/README.md` の冒頭に「HP（corporate site）」表記がちょうど1回あり、導入手順（marketplace add →
  plugin install）と始め方が記載されている。

### #5: marketplace.json と root README に hposal を登録する

**Purpose**: マーケットの機械マニフェストと人の入口の両方に `hposal` を載せ、同期させる。

**Prerequisites**: #4

**Steps**:

- [x] `.claude-plugin/marketplace.json` の `plugins` に `hposal` エントリを追加
      （`name`/`description`(英語)/`source: ./hposal`/`category`）
- [x] root `README.md` の Plugins 一覧に `hposal`（`./hposal/README.md` へのリンク＋一行説明）を追加
- [x] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/5.md` に記録）
- [x] QA engineer review（subagent）（機械的タスクのため coordinator 網羅検証で代替）
- [x] user review

**Completion criteria**:

- `.claude-plugin/marketplace.json` に `source: ./hposal` を持つ `hposal` エントリが存在し、JSON として
  妥当である。
- root `README.md` の Plugins 一覧に `hposal` が `./hposal/README.md` へのリンク付きで載っている。

### #6: 構造検証とヘッドレス起動確認を通す

**Purpose**: プラグインとマーケットの構造検証、およびスキルのヘッドレス読み込みを確認し、指摘を解消する。

**Prerequisites**: #5

**Steps**:

- [x] `claude plugin validate hposal --strict` を実行し、通るまで直す
- [x] `claude plugin validate .`（マーケットルート）を実行し、通るまで直す
- [x] `claude -p "/hposal:up" --plugin-dir hposal` でスキルが読み込まれることを確認する
- [x] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/6.md` に記録）
- [x] QA engineer review（subagent）（検証タスクのため coordinator 実走で代替）
- [x] user review

**Completion criteria**:

- `claude plugin validate hposal --strict` がエラー・警告なしで完了する。
- `claude plugin validate .` がエラー・警告なしで完了する。
- `claude -p "/hposal:up" --plugin-dir hposal` が、スキルを認識した出力で正常終了する。

### #7: 提案書のスライドHTMLテンプレを用意する（追加スコープ）

**Purpose**: フェーズ4の出力 `04_proposal.html` は「HTMLで作る」方針だけで雛形が無かった。実在の完成 deck
（豆蔵向け `work/04_提案書.html`）を**汎用テンプレ化**し、CSSデザインシステムとスライド構造を引き継ぐ。
ccpm は公開マーケットなので実案件データは持ち込まない（D-4）。

**Prerequisites**: #3

**Steps**:

- [x] 元 deck の CSS（1–374行）をバイト不変で `hposal/references/templates/04_proposal.html` に温存
- [x] 17スライド本体を `{{ }}` プレースホルダ＋見本行＋記入ガイドに汎用化（豆蔵固有データを全除去）
- [x] SKILL.md フェーズ4を HTML テンプレ参照に更新（章立ては 04_proposal.md を併記）
- [x] CHANGELOG `[Unreleased]` に追記
- [x] self-check（CSS原本一致 diff・実データ残留ゼロ grep・PDF 17ページ・代表3ページ目視）

**Completion criteria**:

- `hposal/references/templates/04_proposal.html` が存在し、CSS が元 deck とバイト一致、実案件データ残留ゼロ。
- ヘッドレス Chrome で 16:9・17ページに書き出せ、表紙/画面モック/見積が崩れず描画される。
- SKILL.md フェーズ4が HTML テンプレを骨格として指す。

### #8: 初回実走の事故率を下げる仕上げ（シミュレーション評価由来）

**Purpose**: 全7タスク完了後、AIが `/hposal:up` を実走する想定でシミュレーション評価したところ、出荷を止めはしないが
初回実走で事故りやすい4点が判明。手順書（SKILL.md）と章立て（04_proposal.md）への追記のみで潰す。構造変更なし。

**Prerequisites**: #2, #7

**Steps**:

- [x] A：内部見積前提（単価・ディレクション%・外注税・要員）を着手前に1回で集める節を SKILL に追加。
      未提供は捏造せず q として★へ（捏造単価が下流金額を静かに汚すのを防ぐ）
- [x] B：フェーズ4 export 前に「`{{ }}`／`<!--…例…-->` 残留ゼロ」を grep で機械確認するゲートを追加
      （345プレースホルダの目視取りこぼし→客先PDFへの素抜け防止。`事例`等の正当本文は非マッチで安全）
- [x] C：`04_proposal.md` を正確な対応表に書き換え＋三者ドリフト解消（実物 grep で欠落確認：なぜ私たち=0・チーム=0・連絡=0）
- [x] C2（「やらない理由は？」を受け追加実施）：欠落していた必須/任意3スライドを **HTML骨格に内包**
      （P8 見守り・P10 なぜ私たちか〔⚠️必須〕・P16 連絡先）。既存クラス流用でCSS 1–374行は不変（diff確認）、
      `.pg` を全20ページに採番し直し（前提の P.13→P.15 クロス参照も修正）。ヘッドレスChromeで20ページ・960×540pt(16:9)
      書き出し＋新3ページをPNG目視＝破綻なし。`04_proposal.md`/SKILL⚠️/CHANGELOG を「同梱・記入/削除」に更新
- [x] D：フェーズ1に sitemap 無し／JSレンダリングナビ時のクロール代替（リンク巡回・rendered DOM）を ⚠️ 追加
- [x] CHANGELOG `[Unreleased]` に A–D を追記／`validate hposal --strict`・`validate . --strict` ✔

**Completion criteria**:

- SKILL.md に「Internal estimate inputs」節・フェーズ4の残留 grep ゲート・実績⚠️への骨格欠落注記・
  フェーズ1のクロール代替⚠️ が入っている。
- `04_proposal.md` が17ページ対応表＋欠落必須章セクションを持つ。
- `validate --strict`（plugin/marketplace 両方）が通る。

### #9: dogfood 所見を SKILL.md へ最小追記する（構造変更なし） — DONE through QA

**Purpose**: 実案件 dogfood で見つけた頻出落とし穴を、`hposal/skills/up/SKILL.md` に1行ずつ追記して潰す。
構造（フェーズ・章立て）は変えず、既存のルール/⚠️/完了条件に項目を足すだけ。`dogfood-notes.md` の
反映方針 (i) に対応。

**Prerequisites**: #8

**Steps**:

- [x] Phase 1：標準確認に⑥（301/SEO移行維持＝SC移転をスコープに含めるか）を追加（#1）／移行元が
      サブドメイン型（独自ドメイン非保有）なら301可否・SEO引き継ぎ制約を確認する⚠️（#2）
- [x] Phase 2：toC（個人向け取引・予約・決済）があれば法務ページ群（特商法・プライバシー・キャンセル・
      資格表記）を条件付きで always-include に追加（#3）／見積モデル⚠️に「ノーコード/テンプレ基盤でも
      圧縮できるのは初期デザインのみ。構築・流し込み・付随/法務・移行/301 は別計上」（#7）／契約形態
      （準委任/請負）はAIが決めず q として★へ・デフォルトで請負を置かない⚠️（#8）／工数化の前に採用基盤の
      標準機能で吸収される作業と移行元で実行不能な作業を洗い見積から除外/縮小する「プラットフォーム実態
      ゲート」⚠️（#18）／曖昧な基盤名（"WordPress"等）は見積前に具体形態（.com 管理型／.org 自前サーバ・
      プラン階層）を確定する⚠️（#20）／基盤が複数候補なら共通工数を1回積み基盤分岐だけ案ごとに別建てして
      総額をN本出す（推奨を立てずフラット併記も可）（#19 の SKILL 側）
- [x] Phase 3：完了条件に「明細列の作業見積合計＝役割別集計小計を機械的に突合（再加算で一致確認）」
      ゲートを追加（#9・実証済）／小規模案件は積み上げ後に省略/段階化できる行を★で握る⚠️（#5）
- [x] 横断：トレース節に「現行ページ数（母数＝01）と新サイトのページ数は別。母数を新サイト規模として
      書かない」⚠️（#14）／fill-marker（人間が後で埋める未確定値）は `{{ }}` を使わず `（…）`／`※…記入`
      で書く規約（#15）／「提案書に出さない内部項目」に sourcing 語（内製/外注/外部/二層）を追加（#17）
- [x] CHANGELOG `[Unreleased]` に追記し `validate hposal --strict`・`validate . --strict` 両方
- [x] self-check（追記12点の有無を grep/目視で OK/NG 判定し `.rn/hposal-plugin/checks/9.md` に記録）
- [x] QA engineer review（subagent）＝PASS（13所見すべて忠実・追記のみ・矛盾なし、低重要度メモのみ）

**Completion criteria**:

- SKILL.md に上記12所見（#1・#2・#3・#5・#7・#8・#9・#14・#15・#17・#18・#20＋#19 の SKILL 側）が
  欠落なく追記されている（dogfood-notes.md との項目突き合わせで漏れゼロ）。
- 既存のフェーズ構成・章立て・既存ルールは変わっていない（追記のみ）。
- CHANGELOG `[Unreleased]` に該当行があり、`validate --strict`（plugin/marketplace 両方）が通る。

### #10: 提案書テンプレをパーツ化する（アウトライン＋1パーツ1スライド・中核／D-9） — DONE through QA

**Purpose**: 1044行モノリス（`{{ }}`＋任意スライド削除＋`.pg`手振り）を、**アウトライン＋パーツ**へ作り直す。
dogfood の歪み（複数サイト統合前提・総額1点前提・実現手段の比較層が無い・変種が「削って作り直し」）を、
パーツ選択という**構造**で解消する。1パーツ＝1スライド（種類ごとに変種）。CSS は共有1か所でバイト不変。
最終成果物は今と同じ単一 HTML→PDF。見本の3層比較は private `ikuko-hp/04_proposal.html`（22スライド）を
PII 除去して一般化。`dogfood-notes.md` 反映方針 (ii)＝#4・#10–13・#19・#21 に対応。

**Prerequisites**: #9

**Steps**:

- [x] CSS を共有 head パーツ `references/templates/parts/_head.html` に切り出し（+ `_foot.html`）、
      元モノリス CSS（6–374行）とバイト一致を確認（diff＝OK）
- [x] 既存20スライドを1スライド=1パーツへ分解し `references/templates/parts/` に配置。変種別ファイル：
      現状→目指す姿〔single｜multi〕(#10)／画面〔service-cta｜search-filter｜tree-nav〕(#11)／見積〔total｜range｜compare〕(#12)。
      `work-detail.html`（付録の作業明細）も作成済＝全26パーツ
- [x] 第3層 2列比較パーツを private 22スライド deck から一般化して追加：基盤比較（ニュートラル・推奨マーク
      なし）／作り方(2列)／運用保守(2列)／見積compare（複数額フラット併記）(#19・#21)＝PII除去で作成済
- [x] `04_proposal.md` を**アウトライン＝組み立て仕様**に書き換え：3層の背骨・スロット順・各スロットがどの
      パーツ変種を採るか・層→レイアウト（1–2層=1列／3層=2列比較）・`.pg`は組み立て時採番（#21）
- [x] SKILL.md フェーズ4を「アウトライン順にパーツを選び連結→埋める→export」に更新（#21 の SKILL 側）。
      フェーズ2に #4（基盤未定なら2–3案を同軸＝初期・ランニング・更新主体・拡張性・保守 で比較し★で選ぶ）
- [x] 旧モノリス `04_proposal.html` を削除（パーツが置換）。ソーステンプレ参照は parts/outline へ向け直し済
- [x] #13（`.dense` 表が5–6行超でフッターに被る注記）を両 as-is/to-be パーツに追加（fix round）
- [x] 組み立て検証：代表アウトライン（単一サイト＋2基盤比較）で全パーツ連結→単一 HTML→ヘッドレス Chrome
      16:9 書き出し（20ページ・960×540pt）、新スライド目視・export ゲート（`{{`/`例` 残留0）clean・CSS バイト不変（diff空）
- [x] CHANGELOG `[Unreleased]` に追記し `validate hposal --strict`・`validate . --strict` 両方✔
- [x] self-check（CSS diff・grep・PDF・代表スライド目視・パーツ網羅を OK/NG 判定し `.rn/hposal-plugin/checks/10.md`）
- [x] QA engineer review（subagent）＝PASS-with-notes→2 MED 修正済（#13・CHANGELOG）。再 validate ✔

**Completion criteria**:

- `references/templates/parts/` に 1スライド=1パーツが揃い、dogfood の変種（現状 single/multi・画面 3種・
  見積 total/range/compare・第3層 2列比較）がパーツとして選べる。CSS は共有1か所・元モノリスとバイト一致。
- `04_proposal.md` がアウトライン（3層・スロット順・パーツ変種選択・層→レイアウト・採番）になっている。
- SKILL.md フェーズ4が「パーツを選び連結→埋める→export」を駆動し、フェーズ2に #4 基盤比較が入っている。
- 代表アウトラインで単一 HTML に組み立て→ヘッドレス Chrome 16:9 書き出しが破綻なく、export ゲート clean。
- CHANGELOG `[Unreleased]` に該当行があり、`validate --strict`（plugin/marketplace 両方）が通る。

### #11: ゼロベース dogfood をやり直す（メインエージェントが利用者役） — DONE through QA

**Purpose**: 既存の dogfood 記録を一旦すべて消し、パーツ化後（#10）の hposal を対象に、**メインエージェント自身が
「プラグイン利用者」役**となって `/hposal:up` を頭から実走し、新しい改善所見をゼロベースで集め直す。前回の dogfood は
人間が実案件（private `ikuko-hp`）で回して所見を持ち帰る形だった。今回は AI が利用者役で通すことで、パーツ化テンプレを
直接・バイアスなく検証する。ユーザー指示（2026-06-26）：「ドッグフードを全て削除、ゼロベースで、メインエージェントが利用者役で」。

**Prerequisites**: #10

**Steps**:

- [x] ★ 着手前に2点を会話で確定（fuzzy なので多択でなく対話で）：(a) **削除範囲**＝確定（D-10）：private `ikuko-hp` は
      生ブリーフ `input/ホームページリニューアル要件.md` 以外すべて削除（git 外＝不可逆だが「今の出来では使えず hposal で
      要件から再現可能」とのユーザー判断で完全削除）／公開側 `.rn/hposal-plugin/dogfood-notes.md` も削除。
      (b) **「利用者役」の運用**＝確定（D-10）：二者構成。subagent が `/hposal:up`（＝`hposal/skills/up/SKILL.md`）を起草実走、
      main が利用者/レビュー役で★ゲート・質問に応じる（架空でない実ブリーフだが内部単価等の未提供入力は main が PII なしで供給）。
- [x] 確定した範囲で既存 dogfood 記録を削除する（`ikuko-hp` 下流成果物＋旧 steering、公開側 `dogfood-notes.md`）
- [x] **実ブリーフ**（`ikuko-hp/input/ホームページリニューアル要件.md`）を唯一の入力に、private フォルダで実走（PII 境界＝
      生成物 01–04 は private に留め、公開リポジトリに戻すのは PII を除いた一般化所見のみ）
- [x] メインエージェントが利用者役で `/hposal:up` を phase 1→4 実走する（subagent 起草・main ★レビュー）。各フェーズ★PASS：
      P1 要件15・実URL10機械検証 ／ P2 p1–12・基盤2案比較・WP.com価格は q 保持 ／ P3 32/37人日・機械突合一致 ／
      P4 22pp PDF・ゲート0/0・CSSバイト一致・burn-down15/15・内部値素抜け0
- [x] 実走で見つかった所見を新しい dogfood ノート（一般化・PII なし）に記録する（`dogfood-notes.md`・F1–F14＋T1–T3）
- [x] 所見の plugin 反映方針を整理する（SKILL/テンプレ/パーツ/outline/execution-only に HOW＋優先度でマップ）
- [x] self-check → QA expert review（subagent）＝self-check OK・QA **PASS**
      （trivial 1件 fix 済 `6348c89`）

**Completion criteria**:

- 旧 dogfood 記録が（合意した範囲で）削除されている。
- メインエージェントが利用者役で全フェーズを実走した記録が残っている。
- 新しい所見が PII なしで記録され、plugin への反映方針が整理されている。

### #12: 改善↔dogfood を「安定するまで」反復する（dogfood 反映方針の適用）

**Purpose**: dogfood で検知した所見（#11 の `dogfood-notes.md` 反映方針）を plugin に**適用**し、再び dogfood して
**新たな所見が出なくなる＝安定するまで「改善→dogfood」を繰り返す**。dogfood は「直す対象を検知する手段」であり、検知した
followup を当て→また回す、を収束まで続けるのがこのタスク。ユーザー指示（2026-06-26）：「ドッグフードで検知すること＝その通り。
安定するまで改善とドッグフードを繰り返して。再開後に作業して」。

**Prerequisites**: #11

**Steps**:

- [x] **適用ラウンド1**（Round 1 dogfood の反映方針）：T1＝テンプレ2本（`02_proposal-design.md` に移行標準作業
      チェックリスト＋プラットフォーム実態ゲートの空スロット／`03_work-breakdown.md` に「共通＋基盤分岐＋基盤ごと
      総額」＋役割別突合の空骨格）／T2＝パーツ（`work-detail.common`/`work-detail.branch` ペア新設・
      `estimate.compare` 注記の長さ予算・ページ総数の組み立て時一括置換を outline に文書化）／SKILL の
      F1・F4・F5・F7・F9 のエッジケース追記／outline の F12・F14。CHANGELOG `[Unreleased]` 追記・
      `validate` 両方 ✔（commit `4b5712a`）
- [x] **再 dogfood 1周目**（`dogfood-notes.md` の「Round 2」節）：二者構成・架空案件（学習塾12pp・基盤2案・
      toC リードフォーム・小予算・独自ドメイン+301）で phase 1→3 実走。新所見 G1–G5・H1–H4・J1–J4 を収集
      （commit `b2859c8`）。**Phase 4 は未実走**＝次周に畳む
- [ ] **適用ラウンド2**：`dogfood-notes.md` の「反映方針（apply-round-2 の followup 群）」を当てる。
      とくに **J1＝F8 の未完部分**（03 に役割別突合表は入ったが、SKILL が必須とする移行の責任分担マトリクスが未）。
      CHANGELOG `[Unreleased]` 追記・`validate hposal --strict`／`validate . --strict` 両方
- [ ] **再 dogfood 2周目**：別案件（ユーザー提供・二者構成・main 利用者役・PII なし）で phase 1→4 を
      最後まで実走し、新所見を `dogfood-notes.md` に追記する
- [ ] 「適用→dogfood」を**新所見が軽微に収束するまで反復**する（各周回で `dogfood-notes.md` を更新し、
      何周で何が閉じたかを残す）
- [ ] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/12.md` に記録）
- [ ] QA expert review（subagent）
- [ ] Craft expert review（subagent・writing）
- [ ] Verification expert review（subagent・fact-check）
- [ ] Design expert review（subagent・SKILL/テンプレ/パーツの構造を改訂するため）

**Completion criteria**:

- `dogfood-notes.md` の各周回の所見が、反映先ファイルまで辿れる状態で閉じている（どこにも反映されないまま
  残っている所見がゼロ）。
- 最終周回の dogfood が phase 1→4 を最後まで通り、新所見が軽微のみ（手順・テンプレの**構造**変更を要する所見が
  ゼロ）に収束している。何周で何が閉じたかが `dogfood-notes.md` から読める。
- 反映によるリグレッションが無い：`claude plugin validate hposal --strict` と `claude plugin validate . --strict`
  が通り、Phase 4 の export ゲート（`{{`・見本行の残留ゼロ）が clean、CSS は `parts/_head.html` の1か所のまま
  バイト不変。
- 公開リポジトリ側に PII が無い：`dogfood-notes.md` と `hposal/` 配下に実案件の社名・実額・個人名が残っていない。
- 既存の到達経路が壊れていない：`marketplace.json` と root `README.md` が同期したままで、`/hposal:up` が
  ヘッドレスで起動する。

### #13: 評価サインオフ（Acceptance criteria の実走 → ユーザー承認）

**Purpose**: `steering.md` の Acceptance criteria を最後に通しで実物確認し、その結果をユーザーに提示して
セッションを閉じる。rn の3つの scheduled gate のうち **evaluation gate** にあたるサインオフタスク
（実装/レビューの subagent は立てず、このタスクの Steps 自体がゲート）。

**Prerequisites**: #12

**Steps**:

- [ ] Acceptance criteria を1項目ずつ実物で確認する（`validate --strict` 両方・ヘッドレス起動・ファイル実在・
      言語分岐・marketplace/root README 同期・内容ドリフト有無）。未確認の項目を残さない
- [ ] 実走結果を **PR #8 上**に提示する（`push-and-review` ルール＝レビューはコンソールでなく PR で行う）。
      #9–#12 の成果もこの PR にまとまっているので、ユーザーはここで一度にレビューする
- [ ] ユーザーの verdict を受ける：`/rn:ty`（承認）→ check off、`/rn:gm`（差し戻し）→ 指摘に対応して再提示

**Completion criteria**:

- Acceptance criteria の全項目について OK/NG と根拠が提示されており、未確認の項目がゼロである。
- ユーザーが PR #8 上で承認済みで、未解決の差し戻し指摘が残っていない。

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
