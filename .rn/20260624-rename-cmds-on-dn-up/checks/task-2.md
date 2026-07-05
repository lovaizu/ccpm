# task-2 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| No token rdy/brb/bak remains under rn/references/ | OK | `grep -rnE '\b(rdy\|brb\|bak)\b' rn/references/` returns zero matches (exit=1) | OK | word-boundary + case-insensitive substring sweeps both zero |
| Each updated sentence reads correctly with the new command name (no dangling reference) | OK | steering-template.md L67-68: "written by /rn:dn, read and reset ... by /rn:up", "the signal /rn:up and /rn:dn search for". task-workflow.md L4: "`on` and `up` read this file", L214: "what `/rn:up` matches against `git log`" — all read coherently | OK | mapping verified against skill roles: dn=suspend(writes), up=resume(reads); on/up read task-workflow; skills on/dn/up exist on disk |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK | grep sweep zero; each substitution validated semantically against the real skill roles, not just non-empty |
| Edge case coverage | OK | checked for reversed write/read mapping and wrong-target swaps (e.g. dn vs up at line 4) — none |

## Expert Reviews (code changes only)

### Language Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Best practices | OK | tokens uniform `/rn:on` `/rn:dn` `/rn:up` (bare `on`/`up`); em-dashes/backticks intact |
| Codebase style consistency | OK | surgical: only 4 tokens on 3 hunks changed; surrounding prose byte-identical |
| GWT test format | N/A | docs, no test code |

### Software-engineering Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Separation of concerns | OK | change confined to the two reference files; no collateral logic change |
| System integrity | OK | runtime contract correct — State note: dn writes / up reads; task-workflow names on+up; 214 matcher = /rn:up |
| Maintainability | OK | new tokens match real skill dirs rn/skills/{on,dn,up}; no dangling refs |

## Overall Verdict

- Self-check: OK
- QA: OK
- Language expert: OK
- Software-engineering expert: OK
- Ready for user review: Yes
