# rn — design notes

Not read at runtime — the skill and reference files are pure procedure. This file is for whoever
maintains them and needs to judge whether a step is still right when requirements change. It records
the design's decisions and how the parts fit, not a memo per step.

## Context & constraints

rn helps a user drive a goal to *done* — across context boundaries (a conversation fills up, a day
ends, a `/clear` wipes the thread), one task at a time, with quality built in rather than bolted on
after. A single long conversation cannot hold a real piece of work end to end: context runs out, and
what the agent "remembers" is lost the moment the thread resets. So the design has to survive being
picked up cold by a fresh agent that saw none of the prior conversation.

Constraints that follow from that:

- **The durable record is on disk and in git, not in the agent's head.** Anything a resume needs must
  be reconstructable from `steering.md`, the commit log, and the PR.
- **`steering.md` is read cold every resume.** It must stay small enough to re-read in full and current
  enough to trust — a forward contract for the remaining work, not an archive of the finished work.
- **Quality cannot be a final inspection.** With work split across resumes, each task carries its own
  verification, so a defect is caught at the task that introduced it.
- **The user stays in the loop at task boundaries.** Review happens on the PR, where diffs and long
  documents render properly.

## Approach

- **Coordinator / expert split** — the main conversation agent (coordinator) delegates all
  deliverable work to fresh subagent experts, rather than doing the work itself. Chosen over a single
  agent that both builds and reviews: a builder reviewing its own output is not independent, and the
  coordinator's context stays light when each expert's trial-and-error lives inside the subagent. The
  coordinator keeps only steering and recorded verdicts.
- **Lean forward contract, heavy content externalized — not pruned** — `steering.md` holds only
  requirements, acceptance criteria, remaining tasks, and resume state; design intent lives in
  `design.md`, deliberation and history in git + the PR. Chosen over an earlier *store-then-prune*
  model that kept decisions and completed-task bodies in steering and had `/rn:up` retire and collapse
  them on ship. That model lost because pruning is machinery that can mis-fire and still lets steering
  swell between prunes; never storing the heavy content means there is nothing to prune, and steering
  cannot regrow into a design doc or an archive. The cost — rationale is one indirection away in
  `design.md` — is acceptable because the maintainer who wants the "why" is a different reader from the
  agent resuming the work.
- **Doc-division by kind** — requirements & criteria → `steering.md`, structure & decisions →
  `design.md`, UX → `README`. Chosen over letting each document accrete whatever is convenient: a fixed
  home per kind is what keeps steering lean structurally, instead of by a discipline someone has to
  remember.
- **Three scheduled gates, plus escalation as a separate channel** — the user signs off at exactly
  three points where human judgment is irreplaceable: **plan** (the draft-PR approval before any task
  runs), **design** (the approach / key decisions before anything is built on them), and **evaluation**
  (the end-of-session Acceptance-criteria run). Chosen over the earlier *gate every task* model: a
  per-task user gate fires on every boundary regardless of whether a decision is actually waiting,
  which is ceremony the agent cannot add judgment to — and most task boundaries carry no decision the
  user must make. Those three, by contrast, are exactly the moments where what to build, how to build
  it, and whether it is done are genuinely the user's call. Per-task quality does not need a user: it
  is caught by self-check + QA/expert review + the coordinator's independent review of the committed
  diff. Design folds into the plan gate when it is settled at plan time (one stop), and stands alone
  only when the design needs separate work before heavy build — so it is one of the three, never a
  fourth, and never silently dropped.
- **Escalation is a channel, not a gate** — any execution discovery, blocker, or decision that would
  change the *agreed plan or design* is raised to the user immediately, wherever it surfaces, rather
  than held until the next gate. Chosen over folding it into triage as an exception: a gate fires on a
  schedule, but a plan-changing discovery can land anywhere and must not wait — and if it were merely a
  triage exception, a mid-flight change could ship before the next gate, unseen. So escalation is
  always open and counts as none of the three gates; a normal in-scope finding is still decided against
  the bar (Valid/Invalid), not escalated.

## Structure

| Actor | Responsibility |
|---|---|
| Coordinator | Main conversation agent. Decomposes the goal, picks the expert per task, reviews returned work, writes `steering.md` and `checks/{task-id}.md`. Never touches the deliverable directly. |
| Implementation expert | Subagent. Produces, fixes, and commits/pushes the deliverable (code or docs). |
| QA expert | Subagent. Adversarially verifies the result against the task's completion criteria. |
| Language expert (code only) | Subagent. Judges language-level craft. |
| Software-engineering expert (code only) | Subagent. Judges design and system integrity. |
| `steering.md` | The session's forward contract: goal, criteria, rules, remaining tasks, state, and the `Design:` pointer. |
| `design.md` | The whole-structure design (this doc's shape) that `steering.md` points to. |
| `/rn:on`, `/rn:dn`, `/rn:up` | The skills that start, suspend, and resume a session. |
| `task-workflow.md` | The reference defining the per-task coordinator/expert loop, read by `on` and `up`. |

```
   user goal
       │
       ▼
   ┌────────┐   writes    ┌─────────────┐   points to   ┌───────────┐
   │ /rn:on │ ──────────► │ steering.md │ ────────────► │ design.md │
   └────────┘             └─────────────┘               └───────────┘
       │                        ▲   │
       │ begins task #1         │   │ task loop (task-workflow.md)
       ▼                        │   ▼
   ┌──────────────────────────────────────────────┐
   │ Coordinator ──► Implementation expert         │
   │      ▲                │                        │
   │      │ verdicts       ▼ deliverable + commits  │
   │      └──── QA / Language / SWE experts ──► PR  │
   └──────────────────────────────────────────────┘
       │ context boundary               ▲ resume
       ▼                                 │
   ┌────────┐   writes State    ┌────────┐
   │ /rn:dn │ ────────────────► │ /rn:up │
   └────────┘                   └────────┘
```

## Flow

1. **`/rn:on`** restates the goal, decides the `{slug}` and the `design.md` location with the user,
   writes `steering.md` (allocating content per the doc-division) and any `design.md`, decomposes the
   goal into flat tasks, and opens a draft PR — then waits for approval. This is the **plan gate** (with
   the **design gate** folded in when the design is settled at plan time; otherwise the design gate is a
   separate sign-off before heavy build).
2. **Task loop** (per `task-workflow.md`): the coordinator dispatches the implementation expert,
   reviews the returned diff, dispatches QA (and, for code, the language and software-engineering
   experts), records verdicts in `checks/{task-id}.md`, and — once its own independent review clears —
   checks the task off. No user gate fires per task; one completion marker (`complete task #{id}`) lands
   per task. Mid-flight, any discovery that would change the agreed plan or design is escalated to the
   user immediately via the always-open escalation channel.
3. **`/rn:dn`** suspends: it checks off progress, writes the `State` section (`Status: paused` plus a
   bounded forward pointer in `Notes`), commits and pushes, and hands off to a manual `/clear`.
4. **`/rn:up`** resumes cold in a fresh conversation: finds `steering.md` from git history, reconciles
   the checked-off tasks against the commit log, resets `State`, and continues from the next unchecked
   task via `task-workflow.md`.
5. The loop repeats across as many suspend/resume cycles as the work takes, until every task is done.
   Then the **evaluation gate**: the end-of-session run of the `steering.md` Acceptance criteria, with
   the user signing off on the result before the session closes.

## Open questions

- **Where session-spanning `design.md` lives by default.** Sessions default to `.rn/{slug}/design.md`,
  but a plugin like rn keeps its own design under `rn/docs/`; whether that exception generalizes is
  open.
