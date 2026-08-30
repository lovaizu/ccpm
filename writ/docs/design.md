# writ — design notes

Not read at runtime — for whoever maintains the design and needs to judge whether a decision is
still right when the instruction or the target axes change.

## 1. Background & Goals

### 1.1 What is the goal?

A document that reads as if a person wrote it, not an AI — least reader effort, taken in top to
bottom, graspable at a glance. Packaged as a Claude Code plugin `writ` (skill `up`) so the procedure
applies on demand to any draft, run by a human or by Claude itself.

### 1.2 What goes wrong without this?

Without an ordered, reader-derived procedure, output either stays a direct edit of the input's own
wording (dragging its problems along and reading as patched) or reaches for generic AI patterns by
reflex — padding, restatement, retreat into generalities, flavorless connectives, reflexive
bulleting, a wavering voice, hedging. Any one of these instantly reads as "an AI wrote this,"
regardless of how much polish is layered on top.

### 1.3 What does reaching it require?

Primary mode: brush up an existing draft (read for intent, not reused verbatim). Authoring from
scratch runs the same procedure but is secondary. The procedure must build both quality tiers in by
construction, then verify — never edit the draft in place, since that drags the old wording (and its
problems) along.

### 1.4 What is out of scope?

One plugin (`writ`), one skill (`up`), procedure inline in a single `SKILL.md` (source is short, one
continuous procedure — not split into `references/`). Not a general prose generator: it does not
originate content on its own; it takes only the input's intent and what it must convey, and derives
structure/voice from a reader definition rather than memorizing a template's wording.

## 2. Assumptions & Constraints

### 2.1 What do we take as true?

- Official skills are model-invocable by default; `rn` disables it because its skills are meant for a
  human to drive — `up` is meant for a human or Claude itself, so it stays model-invocable.
- Skills are invoked as `/{plugin}:{skill}`; plugin and skill names are independent slots (`rn:gm` is
  the precedent), so `writ` + `up` is valid.
- `instruction.md` is the verbatim source of record for the skill's pillars, except the five-axis
  skeletons, which D-6 deliberately supersedes with externally sourced structures.

### 2.2 What binds the solution?

Inherited from the repo: version lives only in `writ/.claude-plugin/plugin.json` (not
`marketplace.json`); shipped artifacts are English except `instruction.md` itself, kept verbatim as
the source of record; `README.md` is scenario-style; the skill stays self-contained in one file.
Marketplace `category` is a free string (unverified assumption) — used `"writing"`. `claude plugin
validate` / `claude -p … --plugin-dir` availability in the environment is likewise an unverified
assumption; task #3 falls back to manual verification if absent.

## 3. Design overview

### 3.1 What is the core idea, and why does it solve the problem?

A two-layer `SKILL.md` — process (instructions to the model) and output rules (constraints on the
produced document) — drives an ordered writing procedure that rebuilds the document fresh from the
input's intent, rather than editing it in place. Building fresh means the AI tells never take hold in
the first place; a final floor-net pass (after the ceiling is built) catches only the stragglers.
Voice, form, and axis are all derived from a reader definition captured early in the procedure, so
the output actually varies with who is reading rather than reproducing one memorized shape.

### 3.2 What are the pieces, and what is each responsible for?

| Actor | What it is |
|---|---|
| `instruction.md` | Verbatim source of record for the skill's pillars (except the five-axis skeletons, superseded by D-6 research). |
| `SKILL.md` — process layer | Instructions to the model running the skill: understand → define reader → outline → fill → check story → decide voice/form → write → brush up → clear floor → self-check → reader trial & deliver. |
| `SKILL.md` — §Reference (output rules) | Constraints on the produced document: the two tiers, the five axes, form, voice by reader, the seven-tell floor checklist — with an explicit addressee sentence naming the produced document, not the prompt. |
| The writer (human or Claude) | Runs the skill against an input draft (or a topic, from scratch), producing the document plus a "what changed and why" note. |
| Fresh-context reader (subagent) | Reads the produced document as the step-2 reader, given only the document and that reader definition; reports stumbles and content the reader did not need. Its clean pass gates delivery (D-8). |
| Produced document | The end artifact judged against the floor/ceiling bar — never the prompt itself. |

### 3.3 How does work move?

```mermaid
flowchart TD
  a["Understand the input"] --> b["Define reader & purpose<br/>(one person, one reading stance)"]
  b --> c["Outline from purpose<br/>(pick one of five axes, no mixing)"]
  c --> d["Fill outline with the message"]
  d --> e["Check the story as the reader"]
  e --> f["Decide voice & form<br/>(derived from purpose+story)"]
  f --> g["Write"]
  g --> h["Brush up to the ceiling<br/>(minimal reader effort to the purpose)"]
  h --> i["Clear the floor (final net)<br/>scrub the seven AI tells"]
  i --> j["Self-check the mechanics"]
  j --> k["Reader trial<br/>fresh-context subagent: document + reader only"]
  k -->|"stumble or unneeded content"| l["Fix, re-run steps 10–11"]
  l --> j
  k -->|"clean pass"| m["Deliver<br/>document + what-changed note"]
  b -. "admission gate<br/>(headings, points, rendering, ceiling)" .-> c
  b -. .-> d
  b -. .-> g
  b -. .-> h
```

## 4. Detailed design

### 4.1 What does the process/output-rules separation guarantee, and how is a breach caught?

Guarantees that a rule about the *produced document* (e.g. "render structure/flow as mermaid") is
never misread as a property of the *prompt itself* — the original SKILL.md embedded a procedure
flowchart in its own body, which was exactly this category error (D-3). §Reference carries an
explicit addressee sentence stating its rules target the produced document. A breach — a diagram or
output-only rule creeping back into the process layer, or the addressee sentence going missing — is
caught by the acceptance criteria's Level A check that no mermaid diagram is embedded in the prompt
body.

### 4.2 What does the floor-as-final-net ordering guarantee, and how is a breach caught?

Guarantees that ceiling work (density, concreteness, one thread, earned figures, consistent voice —
step 8) is never wasted by being layered onto a draft's uncleared AI tells, without paying the cost
of a separate pre-scrub pass: because the document is rebuilt fresh rather than edited in place, the
old draft's tells do not propagate into the new prose to begin with, so the floor pass (step 9) only
has to catch stragglers introduced during writing, not the input's original problems. A breach — a
tell surviving into the delivered document — is caught by step 10's self-check, which re-verifies
"none of the seven tells remain" before delivery, and by the what-changed note's closing line naming
any tell the net caught.

### 4.3 What does the five-axis, single-axis outline guarantee, and how is a breach caught?

Guarantees the document has one coherent shape suited to how its reader actually reads (through, or
looking one thing up) rather than a blend of incompatible structures. Guaranteed by step 3 ("exactly
one axis... off-axis material stays out"). A breach — a document mixing axes, or carrying off-axis
material — is caught by step 10's self-check item "Single axis (step 3), no mixing," and off-axis
material is named (not authored) in the what-changed note.

### 4.4 What does the reader-definition gate guarantee, and how is a breach caught?

Guarantees voice, form, and axis are derived from an actual reader rather than assumed or memorized —
the acceptance criteria specifically require that two different reader definitions change the
output's voice and axis, proving derivation rather than memorization (D-6's five-axis re-sourcing
exists in service of this same guarantee: the skeletons come from external best practice, not from
`instruction.md`'s fixed wording). Guaranteed by step 2's gate: "if a line cannot be answered from the
input, ask the user" (or, headless, infer and disclose via `Assumed reader: …`) — never leave a line
blank. A breach — an inferred-but-undisclosed reader, or a document whose voice/axis does not track
its stated reader — is caught by step 10's self-check items "Assumed reader: line present iff the
reader was inferred" and "Voice and closing fit the step-2 reader."

### 4.5 What does reader-gated content admission guarantee, and how is a breach caught?

Guarantees that no sentence ships because someone once wanted it there. The step-2 reader is not
only the source of voice and axis (4.4) but the **admission criterion for content**: a heading
(step 3), a point (step 4), a sentence that first appears at rendering (step 7), or an example added
while reaching for the ceiling (step 8) enters only if that reader needs it to reach the purpose.
Material serving a different reader — a re-reader, a past reviewer, an approver — is routed to the
what-changed note (whose it is, where it belongs) instead of shipping as noise. A user-supplied
outline or format faces the same test slot by slot: an unjustifiable slot is an axis conflict, raised
with the user (headless: recorded in the note) and never silently filled. A breach — noise surviving
into the delivered document — is caught twice: by step 10's admission self-check item, and by the
step-11 reader trial reporting content it did not need.

Origin: a real run (PR #15 comment 5353396410) delivered a document its owner judged noise-ridden
while every writ check passed — because the reader governed only form, so content for other readers
passed straight through.

### 4.6 What does verification independence guarantee, and how is a breach caught?

Guarantees that the experiential claims — the document reaches the purpose read top to bottom, and
the headings alone carry the argument — are judged by someone the curse of knowledge cannot blind.
The author, having built the outline, cannot un-know it, so those two checks move out of step 10 and
into step 11: a fresh-context subagent given **only** the produced document and the step-2 reader
definition — no outline, no draft, no history. Its clean pass gates delivery; stumbles come back as
fixes and the document re-runs steps 10–11. Mechanical checks (single axis, `Assumed reader:` line,
claim statuses) stay with the author, where knowledge of the draft is no handicap. A breach — the
trial run with extra context, or its stumbles waved through — shows up as the same field failure 4.5
records: checks pass, the reader still struggles.

## 5. Alternatives considered

### 5.1 Why this shape, and not another?

- **(D-1) Plugin `writ` / skill `up`, not matching names** — chosen over the official same-name
  convention, because the skill name is typed often (keep it short) and plugin/skill names are
  independent slots (`rn:gm` is the precedent); "up" fits the primary brush-up-a-level mode.
- **(D-2) Model-invocable (no `disable-model-invocation`)** — chosen over `rn`'s pattern of disabling
  model invocation, because the distinguishing axis is who the skill is for, not side effects: `rn`
  is meant for a human to drive, `up` is meant for a human or Claude itself.
- **(D-3) Two layers physically separated in the body** — chosen over the original SKILL.md, which
  embedded a procedure flowchart in the prompt body (see 4.1).
- **(D-5) Rebuild fresh from the input's intent, floor as a final net** — chosen over an edit-the-
  draft-in-place runbook (scrub first, reorder later), which drags the old wording along, reads as
  patched, and behaves as a checklist rather than a writing procedure.
- **(D-6) Five-axis skeletons re-sourced to researched best practice** — chosen over `instruction.md`'s
  verbatim outlines, per the user's ask for the current recommended structures. Source of truth:
  Diátaxis (explanation/reference/tutorials), MADR 4.0, AWS ADR guidance, Google/Microsoft procedure
  style guides, GitLab task types, and Google SRE postmortems — not `instruction.md`. `instruction.md`
  stays the source of record for the other pillars; only the five skeletons deviate.
- **(D-7) Renamed `techting` → `writ`, skill stays `up`** — chosen over keeping the name and just
  rewording the framing, because the plugin name itself was the one thing still narrowing scope to
  "technical" writing. D-6's sourcing already showed the five axes are general document genres, not
  technical-writing-specific — the mechanism was general from the start; only the label lagged.
  `writ` + skill `up` gives `/writ:up`, read as "write it up", with no redundant "up up".
- **(D-8) The reader gates content, and a fresh reader gates delivery** — chosen over adding more
  checks to the author's own self-check list, after a real run (PR #15) shipped a noise-ridden
  document with every check passing. Two structural changes rather than nets: the step-2 reader
  becomes the admission criterion for content, not just the source of voice and axis (4.5), and the
  experiential checks move to a fresh-context subagent whose pass gates delivery (4.6). Consequence:
  the ceiling's target is restated as minimal reader effort to the purpose, with density demoted to a
  means.

### 5.2 What did we trade away?

- **(D-4) Purpose reframed as a human-readable end, quality in two tiers** — chosen over treating
  "reader-first procedure" as the end goal in itself; the procedure is the *means*, not the point.
  Traded away: a simpler one-tier "just make it good" bar, in exchange for an explicit floor/ceiling
  split that makes "cleared but unremarkable" a distinct, nameable state from "actually worth
  reading."
- Choosing a single inline `SKILL.md` (2.2) over a `references/`-split structure trades some
  file-size headroom (capped at <2,000 words) for a self-contained skill that reads start to finish
  without following links — appropriate while the procedure is one continuous flow, at the cost of
  needing to re-split if it grows substantially.
- Re-sourcing the five axes to external best practice (D-6) trades fidelity to the user's original
  verbatim `instruction.md` outlines for current, externally-validated structures — accepted because
  the user explicitly asked for the current recommended shapes over the original wording.
