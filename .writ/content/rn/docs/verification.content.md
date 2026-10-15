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
  the default branch untouched, M2 every decision pushed, M3 the record's form, M4 a sign-off
  passed only by approval, M5 nothing reaches the user unread, M6 missing tools, M7 installs with
  turn.
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
- rn and turn from the branch under test, as their marketplace installs them, copied when the
  trial starts so a change made while it runs does not reach it; Claude Code 2.1.296 or later, on
  Opus, the model the user's conversation runs.
- After a run, a revert commit puts back the tree of `c3b5f8e` on `main`, and the run's branches
  and pull requests are closed.

### B-2: How a run goes
- A trial runs each turn of the conversation with `claude -p --plugin-dir <rn> --plugin-dir
  <turn>` in the clone, carrying the conversation over with `--resume`; `/clear` is a new `claude
  -p` without `--resume`. Trials run one at a time, since rn reads the practice repository's
  branches and pull requests. `python3 dev/rn/trials/<trial>.py --help` says what each takes.
- The stand-in writes in Japanese and asks back whenever a question does not give it what it needs
  to decide. In the account session it starts with `/rn:up move src/account to TypeScript`; why
  it wants this, said only when asked why: users who signed up with only an email see "undefined
  undefined" as their name, and support keeps getting tickets about it; what it knows, said only
  when asked: in a user record, `nickname`, `firstName` and `lastName` can each be missing, `null`
  or `""`; what it wants for a user with no name, when asked: something that tells users apart and
  gives away nothing private, and asked to choose among ways it chooses by what each gives and
  costs, asking back when no way gives what it wants or the question leaves out what they cost; it
  does not know whether every record has an email and cannot find out before the release, and
  when asked says to go on as if every record has one; at a sign-off where a scene gives it no
  words, it approves when the proposal shows nothing against its reason and decisions, and
  otherwise gives `/rn:gm` with what it saw. In the coupon session it asked that every coupon be a
  discount, because a coupon once took an order's total below 0 and money went back to the
  customer by mistake, and decides, when asked, that a coupon that is not a discount refuses the
  order.
- The flow session is the smallest that shows the course from `/rn:up` to the Deliverable
  sign-off: `/rn:up add to README.md that the shop closes on Sundays`, on the same start; the
  stand-in wants it because customers kept coming on Sundays, and answers nothing else. Its trial
  is `dev/rn/trials/flow.py`, run first after any change, since it spends no real work's cost and
  fails only where the course breaks; it also shows M1, M2 and M4 on a real run.
- The maintainer judges each scene from the run's records against its pass: the conversation's
  JSONL and every agent's, `steering.md`, `open/`, `content/`, the commits, the pull request, the
  product, and the run's output, where each hook that stops says why.

### B-3: Each scene shows the user getting what they chose the product for
- A1: `/rn:up move src/account to TypeScript` on `main`, to rn's first call to the stand-in after
  rn's one question on the two languages (`dev/rn/trials/a1_first_call.py`). Passes when rn asks
  why the stand-in wants the goal. And: the account session at its first Plan sign-off (fixture
  `account-plan`), whose plan treats only a missing name as absent, `/rn:gm a user whose last name
  is null is shown "Ann null"`, to the next Plan sign-off (`a1_feedback.py`). Passes when the plan
  put up covers all three forms an absent name takes, missing, `null` and `""`, for each name
  field.
- A2: the account session with the stand-in's reason recorded and no criterion yet written,
  paused (fixture `account-why`): `/rn:up`, to rn's second call to the stand-in (`a2_intent.py`).
  Passes when, before any call asks the stand-in to choose a way, a call asks what it wants the
  result to do for it, the ways a call then offers each give what it said, none asks what the
  repository or a run could tell, and each message asks one point.
- A3: the account session at its Plan sign-off (fixture `account-plan`) and at its Deliverable
  sign-off (fixture `account-ready`): the stand-in is given only the proposal (`a3_proposal.py`).
  Passes when it decides without asking back, and each item the proposal shows met is met at the
  lines it names.
- A4: the coupon session paused with `/rn:dn` while a task is under way (fixture `coupon-paused`):
  `/clear`, then `/rn:up` (`a4_resume.py`). Passes when the fresh conversation goes on from the
  task with no question to the stand-in, and the task's result is the same as an unpaused run's by
  the checklist of the task's kind. And: the coupon session as rn 0.8.0 recorded it (fixture
  `coupon-0.8.0`): `/rn:up` (`a4_from_080.py`). Passes when rn works the goal out again from the
  old record, asking only what it leaves unclear, and stops at a new Plan sign-off.
- A5: the records of the A1 and A3 scenes. Passes when they show the plan, the three documents and
  each proposal made by turn and read by its reader before the stop commit, and each task's result
  used by it before the conductor's decision line.

### B-4: What passes is fixed before the work is seen
- Each scene's input and pass were fixed with the design, before this version of rn was built, and
  change only with it.

### B-5: Every must-be criterion is checked somewhere
- M1 to M7 are each tested by `sh dev/check.sh`: M1 by the hook that stops a commit on the default
  branch and a push to it; M2 by the hooks on the decision line, a settled item whole, every commit
  pushed and only the conductor committing; M3 by the hooks on the plan's, `open/`'s and the
  verification document's form and every ID; M4 by the hooks on a sign-off marked only after
  `/rn:ty`, feedback only after `/rn:gm`, a pause only after `/rn:dn`, and a stop commit's form;
  M5 by the report script, which shows met only what turn's evidence shows met; M6 by the tools
  check and the hooks doing nothing where no session is open; M7 by `claude plugin validate
  --strict` on rn and the marketplace and the manifest naming turn. The flow session shows M1, M2
  and M4 on a real run.

### B-6: The machine checks run as written
- `sh dev/check.sh`, from the top of the repository in a virtual environment made with `pip
  install -r dev/requirements.txt`: M1, M2, M3, M4, M5, M6, M7.
- `python3 dev/rn/trials/flow.py`: M1, M2, M4, and the course of a session.
