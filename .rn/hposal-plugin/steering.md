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

# State

- **Status**: paused（task #8 仕上げを反映・push 済）
- **Date**: 2026-06-23
- **Last completed**: **task #8**（シミュレーション評価由来の仕上げ）を SKILL.md・`04_proposal.md`・`04_proposal.html`・CHANGELOG に反映。
  A=内部見積前提インテイク節／B=フェーズ4 export 前の `{{ }}`・`例` 残留 grep ゲート／C=`04_proposal.md` 対応表書き換え＋三者ドリフト解消／
  D=フェーズ1クロール代替⚠️。**C2（「やらない理由は？」を受け実施）**：欠落していた必須/任意3スライドを HTML骨格に内包（P8見守り・
  P10なぜ私たちか〔必須〕・P16連絡先）、CSS 1–374行不変・全20ページ採番・16:9で20ページ書き出し＋新3ページPNG目視✔。
  `validate hposal --strict`・`validate . --strict` ✔。
  〔前セッションまで〕言語方針を **D-6** に再決定し反映・push（02636e3 まで）。読者層で分岐するルールを
  `.claude/rules/language.md` に追記（Japan限定プラグインは利用者向け成果物を当該言語で・作成前に確認しsteeringへ明示）。
  hposal＝日本限定として README＋テンプレ5本を日本語化、`04_proposal.html` のコメント/ヘッダは 74c006a・c835814 を
  revert して原本日本語を復元。SKILL.md・メタは英語維持。`validate --strict` ✔・全層の言語振り分け網羅確認✔。
  〔前セッションまで〕本体7タスク＋(1) D-5 で道具を英語化（D-6 が撤回）(2) 出力先/再開モデル追加・SKILL 一本化。
- **Next**: ユーザーの分岐選択待ち — **(A)** PR #8 をレビュー・マージ、または **(B)** リリース
  （D-3：CHANGELOG `[Unreleased]`→`## [0.1.0] - YYYY-MM-DD`・`plugin.json` の version 据え置き 0.1.0・
  `hposal-v0.1.0` 注釈タグを main に・CHANGELOG 該当節を notes に GitHub Release 公開）。
- **Notes**:
  - 言語の最終形（**D-6**・hposal＝日本限定）：日本語＝README／references テンプレ本文5本（01-03・
    site-inventory・04_proposal.md）／`04_proposal.html` の使い方ヘッダ＋記入ガイドコメント＋クライアント
    可視コピー＋`{{}}`（提出物）／実行時生成物・コンソール会話。英語＝SKILL.md／plugin.json・
    marketplace.json・CHANGELOG／root README 一覧行。CSS（1–374行）は原本バイト一致のまま不変。
  - D-6 反映の実走確認：利用者向け6ファイルの先頭=日本語・AI/メタ=英語を網羅チェック✔／html の英語ガイド
    コメント残留ゼロ（grep）／`validate hposal --strict` ✔。html コメント/ヘッダは 74c006a・c835814 を revert
    して原本日本語を正確復元（SKILL.md は英語のまま参照リテラルだけ `<!-- 例 -->` に戻る）。
  - 英語化のドリフトゼロ検証（本セッション実走）：⚠️ 26/26・フェーズ4・完了条件4・★ゲート保持／
    `validate hposal --strict` ✔・`validate . --strict` ✔／.md・.json の散文日本語ゼロ（SKILL の `<!-- e.g. … -->`
    参照のみ）／可視コピー保持（grep 34件）／`04.html` 差分はコメント＋ヘッダのみ（≥379行・CSS無改変）。
  - CHANGELOG `[Unreleased]` に追加挙動（出力先・再開）を1行追記済み。提案書テンプレ追加分も同 `[Unreleased]`。
  - D-2 は D-5 にスーパーシード（「中身は日本語維持」を撤回）。Acceptance/Rules/Assumptions の該当行も更新済み。
  - PR #8（OPEN・レビュー未着手）に全コミット push 済み。未 push なし（task #8 の 92e899b・8cebd66 含む）。
  - 〔本セッション〕シミュレーション評価で初回実走の事故ポイント4点を特定→task #8 で対処：A 内部見積前提の前倒し収集
    （単価等は捏造せず q）／B フェーズ4 export 前に `{{ }}`・`<!--…例…-->` 残留ゼロを grep ゲート／C 対応表整合＋
    D-クロール代替⚠️／C2 欠落必須スライドを HTML骨格に内包。`04_proposal.html` は **20ページ**（P8見守り〔任意〕・
    P10なぜ私たちか〔必須〕・P16連絡先〔任意〕を追加）。CSS 1–374行はバイト不変のまま（diff確認）。16:9・20ページ書き出し＋
    新3ページPNG目視で破綻なしを実走確認。残課題なし＝次は当初の分岐（PR #8 レビュー or リリース）。
  - 元キットのローカルパス＝`/Users/kiyo/Library/CloudStorage/GoogleDrive-kiyohito.itoh@gmail.com/
    マイドライブ/mz/【豆蔵様】HPリニューアル/mz-hp/corporate-site-kit`。元 deck＝同 `…/mz-hp/work/04_提案書.html`。
  - 〔dogfood 作業フォルダ〕`/Users/kiyo/work/private/ikuko-hp/`（公開リポジトリ外・PII を含むため成果物本体は持ち込まない）。
    `01_requirements.md`・`02_proposal-design.md`・`inventory/`・`input/`（hposal の「作業フォルダ直下」仕様）と、
    その提案書セッションを包む rn ステアリング（slug=`ikuko-hp`）が rn 規約どおり
    `/Users/kiyo/work/private/ikuko-hp/.rn/ikuko-hp/steering.md` に在る。
    phase 2 ★承認済み → **phase 3（作業リスト）から再開**。dogfood で得た plugin 改善メモは一般化（PII 無し）して
    `.rn/hposal-plugin/dogfood-notes.md` に持ち帰る。次の resume はこのパスを辿れば private 側ステアリングで続きが分かる。
