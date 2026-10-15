# What rn's hooks on the record's form say

The work is the first of three units of rn's hooks, one purpose: the record keeps the form every
command and check reads it by, checked right after each write to it and at each end of the
conductor's turn, so a breach is stopped where it happens. The files: `rn/hooks/hooks.json`; the
entry files `rn/hooks/posttooluse.py` and `rn/hooks/stop.py`; `rn/hooks/record.py`, the one file
that reads the repository; the checks `rn/hooks/checks/__init__.py`,
`rn/hooks/checks/steering_form.py`, `rn/hooks/checks/open_names.py`, `rn/hooks/checks/trace.py`;
and the tests `dev/rn/tests/test_record.py`, `dev/rn/tests/test_form.py`,
`dev/rn/tests/test_fixtures.py`. Python 3.9 with the standard library only. The two later units add
the checks on commits and on the conductor's course to these entry files.

## code

### B-1: Tests hold what the code must do
- Each test is written from a sentence below, named by what must happen, with Given, When and Then
  in plain words; each check has a test on what it stops and one on what it lets through.

### B-26: Each behavior tested on its own code
- Each check is a function of the record's parts given as values, the text of the plan, the names
  of the files in `open/`, the text of each item in `open/`, the text of the verification document
  or `None`, and the `rn` field; it reads no file and runs no command, so its tests give it strings
  and take milliseconds. `record.py` alone reads the repository: the top from the event's `cwd`,
  the open session, the plan, `open/` and the verification document; its tests use one temporary
  repository made once for the test class. Each entry file is tested once end to end through
  `subprocess` with the event's JSON on standard input, as Claude Code runs it, on that repository.

### B-14: Run with only what the README names
- Only the standard library, and git as a command.

### B-16: Stopped before a wrong input is used
- Each entry file reads the event's JSON from standard input; one that is not JSON, or has no
  session open, lets the call through.

### B-17: A stop says what went wrong
- Every stop is one sentence to standard error, prefixed `rn:`, naming what of the record's form
  is broken, where (the file and the key, heading, ID or name), and why the form matters, and
  exits 2; a call let through exits 0 and says nothing.

### B-20: One name for one thing
- "the session", "the record", "the plan" (for `steering.md`), "an item of open/", "the
  verification document", "a check" throughout the hooks, their messages and tests.

### B-23: The tests run by the command given
- `python3 -m unittest discover -s dev/rn/tests` from the top of the repository.
  `test_fixtures.py` builds the record from each fixture's tree under
  `dev/rn/trials/fixtures/<name>/tree` and passes when each passes the form checks.

## hook

### B-3: Nothing stopped outside its session
- A session is open when the repository the event's `cwd` is in has a `.rn/` directory and the
  branch changed a `.rn/*/steering.md` whose `status` is not `finished`, found as
  `rn/references/record.md` says; without one, every hook lets every call through. The commands in
  `hooks.json` run `python3` only when it is found, and otherwise exit 0 outside a repository with
  `.rn/`, and inside one write `rn: its checks need python3 (3.9 or later); install it and run
  again` to standard error and exit 2.

### B-4: Only the call it judges
- `hooks.json`: `PostToolUse` with the matcher `Write|Edit` runs `posttooluse.py`; `Stop` runs
  `stop.py`.
- `posttooluse.py` runs the form checks only on a write to `steering.md`, a file under `open/` or
  the verification document the plan names; a write elsewhere is not checked.
- `stop.py` runs the form checks at every end of the conductor's turn.

### B-5: The process, not the content
- Each check judges the record's form, never whether the plan or a document is good.

### B-6: One check per file
- `steering_form`: the plan has front matter with every key `plan.md`'s template gives (`rn`,
  `pr`, `status`, `artifact-language`, `conversation-language`, `readme`, `design`,
  `verification`), `status` running or finished, every heading of the template, task headings as
  `### [ ] #N: name` or `### [x] #N: name`, and task and criterion IDs unique.
- `open_names`: each file under `open/` is `{NN}-{kind}-{about}.md` with the kind `report`,
  `feedback` or `notes`.
- `trace`: every criterion ID a task's `Serves:` line, a scene heading or a question item refers to
  exists in the plan; the verification document, when the plan names one that exists, opens with
  `name: verification` and `version`, has `## Scenes` with a `### A1:` heading for each attractive
  criterion and `## Machine checks`, and names every must-be criterion in a scene's pass or a
  check's criteria; once tasks beyond the sign-offs are planned, every acceptance criterion has a
  task that serves it; a question item's first line is `Serves:` with criterion IDs that exist or
  `goal`; a session whose `rn` field is `0.9.x` may have a verification document without front
  matter, since 0.9.0 wrote none.
- `record.py` builds the record from the repository and gives `report(problems)`, which writes the
  sentences and exits 2; the entries call the three checks on it.

### B-7: A stop never holds the AI in a loop
- Each stop names what to change in the record, which the conductor can always do.

### F-1: Shape
- `hooks.json` as above; each entry file reads standard input, builds the record, runs its checks
  and exits 2 with their sentences on standard error or 0; each check is `check(record)` in its own
  file under `checks/`, returning the sentences of a stop or an empty list, with `__init__.py`
  saying so.
