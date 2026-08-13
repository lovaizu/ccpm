# techting — requirements (the goal the AIYA core converges on)

> **Provenance.** Extracted verbatim from the sibling worktree
> `.claude/worktrees/techting/.rn/techting/steering.md` (branch `worktree-techting`, PR #5).
> **Requirements only** — the `Goal` and `Acceptance criteria` sections. The solution path
> (`Tasks`, `Decisions` D-1..D-4, the existing `techting/skills/up/SKILL.md`, packaging) is
> **deliberately left behind** so the AIYA core derives the path from the goal rather than being
> handed it. The verbatim original instruction stays at the techting worktree's
> `.rn/techting/instruction.md` (Japanese, source of record) if the core needs to consult it.
>
> This file is the **goal-derived simulation input** for the core's first real end-to-end run
> (`aiya/docs/design.md` §4.2, test-first simulation): the acceptance criteria below are the success
> scenarios, fixed before generation.

# Goal

Make a document read as if a person wrote it — not an AI — so the reader takes it in with the least
effort. Package this as a Claude Code plugin `techting` (skill `up`, invoked `/techting:up`) so the
procedure can be applied on demand to any draft, by a human or by Claude itself. Primary mode is
brushing up an existing draft; authoring from scratch runs through the same procedure but is
secondary. The verbatim instruction is preserved at `.rn/techting/instruction.md` as the source of
record, and the skill body is derived from it.

**Purpose (the end):** a human-readable document. Concretely — the reader's cognitive load is low,
it goes in when read top to bottom, and its structure is graspable at a glance through diagrams and
lists.

**Quality, in two tiers:**

- **Floor — table-stakes quality (b):** clearing it earns no praise, but failing it instantly reads
  as "an AI wrote this." Scrub the fingerprints: padding and throat-clearing, restatement, retreat
  into generalities, flavorless connectives, reflexive bulleting, a wavering voice.
- **Ceiling — attractive quality (a):** on a cleared floor, what makes it worth reading — density,
  concreteness (names, numbers, examples), a single load-bearing thread (conclusion first), diagrams
  and lists that earn their place, a consistent voice. Adding ceiling onto an uncleared floor is
  wasted.

So the skill works in that order: **first clear the floor** (inspect and remove the AI tells), **then
reach for the ceiling** (derive and add the attractive qualities).

**Means (not the end):** reader-first derivation — define the reader (who they are / what they must
decide or do / how they read), then derive the axis, voice, and structure from that definition
rather than from memory.

# Acceptance criteria

- **Level A — the `SKILL.md` artifact (the prompt itself):** `techting/skills/up/SKILL.md` exists
  and carries all source intent — reader definition (who / what they must decide-or-do / how they
  read), the five outline axes (article, guide, reference, record-ADR, evaluation), and a pre-output
  self-check. The body separates two layers: **process** (instructions to the model running the
  skill) from **output rules** (constraints on the produced document), with the §output-rules layer
  carrying an explicit addressee sentence stating its rules target the produced document, not this
  prompt. The body is imperative and lean (<2,000 words). **No mermaid diagram is embedded in the
  prompt body** (and none is required by these criteria) — the mermaid rule lives only in
  §output-rules as a directive to the produced document.
- **Level A — the two-tier quality is encoded:** the process instructs the **floor-then-ceiling
  order** — first inspect the draft and remove the AI tells (the floor), then derive and add the
  attractive qualities (the ceiling) — and names the floor checklist (padding / throat-clearing,
  restatement, retreat into generalities, flavorless connectives, reflexive bulleting, a wavering
  voice). The §output-rules layer states **both tiers**: floor (b) = none of those AI tells present;
  ceiling (a) = density, concreteness (names / numbers / examples), a single load-bearing thread
  (conclusion first), diagrams and lists that earn their place, a consistent voice.
- **Level B — the document the skill produces (dogfood-verified):** running `up` on a draft yields
  output whose structure/flow is shown as mermaid wherever there is order or branching, with no
  diagram/prose duplication; feeding two different reader definitions changes the output's voice and
  axis (proving the procedure derives, not memorizes); each produced document holds a single axis,
  not mixed.
- **Level B — the floor is cleared before the ceiling is reached:** the produced document carries
  none of the named AI tells (floor cleared), and the "what was changed and why" report separates
  **floor fixes** (AI tells removed) from **ceiling lifts** (attractive qualities added), in that
  order.
- The skill states the brush-up use case explicitly: input = an existing draft, output = the
  revised document plus "what was changed and why" (the latter split into floor fixes then ceiling
  lifts).
- The SKILL.md frontmatter is model-invocable (no `disable-model-invocation`) and its description is
  written so it can fire for a human or for Claude itself.
- `techting/.claude-plugin/plugin.json` has name, description, version (semver), and author, and the
  version lives only in plugin.json (no version field in marketplace.json).
- `techting/README.md` exists and shows how to use `/techting:up` in a scenario + real-console style.
- `.claude-plugin/marketplace.json` has a techting entry (name / description / source `./techting` /
  category) and the root `README.md` Plugins list also links to techting (the two stay in sync).
- `claude plugin validate ./techting --strict` and `claude plugin validate . --strict` both pass.
- `claude -p "/techting:up …" --plugin-dir ./techting` loads the skill and starts the brush-up
  procedure, confirmed headlessly.
- All shipped artifacts (plugin.json / SKILL.md / README / commit messages / PR) are in English.
