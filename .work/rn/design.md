# rn Plugin Design

## 1. Requirements

rn (Right Now) is a Claude Code plugin that manages goal-driven work sessions through a `steering.md` file. It provides three commands:

| Command | Function | Trigger |
|---|---|---|
| `/rn:gm` | Start a new session | User states a goal |
| `/rn:bb` | Suspend the session | User needs to stop (context limit, break, etc.) |
| `/rn:hi` | Resume a suspended session | User returns in a new conversation |

The plugin must:

1. Capture the user's goal verbatim and decompose it into verifiable tasks
2. Execute tasks one at a time with independent quality reviews (subagents)
3. Persist session state to git so work survives across conversations
4. Work in any repository, any language — no project-specific dependencies

## 2. Assumptions and Constraints

### Platform constraints (Claude Code)

- Skills cannot invoke `/clear` — after `/rn:bb`, the user must `/clear` manually
- Hooks cannot receive context usage — automatic bb→clear→hi on threshold is not possible (future work)
- Subagents (Agent tool) have no conversation history — all review context must be passed in the prompt
- Custom commands are skills: a flat `commands/*.md` file and a `skills/<name>/SKILL.md` both create `/<name>`. Only the skill (directory) form can bundle supporting files. ([skills doc](https://code.claude.com/docs/en/skills))
- `${CLAUDE_PLUGIN_ROOT}` is substituted inline in skill content and resolves to the plugin's installed directory; everything under the plugin root is copied to the cache on install. ([plugins-reference](https://code.claude.com/docs/en/plugins-reference))

### Design constraints

- All user interactions are proposals, never questions (action.md D principle)
- Rule files (.md read by AI) are written in English
- 1 task = 1 commit
- Prompt workflows are structured as **Phase > Step > Action**: a Phase groups related steps toward one sub-goal, a Step is a unit of work, an Action is a concrete operation.

## 3. Workflow

```
/rn:gm                    /rn:bb              /rn:hi
  │                          │                   │
  ▼                          ▼                   ▼
Create steering.md    Commit work           Find steering.md
  │                   Write State section    Read State section
  ▼                   Push                   Sync tasks with git log
Decompose tasks          │                   Reset State section
  │                      ▼                      │
  ▼                   "Session suspended"        ▼
Begin task #1         ← user does /clear →   Begin next task
  │                                              │
  ▼                                              ▼
[task-workflow]                            [task-workflow]
  │                                              │
  ├─ Phase: Execute                              │
  ├─ Phase: Verify (self-check + reviews)        │
  └─ Phase: Complete (user review + commit)      │
```

## 4. Plugin Structure

```
rn/
├── .claude-plugin/
│   └── plugin.json              # { "name": "rn" }
├── skills/
│   ├── gm/
│   │   └── SKILL.md             # Procedure: start session
│   ├── bb/
│   │   └── SKILL.md             # Procedure: suspend session
│   └── hi/
│       └── SKILL.md             # Procedure: resume session
├── references/
│   ├── task-workflow.md         # Shared knowledge: task execution, reviews, check files
│   └── steering-template.md     # steering.md template
└── README.md
```

Each command is a skill directory so it can be invoked as `/rn:gm` etc. The shared task-execution knowledge lives once in `references/task-workflow.md`; `gm` and `hi` read it on demand via its `${CLAUDE_PLUGIN_ROOT}` path. `references/` is not a component directory — it is plain bundled content, copied to the cache on install and addressable through `${CLAUDE_PLUGIN_ROOT}/references/…`.

### Component responsibilities

| Component | Layer | What it specifies |
|---|---|---|
| skills/gm/SKILL.md | Procedure | Define goal → plan tasks → launch task #1 (reads task-workflow.md, steering-template.md) |
| skills/bb/SKILL.md | Procedure | Capture state → persist (commit, push, report). Reads nothing |
| skills/hi/SKILL.md | Procedure | Recover state → reconcile with git → resume next task (reads task-workflow.md) |
| references/task-workflow.md | Knowledge | Task execution workflow (Execute / Verify / Complete), subagent review dispatch, review policies, check file format |
| references/steering-template.md | Reference | Full steering.md template |

### Invocation control

All three skills set `disable-model-invocation: true`. They are explicit workflows with side effects (commit, push, `/clear` handoff); Claude must not trigger them automatically. The user invokes each with `/rn:gm` / `/rn:bb` / `/rn:hi`.

### File reads

| When | What it reads | Why |
|---|---|---|
| gm Phase 2 | `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md` | Create steering.md from template |
| gm Phase 3 | `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md` | Execute task #1 |
| hi Phase 3 | `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md` | Execute next task |
| bb | Nothing | Suspend only, no task execution |

## 5. steering.md Specification

### 5.1 Template (references/steering-template.md)

```markdown
# Goal

<user's exact words — never paraphrase>

## Verification

- <how to verify the goal is achieved>
- <two axes: goal alignment + quality>

# Assumptions

- <distinguish facts from assumptions — state explicitly if unverified>
- <define complete scope, never sample>

# Rules

- 1 task = 1 commit
- <task-specific conventions>

# Tasks

### #1: <task name>

**Purpose**: what to achieve, 1-2 sentences
**Prerequisites**: tasks that must be completed first (or "none")
**Steps**:
- [ ] specific step 1
- [ ] specific step 2
- [ ] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [ ] QA engineer review (subagent)
- [ ] (code changes only) language expert review (subagent)
- [ ] (code changes only) software engineer review (subagent)
- [ ] user review

**Completion criteria**:
- objectively verifiable by a third party
- no vague terms ("appropriate", "correct")

# Decisions

## D-N: <what was decided>
- **Conclusion**: <the decision>
- **Rationale**: <why>
- **Evidence**: <facts/numbers backing the rationale>

# State

(written by /rn:bb, read and reset to this placeholder by /rn:hi)

- **Status**: paused
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
```

### 5.2 Task definition requirements

| Requirement | Rule |
|---|---|
| Granularity | Purpose expressible in one sentence; split if it grows |
| Specificity | Not "implement" but "implement `methodName()` in `ClassName`" |
| Objectivity | Completion criteria judgeable by a third party |
| Prerequisites | List dependencies explicitly; enables parallel/sequential judgment |

### 5.3 steering.md discovery

| Command | How it finds steering.md |
|---|---|
| gm | Never searches. Creates a new file at the proposed location |
| bb | Uses the path already known from the current session. Fallback: commit history search |
| hi | Always searches via commit history |

**Commit history search algorithm:**

1. `git log --diff-filter=AM --name-only --pretty=format: -- '*/steering.md' | head -5`
2. Filter to files that exist on disk (`test -f`)
3. One result → use it
4. Multiple → rank by (a) has `Status: paused` in State section, (b) most recent commit. Propose top candidate
5. Zero → "No steering.md found. Run `/rn:gm` to start."

## 6. Command Steps

Each command is structured as **Phase > Step > Action**.

### 6.1 /rn:gm — Start

**Phase 1: Define** — fix the goal and where it lives

| Step | Actions |
|---|---|
| 1. Hear the goal | Use the user's message or `$ARGUMENTS`. If none, ask. Record exact words — never paraphrase |
| 2. Propose location | Propose a `{slug}` from the situation (git branch name / issue reference in `$ARGUMENTS` / kebab-case work name from the goal). Recommend one + alternatives. Propose `.rn/{slug}/steering.md`. Wait for confirmation |

**Phase 2: Plan** — turn the goal into verifiable tasks

| Step | Actions |
|---|---|
| 3. Create steering.md | Read `${CLAUDE_PLUGIN_ROOT}/references/steering-template.md`. Fill Goal, Verification, Assumptions, Rules. Leave Tasks, Decisions, State empty |
| 4. Decompose tasks | Work backwards from the Verification end state. Give each task Purpose, Prerequisites, Steps, Completion criteria |

**Phase 3: Launch** — get approval and start

| Step | Actions |
|---|---|
| 5. Present and approve | Show the complete steering.md. Do not proceed without user approval |
| 6. Begin task #1 | After approval, write the completed steering.md to the confirmed path, then commit it (`chore: start session — {slug}`). Read `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md`. Execute task #1 |

### 6.2 /rn:bb — Suspend

**Phase 1: Capture** — record where work stands

| Step | Actions |
|---|---|
| 1. Find steering.md | Use the known path, or commit history search |
| 2. Commit work | Clean tree → skip. Dirty: all task steps checked → normal commit; some unchecked → `wip:` prefix |
| 3. Write State | Check off done tasks. Add new tasks/decisions. Write the State section (status, date, last completed, next, notes). Notes must carry enough context for `/rn:hi` to resume without the conversation: current work, blockers, pending decisions, next concrete action |

**Phase 2: Persist** — push and confirm

| Step | Actions |
|---|---|
| 4. Commit and push | `git commit` + `git push`. If push fails, continue (user can push later) |
| 5. Verify clean | `git status` must show a clean tree |
| 6. Report | Output: last completed, next task, branch name |

### 6.3 /rn:hi — Resume

**Phase 1: Recover** — reconstruct the prior state

| Step | Actions |
|---|---|
| 1. Handle dirty tree | Clean → proceed. Dirty → propose wip commit or discard; wait for confirmation |
| 2. Find steering.md | Commit history search |
| 3. Read State | Read the State section: last completed, next task, notes |

**Phase 2: Reconcile** — align the file with git reality

| Step | Actions |
|---|---|
| 4. Sync tasks | Cross-check git log against unchecked tasks. A commit matches a task when its message contains `complete task #{id}` (the format written by task-workflow Complete, §7.4); check that task off |
| 5. Check blockers | If State notes mention a blocker: investigate and find an alternative approach before removing tasks |
| 6. Clean up State | Replace the State section with its placeholder. Commit |

**Phase 3: Resume** — continue execution

| Step | Actions |
|---|---|
| 7. Begin next task | Read `${CLAUDE_PLUGIN_ROOT}/references/task-workflow.md`. Execute the next unchecked task. If all done, propose running Verification |

## 7. Task Workflow (references/task-workflow.md)

The shared execution loop, structured as **Phase > Step > Action**. `gm` and `hi` read this file when they reach task execution.

### 7.1 Process selection

| Task type | Verify phase steps |
|---|---|
| Non-code (docs, config, design) | Self-check → QA review → User review |
| Code changes | Self-check → QA review → Language expert review → Software engineer review → User review |

### 7.2 Phase: Execute

| Step | Actions |
|---|---|
| Do the work | Carry out the task's Steps from steering.md until each is complete |

### 7.3 Phase: Verify

**Step — Self-check**

- Action: verify each completion criterion, recording OK/NG with specific evidence
- Action: (code) measure coverage with a project-appropriate tool (Jest, pytest, JaCoCo, gcov, etc.); record line/branch coverage and uncovered areas
- Action: write results to `{steering_dir}/checks/{task-id}.md`

**Step — QA review (subagent)**, then expert reviews for code tasks. Each reviewer runs as an independent subagent (Agent tool, no conversation history).

- Action: build the review prompt with 5 elements — (1) Role, (2) Artifact (full content or diff), (3) Criteria (the checklist below), (4) the task's Completion criteria from steering.md, (5) Output format (OK/NG per criterion with evidence, overall pass/fail)
- Action: dispatch the subagent and collect the verdict
- Action: apply the iteration protocol — any NG → fix → re-run the same reviewer; max 3 iterations; still NG after 3 → record findings and escalate to user review with unresolved items

Reviewer checklists:

- **QA engineer**: tests/verifications meaningful to the purpose (not just "passed"); edge cases covered (boundary, error, empty, max, type conversion)
- **Language expert** (code only): best practices (naming, error handling, null/thread safety); consistency with existing codebase style; test code in GWT (Given/When/Then) format
- **Software engineer** (code only): separation of concerns; system-wide integrity (interface contracts, API compatibility); maintainability (no duplication, deep nesting, magic numbers)

Review policy (all reviewers):

- Address every finding. Never skip as "minor" or "low priority"
- To skip a finding, get user confirmation first
- Only dismiss a finding with a factual error, stating the evidence

### 7.4 Phase: Complete

| Step | Actions |
|---|---|
| User review | Present results; do not proceed without approval |
| Commit | Check off the task in steering.md. Commit: `docs: complete task #{id} — {description}` |
| Advance | Begin the next unchecked task immediately. If all tasks are done → propose running the Verification criteria |

### 7.5 Check file format

Output to `{steering_dir}/checks/{task-id}.md`:

```markdown
# {task-id} Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| (text) | OK / NG | (what was confirmed) | OK / NG | (findings) |

## QA Engineer Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK / NG | |
| Edge case coverage | OK / NG | |

## Expert Reviews (code changes only)

### Language Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Best practices | OK / NG | |
| Codebase style consistency | OK / NG | |
| GWT test format | OK / NG | |

### Software Engineer

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Separation of concerns | OK / NG | |
| System integrity | OK / NG | |
| Maintainability | OK / NG | |

## Overall Verdict

- Self-check: OK / NG
- QA: OK / NG
- Language expert: OK / NG / N/A
- Software engineer: OK / NG / N/A
- Ready for user review: Yes / No (reason)
```

## Appendix: Action Principle Traceability

How each action.md principle is enforced in the plugin workflow:

| Principle | Enforcement point | Mechanism |
|---|---|---|
| A.1 Goal as starting point | gm Phase 1 | Goal captured verbatim before any planning |
| A.2 Work backwards from end state | gm Phase 2 | Task decomposition starts from Verification criteria |
| A.3 Means adapt, goal fixed | All commands | Goal section is read-only after creation |
| A.4 Find alternatives before giving up | hi Phase 2 | Blockers trigger alternative search, not task removal |
| A.5 No reinterpretation | gm Phase 2 | User's exact words stored, never paraphrased |
| B.1 Act on verified facts | task-workflow | Assumptions section forces explicit declaration |
| B.2 Verify complete population | QA review | Subagent checks edge case coverage exhaustively |
| C.1 Define hypothesis + verification | gm Phase 2 | Verification section written before tasks |
| C.4 Two-axis verification | Verify phase | Goal alignment + quality as separate review passes |
| C.5 Address every finding | Review policy | No skipping without user confirmation |
| D.1 Always propose | All user interactions | Questions replaced with proposals |
| D.3 Issue-Conclusion format | Decisions section | All decisions recorded in structured format |
