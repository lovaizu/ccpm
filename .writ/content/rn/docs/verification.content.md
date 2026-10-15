# What rn/docs/verification.md says

## doc

### B-9: The point from the opening
- These checks are run after any change to rn, to see whether it still gives what its design
  (`design.md`) promises, criterion by criterion, and whether something that worked broke.

## verification

### B-1: Each run starts the same
- The practice repository `lovaizu/rn-try`: a small shop backend, its cart and checkout in
  TypeScript and its account helpers in JavaScript. Its default branch `main` holds the tree of
  `c3b5f8e`, which has no `.rn/` directory, and it has no other branch and no open pull request,
  so no earlier session's plan or code is there to be found.
- rn and turn from the branch under test, as their marketplace installs them, copied when the
  trial starts so a change made while it runs does not reach it.
- Claude Code 2.1.296 or later, on the model the user's conversation runs, Opus.
- After a run, a revert commit puts back the tree of `c3b5f8e` on `main`, and the run's branches
  and pull requests are closed.

### B-2: How a run goes
- Each scene is run by its trial in `dev/rn/trials/`, from the state just before the moment it
  checks to the first result that shows it. A state partway through a session is a fixture in
  `dev/rn/trials/fixtures/`, committed on its session branch of a fresh clone with a draft pull
  request. Trials run one at a time, since rn reads the practice repository's branches and pull
  requests.
- Each turn of the conversation runs `claude -p --plugin-dir <rn> --plugin-dir <turn>` in that
  clone, carrying the conversation over with `--resume`. `/clear` is a new `claude -p` without
  `--resume`.
- A stand-in plays the user. It is given only its part below and what rn says to it, writes in
  Japanese, and asks back whenever a question does not give it what it needs to decide.
- The maintainer judges each scene from the run's records: the conversation's JSONL and every
  agent's, `steering.md`, `open/`, `content/`, the commits, the pull request, the product and the
  run's output, where each hook that stops says why; against the scene's pass.
- The account session starts from rough words: `/rn:up move src/account to TypeScript`. Why the
  stand-in wants this, said only when asked why: users who signed up with only an email see
  "undefined undefined" as their name, and support keeps getting tickets about it. What it knows,
  said only when asked: in a user record, `nickname`, `firstName` and `lastName` can each be
  missing, `null` or `""`. What it wants for a user with no name, when asked: something that tells
  users apart and gives away nothing private; asked to choose among ways, it chooses by what each
  gives and costs, and asks back when no way gives what it wants or the question leaves out what
  they cost. It does not know whether every record has an email and cannot find out before the
  release; when asked, it says to go on as if every record has one. At a sign-off where a scene
  gives it no words, it approves when the proposal shows nothing against its reason and decisions,
  and otherwise gives `/rn:gm` with what it saw.
- The flow session is the smallest that shows the flow: `/rn:up add a line to NOTES.md saying
  the shop closes on Sundays`, on a repository holding one file, whose plan has one attractive
  criterion; the stand-in wants it because customers kept coming on Sundays, and answers nothing
  else.

### B-3: Each scene shows the user getting what they chose the product for
- A1, what they really want from rough words: `/rn:up move src/account to TypeScript` on `main`,
  to rn's first call to the stand-in after the languages are settled; passes when rn asks why the
  stand-in wants the goal. The account session at its first Plan sign-off (fixture
  `account-plan`), whose plan treats only a missing name as absent: `/rn:gm a user whose last name
  is null is shown "Ann null"`, to the next Plan sign-off; passes when the plan put up covers all
  three forms an absent name takes, missing, `null` and `""`, for each name field.
- A2, called only for decisions that are theirs: the account session with the stand-in's reason
  recorded and no criterion yet written, paused (fixture `account-why`): `/rn:up`, to rn's second
  call to the stand-in; passes when, before any call asks the stand-in to choose a way, a call asks
  what it wants the result to do for it, the ways a call then offers each give what it said, none
  asks what the repository or a run could tell, and each message asks one point.
- A3, decided from the proposal alone: the account session at its Plan sign-off and at its Design
  sign-off (fixtures `account-plan`, `account-design`): the stand-in is given only the proposal;
  passes when it decides without asking back, and each item the proposal shows met is met at the
  lines it names.
- A4, goes on from where it stopped: the flow session paused with `/rn:dn` while its one task is
  under way, then `/clear` and `/rn:up`; passes when the fresh conversation goes on from the task
  with no question to the stand-in, and reaches the Deliverable sign-off with the line in
  `NOTES.md`.
- A5, read in its receiver's place before the user sees it: the flow session from `/rn:up` to the
  Deliverable sign-off; passes when the records show the plan, the three documents, the task's
  result, the deliverable's use and each proposal made by turn and read by its first user before
  the stop commit or the decision line that follows.

### B-4: What passes is fixed before the work is seen
- Each scene's input and pass above were fixed before this version of rn was built, and are
  changed only with the design.

### B-5: Every must-be criterion is checked somewhere
- M1 to M7 and the missing tools are each a test in `dev/rn/tests/` on the hook or script that
  holds them, in the case that would break them, as the design's Verification lists; the flow
  session's records show M1 (the default branch untouched), M2 (every decision pushed) and M5 (a
  sign-off passed only by `/rn:ty`) on a real run.

### B-6: The machine checks run as written
- `sh dev/check.sh` from the top of the repository, in a virtual environment made with
  `pip install -r dev/requirements.txt`: the linter, the formatter, the type checker, every
  plugin's tests with lines and branches counted, and `claude plugin validate --strict` on each
  plugin and the marketplace; checks M2 to M7.
- `python3 dev/rn/trials/<scene>.py`: one scene, as above; `--help` says what it takes.
