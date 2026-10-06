# Report: the plan (`steering.md`) used as its receivers would

## What I read and used, and what I did not look at

- Read: `.rn/20261006-writ-first-user-saved-output/steering.md` (the work), the viewpoint file
  `rn/0.9.0/references/essentials/plan.md`, the report aim `report.md`.
- What the user said: issue #36 (`gh issue view 36`, author kiyobot, no comments). No other words of
  the user were given to me.
- Used to check the plan's facts: `writ/docs/design.md:80`, `writ/hooks/checks/first_user_history.py`,
  `writ/hooks/pretooluse.py`, `writ/hooks/hooks.json`, `writ/agents/first-user.md:35-37`,
  `rn/hooks/checks/first_user_reads.py`, `dev/writ/tests/test_pretooluse.py:1-40`,
  `.claude/rules/plugin.md`, `writ/CHANGELOG.md`, and the files under `~/.claude/projects/` on this
  machine (Claude Code 2.1.291 here, by `claude --version`).
- Not looked at: commit messages, diffs, the pull request conversation, earlier reports, `writ/README.md`
  beyond one grep, the trials in `dev/writ/trials/`.

## Reading the plan once, what did you take as the reason the user wants the goal?

From the work I understood this: the reason is the wasted step. `steering.md` Goal, last clause: the
check "stops the first user from reading it, so it spends a step finding another way". The issue says
the same under "Why it matters" and adds that "the result was not affected" (the agent read the
documents directly). So I took the reason as: a first user loses a step and has to find a detour when
it reads its own long output; not that a check came out wrong. The plan does not state why a detour
matters to the user beyond the step itself (for example cost, or the first user giving up on part of
the work); I took it no further than the step.

## Reading the attractive criteria beside the reason the user wants the goal, what of that reason do they leave out?

From the work I understood this: A1 (`steering.md`, "Attractive quality") carries the reason: "reads
the whole of what its own command printed ... and goes on using the work without a detour". "Without a
detour" is the wasted step of the Goal. I found nothing of the reason that A1 leaves out.

## Reading each attractive criterion beside what the user said, which of what it says they gain did the user not say?

From the work I understood this, laying A1 beside issue #36:
- "goes on using the work without a detour": the issue says "spends a step finding another way". Said.
- "reads the whole of what its own command printed, even when Claude Code saved it to a file": the
  issue says the agent read the saved file and was stopped, and that the file "held only the agent's
  own output". Said in substance; "the whole" is the plan's word, implied by the issue's "showed a
  preview".
- "as a person scrolls back through their own terminal": not in the issue. It is a picture the plan
  adds; it brings in no further gain I could find, but the user did not say it.
- The issue speaks of "a Bash command". A1 says "its own command", which I read as the same.

## Checking each fact the plan rests on at its source, which did not hold?

Doing as written, this happened:
- Fact `writ/docs/design.md:80`: holds. Line 80 says the first user does not read how the work was
  made, and hooks stop "paths under `.claude/projects`" only when `agent_type` is `writ:first-user`.
  The code matches: `first_user_history.py:12` (`CONVERSATION_RECORDS = re.compile(r"/\.claude/projects(?:/|$|[\s\"'`;|&)])")`)
  and `first_user_history.py:44-45` (returns None unless `agent_type` is `writ:first-user`). It
  searches every string value of `tool_input` (`:48-50`), so any tool, any argument, is stopped.
- Fact `rn/hooks/checks/first_user_reads.py`: holds. The file has no check on `.claude/projects`;
  it stops only git history and `open/` notes and reports (`reads_maker_account`, `check_history`).
- Fact on `~/.claude/projects/`: the layout holds; the pairing of name forms with agents holds only
  partly. I ran a Python count over `~/.claude/projects/*/*/tool-results/*.txt`:
  - Every `tool-results` folder (114) sits at `<project>/<session>/tool-results/`; none under
    `subagents/`. Holds.
  - 497 `.txt` files: 26 named `toolu_….txt`, 471 named by a 9-character id beginning with `b`
    (e.g. `bloej5qd8.txt`).
  - I looked up which transcript first quotes each file's path: `toolu_` files: 20 in a subagent's
    `subagents/*.jsonl`, 6 in the main `<session>.jsonl`. Short ids: 376 in a subagent's transcript,
    95 in the main one.
  - So both name forms occur for both the main conversation and subagents. The plan's "toolu_ … seen
    for subagents" and "short random id … seen for the main conversation" are each true as "seen",
    but the short id is in fact mostly subagents' here. The plan's conclusion, that "the name alone
    does not always say which agent wrote it", holds, and more strongly than the plan puts it: the
    name says nothing of the writer in either form.
  - Not in the plan: `tool-results/` also holds folders such as `pdf-<uuid>/page-1.jpg`
    (`ls -d ~/.claude/projects/*/*/tool-results/*/`), i.e. saved output that is not a `.txt`.
- Rules (`.claude/rules/plugin.md`): the rules quoted hold there (Python 3.9 standard library,
  `unittest` in `dev/<plugin>/tests/`, `## [Unreleased]` without a bump). `writ/CHANGELOG.md` has no
  `## [Unreleased]` today, only `## [0.1.0] - 2026-10-06`; plugin.md says it is re-created, so this
  is consistent, not a failed fact.
- Front matter `verification: writ/docs/verification.md`: the file does not exist
  (`ls writ/docs` shows only `design.md`).

## Acting on the plan, which fact you relied on can neither the repository nor any documentation show, yet is recorded neither as told by the user nor as an Assumption?

From the work I understood this; acting on the plan as far as it reaches (it reaches the open
question "How the check tells the first user's own saved output from any other agent's"), I needed:
- What the hook input carries that ties a saved file to the agent now running. The test fixture
  (`dev/writ/tests/test_pretooluse.py:17-31`) feeds `session_id`, `transcript_path` (the main
  conversation's `.jsonl`), `agent_id`, `agent_type`, `tool_use_id`. Whether `agent_id` matches the
  `subagents/agent-<id>.jsonl` name, and whether that transcript is where the saved path is quoted,
  is seen only on this machine's files, not in the repository or a document the plan cites, and is
  not recorded as an Assumption.
- Which Claude Code version the folder layout was seen on. The issue names 2.1.290; this machine runs
  2.1.291. The plan's Assumption gives no version, and the layout is not documented in the repository.

## Reading the criteria, which kind of input they speak of, such as "a user with no name", has forms where the product runs that neither the repository shows nor the user told, or was tried today on only some of its forms?

From the work I understood this: A1 speaks of "what its own command printed ... saved to a file for
being too long". The issue shows one form: a Bash output saved as `tool-results/<id>.txt`, read with
Read. Forms the plan does not speak of:
- Saved output of other tools than Bash (the hook also matches Read, Grep, Glob, `hooks.json`), and
  non-text saved output such as `tool-results/pdf-<uuid>/page-N.jpg` seen on this machine.
- The way the first user reaches the file: Read on the path, or Bash `cat`/`sed`/`grep` naming it,
  with `~` or `$HOME` (the check matches only the literal `/.claude/projects`; `~/.claude/projects`
  contains it, `$HOME/.claude/projects` contains it too).
- A first user started under rn (as in the issue) or under `/writ:up` or `/writ:pith`; and several
  first users in one session, each of `agent_type` `writ:first-user`, whose outputs share one folder.
  M1 says "the output any other agent saved stay closed", so another first user's output is closed,
  but the plan does not say whether "agent" there means the agent type or the one running instance.
- A `claude -p` run by the first user (design.md:78 says it does this) saves under another
  `<project>/<session>/`; whether that counts as its own output is not said.

## Acting on the plan, which point you relied on is a decision only the user can make, yet is not recorded as theirs?

From the work I understood this:
- What happens when the check cannot tell whose a saved file is (both name forms occur for every
  writer, per the count above): keep stopping it (M1 first) or let it through (A1 first). The plan
  leaves this under "Not yet specified" as a how, not as a choice the user makes between A1 and M1.
- Whether another running `writ:first-user` in the same session is "any other agent" (see above).
- Whether the documents that state the rule change: `writ/docs/design.md:80` ("paths under
  `.claude/projects`") and `writ/agents/first-user.md:35-37` ("A hook stops reading ... conversation
  records"). The plan names `design: writ/docs/design.md` in its front matter but no decision on it.

## Following the tasks in order, which acceptance criterion did no task bring to hold?

Not asked: the tasks that make the deliverable are not yet planned. `steering.md` "Tasks" holds only
`#1: Plan sign-off` and `#2: Design sign-off`, with no body.

## Reading a task's Completion criteria as its generator, what of the task's purpose toward the attractive criteria do they leave out?

Not asked, for the same reason: no task has Completion criteria yet (`steering.md`, "Tasks").

## Following the tasks in order, which work on must-be quality comes before the attractive criteria are nearly met?

Not asked, for the same reason: no task that builds anything is listed yet.

## Carrying the work on from the plan, which parts did you use and which did you pass over?

From the work I understood this:
- Used: Goal; A1, M1, M2; all three Assumptions (each checked above); Rules (to find the test place
  and CHANGELOG rule); "Not yet specified" (it is where acting on the plan stops); front matter `pr`,
  `artifact-language`, `design`.
- Passed over: front matter `readme` and `conversation-language`; `verification`, which points to a
  file that does not exist. The two Tasks headings carried nothing for me to act on. The Goal's second
  sentence restates the folder path that the third Assumption states again in more detail; I used the
  Assumption.

## Conductor's Good and More

- Good A1: the reason (the wasted step) is carried whole by A1, at steering.md "Attractive quality".
- Good M1: the design.md:80 and rn-check facts hold at their sources.
- More A1: "as a person scrolls back through their own terminal" is a gain the user did not state, at steering.md A1.
- More A1: A1 speaks of "what its own command printed", while saved output comes from any tool and in non-text form (`pdf-<uuid>/page-N.jpg`), and is opened by Read or by a shell command, at steering.md A1.
- More M1: the name-form fact pairs each form with one kind of agent, which does not hold (both forms occur for both), and leaves out non-text folders, at steering.md Assumptions.
- More M1: "any other agent" does not say whether another running first user counts, at steering.md M1.
- More M1: what ties a saved file to the running agent, and the Claude Code version the layout was seen on, are not recorded, at steering.md Assumptions.
- More M1: what the check does with a saved file whose writer it cannot tell is not stated, at steering.md "Not yet specified".
- More A1: the first user's own `claude -p` sessions are not covered, at steering.md A1.
- More: the `verification` path points to a file that does not exist, at steering.md front matter.
- More: whether design.md:80 and first-user.md:35-37 change is not decided, at steering.md.
