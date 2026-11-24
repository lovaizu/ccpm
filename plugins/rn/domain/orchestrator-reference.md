# The orchestrator's facts of a run

The orchestrator reads this once in a conversation. It holds the facts of a run that the
orchestrator can't find on its own, and what each script takes and gives. Each fact here serves the
measure of `vital-few.md`, and none comes before it.

## Commands

- rn's folder is the one that the command's skill names. Write it out in full in each command, as a
  Bash command holds no variable of it. Run each command from the repository's top, and never `cd`,
  as each path here is from there. Quote each ground and each of the user's words in a command, as
  the shell splits them otherwise.
- Each script runs as `python3 <rn's folder>/scripts/<script> ...`, and exits 0 with its result.
- On 1, it says what's wrong and how to mend it. Mend it and run it again. Where the mend changes
  the design tree, hand it to a new pruner instead.
- On 2, it says what it couldn't do or check, and why, and a rerun does no more. Where it's a check
  of the repository refusing a deliverable's files, that's a problem with the deliverable. Else tell
  the user what stopped and what they do, and move each other deliverable on meanwhile.

## The run

- The run's folder, `<run>` below, is the path that `repository.py new` or `find` prints, such as
  `.claude/worktrees/rn-<name>/.rn/<name>`. It holds the design tree, `design-tree.json`, in the
  form of `<rn's folder>/domain/best-practices/design-tree/design-tree.schema.json`. The pruner
  alone writes it, by the design tree best practice. Give a pruner `<run>` as an absolute path, the
  repository's top joined with it, so that it reaches the tree wherever it starts.
- The tree's `steps` are the way to the goal, each naming what it settles, with its deliverables. A
  step whose `signoff` is true is one the user checks. The plan is the tree's own deliverable, of
  the kind `design-tree`, and the user signs it off.
- A point for the user is an open decision of its condition, its `decided` null. Their answer
  becomes its `decided`, by `user`.
- Each deliverable's Rounds and Fixes lie in `rounds/<the deliverable's path, percent-encoded>/`,
  numbered in the order made, such as `content-1`, `refactor-3`, and `fix-4`. A Round holds each
  role's Cut and its result `<role>.json`, in the form of
  `<rn's folder>/domain/schemas/<role>-round.schema.json`. A Fix holds its problem, `problem.json`,
  the fixer's Cut, and the fixer's result, `fixer.json`.
- A deliverable takes two Rounds of content, each a generator then an evaluator, and another past
  them only where the pruner wrote a remedy. Then a kind that has a refactor best practice takes one
  Round of refactoring, a generator alone. That ends its Rounds, and the deliverable is put up. A
  Fix counts toward no limit.

## Each event

- `/rn:on`: ask the user what you can help with, an issue's number or a few words alike, and end the
  turn. Their reply is the request.
- The request: read the issue that it names, by `gh issue view`, and the repository's files that it
  bears on. Take the languages by N7.2 of the design tree best practice,
  `<rn's folder>/domain/best-practices/design-tree/best-practice.md`. Write the run's slug, one to
  five lower-case English words joined by `-`, such as `overnight-claude-p-queue`. Take it from the
  issue's title or the request's words. Then run
  `repository.py new "<slug>" "<deliverables' language>" "<conversation's language>"`. It makes the
  run's worktree, and its design tree with the goal open. Where it refuses the name as taken,
  recommend `/rn:up`, and end the turn. Else hold the hearing, as nothing is settled yet to weigh.
- The hearing: talk with the user, one point at a time, as N1, N2, N5, and N7 of the design tree
  best practice say. First whom the goal is for, then what they can do at it. Then the goal in one
  summary for them to confirm. Then the way to the goal: its deliverables and steps, each step by
  what it settles in the user's terms, and which steps the user checks. The hearing ends once the
  way is settled. Hand it whole, in the user's words, to one pruner, with the request and the text
  of each issue it names.
- A pick-up, by `/rn:up`: run `repository.py find`. It prints the folder of the newest run with work
  left, here or on GitHub, and makes its worktree again where none lies. It prints nothing where no
  run is left: then ask which run to pick up. Where it can't ask GitHub, it says why on stderr: tell
  the user. Read where the run stopped from its tree and its last Rounds and Fixes. Start again each
  role that the pause stopped, from a fresh Cut, as SendMessage can't reach a role of another
  conversation.
- A sign-off, by `/rn:ty`: run `tree.py signoff <run>`. It makes done the plan or the deliverable
  that waits for sign-off.
- A send-back by `/rn:gm`, or the user's words: where they only ask, such as what a word means,
  answer from the design tree and their words, and put the same point again. Else a send-back of a
  deliverable whose Rounds are over is a problem with it, its source `send-back`. A send-back whose
  mend changes or adds a decision, or one of the plan, is a point of the user's. Talk such a point
  through with them until they settle it, as each word alone may settle only half of it. Hand what
  they settled, in their words, to one pruner. Where the point was a generator's own, resume that
  generator with what they settled once the pruner has written it.
- A pause or a cancel, by `/rn:dn` or in the user's words: judge by what they mean.
  - A pause first hands one pruner what the user settled that no pruner holds yet, such as the
    hearing so far, as the conversation alone holds it. Wait for it, and for each pruner at work.
    Then stop each generator, evaluator, and fixer by TaskStop, and run `repository.py pause <run>`,
    which commits and pushes the work so far.
  - A cancel can't be undone, so ask once. Then stop each role, and run
    `repository.py cancel <run>`. It removes the run's worktree and branch, closes its open pull
    request, and deletes its branch on GitHub. It says on stderr what it couldn't remove. Hand a
    cancel to no pruner, and end the turn on the script's report.
- A generator's end: read `result` in `<round>/generator.json`. On `point`, hand the path of the
  result to a new pruner, as the point asks a judgment. Resume that generator once the pruner has
  settled it, or talk through with the user the point that the pruner leaves open. On `made` in a
  Round of content, start the evaluator at once, as nothing of it is judged yet. On `made` in a Round of refactoring, its Rounds are over:
  put the deliverable up.
- An evaluator's end: hand the path of its result, `<round>/evaluator.json`, to a new pruner, as a
  judged Round asks a judgment. Read nothing of it yourself.
- A fixer's end: read `result` in `<fix>/fixer.json`. On `fixed`, put the deliverable up again. On
  `decision`, hand its `decision` and the Fix's folder to a new pruner. Until its weighing is
  committed, `tree.py cut` and `tree.py fix` refuse the deliverable, as it waits on the weighing.
  Where the pruner cut the decision, the Fix is over, and the deliverable is put up again.
- A put-up refused: `repository.py put-up` exits 2 with what git said. Where a check of the
  repository refused the deliverable's files, it's a problem with the deliverable, its source
  `put-up`, in the words printed. Where only the user can mend it, such as a push with no network,
  tell them.
- The final check's end: each finding, with its file, is a problem with the deliverable whose file
  it is, its source `final-check`. A finding of a file that the goal doesn't need goes to a pruner.

## Each move

- A new pruner: start `rn:pruner` by Agent in the foreground, with a prompt that gives `<run>` as an
  absolute path, the user's words of the run, the request among them, and one unit. A unit is one of
  these:
  - the settled hearing, or a point the user settled, in their words;
  - a judged Round, by its evaluator's result's path;
  - the final check's findings that no Fix takes, each with its file;
  - a fixer's decision, with its Fix's folder;
  - a script's refusal that asks a judgment, as the script printed it.

  It ends with five lines: `cut:`, `kept:`, `ask:`, `stray:`, and `changed:`, which you tell the
  user.
- After a pruner's end: remove each file on its `stray:` line by `git -C <worktree> rm`. Where the
  plan isn't signed off yet and the `ask:` line is `none`, run `tree.py signoff <run>`. The steps
  the user checks, settled in the hearing, then sign off the plan. Then run
  `tree.py commit <run> "<ground>"`, the ground being what the `kept:` line says the change decides.
  Where it gives 1, hand the fault it printed to a new pruner, as a mend of the tree is a judgment.
- A Fix: run `tree.py fix <run> <deliverable> <source>`, `<source>` being `put-up`, `final-check`,
  or `send-back`, with the problem's words on stdin, word for word. It writes the Fix's folder with
  `problem.json`, and prints its path. Then the fixer is due.
- A role due: run `tree.py cut <run> <role> <deliverable>`, `<role>` being `generator`, `evaluator`,
  or `fixer`. It writes the role's Cut and prints its path, the fixer's in the last Fix. It gives 1
  naming what the deliverable waits on instead. Where that is the pruner, to keep each finding left
  as an open decision, hand what it printed to a new pruner. Else start the role by Agent in the
  background with the Cut's path as its prompt: `rn:generator`, `rn:evaluator`, or `rn:fixer`.
- A put-up: run `repository.py put-up <run> <deliverable>`. It commits and pushes the deliverable in
  the run's pull request, opening it as a draft where none is open. For a step the user checks, it
  prints a link to each of the deliverable's files, for you to give them. For another step, it makes
  the deliverable done.
- The final check, once each deliverable is done: start one plain subagent by Agent in the
  foreground. Give it the confirmed goal, the pull request's URL, and its default branch. Have it:
  - run `repository.py diff <run>`, which prints the pull request's whole diff, and read all of it;
  - check that the diff brings the people to the goal, and agrees with each file it bears on, such
    as a README and a CHANGELOG;
  - check that the diff holds nothing that the goal doesn't need;
  - run `repository.py ci <run>`, which reports how each check of the pushed head ended;
  - change no file, and give back only its findings, each with its file.

  Once each deliverable stays done after its findings, propose the merge. Name each finding left as
  a proposal, and each check that ended neither passing nor failing, for the user to run again.
