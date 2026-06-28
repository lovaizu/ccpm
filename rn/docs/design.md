# rn — design notes

Not read at runtime — for whoever maintains the procedures and must judge whether a step is still
right when requirements change. Key ideas and mechanism only.

## Context & constraints

A piece of real work outlives any single conversation: context runs out, `/clear` wipes the thread,
days pass. So rn keeps the durable state on disk — `steering.md` + git + the PR, never the agent's
memory — and a coordinator drives fresh expert subagents through the work one task at a time. A cold
agent can then resume from `steering.md`, which stays small enough to re-read in full each time.

## Approach

The key decisions, each over the alternative it beat:

- **Coordinator / expert split** — over one agent that builds *and* reviews its own work, which is not
  independent.
- **steering.md is a lean forward contract** — heavy content lives elsewhere (rationale → `design.md`,
  UX → `README`, history → git + PR). Never stored, so it can't drift or grow into an archive.
- **Quality built into each task** — over a final inspection: a defect is caught at the task that
  introduced it.
- **The user gates only plan / design / evaluation** — each evaluating one thing: plan → `steering.md`,
  design → `design.md`, evaluation → the end results (the Acceptance-criteria run and the task checks).
  Over a gate on every task, which is ceremony where no decision is waiting. Escalation is a separate,
  always-open channel for anything that changes the agreed plan or design.

## Structure

```mermaid
flowchart TD
  subgraph execution["Execution model"]
    cmd["Commands (entry points)"] --> coord["Coordinator<br/>(main agent)"]
    coord --> exp["Experts<br/>(sub agents)"]
  end
  subgraph support["Support"]
    steer["steering.md"] -. points to .-> dsgn["design.md"]
  end
  cmd -. read / write .-> steer
  coord -. read / write .-> steer
  exp -. commits .-> pr["PR"]
```

| Actor | What it is |
|---|---|
| Commands (entry points) | `/rn:on`, `/rn:dn`, `/rn:up` — start, suspend, resume a session. |
| Coordinator (main agent) | The conversation agent that decomposes, dispatches, reviews, and records. |
| Experts (sub agents) | Implementation builds; QA and (for code) language and software-engineering review. |
| `steering.md` | The session's forward contract. |
| `design.md` | The whole-structure design (this doc). |

The per-task loop is defined in `task-workflow.md`.

## Flow

```mermaid
flowchart LR
  on["/rn:on"] -->|plan + design gate| loop["Task loop"]
  loop -->|all tasks done · evaluation gate| eval["Acceptance criteria run"]
```

**Task loop** — one task at a time, per `task-workflow.md`:

```mermaid
flowchart TD
  build["Implementation expert<br/>builds + commits"] --> review["QA / expert review"]
  review -->|findings| build
  review -->|clear| coord["Coordinator review"]
  coord -->|clear| off["Check off → next task"]
  off --> build
  build -. suspend / resume .-> dnup["/rn:dn → /rn:up"]
  review -. plan-changing discovery .-> esc["Escalation → user"]
```

## Open questions

- **Default home for a session's `design.md`.** Sessions default to `.rn/{slug}/design.md`, but rn
  keeps its own under `rn/docs/`; whether that exception generalizes is open.
