# What rn's scripts say

The work is rn's scripts and their tests, one purpose: what the conductor's steps need to come out
the same on every run. The files: `rn/scripts/up.py` (the one command the conductor runs, which
puts its own folder on `sys.path` and dispatches to the others), `rn/scripts/checklists.py`,
`rn/scripts/task.py`, `rn/scripts/report.py`, `rn/scripts/tools.sh`, and the tests
`dev/rn/tests/helpers.py`, `dev/rn/tests/test_checklists.py`, `dev/rn/tests/test_task.py`,
`dev/rn/tests/test_report.py`, `dev/rn/tests/test_tools.py`. Python 3.9 with the standard library
only; `tools.sh` is sh since python3 itself may be missing.

## code

### B-1: Tests hold what the code must do
- Each test is written from a sentence below and named by what must happen; each test's Given,
  When and Then say the situation, what is done and what must be so in plain words.

### B-14: Run with only what the README names
- The scripts import only the standard library (`argparse`, `json`, `os`, `re`, `sys`,
  `shutil`, `subprocess` where needed) and run on Python 3.9.

### B-16: Stopped before a wrong input is used
- `up.py` prints the usage and exits 1 on a command it does not know, on a wrong count of
  arguments, and when run with none; the usage lists every command with its arguments:
  `up.py checklists <kind>`, `up.py decisions <session folder> <document>`, `up.py task <session
  folder> --deliverable <path> [<path> ...] --receiver <who> [--use <what for>] --acceptance <what
  they can do> --checklist <path> [<path> ...] --decisions <path> [--reference <path> ...] [--opens
  <path> ...] [--language <language>]`, `up.py report <CCS turn wrote back> <judgments>`. Every stop
  of every command prints its sentence to standard output and exits 1; a command that ends well
  exits 0.
- `tools.sh`: checks, in this order, that `python3`, `jq` and `gh` are found on the PATH; the first
  missing stops with, respectively, `python3 is not found; install Python 3.9 or later
  (https://www.python.org/downloads/) and run rn again`, `jq is not found; install it
  (https://jqlang.org/download/) and run rn again`, `gh is not found; install the GitHub CLI
  (https://cli.github.com) and log in with push access, then run rn again`, printed to standard output, exit 1; with
  all three in place it prints nothing and exits 0.
- `checklists <kind>`: `<kind>` is a word or words joined by hyphens (`[a-z]+(-[a-z]+)*`); any
  other stops with `<kind>: a kind is a word or words joined by hyphens, such as release-notes`.
  rn's checklists are the files `<rn's folder>/checklists/<kind>.md`, the user's
  `.rn/checklists/<kind>.md` from the top of the repository. The command prints, as JSON, a list of
  `{"path", "name", "version"}`: first each checklist that the found ones' openings say applies
  (the text before the first `## ` line names it as `` `<name>.md` `` and rn has that checklist),
  then rn's for the kind, then the user's for the kind, each once; `[]` when none is found, exit 0
  all the same. A checklist whose front matter lacks `name` or `version` stops with `<path>: open
  the checklist with front matter giving its name and version`. The nine kinds rn keeps, `doc`,
  `readme`, `design`, `prompt`, `code`, `checklist`, `plan`, `proposal`, `verification`, are each
  found by name; `readme` gets `doc` first, then `readme`; `code` gets `code` alone.
- `decisions <session folder> <document>`: prints `<session folder>/decisions/<the document's path
  without its extension>.decisions.md`, so `turn/README.md` in session `.rn/20261016-x` gives
  `.rn/20261016-x/decisions/turn/README.decisions.md` and `src/tidy.py` gives
  `.rn/20261016-x/decisions/src/tidy.decisions.md`; a document path that is absolute or leaves the
  repository (`..`) stops with `<path> is outside the repository; name a path from its top`.
- `task <session folder> ...`: `--deliverable` and `--checklist` take one or more paths, `--reference`
  and `--opens` zero or more, and a flag given twice adds to what it was given before (argparse
  `action="extend"`); `--receiver`, `--acceptance` and `--decisions` are required, `--use` and
  `--language` optional; a call missing a required flag stops with the usage. Each checklist, the
  content, each reference and each file the receiver opens must exist, else the command stops before
  writing anything with `<path> does not exist; name it by its path from the top of the repository`.
  It writes the CCS to `<session folder>/tasks/<stem>-<n>.json`, `<stem>` the first deliverable's
  file name without its extension and `<n>` the first number from 1 whose file does not exist, and
  prints two lines, `in: <that path>` and `out: <session folder>/tasks/<stem>-<n>.back.json`. The
  CCS: `focal_entities` holds one `{"deliverable": <path>}` per deliverable in the order given,
  then `{"receiver": ...}`; `goal_orientation` holds `{"use": ...}` only when given, then
  `{"acceptance": ...}`; `retrieved_artifacts` holds `{"checklist": ...}` for each, then
  `{"content": ...}`, then `{"reference": ...}` for each, then `{"receiver_opens": ...}` for each;
  `constraints` holds `{"language": ...}` only when given; `predictive_cue`,
  `uncertainty_signal`, `semantic_gist`, `relational_map` and `episodic_trace` are empty lists.
  JSON with indent 1 and non-ASCII kept, ending in a newline.
- `report <CCS turn wrote back> <judgments>`: both are JSON files; one that is not JSON stops with
  `<path> is not JSON; give the file as turn or the conductor wrote it`. The CCS's `episodic_trace` names turn's evidence; the entry ending
  `list.json` gives the folder, where `list.json` holds `checklists` (each with `checklist`,
  `version`) and `items` (each with `id`, `title`) and `orchestrator.json` holds, per item ID,
  `met` and `lines`. A CCS naming no evidence stops with `<path> names no evidence; turn was
  stopped, so there is no report to make; call turn again to get one`. The judgments file holds `decided` (each `{"point",
  "ground"}`), `questions` (each `{"question", "judged"}`), `unmet` (each `{"item", "judged"}`)
  and `changed` (each `{"lines", "why"}`), any of them absent. Every `question` entry of the CCS's
  `semantic_gist` must have a judgment, else the command stops with `judge the question first:
  <the question>`; every `unmet` entry, whose text is `<item ID> (<item text>): <the way>`, must
  have one for its ID, else `judge the item first: <item ID>`. The report, printed to standard
  output: `Decided for you`, then, indented two spaces, each decided point as `<point>: <ground>`,
  each question as `Question: <question>: <judged>`, each unmet item as `Not met: <item ID> <item
  title>: <judged>` followed by a line indented four spaces `turn: <the way>`, each rule of the CCS
  as `Rule from turn: <rule>`, each change as `Changed after turn: <lines>: <why>`; when none of these, the one line
  `  Nothing.`. Each item met shows its lines as they stand in the document handed back: for each
  deliverable the script compares the copy turn kept, `<the evidence folder>/kept/<path>`, with the
  document now, line by line (`difflib.SequenceMatcher`), and maps each range an item names through
  the changes: lines below an insertion move down, a range all of whose lines are gone shows
  `changed after turn`, one partly gone shows the surviving lines; a kept copy missing for a
  deliverable leaves that item's lines as turn gave them, and the one line `  Lines are as turn read
  the document.` under Decided for you says so. Then, for each checklist of the list, a
  blank line, `<checklist name> <version>`, and for each item of that checklist, indented two
  spaces, `✅ <short ID> <title>: <lines>` when the orchestrator's form says met, else `⬜ <short
  ID> <title>`, the short ID being the item's ID without the checklist name. Then a blank line,
  `The document: <each deliverable of the CCS, joined by ", ">`, and `What it says, item by item:
  <each content path of the CCS>`.

### B-17: A stop says what went wrong
- Each stop above names the input or the condition that was wrong.

### B-18: A stop says what to do
- Each stop above names what to do: what to install, how to name a path, what to judge, how to
  call the command.

### B-20: One name for one thing
- "the session folder", "the decisions file", "the task", "the CCS", "the judgments", "the report",
  "a checklist", "a kind" throughout the scripts, their messages and their tests.

### B-21: Comments say why
- A comment only where the code cannot say why, such as why a flag given twice adds (a skill writes
  one flag per path) and why `tools.sh` is sh.

### B-23: The tests run by the command given
- `python3 -m unittest discover -s dev/rn/tests` from the top of the repository, as
  `dev/rn/README.md` says; the tests put `rn/scripts` on `sys.path`, make a temporary folder as the
  user's repository, run `up.main([...])` from it with its output captured, and run `tools.sh`
  through `sh` with a PATH holding only the tools the case names.

### B-3: A check tested on what it stops
- Each stop above has a test that gives the input it stops and sees the sentence and exit 1: an
  unknown command and no command (also the script run on its own through `subprocess`); each
  tool missing in turn; a kind with a path in it; a user's checklist without its version and one
  without front matter; a document path leaving the repository; a task missing a required flag;
  each of a reference, an opened file, the content and a checklist not there; a judgments file
  that is not JSON; a CCS naming no evidence; a question and an item left unjudged.

### B-4: A check tested on what it lets through
- Each check has a test on what passes: all three tools in place; each of the nine kinds; a kind
  with none found; a document at the top of the repository and one in a folder; a task with every
  flag, one with `--use` and `--language` left out, one with several deliverables, one with a flag
  given twice, a second task taking the next number while the first and its `.back.json` stay; a
  report with each part present and one with nothing for the caller; an item turn decided not met
  shown ⬜ whatever the judgments say.

## hook

None: these are scripts, not hooks.
