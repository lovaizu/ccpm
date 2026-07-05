# Goal

Add a new ccpm project rule — `.claude/rules/output.md` — that defines the **output convention**
for how the assistant produces responses in this repository: conclusion-first structure, brevity by
default, concrete over abstract, a banned-phrases list, a constrained Plan-output shape, code/file
citation discipline, and verification honesty. The convention is declared to take precedence over
generic system-prompt output-efficiency guidance, while staying subordinate to explicit in-the-moment
user instruction. Written in English and in the same style as the existing rule files, so it loads and
reads as a peer of `language.md` / `plugin.md` / `marketplace.md`.

# Acceptance criteria

Goal alignment — the rule captures the user's spec faithfully:

- `.claude/rules/output.md` exists and is committed.
- **Structure** encoded: responses ordered conclusion → rationale → next action; normal replies
  default to ≤3 sentences (details/background only when explicitly asked); composition is skimmable —
  reading the headings top-to-bottom conveys the thread.
- **Banned expressions** encoded: abstract preambles ("詳細に分析" / "包括的に" / "総合的に" and
  their English equivalents); sycophantic praise openers ("素晴らしい指摘です"-type); reworded
  repetition of the same content; defensive justification.
- **Plan output** encoded: ≤200 words; each item in What (target file/command) / Where (`path:line`)
  / Why (≤20 chars) form; headings no deeper than h3.
- **Code & files** encoded: code examples ≤10 lines (else narrow the target or split to a file);
  cite already-shown files by `name:line` instead of re-pasting; offer one alternative before saying
  "can't".
- **Verification** encoded: confirm real artifacts rather than guess; check all items, not a sample;
  state the scope checked when reporting.
- **Precedence** stated: this convention governs assistant responses in this repo and overrides
  generic output-efficiency guidance; it yields to an explicit user instruction in the moment.

Quality:

- Written in English (per `language.md`); H1 is `# Output convention (ccpm)`; uses the existing
  rule-file style — bold lead-ins and `Rationale:` lines.
- Intent-first: each rule leads with the principle and why; numeric limits appear as the concrete bar,
  not as a bare list of numbers.
- Composes with `language.md` without conflict — the file notes explicitly that language *choice*
  comes from `language.md` while *structure and density* come from this rule.
- No other file requires changing for the rule to take effect (verified: rules auto-load by directory;
  the root `README.md` lists plugins, not rules).

# Assumptions

- **Fact** (verified): `.claude/rules/*.md` load as project instructions with no CLAUDE.md, no
  `settings.json`, and no reference to `rules/` anywhere in the repo — confirmed by search. A new file
  in that directory is therefore sufficient; there is nothing to register.
- **Fact** (verified): `language.md` requires English for rule files. The file is written in English;
  the user's Japanese trigger words are kept verbatim as illustrative examples of banned phrases.
- **Assumption**: the user wants this as a persistent ccpm project rule governing assistant output
  when working in this repo — not a one-off instruction for this session.
- **Assumption** (unverified): the numeric limits (≤3 sentences, ≤200 words, ≤10 lines, ≤20 chars)
  are the intended concrete *bar*, written as defaults the principle justifies — not inviolable hard
  fails in every edge case. If the user wants them as absolute hard limits, the wording tightens.

# Rules

- 1 task = 1 commit
- English per `language.md`; match the existing rule-file style (`# … (ccpm)`, bold lead-ins,
  `Rationale:` lines)
- Faithful to the user's spec — preserve full intent, add no scope

# Tasks

### #1: Write `.claude/rules/output.md`

**Purpose**: Author the output-convention rule file capturing every section of the user's spec,
intent-first and in the existing rule-file style, so it auto-loads as a ccpm project rule.

**Prerequisites**: none

**Steps**:

- [x] Draft `.claude/rules/output.md` with `# Output convention (ccpm)` and sections: Structure,
      Banned expressions, Plan output, Code & files, Verification, Precedence
- [x] Lead each rule with its principle + `Rationale:`; keep the numeric limits as the bar
- [x] Add the composition note tying language choice to `language.md`, density to this rule
- [x] Re-read `language.md` to confirm no conflict (language vs structure are orthogonal)
- [x] self-check (OK/NG per completion criterion, record in checks/1.md)
- [x] QA expert review (subagent) — 2 iterations; proper-form pass after user challenge
- [x] language expert review — N/A (non-code; prose craft folded into QA)
- [x] user review — on PR #9

**Completion criteria**:

- `.claude/rules/output.md` exists, in English, titled `# Output convention (ccpm)`, in the existing
  rule-file style
- Every Acceptance-criteria item under "Structure / Banned / Plan / Code & files / Verification /
  Precedence" is present in the file
- The file states its precedence over generic output-efficiency guidance and its subordination to
  explicit user instruction
- The composition note with `language.md` is present
- No file other than `.claude/rules/output.md` is added or modified to make the rule take effect

### #2: Write `.claude/rules/push-and-review.md`

**Purpose**: Add a process rule capturing two working conventions the user asked for — push on every
change, and conduct user review/approval on the PR rather than the console.

**Prerequisites**: none

**Steps**:

- [x] Draft `.claude/rules/push-and-review.md` with `# Push and review (ccpm)`, sections: Push on
      every change; Review happens on the PR
- [x] Note how it composes with the `rn` console review gate (gate moves to the PR)
- [x] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review — folded into PR review per the new rule
- [x] user review — on PR #9

**Completion criteria**:

- `.claude/rules/push-and-review.md` exists, English, titled `# Push and review (ccpm)`, existing
  rule-file style
- Encodes "commit and push on every change, without asking first"
- Encodes "user review and approval happen on the PR, not the console", and states how it relocates a
  workflow's console review gate
- No file other than the rule file is added or modified for it to take effect

# Decisions

## D-1: User review moves from the console to the PR; changes are pushed on every commit
- **Issue**: rn's task-workflow gates each task with a console user-review before commit/push. The user
  wants changes pushed as they happen and confirmation done on the PR instead.
- **Conclusion**: Push every commit immediately; conduct user review/approval on PR #9. The task
  boundary gate still exists — it relocates to the PR. Codified as `.claude/rules/push-and-review.md`.
- **Rationale**: The PR renders real artifacts (diffs, long docs, figures) that the console cannot;
  relocating the gate preserves the step-in point while reviewing the rendered form. Pushing on change
  keeps the shared branch the single source of truth.
- **Evidence**: User instruction "変更したらプッシュする / ユーザー確認はPRで行う"; matches working-style
  memory (push-without-asking, review-rendered-artifacts-on-pr).
- **Sources**: This session's conversation; `.claude/rules/push-and-review.md`.

# State

(written by /rn:bb, read and reset to this placeholder by /rn:hi)

- **Status**: not suspended
- **Date**: 2026-06-15
- **Last completed**: #2 Write `.claude/rules/push-and-review.md`
- **Next**: none — all tasks done; propose running Acceptance criteria
- **Notes**: on branch `worktree-output-rule`; slug `output-rule`; review on PR #9
