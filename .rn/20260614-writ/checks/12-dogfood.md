# Task #12 dogfood — `/writ:up` run against `.claude/rules/plugin.md`

Run by the task-#12 implementer against the rebuilt `writ/skills/up/SKILL.md`, following the body top
to bottom. Input: `.claude/rules/plugin.md`, 830 words. Three fresh-context subagent reader trials ran
— the step-11 cap — each given only the produced document and the step-2 reader definition, and the
run ended on a trial rather than on an edit.

---

## The run

### Step 1 — Understand the input

`Subject:` how a plugin in the ccpm repo carries its version — where the number lives, what earns a
changelog line, and what a release does.
`Must convey:` a user-facing change does not bump the version; only an explicit release instruction
does, and the release is a fixed hand-off in which the assistant does every step except the merge.
`Proposed, not in force:` none. Every rule in the input is in force — it is a checked-in project
instruction, and its own header cites the official docs as its source.

### Step 2 — Define the reader and the purpose

The input names no reader, so the gate fired and this headless run inferred one; the delivered
document carries the `Assumed reader:` line.

- WHO: an assistant working in ccpm that has just changed a plugin, or been told to cut a release.
- WHAT they must decide or do: whether this change touches `version`, what line it earns in the
  CHANGELOG and where that line goes, and — on a release instruction — which steps are theirs.
- HOW they read: looking one thing up at the moment of the change, not straight through.

### Step 3 — Build the outline from the purpose

Read `references/axes.md`. Reader looks things up → **Reference** axis: the map / each element /
errors and terms.

Two-axis offer, made and declined: the release hand-off is an ordered sequence, which reads like the
guide axis. It is not a second part — the same person in the same stance looks up who does what,
rather than following along live with the document open. One axis, no composite.

*Slot → reader.* Three slots, all admitted.

*Reader → slot.* Where the number lives → the map; whether this change bumps it → `version`; what the
changelog line says and where it goes → `CHANGELOG.md`; who does what on a release → the release
steps; what must pass → validation gate. No unslotted need found at this step; one surfaced at trial
round 3 and is raised as a proposed slot in the note.

### Step 5 — Story check

One re-fill against the input: the semver increment bullets had been transcribed near-verbatim
(`major (1.0.0 → 2.0.0) — a breaking change: an existing command/skill is removed or renamed`) and
were re-written from meaning before any rendering happened.

### Step 6 — Voice and form

`Voice: uniqueness and coverage first; no warmth, no intros / Closing: none.`

Form: a table for the three artifacts (same fields compared), a numbered list for the release
hand-off (parallel, order-bearing), prose elsewhere. **No mermaid** — the only flow is a four-step
linear hand-off and one binary condition, both of which a sentence carries faster than a figure.

### Step 10 — Self-check the mechanics (final pass)

| Item | Verdict |
|---|---|
| Reader is one person in one reading stance | PASS |
| One axis, no mixing | PASS — Reference; the guide reading was offered and declined at step 3 |
| Nothing carried over but names, identifiers, defined terms, deliberate quotation | PASS — side-by-side re-read; carryover is limited to identifiers (`plugin.json`, `## [Unreleased]`, `--strict`, `rn-v0.2.0`) and the Keep a Changelog link |
| Every heading and point admitted; every reader need carried by a slot | PASS at authoring; one unslotted need found at trial (see the proposed slot in the note) |
| Form fits content | PASS |
| No prose repeats what a diagram carries | PASS — no diagram |
| Voice and closing fit the reader | PASS |
| None of the seven tells remain | PARTIAL — restatement between the table and the body survives, named in the note |
| `Assumed reader:` present iff inferred | PASS — inferred, and present |
| Produced size against the input's recorded | 830 → 495 words, 0.60×. The shrink is the step-3 admission removing rationale aimed at a reader deciding whether to adopt these rules, inside a document whose reader has already adopted them; each cut is named in the note |
| Every claim carries its status | PASS — all in force; the two ccpm decisions (setting `version` at all; the tag prefix) are written as choices |

---

## The delivered document

`Assumed reader: an assistant in ccpm that has just changed a plugin, or been told to cut a release / decides whether the change touches `version`, what the CHANGELOG records and where, and which release steps are the assistant's / looks one thing up at the moment of the change.`

> # Plugin versioning and release (ccpm)
>
> ## Three artifacts, three moments
>
> | Artifact | Holds | Written when |
> |---|---|---|
> | `<plugin>/.claude-plugin/plugin.json` | the `version` field — the only place a version lives | on a release instruction, never otherwise |
> | `<plugin>/CHANGELOG.md` | what changed, in the user's terms | on every user-impacting change; a release renames its top heading |
> | annotated git tag + GitHub Release on `main` | which commit is which version, and when | after the user merges |
>
> ## `version`
>
> Write it in `plugin.json` and nowhere else. `marketplace.json` carries no `version`, and one written
> there is ignored. Always set it, as semver; `claude plugin validate --strict` fails on an unset
> version.
>
> It rises only on a **release instruction** — the user asking for a version to be cut. Until then the
> change waits under `## [Unreleased]` and `plugin.json` stays put.
>
> ## `CHANGELOG.md`
>
> It sits in the plugin root, in [Keep a Changelog](https://keepachangelog.com) format:
> reverse-chronological, `## [Unreleased]` on top while anything is pending, then one
> `## [x.y.z] - YYYY-MM-DD` section per release. Group lines under `Added`, `Changed`, `Fixed`,
> `Removed` — only the groups that apply.
>
> A change earns a line when a user would notice it: a command or skill behaving differently, arriving,
> or leaving, or a change to what the user reads and approves. Typo fixes, refactors, internal docs and
> formatting earn none.
>
> Each line reads `<what changed> — <why it helps the user>`, in words the user would use.
>
> The line goes under `## [Unreleased]`. Re-create that heading at the top if the previous action was a
> release and it is absent.
>
> ## The release, step by step
>
> Every step is the assistant's except the merge. `main` is protected and only the user holds the
> privileges to clear its required review.
>
> 1. **Assistant** — size the increment, bump `version` to it, rename `## [Unreleased]` to
>    `## [x.y.z] - YYYY-MM-DD` and leave no empty `## [Unreleased]` behind, commit, push. Size by the
>    largest change in the release, as the user experiences it:
>    - **major** — something they do today stops working: a command or skill removed or renamed, or
>      its inputs or behavior changed out from under them.
>    - **minor** — something is new or different, and everything they already do still works.
>    - **patch** — nothing they can see changes: wording, docs, internal refactors.
>
>    Below `1.0.0`, a change that would be major takes minor instead.
> 2. **Assistant** — ask the user to merge the PR. Never merge `main`; never `--admin`.
> 3. **User** — merges, and says so.
> 4. **Assistant** — once told the merge is done, tag `main` with an annotated `<plugin>-v<version>`
>    (`rn-v0.2.0`), and publish a GitHub Release against it with the matching CHANGELOG section as the
>    notes.
>
> ## Validation gate
>
> Both strict validations must pass:
>
> ```bash
> claude plugin validate <plugin-path> --strict
> claude plugin validate <marketplace-root> --strict
> ```
>
> Then confirm behavior headlessly — the skill namespace is the plugin name:
>
> ```bash
> claude -p "/<plugin>:<skill>" --plugin-dir <plugin-path>
> ```

---

## Step 11 — Reader trials

Three rounds, three fresh subagents, each given only the document and the reader definition.

| Round | Purpose reached | Headings carry it | Stumbles reported |
|---|---|---|---|
| 1 | 2 of 3 clean, 1 assembled across sections | "mostly yes"; two headings named as contentless | ~14, incl. a "What goes wrong" table where 5 of 6 rows restated earlier prose |
| 2 | 2 of 3 clean; the increment rules unreachable at change time | "partly" — three bare-noun headings | ~11, incl. the version rule stated four times |
| 3 | 2 of 3 clean; the release steps partly | "yes, mostly, and better than most" | 12, all structural or local; explicitly "no abstract preambles, no throat-clearing" |

**Prose defects fixed** between rounds: the restating error table (cut), the orphan definition of
"release instruction" (folded into its one statement), the contentless "The map" heading, the
redundant "Tag and Release" section (folded into step 4), the non-parallel increment bullets, two
drifting-voice phrases, a map row that disagreed with the body, and the missing "once told the merge
is done" trigger on step 4.

**Prose defects surviving the three-round cap, shipped named** (step 11: a defect that survives three
rewrites is not going to be fixed by a fourth):

- The semver sizing rules are reachable only by reading the release section through — no heading
  names them. Raised as a **proposed slot** below.
- Step 1 welds five actions into one 40-word sentence.
- The table restates the body on three points (where `version` lives, the heading rename, the merge
  hand-off).
- "Re-create that heading at the top if the previous action was a release and it is absent" — the
  pronoun is ambiguous and the two conditions are redundant.
- Semver is the one format given with no example; `--admin` is used and never expanded; the full path
  `<plugin>/.claude-plugin/plugin.json` appears only in the table.
- Cutting "pre-1.0 promises no stability" at round 3 made the `0.x` exception read as arbitrary to the
  round-3 reader — an over-reach of the admission test, and the one cut this run got wrong.

**Subject defects — named for whoever owns `.claude/rules/plugin.md`, not patched:**

1. **A patch release has an empty changelog.** `patch` is defined as "wording, docs, internal
   refactors"; the CHANGELOG rule says typo fixes, refactors, internal docs and formatting "earn
   none". The rule never reconciles the two, so an assistant asked to cut a patch release has a
   version section with nothing under it. Found by the round-1 reader, verbatim: "I get 'it's a patch'
   from one section and 'write nothing' from the other."
2. **The validation gate has no trigger and no pass criterion.** The rule says both strict validations
   "must pass" and to "confirm behavior headlessly", but never says when the gate applies (every
   change, or only a release) or what in the headless output counts as confirmation. Reported
   independently by the round-1 and round-3 readers.
3. **The rule set is split and neither half says so.** A reader who has just renamed a plugin finishes
   `plugin.md` unsure whether `marketplace.json` and the root README are theirs to update; that
   obligation lives in `.claude/rules/marketplace.md`, which this document never names.

**Proposed slot** (step 3, raised from the round-3 trial, with the reader's own words as evidence):
"How much to bump" belongs as its own heading, not as sub-bullets inside release step 1. Evidence —
"if I arrive asking only 'is this minor or patch?', there is no heading that says so … This is the one
thing I could not look up." The supplied shape had no slot for it; it ships named rather than buried.

---

## What-changed note

**Structure.** The input ran in the order it was written: version number, changelog, release
procedure, tags, validation. This reader looks things up, so the document opens with the three
artifacts and when each is written — the fastest answer to "where does this live" — then gives each
artifact one section, in the order a change touches them. The tag-naming section folded into release
step 4, where the tag is actually typed.

**Story.** One condition governs nearly everything this reader decides — was a release instructed —
and the input stated it in three places. It is stated once, under `version`.

**Voice.** Uniqueness and coverage first, no intros, no closing: this reader arrives mid-task with a
question and leaves when it is answered.

**Kept out, and whose it is.** The `plugin.json` → marketplace → commit-SHA resolution order, and the
marketplace's top-level `version` being manifest metadata (serves someone auditing whether the rule is
right, not someone following it). The road not taken — omitting `version` so every commit is a
release (serves whoever argued the decision). The Lerna and Go naming precedents (serve the author
defending the `-` separator). "Read release timing from tags, not merge commits" (serves a reader
doing release archaeology, not one mid-change). The provenance header (serves the document's
reviewer). All belong in the design rationale for these rules, not in the rules a reader follows.

**Tells the final net caught.** Two, both introduced at rendering rather than carried over: a hedged
"generally" in the increment bullets, rewritten as the flat condition it is, and a restatement of the
release-instruction rule inside the tag section, cut.

**Size.** 830 → 495 words, 0.60×. No growth to argue for; the shrink is the admission test removing
adoption-time rationale from a document whose reader has already adopted the rules.

**Unverified at delivery.** Nothing. Round 3 was a trial, not an edit, so every passage in the
delivered document has been read by a fresh reader.
