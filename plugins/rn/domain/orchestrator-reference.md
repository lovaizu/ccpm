# The orchestrator's facts of a run

The orchestrator reads this once in a conversation. Each fact here serves the measure of
`vital-few.md`, and none comes before it.

## Commands

- rn's folder is the one that the command's skill names. Write it out in full in each command, as a
  Bash command holds no variable of it. Run each command from the repository's top, and never `cd`,
  as each path here is from there. Quote each ground and each of the user's words in a command, as
  the shell splits them otherwise.
- Each script runs as `python3 <rn's folder>/scripts/<script> ...`, and exits 0 with its result. On
  1, it says what's wrong and how to mend it, so mend it and run it again, or, where the mend
  changes the design tree, hand it to a new pruner. On 2, it says what it couldn't do or check, and
  why, and a rerun does no more: tell the user what stopped and what they do, and move each other
  deliverable on meanwhile.

## The run

- The run's folder, `<run>` below, is the path that `repository.py new` or `find` prints, such as
  `.claude/worktrees/rn-<name>/.rn/<name>`. It holds the design tree, `design-tree.json`, in the
  form of `<rn's folder>/domain/best-practices/design-tree/design-tree.schema.json`, which the
  pruner alone writes, by the design tree best practice. Give a pruner `<run>` as an absolute
  path, the repository's top joined with it, so that it reaches the tree wherever it starts.
- The tree's `steps` are the way to the goal, each naming what it settles, with its deliverables.
  A step whose `signoff` is true is one the user checks. The plan is the tree's own deliverable, of
  the kind `design-tree`, and the user signs it off.
- A point for the user is an open decision of its condition, its `decided` null. Their answer
  becomes its `decided`, by `user`.
- Each Round lies at `rounds/<the deliverable's path, percent-encoded>/<content or refactor>-<n>/`,
  and holds each role's Cut and its result `<role>.json`, in the form of
  `<rn's folder>/domain/schemas/<role>-round.schema.json`. A deliverable takes at most two Rounds of
  content, each a generator then an evaluator, then one Round of refactoring for a kind that has it,
  a generator alone. A send-back after a put-up starts its Rounds again.

## Each event

- `/rn:on`: ask the user what you can help with, an issue's number or a few words alike, and end
  the turn. Their reply is the request.
- The request: read the issue that it names, by `gh issue view`, and the repository's files that it
  bears on. Take the languages by N7.2 of the design tree best practice,
  `<rn's folder>/domain/best-practices/design-tree/best-practice.md`. Write the run's slug, one to
  five lower-case English words joined by `-`, from the issue's title or the request's words, such
  as `overnight-claude-p-queue`. Run
  `repository.py new "<slug>" "<deliverables' language>" "<conversation's language>"`. It makes the
  run's worktree, and its design tree with the goal open. Where it refuses the name as taken,
  recommend `/rn:up`, and end the turn. Else start no pruner, as nothing is settled yet to weigh,
  and hold the hearing.
- The hearing: talk with the user, one point at a time, as N1, N2, N5, and N7 of the design tree
  best practice say. First whom the goal is for, then what they can do at it, then the goal in one
  summary for them to confirm. Then the way to the goal: its deliverables and steps, each step by
  what it settles in the user's terms, and which steps the user checks. The hearing ends once the
  way is settled. Hand the whole settled hearing, in the user's words, to one pruner, with the
  request and the text of each issue it names.
- `/rn:up`: run `repository.py find`. It prints the folder of the newest run with work left, here
  or on GitHub, and makes its worktree again where none lies, or nothing where no run is left, and
  then ask which run to pick up. Where it can't ask GitHub, it says why on stderr: tell the user.
  Read where the run stopped from its tree and its last Rounds, and start again each role that the
  pause stopped, as SendMessage can't reach a role of another conversation.
- `/rn:ty`: run `tree.py signoff <run>`. It makes done the plan or the deliverable that waits for
  sign-off.
- `/rn:gm` or the user's words: where they only ask, such as what a word means, answer from the
  design tree and their words, and put the same point again. Else talk the point through with them
  until they settle it, as each word alone may settle only half of it. A change by `/rn:gm` is such
  a point too. Then hand what they settled, in their words, to one pruner. Where the point was a
  generator's own, resume that generator with what they settled once the pruner has written it.
- A pause or a cancel, in the user's words or by `/rn:dn`: judge by what they mean. A pause first
  hands one pruner what the user settled that no pruner holds yet, such as the hearing so far, and
  waits for it, as the conversation alone holds it. Then it stops each generator and evaluator by
  TaskStop, and runs `repository.py pause <run>`, which commits and pushes the work so far. A
  cancel can't be undone, so ask once. Then stop each role, and run `repository.py cancel <run>`.
  It removes the run's worktree and branch, closes its open pull request, and deletes its branch on
  GitHub, and says on stderr what it couldn't. Hand a cancel to no pruner, and end the turn on the
  script's report.
- A generator's end: read `result` in `<round>/generator.json`. On `point`, talk its point
  through with the user, as any point of theirs. On `made` in a Round of content, start the
  evaluator at once, as nothing of it is judged yet. On `made` in a Round of refactoring, its Rounds
  are over, as nothing is judged: put the deliverable up.
- An evaluator's end: hand the path of its result, `<round>/evaluator.json`, to a new pruner, as a
  judged Round asks a judgment, and read nothing of it yourself.

## Each move

- A new pruner: start `rn:pruner` by Agent in the foreground, with a prompt that gives `<run>` as
  an absolute path and one unit. The unit is the settled hearing or a point the user settled, in
  their words, a judged Round by its evaluator's result's path, or the final check's findings. It
  can also be a script's refusal that asks a judgment, as the script printed it. It ends with four
  lines: `cut:`, `kept:`, `ask:`, and `stray:`.
- After a pruner's end: remove each file on its `stray:` line by `git -C <worktree> rm`. Where the
  plan isn't signed off yet and the `ask:` line is `none`, run `tree.py signoff <run>`, as the
  steps the user checks, settled in the hearing, sign off the plan. Then run
  `tree.py commit <run> "<ground>"`, the ground being what the pruner's `kept:` line says the change
  decides. Where it gives 1, hand the fault it printed to a new pruner, as a mend of the tree is a
  judgment.
- A role due: run `tree.py cut <run> <role> <deliverable>`. It writes the role's Cut and prints its
  path, or gives 1 naming what the deliverable waits on. Where that is the pruner, to keep each
  finding left as an open decision, hand what it printed to a new pruner. Else start the role by
  Agent in the background with the Cut's path as its prompt.
- A deliverable whose Rounds are over: run `repository.py put-up <run> <deliverable>`. It commits
  and pushes it in the run's pull request. For a step the user checks, it prints a link to each of
  the deliverable's files, for you to give them. For another step, it makes the deliverable done.
- Once each deliverable is done, start one plain subagent by Agent in the foreground, with the
  confirmed goal, the pull request's URL, and its default branch. Have it run
  `repository.py diff <run>`, which prints the pull request's whole diff, and read all of it; check
  that the diff brings the people to the goal, agrees with each file it bears on, such as a README
  and a CHANGELOG, and holds nothing the goal doesn't need; run `repository.py ci <run>`, which
  reports how each check of the pushed head ended; change no file; and give back only its findings,
  each with its file. Hand the findings to a new pruner. Each deliverable that it sends back takes
  its Rounds again. Once each stays done, propose the merge, with each finding left as a proposal,
  naming each check that ended neither passing nor failing, for the user to run again.
