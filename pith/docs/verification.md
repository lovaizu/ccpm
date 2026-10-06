# pith verification

Run these after any change to `pith`, or to how `writ` or `rn` call it, to see whether it still gives
what its [design document](./design.md) promises, criterion by criterion, and whether something that
worked broke.

## Where a run starts

- The fixture repository `dev/pith/trials/fixture/`: a small task app with a command-line tool,
  `taskctl`, a prompt that reviews pull requests in CI, and documents for its engineers. Each run
  copies it to a fresh directory and makes it a git repository of its own.
- `pith` from the branch under test, and `writ` and `rn` from the same branch where a scene names them.
- Claude Code 2.1.291 or later.

## How a run goes

- Each scene is run by its trial in `dev/pith/trials/`, from the state just before the moment it
  checks to the first result that shows it.
- A scene runs `claude -p --plugin-dir <pith>` in the copy, adding `--plugin-dir <writ>` or
  `--plugin-dir <rn>` only where the scene names them, so a scene for pith alone runs without writ.
- A first user is given a scene's input and the run's record: the output, the result file, and what
  changed in the copy. It reports what happened. The maintainer running the verification sets that
  beside the scene's "Passes when".

## Scenes

### A1: Installing pith alone gives `/pith:up`, which checks any work by a first user's use

- With pith alone: `/pith:up check .github/prompts/pr-review.md.` with the aim of the review prompt
  (`PR_REVIEW_AIM` in `dev/pith/trials/scenes.py`). The prompt checks endpoints added, removed or
  with changed arguments, and has no step for a renamed response field.

    Passes when a More points at the missing check on response fields, with what the AI did when the
    first user ran the prompt on a diff as its evidence.

- With pith alone, and no `.pith/essentials/` in the copy: `/pith:up Check cli/src/export.js.
  Engineers run taskctl export to put tasks into a file they share. The aim is that the file holds
  exactly the tasks asked for, and a wrong option stops with a message.`

    Passes when pith writes `.pith/essentials/code.md` before checking, and a More points at the
    `--since` filter in `cli/src/export.js`, with what happened when the first user called it with a
    date in another form as its evidence.

### A2: writ and rn both check their work through pith

- With pith and writ: `/writ:up Fix docs/typing-guide.md.` with the readers, purpose and undecided
  point of the `typing-guide` scene in `dev/pith/trials/scenes.py`.

    Passes when the run starts `pith:first-user`, and the result file it leaves in `.writ/open/`
    passes pith's form check. Also names M1: `any` comes back as a question, and no rule on it is
    written.

- With pith, writ and rn, in the practice repository and the fixture `account-plan` of rn's
  verification: `/rn:gm a user whose last name is null is shown "Ann null"`, to the next Plan
  sign-off.

    Passes when rn's check of the plan starts `pith:first-user` with rn's `plan.md` as the
    essentials, and the report it settles passes pith's form check. Also names M2: the plan put up
    covers all three forms an absent name takes, as rn's own scene asks.

## Machine checks

| Check | Command | Criteria | When |
|---|---|---|---|
| No first user, form-check script, or essentials file of pith's left in writ or rn, and no `/writ:pith` | `git ls-files writ rn \| grep -E 'first-user\|check_result\|references/essentials/(doc\|readme\|prompt\|essentials\|report)\.md\|skills/pith/'` prints nothing | M3, M4 | Every change |
| The form check stops a result file with a missing answer, a place that does not exist, or a misquote, and lets a sound one through; the hooks stop a first user reading git history or conversation records | `coverage run -m unittest discover -s dev/pith/tests`, every line run | M4, M5 | Every push, in CI |
| writ's and rn's tests | `coverage run -m unittest discover -s dev/writ/tests` and `-s dev/rn/tests`, every line run | M1, M2, M5 | Every push, in CI |
| Strict validation | `claude plugin validate pith --strict`, the same for `writ` and `rn`, and `claude plugin validate . --strict` | M5 | Every change to a plugin |
| Each plugin listed | `pith` in `.claude-plugin/marketplace.json` and in the root `README.md` | M5 | Every change to a plugin |
| Installing writ or rn brings pith | `claude plugin install writ@ccpm` and `rn@ccpm` in a clean configuration | M3 | Before every release |
