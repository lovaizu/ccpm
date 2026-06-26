# Goal

`corporate-site-kit`（HP＝コーポレートサイトの見積・提案書を作る、日本語の「読み物キット」：README＋
唯一の手順書 `workflow.md`＋記入用 `templates/` 5本）を、Claude Code から `/コマンド` で呼び出せる
プラグイン **`hposal`**（HP proposal）に作り変え、この `ccpm` マーケットプレイスに `rn` と並べて
`/plugin install` で導入できるようにする。

お手本は完成済みの `rn` プラグイン（`rn/` 配下の構成をそのまま型として踏襲する）。キットの中身（手順・
テンプレ）は日本語のまま保ち、マーケット一覧に出る説明文だけ英語にする。着手の前に、元キット一式を本
セッションのステアリングと同じフォルダにベース素材としてコピーしておく（原本は Google Drive にあり、
リポジトリ内に変換のたたき台と「変換前」の比較対象を持つため）。

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
  （2か所に登録）／language.md（成果物は英語既定。「指示があれば別」に従いユーザー接点のみ日本語＝D-5）。

# Assumptions

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

- 1 task = 1 commit
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

### #9: dogfood 所見を SKILL.md へ最小追記する（構造変更なし）

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
- [ ] user review（PR 上で実施＝push-and-review ルール）

**Completion criteria**:

- SKILL.md に上記12所見（#1・#2・#3・#5・#7・#8・#9・#14・#15・#17・#18・#20＋#19 の SKILL 側）が
  欠落なく追記されている（dogfood-notes.md との項目突き合わせで漏れゼロ）。
- 既存のフェーズ構成・章立て・既存ルールは変わっていない（追記のみ）。
- CHANGELOG `[Unreleased]` に該当行があり、`validate --strict`（plugin/marketplace 両方）が通る。

### #10: 提案書テンプレをパーツ化する（アウトライン＋1パーツ1スライド・中核／D-9）

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
- [ ] user review（PR #8）

**Completion criteria**:

- `references/templates/parts/` に 1スライド=1パーツが揃い、dogfood の変種（現状 single/multi・画面 3種・
  見積 total/range/compare・第3層 2列比較）がパーツとして選べる。CSS は共有1か所・元モノリスとバイト一致。
- `04_proposal.md` がアウトライン（3層・スロット順・パーツ変種選択・層→レイアウト・採番）になっている。
- SKILL.md フェーズ4が「パーツを選び連結→埋める→export」を駆動し、フェーズ2に #4 基盤比較が入っている。
- 代表アウトラインで単一 HTML に組み立て→ヘッドレス Chrome 16:9 書き出しが破綻なく、export ゲート clean。
- CHANGELOG `[Unreleased]` に該当行があり、`validate --strict`（plugin/marketplace 両方）が通る。

### #11: ゼロベース dogfood をやり直す（メインエージェントが利用者役）

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
- [ ] self-check → QA engineer review（subagent）→ user review（PR）
      ＝self-check OK・QA **PASS**（trivial 1件 fix 済 `6348c89`）。**残るは PR #8 上の user review のみ**

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

- [ ] 反映方針の **followup 群を plugin に適用**：T1＝テンプレ2本（`02_proposal-design.md` に移行標準作業チェックリスト＋
      プラットフォーム実態ゲートの空スロット／`03_work-breakdown.md` に「共通＋基盤分岐＋基盤ごと総額」＋役割別突合の空骨格）／
      T2＝パーツ（`work-detail.common`/`work-detail.branch` ペア新設・`estimate.compare` 注記の長さ予算・ページ総数の組み立て時
      一括置換を outline に文書化）／SKILL の F1・F4・F5・F7・F9 のエッジケース1–2行追記／outline の F12（title は組み立て fill）・
      F14。CHANGELOG `[Unreleased]` 追記・`validate hposal --strict`／`validate . --strict` 両方
- [ ] 反映後に**再び dogfood**（同じ二者構成・main 利用者役・PII なし・架空/一般化案件で可）を phase 1→4 実走し新所見を集める
- [ ] 「適用→dogfood」を**新所見が出なくなる/軽微に収束＝安定するまで反復**（各周回で `dogfood-notes.md` を更新し、
      何周で何が収束したかを残す）
- [ ] self-check → QA engineer review（subagent）→ user review（PR）

**Completion criteria**:

- 反映方針の followup が plugin（SKILL／テンプレ／パーツ／outline）に適用され、`validate --strict`（plugin/marketplace 両方）が通る。
- 反映後の再 dogfood が実走され、**新所見が安定（出なくなる/軽微のみ）に収束**したことが `dogfood-notes.md` に記録されている。
- 各周回の所見と反映が PII なしで残る。

# Decisions

## D-1: 1スキル `up` で4フェーズ全体を駆動する
- **Issue**: workflow の4フェーズを、1スキルにまとめるか、フェーズごとに別スキル（4コマンド）へ割るか。
  また、その1スキル（コマンド）の名前をどうするか。
- **Conclusion**: 1スキル `/hposal:up` に `workflow.md` 全体を載せる。
- **Rationale**: workflow は ★人間ゲートで区切られた一続きの工程で、前フェーズの文書が次の入力になる
  依存連鎖。独立に呼ぶ4コマンドではなく、上から順に通す1手順として呼ぶのが元キットの使い方に忠実。
  名前は `up`＝「提案を起こす」を表す短い合図。名前空間 `hposal`（HP proposal）が用途を示すので、
  コマンド側は動作の合図で足り、`rn` の `gm`/`bb`/`hi` という短い口語コマンドの流儀に揃う。
  自己説明性の低さは README 冒頭の一文で補う。
- **Evidence**: `workflow.md` は「上から順に進める」一本道。`README.md` も「workflow.md に従って作って」と
  1ファイルを指す。rn が3スキルなのは start/suspend/resume という独立した3場面があるからで、hposal には
  そうした分岐がない。rn のコマンドは `gm`/`bb`/`hi` と短い口語で統一されている。
- **Sources**: 元キット `workflow.md` 1–10行・`README.md` 27行／お手本 `rn/skills/`（`gm`/`bb`/`hi`）／
  ユーザー確認（本セッション：`up`＝「起こす」）。

## D-2: 中身は日本語維持・説明文のみ英語・README で HP を一度補う
- **⚠️ SUPERSEDED by D-5（2026-06-23）**：「キット中身を日本語維持」は撤回。layout は残すが結論は D-5 が正。
- **Issue**: language.md は成果物の既定を英語とするが、本キットは意図的に日本語で書かれている。
- **Conclusion**: SKILL.md・templates は日本語のまま。英語にするのは plugin.json と marketplace.json の
  description のみ。README は冒頭で一度だけ「HP（corporate site）」と補う。
- **Rationale**: キットの中身は日本語クライアント向け提案を日本語でレビューしながら作るための道具で、
  日本語であること自体が機能。一方マーケット一覧の説明文は不特定多数が読むので英語が通りやすい。「HP」は
  和製の語なので、入口（README）で一度だけ国際語の corporate site を添えれば誤解を防げる。
- **Evidence**: `workflow.md` 20行「このキット自体は日本語で書く（人間がレビューできるように）」。
- **Sources**: 元キット `workflow.md` 20行／ユーザー確認（本セッション）／.claude/rules/language.md。

## D-3: 初期 version 0.1.0・タグ/Release はスコープ外
- **Issue**: 新規プラグインの version と、リリース（タグ・GitHub Release）をどこまで本セッションでやるか。
- **Conclusion**: `plugin.json` に `version: 0.1.0` を置く。タグ付けと GitHub Release は別の明示指示で
  行う作業とし、本セッションでは行わない。
- **Rationale**: `--strict` 検証に version は必須なので 0.1.0 を置く。一方 plugin.md は「リリース指示が
  あるときだけ昇格・タグはリリース時」と定めるので、リリース行為は指示を待つ。
- **Evidence**: .claude/rules/plugin.md「Bump only on an explicit release instruction」「Tag each
  release on main」。
- **Sources**: .claude/rules/plugin.md。

## D-4: スライドHTMLは汎用テンプレ化（実案件データを公開リポジトリに持ち込まない）
- **Issue**: 完成 deck（豆蔵 `work/04_提案書.html`）を雛形にする際、(A)汎用テンプレ化／(B)丸ごと見本同梱／
  (C)両方 のどれにするか。ccpm は公開マーケットプレイス。
- **Conclusion**: A。CSSデザインシステムと全スライド構造は引き継ぎ、豆蔵固有の中身（社名・実額¥3,080,000・
  件数・提案者名）は `{{ }}` プレースホルダ＋見本行＋記入ガイドに置換。
- **Rationale**: 再利用資産の本体は CSS とレイアウトで、中身は案件固有。B/C は実在クライアントの見積・社名を
  公開リポジトリに残すため不採用。A なら設計資産を完全継承しつつ実データ流出を避けられる。
- **Evidence**: 元 deck の CSS は実データを含まず（コメントも汎用）、温存してバイト一致を確認。
- **Sources**: 元 deck `work/04_提案書.html`／ユーザー確認（本セッション：A を選択）／.claude/rules/marketplace.md。

## D-5: 言語はルール通り＝成果物（道具）は英語・ユーザー接点は日本語（D-2 を撤回）
- **⚠️ SUPERSEDED by D-6（2026-06-23）**：軸が「道具 vs ユーザー接点」では粗い。正しい軸は「プラグインの読者層が
  日本に限定されるか」。hposal は限定されるので、利用者が読む README・テンプレ本文も日本語が正。結論は D-6。
- **Issue**: 「全部日本語」は中途半端。language.md（成果物は英語既定・指示があれば別）をどう正しく適用するか。
- **Conclusion**: お手本 `rn`（SKILL.md も README も英語）に揃え、**道具＝英語／ユーザー接点＝日本語**。
  英語：SKILL.md・テンプレ本文（01-03・site-inventory・04_proposal.md）・README・plugin.json・
  marketplace.json・CHANGELOG・`04_proposal.html` のコメント/使い方ヘッダ。日本語：`04_proposal.html`
  のクライアント可視コピー＋`{{}}`（提出物そのもの）と、実行時に生成する中間文書・コンソール会話。
- **Rationale**: language.md の狙い（広い読者・AI学習量）は「道具」で効く。日本語であるべきは人が読む出力＝
  クライアント提出物とレビュー会話だけ。AI向け作業指示は英語の方が安定し、language.md「指示があれば別」に
  も合致。`rn` の steering（英語見出し＋日本語中身）と同じ層分け。
- **Evidence**: `rn/skills/gm/SKILL.md`・`rn/README.md` が英語。CSS（1–374行）は実データを含まず原本
  バイト一致のまま温存。本セッションで英語化後、⚠️ 26/26・フェーズ4・★ゲート保持を実数検証。
- **Sources**: .claude/rules/language.md／お手本 `rn`／ユーザー確認（本セッション：「ルール通り」）。

## D-6: 言語はプラグインの読者層で分岐＝hposal は日本限定なので利用者が読む成果物は日本語（D-5 を撤回）
- **Issue**: D-5 は README・テンプレ本文まで英語化した。だが hposal の利用者は「日本語クライアント向け提案を作る
  日本語話者」に限定される。README を読み・テンプレを記入するその人が日本語話者なら、英語化はコストを上げるだけで
  到達は広がらない。正しい軸は「道具 vs ユーザー接点」ではなく「**プラグインの読者層が一言語に限定されるか**」。
- **Conclusion**: language.md の例外に従い、**利用者が読む成果物は日本語**にする。
  - 日本語：`hposal/README.md`／`references/templates/` のテンプレ本文（01_requirements・02_proposal-design・
    03_work-breakdown・04_proposal.md・site-inventory）／`04_proposal.html` の記入ガイド・コメント＋クライアント
    可視コピー＋`{{}}`（提出物そのもの）／実行時生成の中間文書・コンソール会話。
  - 英語のまま：`SKILL.md`（AI向け作業指示）／`plugin.json`・`marketplace.json` とその description／`CHANGELOG.md`／
    root `README.md` のプラグイン一覧行／コミット・PR 文。
- **Rationale**: hposal は日本語クライアント向け提案でのみ意味を持つ＝利用者は日本に限定される（読者層の確定）。
  language.md の「読者が一言語に限定されるプラグインは、その利用者が読む成果物をその言語で書く」例外がそのまま当てはまる。
  AI向けプロンプトと機械/マーケット向けメタは広い読者を保つので英語のまま。
- **Audience decision（要・作成前確認）**: hposal の読者層＝**日本限定**（2026-06-23 ユーザー確認済）。今後の
  プラグインは作成前にこの読者層を確定し、ここに明示する（language.md の手続き規定）。
- **Evidence**: ユーザー指示（2026-06-23：「今回のプラグインは利用者が読む成果物は日本語、rn とかは利用者を日本に
  限定してない」）。英語化前の日本語原本が `.rn/hposal-plugin/corporate-site-kit/templates/` に現存し復元の土台になる。
- **Sources**: .claude/rules/language.md（本セッションで追記した例外節）／ユーザー確認（本セッション）。

## D-9: 04 提案書テンプレはモノリスでなく「アウトライン＋パーツ（1パーツ1スライド）」にする
- **Issue**: 元の `04_proposal.html` は CSS＋20スライドを1ファイルに詰めた 1044行モノリスで、運用は
  「`{{ }}` を埋める／要らない任意スライドを削る／`.pg` を手で振り直す」。だが dogfood で、各スライドには
  本物の変種があり（現状＝単一/複数統合・画面＝サービスCTA/絞り込み検索・見積＝総額/レンジ/複数額比較）、
  実現手段に分岐がある案件では比較が“層”として複数スライドにまたがる（#21）。モノリスはこれを
  「1枚だけ同梱・残りは削って手で作り直し」「比較は手で2列化」にしてしまい、これが #10–13・#19・#21 の摩擦の正体。
- **Conclusion**: テンプレを**アウトライン＋パーツ**に分解する。**1パーツ＝1スライド**（種類ごとに変種ファイル）。
  `04_proposal.md` を「3層の背骨・スロット順・各スロットが採るパーツ変種・層→レイアウト（1–2層=1列／3層=2列比較）・
  `.pg` は組み立て時採番」を定める**アウトライン＝組み立て仕様**にする。CSS は共有 head パーツ1か所（バイト不変）。
  SKILL フェーズ4は「アウトライン順にパーツを選び連結→埋める→export」を駆動。最終成果物は今と同じ単一 HTML→PDF。
- **Rationale**: 変種を「選択（合成）」に変えることで、削除・手作り直し・採番ズレ・2列化手術が消える＝性質を
  **ルールでなく構造で担保**できる（[[structure-not-rules]]）。比較を“層”で通す #21 は「第3層スロットに2列比較
  パーツを採る」だけになる。トレードオフ＝組み立て（連結）の一手が増えるが、CSS を共有 head に1回・本体を断片で
  連結すれば最終 HTML は今と同一・ヘッドレス Chrome の1ファイル印刷もそのまま・CSS バイト不変も保てる。AI が回す
  前提なら連結は苦にならない。
- **Granularity decision（ユーザー確認）**: 1パーツ＝1スライド（2026-06-26 確認済）。ブロック単位（価値カード・
  比較行）まで割らない＝アウトラインがスライド列に素直に対応し、proposal deck にこの粒度が合うため。
- **Evidence**: dogfood-notes #10/#11/#12/#19/#21。第3層 2列比較の実装見本＝private `ikuko-hp/04_proposal.html`
  （22スライド3層デッキ）。元モノリス CSS 1–376行は実データを含まず、共有パーツへバイト一致で温存できる。
- **Sources**: dogfood-notes.md（#10–13・#19・#21）／private `ikuko-hp/04_proposal.html`／ユーザー確認（本セッション 2026-06-26）。

## D-10: ゼロベース dogfood は実ブリーフ起点・二者構成（subagent 起草／main 利用者役）で回す
- **Issue**: task #11 の★ゲート2点 — (a) 何を削除して何を起点にするか、(b)「メインエージェントが利用者役」をどう運用するか。
  当初案は「PII なしの架空案件をゼロベースで用意」だったが、ユーザーは実案件のブリーフを起点にすると判断。
- **Conclusion**:
  - **(a) 起点＝実ブリーフ**：private `ikuko-hp/input/ホームページリニューアル要件.md`（施主の生要件）だけを残し、前回 dogfood の
    下流成果物（01–04・inventory・書き出し・旧 `.rn` steering）と公開側 `dogfood-notes.md` を削除。生成物は hposal が要件から
    いつでも再現できる前提なので完全削除でよい（git 外＝不可逆を承知の上）。
  - **(b) 二者構成**：subagent が `/hposal:up`（＝`hposal/skills/up/SKILL.md`）を起草実走し、★ゲート/質問で main に返す。main は
    利用者/レビュー役として質問に答え（内部単価など未提供入力は PII なしの仮値を供給）、ドラフトを批判的にレビューし承認/差し戻す。
- **Rationale**: (a) dogfood の目的は「生ブリーフ1枚→完成提案を `/hposal:up` が導けるか」の検証。実ブリーフの方が架空より現実の歪みを
  あぶり出す。再現性向上を何度も dogfood して積む狙いにも、実案件起点が合う。(b)「利用者役」の素直な実装は main＝人間（レビュー）側・
  起草 AI は別エージェント。★ゲートと質問機構＝AI↔利用者のやり取りを実際に動かして初めて「AI が訊くべきを訊いたか／ゲートが分かるか」を
  測れる。main 単独の自己起草・自己承認では独立チェックが効かない。
- **PII 境界**: 実走は private フォルダで行い生成物 01–04 は private に留める。公開リポジトリ（ccpm）に戻すのは PII を除いた一般化所見の
  新 `dogfood-notes.md` のみ。
- **Evidence**: ユーザー指示（2026-06-26）「今の出来では使えないので消して大丈夫／hposal があればいつでも再現できる、そのために
  プラグインを作っている／これから何度も dogfood して再現性を高める」「利用者役は案1（二者構成）」。
- **Sources**: ユーザー確認（本セッション 2026-06-26）／task-workflow.md（coordinator＝main／implementation expert＝subagent）。

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**:
- **Last completed**:
- **Next**:
- **Notes**:
