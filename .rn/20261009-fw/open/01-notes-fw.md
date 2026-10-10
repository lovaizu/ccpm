# Where turn and ben stand

pith, writ and rn are rebuilt one at a time, each in its own pull request: #51 (PR #55) first, then
#52 pith, #53 writ, #54 rn. The older issues are judged once their plugin is rebuilt: #35 in #52;
#36, #37 in #53; #39, #41, #43-#46 in #54. Work before is in the closed PR #50 (b504cf1), material only.

## #51, PR #55: rebuilt from zero

- The user stopped the built turn and ben (4c571ba and before): built by delegating to workers who
  patched to pass flow checks. Now: README and design are the source; the implementation realizes
  them, minimal; checked with ben; a shortfall is traced through the JSONL to its cause, never
  patched. I judge; workers only report facts and do decided fixes. The old code is material only.
- Order: ben README + design, turn README + design (Japanese for review) → the user approves on
  PR #55 → minimal implementation → ben checks → English before merge → the user merges.
- Done: ben/README.md, turn/README.md, dev/ben/design.md, dev/turn/design.md written, read by writ
  first users, and their fixes applied. In ben, 成果物 is what the plugin hands its user and 結果 is
  ben's result file, in the README too; changing only the run count keeps the same scene.
  Implementation differences the first users saw are for the rebuild, not doc fixes.
- Next: the user reviews the four documents on PR #55.
- Decided: name ben (not jig); BEN_PYTHON or ~/.ben/bin/python; /ben:check <plugin> writes a scene,
  /ben:check <scene file> checks again; a scene lives in the checked plugin's git repository.
- Decided: "words read" is counted as characters.
- Decided: rn's scene runs in the private practice repository lovaizu/rn-try.
- Decided: the learner stays an agent apart: each piece of work is done by an agent focused on
  it, so the conductor does not drift (dev/turn/design.md §1). rn-try is in .claude/rules/plugin.md.
