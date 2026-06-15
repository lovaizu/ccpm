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

- キットの中身（SKILL.md・templates）は日本語のまま。英語にするのは plugin.json の description と
  marketplace.json の description（マーケットの並びに合わせる）だけ。
- `claude plugin validate hposal --strict` と `claude plugin validate .`（マーケットルート）の両方が
  通る。
- ヘッドレス確認 `claude -p "/hposal:<name>" --plugin-dir hposal` でスキルが読み込まれて起動する。
- 内容ドリフトがない：変換後のスキル/テンプレが元キットの意図と一致し、ルールの取りこぼしや、参照の
  受け渡し点に挿入された要約が無い（`.rn/hposal-plugin/` のベースコピーと差分照合できる）。
- リポジトリのルールに沿う：plugin.md（version は plugin.json のみ・CHANGELOG を置く）／marketplace.md
  （2か所に登録）／language.md（成果物は英語既定。ただしキット中身は方針として日本語を維持）。

# Assumptions

- 〔事実・確認済〕元キット＝`README.md`＋`workflow.md`（128行）＋`templates/` 5本、すべて日本語。
- 〔事実・確認済〕`rn` がプラグインの型：`.claude-plugin/plugin.json`／`skills/<name>/SKILL.md`／
  `references/`／`README.md`／`CHANGELOG.md`。`skills/<フォルダ名>` がコマンド名になる。
- 〔事実・確認済〕現状 `marketplace.json` と root `README.md` は `rn` のみを載せている。
- 〔事実・確認済〕Google Drive 上の元キットパスは読み取り可能（コピー可能）。
- 〔事実・ユーザー確認済〕名前は `hposal`。中身は日本語維持、説明文は英語。README 冒頭で一度だけ
  「HP（corporate site）」と補う。
- 〔判断・要レビュー〕1スキルで4フェーズ全体を駆動する（フェーズごとに別スキルへ割らない）。workflow は
  ★ゲートで区切られた一続きの工程だから（D-1）。
- 〔判断・要レビュー〕スキル名＝コマンド名は `up`（`/hposal:up`）。「提案を起こす」を表す短い合図で、
  `rn` の `gm`/`bb`/`hi` の流儀に揃える（D-1）。
- 〔判断・方針〕初期 version は `0.1.0`。タグ付け／GitHub Release は別の明示指示で行う作業で、本セッションの
  スコープ外（D-3、plugin.md の「リリース指示があるときだけ昇格」に従う）。

# Rules

- 1 task = 1 commit
- キット中身（workflow→SKILL.md、templates）は日本語のまま。英語にするのは plugin.json と
  marketplace.json の description のみ。
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

- [ ] Google Drive の `corporate-site-kit`（README.md / workflow.md / templates/ 5本）を
      `.rn/hposal-plugin/corporate-site-kit/` に再帰コピーする
- [ ] コピー後のファイル数・相対構成が元と一致することを確認する
- [ ] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/1.md` に記録）
- [ ] QA engineer review（subagent）
- [ ] user review

**Completion criteria**:

- `.rn/hposal-plugin/corporate-site-kit/` に `README.md`・`workflow.md`・`templates/` の5本が存在する。
- コピー先の各ファイルの内容が Google Drive 上の原本とバイト一致している。

### #2: workflow.md をスキル `hposal/skills/up/SKILL.md` に変換する

**Purpose**: 唯一の手順書 `workflow.md` を、frontmatter を備え `${CLAUDE_PLUGIN_ROOT}/references/` を指す
正しい SKILL.md に作り変える。フェーズ・ルール・⚠️・★ゲートは欠落なく保つ。

**Prerequisites**: #1

**Steps**:

- [ ] `hposal/skills/up/SKILL.md` を作成し、`name: up` と description を持つ frontmatter を付ける
- [ ] `workflow.md` の本文（4フェーズ・共通ルール・たどれるようにする・全 ⚠️・★ゲート）を本体に移し、
      テンプレ参照箇所を `${CLAUDE_PLUGIN_ROOT}/references/templates/...` の実パスに置き換える
- [ ] 元 `workflow.md` のフェーズ/ルール/⚠️ を1件ずつ突き合わせ、取りこぼしゼロを数えて確認する
- [ ] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/2.md` に記録）
- [ ] QA engineer review（subagent）
- [ ] user review

**Completion criteria**:

- `hposal/skills/up/SKILL.md` が存在し、`name` と `description` を含む有効な frontmatter を持つ。
- 元 `workflow.md` の4フェーズ・各フェーズの完了条件・全 ⚠️ 落とし穴・★人間ゲートが SKILL.md に
  すべて含まれている（`.rn/hposal-plugin/corporate-site-kit/workflow.md` との項目突き合わせで漏れゼロ）。
- テンプレへの参照が `${CLAUDE_PLUGIN_ROOT}/references/templates/` 配下の実在パスを指している。

### #3: templates を references に配置しスキルから参照させる

**Purpose**: 記入用テンプレ5本を `hposal/references/templates/` に置き、SKILL.md がそこを指すようにする。

**Prerequisites**: #2

**Steps**:

- [ ] `templates/` の5本を `hposal/references/templates/` にコピーする（内容は日本語のまま不変）
- [ ] SKILL.md のテンプレ参照パスが実在ファイルを指していることを確認する
- [ ] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/3.md` に記録）
- [ ] QA engineer review（subagent）
- [ ] user review

**Completion criteria**:

- `hposal/references/templates/` に元の5本（01_requirements / 02_proposal-design / 03_work-breakdown /
  04_proposal / site-inventory）が存在し、内容が元キットと一致している。
- SKILL.md 内のテンプレ参照パスがすべて `hposal/references/templates/` 配下の実在ファイルに解決する。

### #4: プラグインの自前メタ・ドキュメントを書く（plugin.json / CHANGELOG / README）

**Purpose**: `hposal` の名札・変更履歴・人が読む入口を用意する。README は冒頭で一度だけ
「HP（corporate site）」と補い、導入・始め方を `rn` の流儀で書く。

**Prerequisites**: #2, #3

**Steps**:

- [ ] `hposal/.claude-plugin/plugin.json` を作成（`name: hposal` / 英語 description / `version: 0.1.0` /
      `author: lovaizu`）
- [ ] `hposal/CHANGELOG.md` を Keep a Changelog 形式で作成（`## [Unreleased]` に初期内容）
- [ ] `hposal/README.md` を作成（冒頭で一度だけ「HP（corporate site）」、何をするか、marketplace add →
      plugin install、始め方）
- [ ] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/4.md` に記録）
- [ ] QA engineer review（subagent）
- [ ] user review

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

- [ ] `.claude-plugin/marketplace.json` の `plugins` に `hposal` エントリを追加
      （`name`/`description`(英語)/`source: ./hposal`/`category`）
- [ ] root `README.md` の Plugins 一覧に `hposal`（`./hposal/README.md` へのリンク＋一行説明）を追加
- [ ] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/5.md` に記録）
- [ ] QA engineer review（subagent）
- [ ] user review

**Completion criteria**:

- `.claude-plugin/marketplace.json` に `source: ./hposal` を持つ `hposal` エントリが存在し、JSON として
  妥当である。
- root `README.md` の Plugins 一覧に `hposal` が `./hposal/README.md` へのリンク付きで載っている。

### #6: 構造検証とヘッドレス起動確認を通す

**Purpose**: プラグインとマーケットの構造検証、およびスキルのヘッドレス読み込みを確認し、指摘を解消する。

**Prerequisites**: #5

**Steps**:

- [ ] `claude plugin validate hposal --strict` を実行し、通るまで直す
- [ ] `claude plugin validate .`（マーケットルート）を実行し、通るまで直す
- [ ] `claude -p "/hposal:up" --plugin-dir hposal` でスキルが読み込まれることを確認する
- [ ] self-check（各完了基準を OK/NG で判定し `.rn/hposal-plugin/checks/6.md` に記録）
- [ ] QA engineer review（subagent）
- [ ] user review

**Completion criteria**:

- `claude plugin validate hposal --strict` がエラー・警告なしで完了する。
- `claude plugin validate .` がエラー・警告なしで完了する。
- `claude -p "/hposal:up" --plugin-dir hposal` が、スキルを認識した出力で正常終了する。

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

# State

(written by /rn:bb, read and reset to this placeholder by /rn:hi)
