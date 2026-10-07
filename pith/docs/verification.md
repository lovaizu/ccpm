# pith verification

Run these after any change to `pith`, or to how `writ` or `rn` call it, to see whether it still gives
what its [design document](./design.md) promises, and whether something that worked broke.

## Where a run starts

- The fixture repository `dev/writ/trials/fixture/`, which pith shares with writ: a small task app with
  a command-line tool, `taskctl`, a prompt that reviews pull requests in CI, and documents for its
  engineers. Each run copies it to a fresh directory and makes it a git repository of its own.
- `pith` and `writ` from the branch under test, with any installed copies turned off.

## How a run goes

`python3 dev/pith/trials/run.py play <scene> <workdir>` runs `claude -p` with `/pith:up`, and pith
alone, in the copy, and leaves what happened in `<workdir>/<scene>/play.md`, with how long it took. The
scenes are in `dev/pith/trials/scenes.py`; the runner and the fixture are writ's, which pith shares.
Each scene is a whole story of the README, from the user's request to the result they act on. The
maintainer sets what happened beside the scene's "Passes when".

## Scenes

### Where the receiver falls short, from what happened in use

- `pr-review-hole`: `/pith:up` checks `.github/prompts/pr-review.md` with the aim of the review prompt.

    Passes when a More points at a place in the prompt where the AI, given a diff, missed a breaking
    change or decided what the aim leaves to the PR author, with what the AI did as its evidence; and
    the short result holds pith's view and each More, with every Good left in the result file.

- `pr-review-sound`: the same with `.github/prompts/pr-review.good.md`.

    Passes when the question the other scene's More answers comes back Good.

### A kind of work no one has written questions for

- `export`: `/pith:up` checks `cli/src/export.js`, the README's example, with no essentials file for
  code.

    Passes when pith writes `.pith/essentials/code.md`, every question is answered from what happened
    when the first user called the code, and a More shows a mistyped `--since` taken without a word.

### writ and rn check through pith

- Seen in writ's and rn's whole stories (`dev/writ/trials/run.py`, `dev/rn/trials/story.py`).

    Passes when each check there starts one first user and leaves a result file that passes
    `check_result.py`.

### What a check costs

- Every scene above records how long the caller waited. Run the same scene with `/writ:pith` of writ
  0.1.0, and hand both short results to a reader who is not told which is which:
  `python3 dev/pith/trials/run.py versus <scene> <workdir> <0.1.0-workdir>`.

    Passes when the reader would rather act on pith's, the caller waited no longer than with 0.1.0,
    and the short result is no longer than its Mores need.

## Machine checks

| Check | Command | When |
|---|---|---|
| The form check stops a result file with a missing answer, a place that does not exist or a misquote, and lets a sound one through; pith's essentials for a plugin are the plugin rules' questions word for word; every line run | `coverage run -m unittest discover -s dev/pith/tests` | Every push, in CI |
| Strict validation | `claude plugin validate pith --strict` and `claude plugin validate . --strict` | Every change |
| No `/writ:pith`, first user, form check or essentials file left in writ or rn | `git ls-files writ rn \| grep -E 'first-user\|check_result\|essentials/(doc\|readme\|prompt\|essentials\|report)\.md\|skills/pith/'` prints nothing | Every change |
