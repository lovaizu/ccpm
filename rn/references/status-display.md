# Session-Status Display

The compact session map that opens every message stopping for user input while a session is active.
Read wherever a stop point instructs opening the message with the session-status block per
`status-display.md`. The block comes first in that message — before the ask and anything else.

## Rules

- **Emit only while a session is active** — its `steering.md` exists and is identified. A stop before
  that carries no block: e.g. planning's goal / slug / design-location asks before `steering.md` is
  persisted, `/rn:up` before a suspended `steering.md` is identified (including its
  multiple-candidates proposal), `/rn:gm` or `/rn:ty` with no active session.
- **Asks and flow-ending reports both count as stops** — the class is any message that halts the
  flow awaiting the user's next move (e.g. a suspend report, an abort or loop-completion report, a
  nothing-pending reply, a session-close report); such a message opens with the block too, and on a
  report the 👉 line states where the session stands and the user's next move instead of an ask.
- **Derive the block fresh from the active `steering.md` at emit time** — its `Goal`, task list, and
  check-offs are the only source; never reuse an earlier block.
- **A task counts ✅ when `steering.md` records it complete** — checked off, or carrying an explicit
  done annotation on the task (e.g. a "DONE …" note in its heading). Done-but-awaiting (e.g. a review
  still pending) still counts ✅; the pending item goes on the outlook line when it affects what
  follows.
- **Write the block in the user's conversation language.** This spec and its examples are English; the
  emitted block follows the conversation.
- **Markers are fixed**: ✅ completed / 👉 current / ⬜ remaining.

## Format

```
── {slug}: {goal one-liner} ──
✅ {ids}   {short labels}
👉 #{id}   {task name} ── asking now: {what this stop is asking the user}
⬜ {ids}   {short labels}
({outlook — what follows this stop})
```

- **Header** — `── {slug}: {goal one-liner} ──`: the session's slug (the steering directory name,
  date prefix dropped) and a one-line compression of steering's `Goal`.
- **✅ completed** — the completed tasks (per the ✅-membership rule above). Group consecutive ids
  into ranges (e.g. `#1–#6`) and comma-separate non-consecutive groups (e.g. `#1–#14, #16`), with a
  short label per task, `/`-separated; several ✅ lines are fine when one grows long. No completed
  tasks yet → no ✅ lines.
- **👉 current** — exactly one line: the task the session is stopped on, plus what is being asked of
  the user right now — the verdict, answer, or decision this stop waits for. On a report stop the 👉
  line replaces `asking now:` with where the session stands and the user's next move (e.g.
  `👉 #2   root-cause fix ── suspended here; next move: /clear, then /rn:up`). A stop not tied to a
  numbered task (the plan gate; an escalation that spans tasks) names the gate or moment instead of an
  id.
- **⬜ remaining** — the unchecked tasks ahead, labeled and ranged as for ✅. **No remaining tasks →
  omit the ⬜ lines entirely** — never render an empty ⬜ section.
- **Outlook** — one closing parenthesized line: what follows this stop (the next task, or — when
  nothing remains — what closes the session).

## Examples

Mid-session, tasks remaining (an `/rn:dn` untracked-path ask):

```
── payment-fix: payments complete on the payment screen ──
✅ #1–#2   reproduction test / root-cause fix
👉 #3      regression check ── asking now: how to handle the untracked `perf-notes.txt`
⬜ #4      evaluation sign-off
(after your answer the suspend completes; #3 resumes on /rn:up)
```

Last task, nothing remaining (⬜ omitted):

```
── payment-fix: payments complete on the payment screen ──
✅ #1–#3   reproduction test / root-cause fix / regression check
👉 #4      evaluation sign-off ── asking now: your verdict via /rn:ty or /rn:gm
(#4 is the last task; after approval only the merge remains)
```

Report form (the `/rn:dn` suspend report — the 👉 line carries the next move, no ask):

```
── payment-fix: payments complete on the payment screen ──
✅ #1      reproduction test
👉 #2      root-cause fix ── suspended here; next move: /clear, then /rn:up
⬜ #3–#4   regression check / evaluation sign-off
(#2 starts on /rn:up)
```
