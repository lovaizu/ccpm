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
- The property tests try every input a hook may receive. A word holding `<<` inside quotes and a
  word of operator signs alone are read as they are, not as a heredoc's start or as operators. Left
  out, as the user decided, since a hook never receives them: a null character, a branch name
  beginning with `-`, a heredoc's line that is its end word, and a lone surrogate; each is written
  beside the test with that reason, as code.md B-16 asks.
- Mutation testing reaches the hooks as well as the scripts: `dev/rn/cosmic-ray.toml` is widened
  to both, with the type check given both folders.
- Of `prompt.md`, the hooks answer the items a hook gives, B-6, B-8, B-10, B-12, B-20, B-25 and
  B-26, read on the checks and their stops; the items on a prompt's own text, its front matter,
  Role, Steps, forms, details and examples, are the skills', and are answered yes for the hooks.
- The hooks act only in a repository whose checked-out branch holds a session, or, for the default
  branch, where a session's folder `.rn/<yyyymmdd>-<slug>/` is in the repository, so they never
  stop work that is not rn's.

## The checks

- Each check passes only the forms it reads whole, and stops every other command that names what
  it guards, saying the form to use instead: a conductor stopped by a guard may try the same move
  another way, as turn's generator split the word `git` to get past `no_commit`, and the shell has
  more ways than any list of them can hold, so a guard listing the ways round it never closes;
  input is checked against the forms allowed, not the ones refused (OWASP Input Validation Cheat
  Sheet, allowlist validation).
- Git is judged in the folder it acts on, not only the event's. The forms read whole are `git …`
  and `git -C <folder> …`, alone or after `cd <folder> &&`, with the branch checked out in the
  folder reached, a git worktree's own; a command holding the word `git` together with `commit`
  or `push` in any other form is stopped.
- Not stopped: a command or a path built from variables, command substitution or a git alias, in
  which none of the words a check guards appears; the guards keep a conductor to rn's steps, and
  are not a security boundary.
- The session's own branch: a `git commit` or `git push` while the default branch is checked out,
  or a push whose destination is the default branch, is stopped: the work goes on the session's
  branch and reaches the default branch only by the user's merge.
- A sign-off passed only by the user: clearing the sign-off in `state.json` (`rn.py state
  signoff=`) is stopped unless the user's last message in the conversation is `/rn:ty`; and
  a write or edit of `state.json`, and a shell command naming `state.json` or the session's folder
  in a form other than those the check knows write nothing there (`python3 <rn.py> state …`,
  `git add`, `git commit`, a command that only reads), is stopped.
- The plan in its form: a `git commit` while the session's staged `steering.md` does not hold the
  front matter keys and the headings of the template in rn's plan checklist
  (`rn/checklists/session/plan.md`, F-1) is stopped, the template read from that checklist so the
  form is kept in one place.
- A decision kept before the work that follows it: the conductor starting turn's `turn:up` agent
  (an event with no `agent_id`) is stopped while the session's folder has changes not committed,
  or the branch has commits not pushed, so a fresh conversation goes on from every decision the
  work was made from.
