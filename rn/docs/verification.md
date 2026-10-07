# rn verification

Run these after any change to `rn` to see whether it still gives what its
[design document](./design.md) promises, criterion by criterion, and whether something that worked
broke.

## The whole story

`rn` is judged on the README's story at the size the README promises: a Claude Code plugin that draws
the intent out of a pull request's commits and review comments, writes it as rules, and makes the
code or viewpoints that check them, work that takes days, from rough words. On work Claude finishes
well alone, `rn`'s gain cannot show.

- Where it starts: the practice repository [`lovaizu/rn-try`](https://github.com/lovaizu/rn-try), its
  `main` set to `dev/rn/trials/fixtures/start/`, a repository for a team's plugins with nothing in it
  yet. The pull requests learned from are real: pydantic/pydantic-ai #3611 to build and try on, and
  #5143 to see whether the rules prevent mistakes elsewhere.
- How it runs: `python3 dev/rn/trials/story.py --rn rn --writ writ --pith pith --out <dir>` runs each
  turn with `claude -p` and the three plugins from the branch under test, Claude Code 2.1.291 or
  later. A stand-in plays the user from its part in `story.py`: it says why only when asked, names
  the pull requests when asked, values about a week of work, and after each approval clears the
  conversation and comes back with `/rn:up`. The run records in `spent.json` how long the user waited
  at each call, how many lines they read, each time they were called, and what it cost.
- What it is set beside: the same story run with the version in use, rn 0.8.0
  (`git archive rn--v0.8.0 rn`). Runs share the practice repository, so they go one at a time.

Passes when:

- A1: the plan's goal is that a mistake pointed out once is caught before the next review, from the
  stand-in's reason, not only that rules are written; and the plugin, run on #3611's early commits,
  catches what its reviewers later pointed out, and on #5143 catches mistakes of the same kinds.
- A2: every call to the stand-in asks only what is theirs, one point per message, and none asks what
  the request, the repository or the documentation settles.
- A3: at each sign-off the stand-in decides from the proposal alone.
- A4: after each `/clear`, `/rn:up` goes on without the stand-in explaining anything again.
- Against 0.8.0: a reader handed both plugins without being told which is which would rather use this
  one, and the user waited less, read less at each sign-off, and was called less.

## Machine checks

| Check | Command | Criteria | When |
|---|---|---|---|
| The reminder after a summary reaches only a conversation that typed an rn command, on the session this branch changed, and runs every line | `coverage run -m unittest discover -s dev/rn/tests` | A4, M10 | Every push, in CI |
| `main` of the practice repository changes only by the run's own setup commit | `git ls-remote origin main`, after setup and after the run | M1 | Every run |
| Strict validation | `claude plugin validate rn --strict` and `claude plugin validate . --strict` | M7 | Every change to the plugin |
| Installing `rn` brings `writ` and `pith` | `claude plugin install rn@ccpm` in a clean configuration | M7 | Before every release |
