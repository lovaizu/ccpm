# What rn's hooks say

The work is rn's hooks and their tests, one purpose: what a machine can judge of the conductor's
course is checked as it happens, so a breach is stopped where it happens. The files:
`rn/hooks/hooks.json`; the entry files `rn/hooks/userpromptexpansion.py`, `rn/hooks/pretooluse.py`,
`rn/hooks/posttooluse.py`, `rn/hooks/stop.py`, `rn/hooks/sessionstart.py`; what the checks share,
`rn/hooks/record.py` (the session directory, `steering.md`, `open/`, git and the commit messages
as the checks read them) and `rn/hooks/shell.py` (which git commands a shell command runs, and
where); one check per file under `rn/hooks/checks/`; and the tests `dev/rn/tests/harness.py` (a
repository with a session, as the tests start one) and `dev/rn/tests/test_pretooluse.py`,
`test_posttooluse.py`, `test_stop.py`, `test_sessionstart.py`, `test_fixtures.py`. Python 3.9 with
the standard library only.

## code

### B-1: Tests hold what the code must do
- Each test is written from a sentence below, named by what must happen, with Given, When and Then
  in plain words; each check has a test on what it stops and one on what it lets through.

### B-14: Run with only what the README names
- Only the standard library, and git and gh as commands.

### B-16: Stopped before a wrong input is used
- Each entry file reads the event's JSON from standard input; one that is not JSON, or has no
  session open, lets the call through.

### B-17: A stop says what went wrong
- Every stop is one sentence to standard error, prefixed `rn:`, naming the step of
  `rn/references/conduct.md` or the command it concerns, what went wrong and why, and exits 2; a
  call let through exits 0 and says nothing.

### B-20: One name for one thing
- "the session", "the record", "the conductor", "a stop commit", "the decision line", "an item of
  open/", "the default branch" throughout the hooks, their messages and tests.

### B-23: The tests run by the command given
- `python3 -m unittest discover -s dev/rn/tests` from the top of the repository; the hook tests
  make a temporary git repository with a session on a branch pushed to a bare remote, a session
  record in the form `rn/checklists/plan.md` gives (with `rn: 0.10.0`), and run each entry file
  through `subprocess` with the event's JSON on standard input, as Claude Code does, checking the
  exit code and what is written to standard error; `test_fixtures.py` runs the form checks over
  each fixture under `dev/rn/trials/fixtures/` and passes when each passes them.

## hook

### B-3: Nothing stopped outside its session
- A session is open when the repository the call's `cwd` is in has a `.rn/` directory and the
  branch changed a `.rn/*/steering.md` whose `status` is not `finished`, found as
  `rn/references/record.md` says; without one, every hook lets every call through. The commands in
  `hooks.json` run `python3` only when it is found, and otherwise exit 0 outside a repository with
  `.rn/`, and inside one write `rn: its checks need python3 (3.9 or later); install it and run
  again` and exit 2.

### B-4: Only the call it judges
- `hooks.json`: `UserPromptExpansion` runs `userpromptexpansion.py`; `PreToolUse` with the matcher
  `Bash|Write|Edit|NotebookEdit|Agent|SendMessage` runs `pretooluse.py`; `PostToolUse` with
  `Bash|Write|Edit` runs `posttooluse.py`; `Stop` runs `stop.py`; `SessionStart` with the matcher
  `compact` runs `sessionstart.py`.

### B-5: The process, not the content
- Each check below judges whether a step happened in its order with its inputs read and outputs
  written, never whether the work is good; what the work gives its receiver is turn's reader's.

### B-6: One check per file
- `userpromptexpansion.py` remembers in rn's data folder (`CLAUDE_PLUGIN_DATA`, or `~/.rn-data`)
  that the user typed `/rn:ty`, `/rn:gm` or `/rn:dn`, for the check on commits to spend.
- `pretooluse.py` runs, before the call: `conductor_only_git` (only the conductor commits or pushes
  on the session's repository: a call by an agent, one with an `agent_id`, that runs `git commit`
  or `git push` on it is stopped with `rn: only the conductor commits or pushes, since every commit
  records a decision that is the conductor's; an agent returns its result and the conductor
  commits it`; git run elsewhere, such as in a clone of the agent's own, or named only in text such
  as `grep 'git push'`, passes); `commit_then_push` (a conductor command that both commits and
  pushes is stopped with `rn: commit first and push in a command of its own, since the checks on a
  commit run after it is made and before it is pushed, so a breach does not reach the pull
  request`); `foreground_agents` (an `Agent` call with `run_in_background` true, or a `SendMessage`
  to an agent, is stopped with `rn: start every agent in the foreground and wait for it, since an
  agent left running reports to a turn that has ended and the user waits on work no one carries
  on`). `shell.py` finds which git commands a shell command runs, past prefixes such as `cd x &&`,
  `env`, options such as `-C`, and unusual quoting, leaving out heredocs' text, and whether each
  runs on the session's repository.
- `posttooluse.py` runs, after the call: on a write to `steering.md`, a file under `open/` or the
  verification document, the form checks `steering_form` (front matter with every key `plan.md`
  gives and `status` running or finished, every heading of the form, task and criterion IDs
  unique; a breach says which key, heading or ID), `open_names` (each file under `open/` is
  `{NN}-{kind}-{about}.md` with the kind `report`, `feedback` or `notes`) and `trace` (every
  criterion ID a task, a scene or a question refers to exists; the verification document opens
  with `name: verification` and `version`, has `## Scenes` with a `### A1:` heading for each
  attractive criterion and `## Machine checks`, and names every must-be criterion in a scene's
  pass or a check's criteria; once tasks are planned, every acceptance criterion has a task; a
  question item's first line is `Serves:` with written criterion IDs or `goal`; a session whose
  `rn` field is `0.9.x` may have a verification document without front matter); and, on a Bash
  call that ran `git commit` on the session's repository, before it is pushed: `decision_line`
  (the message's last line, past trailers such as `Co-Authored-By`, is `● … ── … → …`),
  `settled_whole` (each item that left `open/` in the commit is in its message under its file name,
  whole, each line indented, with a decision `→ fixed:`, `→ let go:` or `→ to the user:` on each
  More; a report on a question lets no More go), `stop_commit` (a commit whose decision line ends
  `waiting for #{id} {sign-off name}` leaves `open/` empty, has the latest default branch merged in,
  and has as its body a proposal with the map line `── {slug}: … ──`, `Goal:`, `Judged by:`,
  `Toward what you would choose it for:` with a line for every attractive criterion of the plan by
  its ID, and `Decided for you`; one ending `── approved → …` leaves `open/` empty; one ending `──
  feedback in {file} → …` leaves only that `feedback` item; one ending `→ paused at …` leaves a
  `notes` item on where the task stands), `typed_command` (a sign-off marked `[x]`, or `status`
  set to `finished`, only in a commit after the user typed `/rn:ty`, feedback recorded only after
  `/rn:gm`, a pause only after `/rn:dn`, each typing spent by the commit that records it, an amend
  of that commit allowed, a second such commit stopped). A command other than a commit, and a write
  outside the record, are not checked after they run.
- `stop.py` runs at every end of the conductor's turn: the form checks; `pushed` (every commit on
  the branch is on its remote branch; a branch with no remote branch is stopped); `turn_end` (the
  turn ends only when the last decision line is a stop or a question item is open in `open/`;
  otherwise the conductor is sent on once with `rn: go on: nothing is waiting on the user, and a
  turn that ends with nothing to decide leaves them watching the work`, and a second end passes,
  for a turn that answered the user's own words); `conversation_language` (the conductor's last
  message is in the `conversation-language` of `steering.md`, judged by its script, Japanese or
  English, what it quotes from the record not counting: the map's goal line, the goal, task names
  and decision lines; a message in the wrong language is stopped every time with `rn: say it again
  in <language>, since the user reads your words in the language they chose`).
- `sessionstart.py`, after a compact, has the conductor read the record again as `/rn:up` does,
  naming the session's `steering.md`, past other folders and blank lines; with no session it says
  nothing.

### B-7: A stop never holds the AI in a loop
- `turn_end` sends the conductor on once and lets a second end pass; `conversation_language` can
  always be met by saying it again; every other stop names the step the conductor can take.

### F-1: Shape
- `hooks.json` as above; each entry file reads standard input, runs its checks and exits 2 with
  their sentences on standard error or 0; each check is `check(...)` in its own file under
  `checks/`, returning the sentences of a stop or an empty list, with `__init__.py` saying so.
