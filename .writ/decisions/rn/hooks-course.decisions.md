# What rn's hooks on the conductor's course say

The work is the third of three units of rn's hooks, one purpose: the conductor stays on its course
while the user is away: it waits for every agent, ends its turn only with something for the user to
decide, speaks in the language the user chose, and reads the record again when Claude Code has
summarized the conversation. The files: `rn/hooks/hooks.json`, `rn/hooks/pretooluse.py` and
`rn/hooks/stop.py`, made again so that they run the first two units' checks as before and these
too; `rn/hooks/sessionstart.py`; the checks `rn/hooks/checks/foreground_agents.py`,
`rn/hooks/checks/turn_end.py`, `rn/hooks/checks/conversation_language.py`; and the tests
`dev/rn/tests/test_course.py`, `dev/rn/tests/test_sessionstart.py`. The first two units' files
are followed, not remade; `record.py` may gain the last decision line, the open question items and
the conductor's last message, read from the transcript the event names. Python 3.9 with the
standard library only.

## code

### B-1: Tests hold what the code must do
- Each test is written from a sentence below, named by what must happen, with Given, When and Then
  in plain words; each check has a test on what it stops and one on what it lets through.

### B-26: Each behavior tested on its own code
- Each check is a function of values: the tool call's name and input, the branch's last decision
  line, the names of the items in `open/`, the plan's `conversation-language`, the conductor's last
  message, and whether this end of the turn is the second (`stop_hook_active`); it reads no file
  and runs no command, and its tests give it strings.

### B-16: Stopped before a wrong input is used
- Each entry file reads the event's JSON from standard input; one that is not JSON, or has no
  session open, lets the call through.

### B-17: A stop says what went wrong
- Every stop is one sentence to standard error, prefixed `rn:`, naming the moment (`before the
  call:`, `at the end of the turn:`), what went wrong and why, and exits 2.

### B-23: The tests run by the command given
- `python3 -m unittest discover -s dev/rn/tests` from the top of the repository.

## hook

### B-3: Nothing stopped outside its session
- As the first unit: without a session open, every hook lets every call through.

### B-4: Only the call it judges
- `hooks.json`: `PreToolUse` with the matcher `Bash|Agent|SendMessage` runs `pretooluse.py`;
  `Stop` runs `stop.py`; `SessionStart` with the matcher `compact` runs `sessionstart.py`; the
  other events as the earlier units set them.
- `pretooluse.py` adds `foreground_agents` on `Agent` and `SendMessage` calls; `stop.py` adds
  `turn_end` and `conversation_language` at every end of the conductor's turn.

### B-5: The process, not the content
- Each check judges how the conductor's turn goes, never what it says or makes.

### B-6: One check per file
- `foreground_agents`: an `Agent` call with `run_in_background` true, or a `SendMessage` to an
  agent, is stopped with `rn: before the call: start every agent in the foreground and wait for
  it, since an agent left running reports to a turn that has ended and the user waits on work no
  one carries on`.
- `turn_end`: the turn ends only when the branch's last decision line is a stop (ends `waiting
  for …`, `── approved → …`, `── feedback in …` or `→ paused at …`) or a `notes` item on a
  question is open in `open/`; otherwise the conductor is sent on once with `rn: at the end of
  the turn: go on, since nothing is waiting on the user, and a turn that ends with nothing to
  decide leaves them watching the work`, and a second end in the same state passes, for a turn
  that answered the user's own words.
- `conversation_language`: the conductor's last message is in the `conversation-language` of the
  plan, judged by its script, Japanese or English; what it quotes from the record does not count:
  the map's goal line, the goal, task names and decision lines; a message in the wrong language is
  stopped every time, a second end included, with `rn: at the end of the turn: say it again in
  <language>, since the user reads your words in the language they chose`; a message with no
  letters of either script passes.
- `sessionstart.py`: after a compact, writes to standard output, for the conductor, to read the
  session's plan, `open/` and the last decision line again as `/rn:up` does, naming the plan's
  path, since a summary drops details the record holds whole; with no session it writes nothing.

### B-7: A stop never holds the AI in a loop
- `turn_end` sends the conductor on once and lets a second end pass; `conversation_language` is
  met by saying it again; `foreground_agents` by starting the agent in the foreground.

### F-1: Shape
- As the first unit: each entry reads standard input, builds the record, runs its checks and exits
  2 with their sentences or 0; each check is `check(...)` of values in its own file under `checks/`.
