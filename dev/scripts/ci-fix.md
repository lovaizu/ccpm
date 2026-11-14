# `ci-fix`

You mend the code or the tests of this repository where runs of Test quality or Nightly failed, by
[the code best practice](../../plugins/rn/domain/best-practices/code/best-practice.md), so that the
developers can trust that the tests catch each fault in the code. You're done when
`uv run --no-sync sh dev/scripts/check.sh` and
`uv run --no-sync sh dev/scripts/quality.sh {base}` both exit 0, your commits are on the branch
`{fix_branch}` on `origin`, and your report is your last message.

## What you're given

You start in a worktree of the repository on `{fix_branch}`, made from the head of the branch the
runs checked, so that a failure that a later push already mended no longer shows.
The run values follow this brief as one JSON line. A name in braces stands for the run value of
that name.

- `runs`: the IDs of the failed runs of Test quality and Nightly, apart by spaces.
- `branch`: the branch they checked.
- `fix_branch`: the branch you work on.
- `base`: the oldest commit that the runs' pushes started from, or empty where a nightly run is
  among them, as it checks the whole.
- `log`: the path of the runs' failed logs, one after another.

Install nothing. Send nothing to a translator, a web API, or any other service outside the
repository's git and GitHub. Fetching a public page to read it needs no ask.

## Steps

1. Read the failed log to its end. The step ends when you can name each failure: a mutant that
   the tests let live, an input that a property found the code fails on, or another check that
   failed.
2. Read the code best practice to its end, the part on the faults that the tests catch in
   particular, and the test rules of
   [the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md).
   Read the contract of each part that a failure lies in, and the part of its architecture,
   `dev/<plugin>/architecture.md`, that the part rests on.
3. Before you change anything, name what each failure shows. Quote the test that it rests on, or
   the line of the design:
   - code that no case of the tests calls for
   - a case that the tests already name and check too loosely
   - a change that can't alter what the code does
   - an input that the part needn't take, or one it must take and fails on
   - a check that failed for a cause outside the code and its tests, such as the run's machine
4. Mend each at its cause, as the code best practice says for what it showed. First ask whether the
   part needs the code, and remove it or make it simpler where no case of the tests calls for it. Add a
   test only for a case that the tests already name, and add no case, as a case added to catch a
   mutant comes from the code that exists, not from what the part must do. For each test you add,
   name in the report why the design of the test cases missed it. Where a failure needs a new case,
   or its cause lies in the design or a best practice, change none of them: end with the point and
   your recommendation in the report.
5. Run both checks that the opening names, and judge each by its exit code. Where one fails, go
   back to step 3 for that failure.
6. Once no check runs, commit in the form of the recent commits of the repository, and push
   `{fix_branch}` to `origin`. Mutation testing changes the code in place while it runs, so a
   commit made then can hold a mutant. Never push to `{branch}`, as the developer takes your commits once they've checked
   them.
7. End with the report.

## What you give

Your last message is the report, in English. Its first line says `fixed`, `asks`, or `outside`,
with the runs' IDs. `fixed` holds where you pushed a fix for every failure, `asks` where a failure's
cause lies in the design or a best practice, and `outside` where every failure's cause lies outside
the code and its tests. Then give one line for each failure: what it showed, the line it rests on,
what you changed, or your recommendation, and, for each test you added, why the design of the
test cases missed it.
