# Session-Status Display

The compact session map that opens every message stopping for user input. Read wherever a stop point
instructs "open the message with the session-status block per `status-display.md`". The block comes
first in that message — before the ask and anything else.

## Rules

- **Derive the block fresh from the active `steering.md` at emit time** — its `Goal`, task list, and
  check-offs are the only source; never reuse an earlier block.
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
- **✅ completed** — the checked-off tasks. Group consecutive ids into ranges (e.g. `#1–#6`) with a
  short label per task, `/`-separated; several ✅ lines are fine when one grows long. No completed
  tasks yet → no ✅ lines.
- **👉 current** — exactly one line: the task the session is stopped on, plus what is being asked of
  the user right now — the verdict, answer, or decision this stop waits for. A stop not tied to a
  numbered task (the plan gate; an escalation that spans tasks) names the gate or moment instead of an
  id.
- **⬜ remaining** — the unchecked tasks ahead, labeled and ranged as for ✅. **No remaining tasks →
  omit the ⬜ lines entirely** — never render an empty ⬜ section.
- **Outlook** — one closing parenthesized line: what follows this stop (the next task, or — when
  nothing remains — what closes the session).

## Examples

Mid-session, tasks remaining:

```
── payment-fix: payments complete on the payment screen ──
✅ #1–#2   reproduction test / root-cause fix
👉 #3      regression check ── asking now: how to handle the untracked `perf-notes.txt`
⬜ #4      evaluation sign-off
(after your answer, #3 resumes; #4 then closes the session)
```

Last task, nothing remaining (⬜ omitted):

```
── payment-fix: payments complete on the payment screen ──
✅ #1–#3   reproduction test / root-cause fix / regression check
👉 #4      evaluation sign-off ── asking now: your verdict via /rn:ty or /rn:gm
(#4 is the last task; after approval only the merge remains)
```
