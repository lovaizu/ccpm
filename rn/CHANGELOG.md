# Changelog

All notable, user-facing changes to the `rn` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A version goes up by what changes for you: the middle number for anything you would notice, the
last for fixes that change nothing you do.

## [0.9.0] - 2026-09-25

### Added

- `rn` は作業中、次に何をするかを決めるたびに1行で伝える。何が起きたかが分かる。
- 評価はどれもプルリクエストにコミットされ、良いところと足りないところを、それぞれの根拠と、足りないところの直し方と一緒に伝える。成果が通った理由や、戻された理由が分かる。

### Changed

- `/rn:on` はゴールについて1問ずつ、おすすめの答えを添えて聞く。一言で答えられ、計画が本当に欲しいものに合う。
- 計画はあなたの次の判断までで止まり、その先のタスクはあなたが決めてから立てる。
- タスクは何に届くべきかだけを書き、踏む手順は書かない。成果は、それが何をするかで判断される。
- 計画の「Acceptance criteria」と「Completion criteria」は「Goal reached when」と「Purpose reached when」になった。各行が、する作業ではなく、ゴールに届いたと分かる状態を書く。
- `/rn:ty` は承認を記録して止まる。`/rn:gm` はフィードバックどおりにすぐ直し、もう一度あなたの答えを待って止まる。どこで止まっても `/clear` して `/rn:up` で続けられる。
- 最後に止まるのは Deliverable サインオフ。計画と各設計はそれぞれのサインオフで承認済みなので、ここではゴールに照らして成果物だけを承認する。
- 設計は、ゴールと同じように1点ずつあなたと話して詰め、あなたの README と設計書に書いて承認を受ける。プロダクトはそのとおりに作られ、README と設計書はセッションのあともプロダクトに残る。
- `rn` は次の一手をすべてゴールそのものから決める。評価者は成り立っていることといないことを伝え、役目を果たしているタスクを細部のために戻さない。
- 作業が失敗し続けるときは、同じやり方を繰り返さず、別のやり方をあなたと考える。
- 以前の `rn` で始めたセッション（版の最初の2つの数字が違うもの）は、`/rn:up` が古い計画と済んだことから今の形にし、分からないところだけを聞き、新しい計画の承認を待つ。ほかのコマンドは、先に `/rn:up` を実行するよう伝える。
- 各タスクは、`checks/` に記録する複数の専門レビューではなく、何に届くべきかに照らして新しい評価者1人が評価する。
- `/rn:on` は、今いるブランチとそのプルリクエストがあればそこで始め、毎回新しく作らない。

### Removed

- セッションの中の、1問ずつ答える `design.md` のひな形。設計は、作業がプロダクトのあるべき姿を変えるところか、あなたが決めることがあるところでだけ、リポジトリ自身の README と設計書に書く。

## [0.8.0] - 2026-07-07

### Added

- Every session now records which version of `rn` it started under, and each command checks that against the installed version on every run — on a mismatch, it reconciles the session's plan, design, and remaining tasks to the current conventions automatically before continuing, so older sessions keep working correctly as `rn` itself evolves, with nothing extra for you to do.

### Changed

- Writing or updating a session's `design.md` now requires an explicit decision and the reasoning behind it for every question the design template raises — a section can no longer be left blank or silently skipped — so the resulting design doc always shows what was decided and why, not just what was ultimately built.
- Starting a session no longer always creates a brand-new `design.md`: if an existing one already covers the work's area, the assistant now points at it and walks through an update instead of authoring from scratch, so related work accumulates in one design doc instead of spawning duplicates.

## [0.7.0] - 2026-07-05

### Added

- `/rn:ty` (approve) and `/rn:gm` (revise) give you one accept/revise vocabulary at every gate and confirmation point — plan, design, evaluation, or any reviewed result — so you always know how to respond and the assistant never has to guess your intent from prose.
- `/rn:gm` with no argument now works through your PR's unresolved review threads one at a time — addressing each and replying with the fix, or asking a question when the ask is unclear — and leaves resolving each thread to you on GitHub, so review feedback gets handled systematically without anything getting closed out from under you.
- Once a session is underway, every message that stops for your input opens with a compact session map — ✅ done / 👉 now / ⬜ ahead, plus what's being asked — so you can answer on the spot without opening `steering.md` to see where things stand.

### Changed

- Session directories now carry a date prefix — `.rn/{yyyymmdd}-{slug}/` (e.g. `.rn/20260702-payment-fix/`) — so as sessions accumulate under `.rn/`, a directory listing reads in chronological order.
- You now sign off at three points — the plan up front, the approach when it needs a separate look, and the result at the end — instead of approving every task; in between, the assistant works through the tasks and has them checked behind the scenes, and only interrupts you mid-flight when a call is genuinely yours — so you get fewer interruptions while keeping the say on the moments that matter.
- Completion criteria in a plan are now written as two questions anyone can answer with evidence — is the goal actually achieved, and are new problems absent — so a criterion can't pass just because some file was produced.
- `steering.md` stays a lean plan for the remaining work: design intent and decisions now live in a separate `design.md` it points to, finished-task detail and deliberation stay in git and the PR, and a pause records only a short forward pointer — so the plan never piles up across pause/resume cycles.

### Fixed

- `/rn:dn` (pause) now finishes with a genuinely clean worktree — leftover test/build files are git-ignored so they stop keeping the tree dirty, anything ambiguous is shown to you rather than deleted, and the pause always completes instead of getting stuck.

## [0.6.0] - 2026-06-24

### Changed

- **Breaking:** the three commands are renamed to `/rn:on` (start), `/rn:dn` (pause), and `/rn:up` (resume) — a two-letter on / down / up set that follows the session's lifecycle: power **on** to start, take it **dn** (down) to pause, then **up** to resume. Update any habits or notes from the old `/rn:rdy`, `/rn:brb`, `/rn:bak`.

## [0.5.0] - 2026-06-24

### Changed

- **Breaking:** the three commands are renamed to `/rn:rdy` (start), `/rn:brb` (pause), and `/rn:bak` (resume) — short, consistent chat-shorthand names that make the start→pause→resume flow easier to remember. Update any habits or notes from the old `/rn:gm`, `/rn:bb`, `/rn:hi`.

## [0.4.0] - 2026-06-15

### Changed

- Each task's hands-on work — writing the change and committing it — is now done by a dedicated implementation expert, while the assistant you talk to stays focused on planning, review, and getting your approval; your work accumulates as plain commits with a single completion marker per task, so the history stays easy to follow.

## [0.3.0] - 2026-06-15

### Changed

- When a task involves messy trial-and-error, that now happens out of sight, so only the finished, already-reviewed change reaches you for approval at every task boundary — keeping the conversation light and leaving you in control of what gets committed.
- Routine review fixes are now decided against a clear quality bar instead of asking you about minor things, so you are consulted only on decisions that are genuinely yours.

## [0.2.0] - 2026-06-14

### Added

- `/rn:gm` restates your goal in its own words and opens a draft PR with the full plan, so you can review and fix the direction before any work starts.
- Each task is now checked by a reviewer that deliberately looks for problems before the work is committed, so mistakes are caught early instead of after the fact.

### Changed

- The plan in `steering.md` is clearer to review on the PR: a single **Acceptance criteria** section (previously "Verification") spells out when the goal is done and what is in or out of scope.

## [0.1.0] - 2026-06-13

### Added

- Initial release — goal-driven work sessions with `/rn:gm` (start), `/rn:bb` (step away), and `/rn:hi` (resume), so one goal carries across conversations without losing the thread.
