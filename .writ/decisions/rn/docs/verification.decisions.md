# What rn/docs/verification.md says

## doc

### B-9: The point from the opening
- These checks are run after any change to rn, to see whether it still gives what its design
  (`design.md`) promises and whether something that worked broke: the scenes below try each
  attractive criterion as rn's user, and the machine checks test each must-be criterion. The
  design's Verification holds the rest: the one-dimensional qualities, measured on the account
  session against the version in use, and the backward compatibility checks.

### B-12: Every term known
- The criteria, by the IDs the design's Goals give them in order: A1 what they really want from
  rough words, A2 called only for decisions that are theirs, A3 decided from the proposal alone,
  A4 goes on from where it stopped, A5 read in its receiver's place before the user sees it; M1
  the default branch untouched, M2 every decision pushed, M3 the record's form, M4 only the user
  passes a sign-off, gives feedback or pauses, M5 nothing reaches the user unread, M6 missing tools, M7 installs with
  turn, M8 the conductor stays on course.
- A trial: a script in `dev/rn/trials/` that runs one scene as rn's user would; a fixture: a state
  partway through a session, kept in `dev/rn/trials/fixtures/`, from which a trial starts; the
  stand-in: an AI playing the user, given only its part and what rn says to it.

## verification

### B-1: Each run starts the same
- Every run starts from the practice repository `lovaizu/rn-try`: a small shop backend, its cart
  and checkout in TypeScript and its account helpers in JavaScript, with a README. Its default
  branch `main` holds the tree of `c3b5f8e`, which has no `.rn/` directory, and it has no other
  branch and no open pull request, so no earlier session's plan or code is there to be found. A
  trial that starts partway through a session commits its fixture on that session's branch of a
  fresh clone, with a draft pull request.
- rn and turn are the `rn/` and `turn/` folders of the branch under test, copied when the trial
  starts so a change made while it runs does not reach it, and passed to Claude Code with
  `--plugin-dir`; Claude Code 2.1.296 or later, on Opus, the model the user's conversation runs.
- After a run, the trial closes the run's pull request and deletes its branch; `main` is never
  changed by rn (M1), so nothing is put back. Before a run, the maintainer sees that the start
  holds and brings it back where a run that stopped partway left something: the branches
  (`gh api repos/lovaizu/rn-try/branches --jq '.[].name'`, `main` alone), the open pull
  requests (`gh pr list -R lovaizu/rn-try --state open`, none) and `main`'s commit
  (`git ls-remote https://github.com/lovaizu/rn-try.git main`, `c3b5f8e`); a pull request left
  open is closed with `gh pr close <number> -R lovaizu/rn-try --delete-branch`, a branch left
  without one deleted with `git push https://github.com/lovaizu/rn-try.git --delete <branch>`,
  and `main` moved put back with `git push --force https://github.com/lovaizu/rn-try.git
  c3b5f8e:main`.
- The document's own front matter: `name: verification`, `version: 0.1.0`, raised once for each
  release of rn that changes it.

### B-2: How a run goes
- A trial runs each turn of the conversation with `claude -p --plugin-dir <rn> --plugin-dir
  <turn>` in the clone, carrying the conversation over with `--resume`; `/clear` is a new `claude
  -p` without `--resume`. Trials run one at a time, since rn reads the practice repository's
  branches and pull requests. `python3 dev/rn/trials/<trial>.py --help` says what each takes.
- The stand-in's part for each session, everything it knows and decides, is in
  `dev/rn/trials/common.py` (`ACCOUNT_PART`, `COUPON_PART`) and `dev/rn/trials/flow.py`
  (`FLOW_PART`), the one place that holds them, since that is what reaches the stand-in. It talks in
  Japanese and asks the repository to be written in English, and says so when asked what it does
  not know. What the passes rest on: in the account session, started
  with `/rn:up move src/account to TypeScript`, it wants the goal because users who signed up with
  only an email see "undefined undefined" as their name, knows that `nickname`, `firstName` and
  `lastName` can each be missing, `null` or `""`, and wants for a user with no name something that
  tells users apart and gives away nothing private, and, asked to choose among ways, asks back
  when no way gives what it wants or the question leaves out what they cost; in the coupon session it wants every coupon to
  be a discount and decides that a coupon that is not one refuses the order.
- The flow session is the smallest that shows the course from `/rn:up` to the Deliverable
  sign-off: `/rn:up add to README.md that the shop closes on Sundays`, on the same start, the
  practice repository; the stand-in wants it because customers kept coming on Sundays, and, asked anything
  else, says it does not know and to go on as rn proposes. Its trial is `dev/rn/trials/flow.py`, run first after any change, since it spends
  no real work's cost and fails only where the course breaks. It passes when the session reaches
  the Deliverable sign-off approved and no hook stopped a call on the way; its records show M1
  (no commit on `main`), M2 (every commit pushed as it was made) and M4 (`/rn:ty` typed before
  each sign-off passed) on a real run. The design's Verification says what each scene passes on and points here for the scenes,
  their fixtures and their trials; this document is the one place that holds them.
- The maintainer judges each scene from the run's records against its pass: the conversation's
  JSONL and every agent's, `steering.md`, `open/`, `decisions/`, the commits, the pull request, the
  product, and the run's output, where each hook that stops says why.

### B-3: Each scene shows the user getting what they chose the product for
- A1: `/rn:up move src/account to TypeScript` on `main`, to rn's first call to the stand-in after
  the stand-in answered rn's one question on the two languages (`dev/rn/trials/a1_first_call.py`).
  Passes when rn asks why the stand-in wants the goal. And: the account session at its first Plan
  sign-off (fixture `account-plan`), `/rn:gm a user whose last name is null is shown "Ann null"`,
  to the next Plan sign-off (`a1_feedback.py`). Passes when the plan
  put up covers all three forms an absent name takes, missing, `null` and `""`, for each name
  field.
- A2: the account session with the stand-in's reason recorded and no criterion yet written,
  paused (fixture `account-why`): `/rn:up`, to rn's second call to the stand-in (`a2_intent.py`).
  Passes when, before any call asks the stand-in to choose a way, a call asks what it wants the
  result to do for it, the ways a call then offers each give what it said, none asks what the
  repository or a run could tell, and each message asks one point.
- A3: the account session with its plan settled and its Plan sign-off's proposal not yet made
  (fixture `account-ready`): `/rn:up`, to the proposal; then two of the stand-in, each given the account
  session's part and what it answered rn on the way, decide, one given the proposal alone and no
  tools, and one that reads the pull request and the files on its branch in a clone of its own,
  neither answer sent (`a3_proposal.py`). Passes when the one with the proposal alone answers
  `/rn:ty` or `/rn:gm` without asking back, and the two answer the same, so each item the proposal shows met is met where it names.
- A4: the coupon session paused with `/rn:dn` while a task is under way (fixture `coupon-paused`):
  `/clear`, then `/rn:up` (`a4_resume.py`). Passes when the fresh conversation goes on from the
  task with no question to the stand-in, and carries the task to its decision line.
- A5: the records of the A1, A3 and flow scenes: the JSONL Claude Code keeps of the conversation
  and of each agent turn started, under `~/.claude/projects/`. Passes when they show the plan, the
  three documents and each proposal made by turn's generator and read by turn's first user before
  the stop commit, and the flow session's deliverable used by turn's first user, as the product's user in each
  scene of the session's verification document, before the conductor's decision line
  `● deliverable ── used → ...`.

### B-4: What passes is fixed before the work is seen
- Each scene's input and pass were fixed with the design, before this version of rn was built, and
  change only with it.

### B-5: Every must-be criterion is checked somewhere
- M1 to M8 are each a test run by `sh dev/check.sh`, in the case that would break it, as the
  design's Verification lists; the flow session shows M1, M2 and M4 on a real run as well.

### B-6: The machine checks run as written
- `sh dev/check.sh`, from the top of the repository in a virtual environment made with `pip
  install -r dev/requirements.txt`: M1, M2, M3, M4, M5, M6, M7, M8.
- `python3 dev/rn/trials/flow.py --out <a new folder>`: M1, M2, M4, and the course of a session.
  Every trial takes `--out <a new folder>` for its clone and record.
