# What rn's hooks on commits say

The work is the second of three units of rn's hooks, one purpose: every decision is pushed as it
is made, on the session's branch, with a decision line, whole, and a sign-off is passed only by the
command the user typed; each checked on the commit before it is pushed, or before the command that
would break it. The files: `rn/hooks/hooks.json`, `rn/hooks/pretooluse.py`,
`rn/hooks/posttooluse.py` and `rn/hooks/stop.py`, made again so that they run the first unit's form
checks as before and these checks too; `rn/hooks/shell.py`, which tells from a shell command which
git commands it runs; the checks `rn/hooks/checks/default_branch.py`,
`rn/hooks/checks/commit_then_push.py`, `rn/hooks/checks/decision_line.py`,
`rn/hooks/checks/settled_whole.py`, `rn/hooks/checks/stop_commit.py`,
`rn/hooks/checks/typed_command.py`, `rn/hooks/checks/pushed.py`; and the tests
`dev/rn/tests/test_shell.py`, `dev/rn/tests/test_commits.py`. The first unit's `record.py`, its
form checks and tests are followed, not remade; `record.py` may gain what these checks need of the
repository, said below. Python 3.9 with the standard library only.

## code

### B-1: Tests hold what the code must do
- Each test is written from a sentence below, named by what must happen, with Given, When and Then
  in plain words; each check has a test on what it stops and one on what it lets through.

### B-26: Each behavior tested on its own code
- Each check is a function of values: the shell command's text, the commit's message, the names
  of the files in `open/` before and after the commit and the text of each that left, whether the
  default branch is merged in, whether every commit is on the remote, the branch's name and the
  default branch's name, and the last thing the user typed; it reads no file and runs no command.
  `record.py` gives these from the repository: the commit message of HEAD, the files of `open/` in
  HEAD and in its parent, whether `origin/<default branch>` is an ancestor of HEAD, whether HEAD
  is on `origin/<branch>`, and the last user prompt of the session, read from the transcript the
  event names in `transcript_path` (the last line whose `type` is `user` and whose content is
  text); `shell.py` is a function of the command's text alone. Each is tested on strings; the
  repository-reading parts on one temporary repository made once for the test class.

### B-16: Stopped before a wrong input is used
- Each entry file reads the event's JSON from standard input; one that is not JSON, or has no
  session open, lets the call through.

### B-17: A stop says what went wrong
- Every stop is one sentence to standard error, prefixed `rn:`, naming the moment (`before the
  command:`, `on the commit:`, `at the end of the turn:`), what went wrong and why, and exits 2.

### B-20: One name for one thing
- "the conductor", "the session's branch", "the default branch", "a stop commit", "the decision
  line", "the command the user typed", "an item of open/".

### B-23: The tests run by the command given
- `python3 -m unittest discover -s dev/rn/tests` from the top of the repository.

## hook

### B-3: Nothing stopped outside its session
- As the first unit: without a session open, every hook lets every call through; `hooks.json`
  keeps its guard on python3.

### B-4: Only the call it judges
- `hooks.json`: `PreToolUse` with the matcher `Bash` runs `pretooluse.py`; `PostToolUse` with
  `Bash|Write|Edit` runs `posttooluse.py`; `Stop` runs `stop.py`.
- `pretooluse.py` judges a Bash command before it runs, by what git commands `shell.py` finds in
  it; `posttooluse.py` judges a Bash command that ran `git commit` on the session's repository
  after it, before it is pushed, and keeps the first unit's form checks on writes; a command that
  made no commit is not checked after it runs. `stop.py` keeps the form checks and adds `pushed`.

### B-5: The process, not the content
- Each check judges that a commit was made as the record asks, never what the work in it is worth.

### B-6: One check per file
- `shell.py`: from a shell command's text, each git command it runs with its subcommand and
  arguments, past prefixes such as `cd x &&` and `env`, options such as `-C <path>`, and quoting,
  leaving out heredocs' text and git named only in text such as `grep 'git push'`; and whether a
  `-C <path>` points outside the repository.
- `default_branch`: a `git commit` while the repository is on its default branch, or a `git push`
  whose target is the default branch, is stopped with `rn: before the command: the default branch
  changes only when the user merges; work on the session's branch`.
- `commit_then_push`: a command that both commits and pushes is stopped with `rn: before the
  command: commit first and push in a command of its own, since the checks on a commit run after
  it is made and before it is pushed, so a breach does not reach the pull request`.
- `decision_line`: the commit message's last line, past trailers such as `Co-Authored-By:`, is
  `● … ── … → …`; else stopped, with the form and why: a later conversation goes on from it.
- `settled_whole`: each item that left `open/` in the commit is in its message under its file name,
  whole, each line indented, with a decision `→ fixed:`, `→ let go:` or `→ to the user:` on its own
  line under each More; a report on a question lets no More go.
- `stop_commit`: a commit whose decision line ends `waiting for #{id} {sign-off name}` leaves
  `open/` empty, has the latest default branch merged in, and has as its body a proposal with the
  map line `── {slug}: … ──`, `Goal:`, `Judged by:`, `Toward what you would choose it for:` with a
  line for every attractive criterion of the plan by its ID, and `Decided for you`; one ending
  `── approved → …` leaves `open/` empty; one ending `── feedback in {file} → …` leaves only that
  `feedback` item; one ending `→ paused at …` leaves a `notes` item on where the task stands.
- `typed_command`: a commit that marks a sign-off `[x]`, or sets `status` to `finished`, is allowed
  only when the last thing the user typed is `/rn:ty`; one that records feedback only when it is
  `/rn:gm`; one that pauses only when it is `/rn:dn`; else stopped with which command the user
  must type and why: a sign-off is passed by the user alone.
- `pushed`: at the end of the turn, every commit on the branch is on its remote branch; a branch
  with no remote branch is stopped; a second end of the turn is checked the same.

### B-7: A stop never holds the AI in a loop
- Each stop names what to change in the commit or the command, which the conductor can always do.

### F-1: Shape
- As the first unit: each entry reads standard input, builds the record, runs its checks and exits
  2 with their sentences or 0; each check is `check(...)` of values in its own file under `checks/`.
