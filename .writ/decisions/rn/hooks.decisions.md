# What rn's hooks check

rn's hooks are the guards of the design (`dev/rn/design.md`): at each move a machine can judge, they
stop the conductor before it makes it, naming the step and why. This unit builds the four the design
names; each serves every unit.

## Form

- `rn/hooks/hooks.json` with one entry per hook event, `rn/hooks/<event>.py`, and each check in its
  own file under `rn/hooks/checks/`, as turn's hooks are (`turn/hooks/`); Python 3.9 or later with
  the standard library alone; without `python3` the hooks let everything through, as turn's do.
- A check finds the session as `rn/scripts/rn.py` does, through that script's functions, not a
  copy of them.
- A stop exits 2 with `rn: ` and what to do instead, and why, on stderr, as turn's do.
- Tests in `dev/rn/tests/`, fed the events Claude Code hands each hook in their real shape, with a
  repository made in a temporary folder where a check reads git; every line and branch run, every
  mutant caught, property tests where an input varies.
- Mutation testing reaches the hooks as well as the scripts: `dev/rn/cosmic-ray.toml` is widened
  to both, with the type check given both folders.
- Of `prompt.md`, the hooks answer the items a hook gives, B-6, B-8, B-10, B-12, B-20, B-25 and
  B-26, read on the checks and their stops; the items on a prompt's own text, its front matter,
  Role, Steps, forms, details and examples, are the skills', and are answered yes for the hooks.
- The hooks act only in a repository whose checked-out branch holds a session, or, for the default
  branch, where a session's folder `.rn/<yyyymmdd>-<slug>/` is in the repository, so they never
  stop work that is not rn's.

## The checks

- The session's own branch: a `git commit` or `git push` while the default branch is checked out,
  or a push whose destination is the default branch, is stopped: the work goes on the session's
  branch and reaches the default branch only by the user's merge.
- A sign-off passed only by the user: clearing the sign-off in `state.json` (`rn.py state
  signoff=`) is stopped unless the user's last message in the conversation is `/rn:ty`; and
  writing or editing `state.json` other than through `rn.py state` is stopped, so no move gets
  round the check.
- The plan in its form: a `git commit` while the session's staged `steering.md` does not hold the
  front matter keys and the headings of the template in rn's plan checklist
  (`rn/checklists/session/plan.md`, F-1) is stopped, the template read from that checklist so the
  form is kept in one place.
- A decision kept before the work that follows it: the conductor starting turn's `turn:up` agent
  (an event with no `agent_id`) is stopped while the session's folder has changes not committed,
  or the branch has commits not pushed, so a fresh conversation goes on from every decision the
  work was made from.
