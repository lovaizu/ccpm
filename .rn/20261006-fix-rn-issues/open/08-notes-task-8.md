# Where #8 stands

Runs under way (scratchpad of this session, `/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-fix-rn/4b162259-4084-4d1d-b962-7cdf148368c0/scratchpad`):

- `prompts/{rn,writ,pith}/<name>.md`: pith's check of every prompt (`dev/pith/trials/prompts.py`, lists in
  `dev/<plugin>/trials/prompts.json`). Next: fix each More at its cause, by the rules.
- `resume/typing-guide/resume.md`: writ cleared partway through the plan; does the fresh conversation go on
  without the user explaining again.
- `pith-r2/pr-review-hole/versus.md`: pith's short result against writ 0.1.0's `/writ:pith`, blind.

Then, before asking the user to merge PR #50:

- Run rn's whole story again (`dev/rn/trials/story.py`, practice repo clean on main d2293cd), since rn's
  conduct changed after the last run: ways must give what the user said, each task's receiver needs are
  worked out before the generator, the conductor reads plan.md and conductor.md.
- Report per attractive criterion against rn 0.8.0 (22 calls, 77 min waited, 412 lines, $350) and the
  last run (16 calls, 55 min, 160 lines, $65), and writ/pith against 0.1.0.

Done and checked: rules as essentials and conventions; the three plugins aligned; hooks down to rn's
reminder after a summary (112 lines from 985); A1-A4, A6-A11 compared; descriptions start writ and pith
from the user's own words; files no run touched found and fixed.

## Results so far (2026-10-07)

- writ resume: a fresh conversation went on from the plan file without asking again.
- pith against writ 0.1.0's /writ:pith, blind: pith's preferred; 8.0 min against 4.8.
- Prompt checks: rn on, up, dn, ty finished (results in scratchpad `prompts/rn/`); the other 19 stopped
  at the usage limit. Rerun only those: `python3 dev/pith/trials/prompts.py <plugin> <workdir> <name>...`.
- Seen in them: one first user ran /rn:dn 30 times over 17 situations on three models; a check that
  heavy costs the user's wait and usage, so the prompt essentials' first user needs a bound by purpose.
