Rn version: 0.8.0
Design: .rn/webplan/design.md

# Goal

Web サイト（HP／LP）制作の**計画ツール**を Claude Code プラグインとして作り、この `ccpm` マーケットプレイスから
`/plugin install` できるようにする。計画＝「決めごと（Base／Scope／Level・進め方の上限・コンテンツの担当・体制・
契約形態…）を一つずつ人と決め、決定が揃ったら提案書＋タスク一覧に畳む」こと。提案書とタスク一覧はその出力であって目的ではない。

作り方は **learn-by-doing**。先に仮の案件（公開されている技術ブログを題材に、提案者が勝手に提案を考えてみる）を
プラグイン抜きで手で最後まで進め、その作業記録から学びをため、たまった学びを再現できる形でプラグインに設計 → 実装 →
dogfood する。旧 `hposal`（v1）とその派生物は削除した（コミット履歴からも除去）。残すのは案件の生の入力（ブリーフ・
提案者の回答・サイト実測・競合の複製）だけで、決定はすべて #1 で新たに下す。

# Acceptance criteria

利用者＝Web サイト制作の提案者（Provider）。場面＝案件の相談を受けてから提案書とタスク一覧を出すまで。基準は利用者が
得るベネフィットで書き、作り方・成果物の形には依存しない。各項目の「確認」は検証の手段であって基準ではない。

1. **何を決めればよいか迷わない** — 決めるべき事項が最初から全部見えていて、順に決めていけば漏れなく揃う。
   - 確認：#1 とは別の案件で最後まで進め、途中で「決め忘れ」に気づいて戻ることが起きない。手順の外で人が補った
     決定が無い。
2. **決定が揃えば提案書とタスク一覧が出る** — 決めた内容以外を書く作業が無く、提案書・タスク一覧・決定の間に食い違いが無い。
   - 確認：決定の一覧と提案書・見積を突き合わせ、提案書にしか無い事項／決定にしか無い事項がゼロ。
3. **見積に根拠がある** — 決定と定数から誰がやっても同じ額になり、施主に説明できる。
   - 確認：決定と定数だけを渡した第三者（subagent）が見積を再導出して額が一致する。どの額も「どの決定から来たか」
     が答えられる。
4. **どの案件でも同じ手順で使える** — 別の案件・別の人でも、同じ順序で同じ水準の提案に至る。
   - 確認：#1 の案件と #4 の別案件で、決定の順序と提案書の構成が同じ。`ccpm` から install して起動でき、
     手順を知らない人（subagent）が起動だけで最後まで進める。
5. **安心して出せる** — 非公開情報が外に出ず、成果物のミスは人が目視する前に機械的に捕まる。
   - 確認：push される範囲に案件の非公開情報が無い。提案書・見積の既知のミス類型（残留プレースホルダ・参照切れ・
     見積の不一致）が、人のレビューより前に検出される。

# Assumptions

（`D-n` は本セッションの決定。実体は `design.md`。）

- 〔事実・確認済〕リポジトリ `lovaizu/ccpm` は PUBLIC。案件の作業場所 `.rn/webplan/project/` は `.gitignore` で除外済み。
- 〔事実・確認済〕仮案件の題材は公開サイト（技術ブログ）・公開ソース・公開求人。内部値（単価・進行管理率・稼働率）は
  架空の仮値。施主の発言・実案件の日程は非公開なので `project/` から出さない。
- 〔事実・確認済〕v1（hposal）の資産と、案件フォルダの派生物（要件整理・提案整理・見積・提案書・ゲート質問・所見）は
  2026-09-06 に削除した。AI は手元にあるものを読んでしまうので、「読まない」約束ではなく物理的に無くして防ぐ。
- 〔判断・D-1〕learn-by-doing：案件実走 → 設計 → 実装 → dogfood の順。案件とスキル作成を並行しない。
- 〔判断・D-2〕読者層＝日本限定（v1 の D-6 を引き継ぐ）。
- 〔判断・D-3〕語彙（Base／Scope／Level・工程・上限・ロール）は #1 の案件で試し、#2 で確定する。
- 〔判断・D-4〕プラグイン名は #2 で決める（`hposal` は HP 限定に読めるため使わない）。作業 slug は `webplan`。

# Rules

- 変更のたびに commit & push する。完了マーカー（`complete task #{id}`）は1タスクにつき1つ。
- `.rn/webplan/project/` は push しない（`.gitignore`）。学びは `learnings.md` に一般化してから置く。
- 言語は D-2：利用者が読む成果物＝日本語、SKILL.md／plugin.json／marketplace.json／CHANGELOG／root README 一覧行／
  コミット・PR＝英語。
- version は `plugin.json` の1か所だけ。`marketplace.json` と root `README.md` は同じ変更内で同期させる。

# Tasks

### #1: 仮案件を手で最後まで進め、作業記録と学びを残す

**Purpose**: `.rn/webplan/project/` の仮案件（技術ブログのリデザイン提案）を、プラグイン抜きで今回揃えた概念
（Project overview、Base／Scope／Level、Direction 2 案 → Refinement revision 2 回 → Rollout、Content の担当表、
工程とロール）で提案書とタスク一覧まで仕上げる。作業のたびに `project/worklog.md` へ〔決めたこと／順序／入力／成果物／
詰まった点〕を追記し、最後に一般化して `.rn/webplan/learnings.md` にする。

**Prerequisites**: none

**Steps**:

- [x] 最終成果物を合意する（何を・どんな形で出すか）→ D-5
- [x] 逆算：最終成果物に「決まっていないと書けない決定」を洗い出し、各決定の入力元と依存順＝進め方を合意する → D-5
- [x] 決定を 1 つずつ素の対話で決め、`project/worklog.md` に〔決めたこと／順序／入力／成果物／詰まった点〕を記録する（方針転換：判断はアウトラインと方針のみ、AI が全見出しを起案し計画を通しレビュー）
- [ ] 決定が揃ったら提案書とタスク一覧に畳む → ユーザーレビュー → 修正 → 納品形
- [ ] `worklog.md` を一般化して `.rn/webplan/learnings.md` に書く：〔決定の一覧と順序／各決定の入力と出力／
      v1 に足りなかったもの／v1 から引き継ぐもの〕。社名・実額・個人名・他社著作物の複製を含めない
- [ ] self-check（各完了基準を OK/NG で判定し `.rn/webplan/checks/1.md` に記録）
- [ ] QA expert review（subagent・`learnings.md` が worklog を忠実に一般化しているか）
- [ ] Craft expert review（subagent・writing）
- [ ] Verification expert review（subagent・fact-check）

**Completion criteria**:

- 提案者として、仮案件で「決めごとを決める → 提案書＋タスク一覧に畳む」を自分の手で最後まで経験し、提案書とタスク一覧が施主に
  出せる状態に達している（ユーザーが納品形として認める）。
- #2 で設計に着手できる入力が揃っている：決めた順序・各決定の入力と出力・詰まった点が、別案件でなぞれる粒度で
  言語化されている（`learnings.md`）。
- 非公開情報（社名・実額・個人名・他社著作物の複製）が push 範囲に出ていない。

### #2: v2 を設計する（名前・フロー・語彙・design.md）＝ Design sign-off

**Purpose**: `learnings.md` を入力に、プラグインの名前・フロー・語彙・v1 から引き継ぐ資産・
機械検査の同梱方針・Acceptance criteria の確定版を `design.md` に書き、ユーザーの設計サインオフを受ける。

**Prerequisites**: #1

**Steps**:

- [ ] `learnings.md` から設計入力を一覧にする
- [ ] 名前を 2〜3 案出し、ユーザーと会話で 1 つに決める（D-4）
- [ ] `design.md` を書く（背景 → ペイン → ベネフィット → UX → 構造 → 部品の順。決定 D-n を追加）
- [ ] steering の Acceptance criteria を確定版に更新し、#3／#4 の Steps を具体化する
- [ ] ★ Design sign-off：PR 上で `design.md` を提示し、`/rn:ty`（承認）／`/rn:gm`（差し戻し）を受ける

**Completion criteria**:

- 設計を読めば、Acceptance criteria の 5 つのベネフィットがそれぞれどの仕組みで実現されるか分かる（宙に浮いた
  ベネフィットが無い）。
- #1 で経験した決定の順序と入出力が、設計のフローとして再現されている。
- ユーザーが PR 上で設計を承認済み。

### #3: v2 を実装する

**Purpose**: #2 の設計どおりに新プラグインを作り（SKILL・テンプレ・パーツ・検査スクリプト・README・CHANGELOG・
plugin.json）、marketplace と root README に登録し、`validate --strict` とヘッドレス起動を通す。

**Prerequisites**: #2

**Steps**:

- [ ] （#2 で具体化する）
- [ ] self-check（`.rn/webplan/checks/3.md`）
- [ ] QA expert review（subagent）
- [ ] Craft expert review（subagent・writing）
- [ ] Verification expert review（subagent・fact-check）
- [ ] Design expert review（subagent）

**Completion criteria**:

- `ccpm` から install した状態で提案者がスキルを起動し、設計どおりの順で決めごとを進めて提案書とタスク一覧に到達できる
  （1 案件で最後まで通る）。
- #2 で各ベネフィットに割り当てた仕組みがすべて動いている（未実装・動かない仕組みが無い）。

### #4: v2 を dogfood する（別案件・二者構成・収束まで）

**Purpose**: v2 を #1 とは別の案件で subagent 起草／main 利用者役の二者構成で最後まで通し、所見の適用 → 再 dogfood を
新所見が軽微に収束するまで繰り返す。

**Prerequisites**: #3

**Steps**:

- [ ] （#2 で具体化する）
- [ ] self-check（`.rn/webplan/checks/4.md`）
- [ ] QA expert review（subagent）

**Completion criteria**:

- #1 とは別の案件で、Acceptance criteria の 5 項目の「確認」がすべて OK になっている（決め忘れによる後戻りが無い・
  決定と提案書・見積に食い違いが無い・見積が再導出で一致する・手順を知らない役が起動だけで最後まで進める・
  既知のミス類型が人より前に検出される）。
- 最終周回の新所見が軽微のみで、何周で何が閉じたかが記録から読める。

### #5: 評価サインオフ（Acceptance criteria の実走 → ユーザー承認）

**Purpose**: Acceptance criteria を最後に通しで実物確認し、結果を PR 上でユーザーに提示してセッションを閉じる
（evaluation gate。subagent は立てず、このタスクの Steps がゲート）。

**Prerequisites**: #4

**Steps**:

- [ ] Acceptance criteria を1項目ずつ実物で確認する。未確認の項目を残さない
- [ ] 実走結果を PR 上に提示する
- [ ] ユーザーの verdict を受ける：`/rn:ty`（承認）→ check off、`/rn:gm`（差し戻し）→ 対応して再提示

**Completion criteria**:

- Acceptance criteria の 5 項目すべてについて OK/NG と根拠が提示されており、未確認の項目がゼロである。
- ユーザーが PR 上で承認済みで、未解決の差し戻し指摘が残っていない。

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: paused
- **Date**: 2026-09-08
- **Last completed**: #1 Step 4 の途中（計画の通しレビューを終了。採用導線の位置・Process の図と範囲の文・アイコン行を反映。learnings 36 書き直し、37・38 追加を push 済み）。
- **Next**: #1 Step 4 の続き＝見積を詰める。`out/estimate.html` のレビュー → Schedule・Cost の人日と単価の議論（Direction 4 枚に対する人日の見直し含む）→ 提案書 `out/proposal.html` のレビュー → 納品形。
- **Notes**:
  - PR #8（OPEN）、ブランチ `hposal-plugin`。案件フォルダ `project/` は gitignore。数値の正は `project/mamezou-devsite/work/plan.data.json`、`work/render.py plan.md out work/plan.data.json` で提案書・見積を生成し額の一致を検査。
  - ユーザーの判断はアウトラインと提案の方針のみ。見出しごとの確認は求めない。計画のレビューはユーザー判断で打ち切り（再開後は見積から）。
  - 未解決の user-deferred パス：なし。
