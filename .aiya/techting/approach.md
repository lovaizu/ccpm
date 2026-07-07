# techting dogfood — approach

Drafted by the Conductor from the approved `goal.md`. Throwaway build — nothing here ships; this
plugin lands at `.aiya/techting/build/techting/`, never over any real `techting`/`writ` location.

## Testing

Acceptance Scenarios are the goal.md Acceptance-criteria bullets, fixed now, before any Step runs:

1. `techting/skills/up/SKILL.md` exists; carries reader definition, five outline axes, pre-output
   self-check; separates §process from §output-rules with an explicit addressee sentence in
   §output-rules; body <2,000 words, imperative; no mermaid diagram embedded in the prompt body.
2. The process instructs floor-then-ceiling order and names the floor checklist; §output-rules states
   both tiers (floor = tells absent; ceiling = density/concreteness/single thread/earned diagrams-
   lists/consistent voice).
3. Running `up` on a draft (dogfood-verified, not asserted): output shows structure/flow as mermaid
   wherever there is order/branching, no diagram/prose duplication; two different reader definitions
   change voice and axis; each output holds a single axis.
4. Floor is cleared before ceiling: output carries none of the named AI tells; the "what changed and
   why" report separates floor fixes from ceiling lifts, in that order.
5. Brush-up use case stated explicitly (input = draft, output = revision + changed-and-why report).
6. Frontmatter is model-invocable, description fires for human or Claude-self-invocation.
7. `plugin.json` has name/description/version(semver)/author; version lives only there.
8. `README.md` exists, scenario + real-console style, shows `/techting:up`.
9. `marketplace.json` (root, this repo's own) + root `README.md` both list techting, in sync.
10. `claude plugin validate ./techting --strict` and `claude plugin validate . --strict` — wait, this
    build is throwaway and not registered in the *real* marketplace; validate `./techting` alone
    (the throwaway plugin standing on its own), skip the repo-root pass (that would falsely touch
    ccpm's real marketplace.json). Recorded as an honest scope reduction in `dogfood.md`.
11. `claude -p "/techting:up …" --plugin-dir ./techting` loads the skill and starts the brush-up
    procedure, confirmed headlessly.
12. All shipped artifacts in English.

**How each is checked (test-first, mechanical where possible):** 1/2/6/7/8/9/12 are static-artifact
checks (read the file, grep for the required elements) — an LLM verify-Turn judgment, since there is no
mechanical parser for prose shape. 3/4/5 are **simulated**: a verify-Turn actually invokes the produced
`/techting:up` on two small fixture drafts with two different stated reader definitions and inspects
the two real outputs — not judged by appearance. 10/11 are mechanical (`claude plugin validate`,
`claude -p`), run and their exit status recorded.

**Sealed-reference rule (Conductor's own testing discipline, not a goal.md requirement):** a hand-built
predecessor already exists at `.claude/worktrees/techting/writ/` (branch `worktree-writ`, plugin
currently named `writ`, PR #5 closed unmerged). The Conductor and every Turn build **from goal.md
alone** and do not open `writ/`'s `SKILL.md` or `README.md` content until every Step has closed —
opening it earlier would let the hand-built solution leak into generation, defeating the point of the
dogfood (does aiya *derive* the plugin, not copy an answer key). The delta comparison in `dogfood.md`
is the first time that content gets read.

## Technology

- A single Claude Code plugin, one skill (`up`), Markdown-only — no JS orchestration, matching this
  repo's own `.claude/rules/plugin.md` conventions (version lives only in `plugin.json`; CHANGELOG in
  Keep-a-Changelog form; marketplace entry `name`/`description`/`source`/`category`).
- Built at `.aiya/techting/build/techting/` (throwaway root), with a throwaway
  `.aiya/techting/build/.claude-plugin/marketplace.json` + `.aiya/techting/build/README.md` standing in
  for "the repo's own marketplace/root README" for scenario 9/10 above — never the real
  `ccpm/.claude-plugin/marketplace.json` or `ccpm/README.md`.
- `claude plugin validate` / `claude -p --plugin-dir` run against that throwaway root.

## Design

- `techting/skills/up/SKILL.md` — the one deliverable prompt. Two layers per goal.md: §process
  (imperative instructions to the model running the skill: define the reader, floor-then-ceiling
  order, the five outline axes, the pre-output self-check) and §output-rules (constraints on the
  *produced* document, opening with an explicit addressee sentence — e.g. "These rules govern the
  document `up` produces, not this prompt" — covering both quality tiers, the mermaid-for-structure
  rule, and single-axis).
- `techting/README.md` — scenario + real-console style per this repo's own README convention.
- `techting/.claude-plugin/plugin.json`, `techting/CHANGELOG.md` — packaging, mirroring aiya's own
  task #4 shape (already-proven pattern in this same repo).
- `techting/.claude-plugin/marketplace.json` (throwaway root's own) + throwaway root `README.md` — the
  registration pair, kept in sync in the same Step.

## Constraints fed to every Turn

- Never write outside `.aiya/techting/`.
- Never open `.claude/worktrees/techting/writ/**` until instructed post-Step-loop (sealed-reference
  rule above).
- English for all shipped artifact content (goal.md's own rule, carried through).
