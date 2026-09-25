# steering.md

セッションが持つ唯一のファイル。新しい会話はこれと git だけから再開し、どのコマンドもフィールド名と見出しを頼りに動くので、それらは書かれたとおりに保つ。

## ひな形

```markdown
---
rn: <インストールされている rn の version>
issue: <このセッションが対応する issue — なければ行ごと省く>
pr: <セッションのプルリクエストの URL>
design: <Design sign-off の選択肢を示した文書 — できるまで省く>
status: running
---

# Goal

<利用者が望むことと、その理由。利用者と合意したもの>

# Goal reached when

- <利用者が得る状態>

# Assumptions

- **Fact** (<どう確かめたか>): <計画が頼っていること。利用者がした選択も含む>
- **Assumption**: <確かめないまま計画が頼っていること>

# Rules

- commit and push every change
- <作業担当が Goal からは知り得ないこと。このリポジトリの決まり>

# Tasks

### #1: Plan sign-off

**Purpose**: The user agrees this plan before any work starts.

**Prerequisites**: none

**Steps**:

- [ ] Approved by the user

**Purpose reached when**:

- The user approved the plan.

### #2: <タスク名>

**Purpose**: <このタスクが届くところと、それが受け持つ Goal reached when の行>

**Prerequisites**: <タスクの id、または none>

**Steps**:

- [ ] <手順>

**Purpose reached when**:

- <Purpose に届いたと分かる状態>

# State

- **Next**: #1 Plan sign-off
- **Feedback**: none
- **Notes**: none
```

- タスクはサインオフで終わる。利用者が選ぶことには「Design sign-off」、完成物には「Evaluation sign-off」。サインオフのタスクの手順は `Approved by the user` の1つだけ。タスクは手順がすべて `[x]` になったら完了。後から足すタスクは、まだ使っていない次の id を取る。
- `status` は `/rn:dn` から `/rn:up` までの間 `paused` で、`paused_at: <YYYY-MM-DD>` を添える。
- `Next` は取るべきタスクと、どこまで進んだか。`Feedback` は直しを求める利用者の言葉で、その直しが評価を通るまで残す。`Notes` は、ほかのどこにも残らない、次の会話に要ること。
- `steering.md` の隣の `evaluations/` には、Evaluation sign-off まですべての評価を置く。

## セッションを見つける

1. この会話で扱ってきた `steering.md`。
2. なければ、このブランチが変えたもの。
   `git diff --name-only $(git merge-base HEAD origin/HEAD) HEAD -- '.rn/*/steering.md'`
   （`origin/HEAD` が未設定なら、先に `git remote set-head origin --auto`）。
3. なければ、開いているプルリクエストのブランチが変えたもの
   （`gh pr list --state open --json headRefName`）。1つを提案して待つ。

見つからなければ「No open session. Run `/rn:on` to start.」、終わったセッションならそう伝える。どちらも止まる。

`rn` フィールドがない、または `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` の `version` と違うセッションは、前の版の `rn` で始まったもの。`/rn:up` が今の版に合わせる。ほかのコマンドは、先に `/rn:up` を実行するよう利用者に頼んで止まる。

## 前の版のセッションを今の版に合わせる

この `rn` で動かせるよう、ひな形の形に書き直す。計画も進み具合も失わず、利用者が承認した文言は変えない。前の版は、ヘッダーを `Rn version:` と `Design:` の行で書き、基準を Acceptance criteria と Completion criteria と呼び、状態を `State` に持ち、Plan sign-off のタスクを持たず（計画はプルリクエストで承認していた）、独自のレビューを手順として `checks/` に記録していた。そのレビューは、この `rn` の評価に置き換わる。

`chore: bring session up to rn {version}` でコミットしてプッシュし、`${CLAUDE_PLUGIN_ROOT}/references/turn.md` のとおりに計画を評価させる。
