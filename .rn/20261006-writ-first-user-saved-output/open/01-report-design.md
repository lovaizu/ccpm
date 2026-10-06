# First user's report: design (writ first user's own saved output)

## What I read and used, and what I did not look at

- Read: `steering.md` (goal, A1, M1, M2), the viewpoint file `rn/0.9.0/references/essentials/design.md`, `writ/README.md` (whole), `writ/docs/design.md` (whole), `writ/docs/verification.md` (whole).
- Used to check facts the design rests on: today's hook `writ/hooks/checks/first_user_history.py:40-50`, its test fixture `dev/writ/tests/test_pretooluse.py:17-31`, `writ/agents/first-user.md:35-37`, and my own subagent conversation record under `~/.claude/projects/-Users-kiyo-...-fix-writ-bug/84a16f0b-.../subagents/agent-a8730432ba19d21ac.jsonl`. My own first `cat` of README + design.md was saved by Claude Code to `.../tool-results/bwmhpbxzp.txt`, so I had a real saved output of my own to look at.
- Ran today's `check()` from outside the repository, with `PYTHONDONTWRITEBYTECODE=1 python3 -I -B`; `git status --short` was empty afterwards.
- Not looked at: commit messages, diffs, earlier versions, the pull request, earlier reports, `notes`. I did not run the unittest suite or the A1 trial (neither the new hook nor the trial exists yet).

## Reading the README as the product's user, what did you take as what the product does for you once the goal is achieved?

From the work I understood this: the README does not change for this goal and says nothing about saved output, hooks, or `.claude/projects`. What it promises that this goal touches is at `writ/README.md:46` ("Before returning the document, writ has a first user use it ... reports what it took in and what it set out to do") and `writ/README.md:145` ("The first user actually gives the prompt to an AI and runs it ... It does not judge; it reports what happened"). As the user, I took it that the first user's report rests on what really happened in use; nothing in the README tells me that a long output would be hidden from it today, nor that it will be readable after. The user-facing gain of A1 (a report that quotes the whole output, without a detour) is visible only in the design document (`writ/docs/design.md:82`) and the verification document (`writ/docs/verification.md:28-42`), not in the README.

## Following the README's use step by step against the design document, which step did the design give no way to take?

From the work I understood this: following `/writ:up` (`README.md:17-46`) and `/writ:pith` "Checking what you made" (`README.md:126-147`) against `design.md`, every step has a feature (`design.md:34-68`). The step this goal touches, the first user using the work (`README.md:46`, `README.md:145`), is given a way by `design.md:80-82`: when the first user runs a command whose output Claude Code saves, the hook lets it read that file. I found no README step the design gives no way to take.

## Tracing each acceptance criterion through the design document, which criterion did no feature make hold?

From the work I understood this:

- A1: `design.md:82` "the hook lets a path under `.claude/projects` through only when the first user's own conversation record, found from `transcript_path` and `agent_id` in the hook's input, quotes it as saved output". `design.md:458` and `verification.md:53` repeat it.
- M1: `design.md:82` stops "a call that names any other path there, a folder included, whatever the tool", and stops the call "when the hook cannot find or read that record". `verification.md:54-58` lists another agent's output, a conversation record, a path beside its own, a folder, and a missing record.
- M2: `design.md:80` "the hooks stop these only when it is `writ:first-user`"; `verification.md:59`.

Every criterion has a feature. What I met when checking M1 against a real record: my own record holds the saved path in two kinds of place. At line 23, a `tool_result` whose `toolUseResult` has the field `persistedOutputPath` (keys printed: `stdout, stderr, interrupted, isImage, noOutputExpected, persistedOutputPath, persistedOutputSize`). At line 44, a later plain `tool_result` (output of my own `grep`) that holds the same path as text, and at line 47 a `tool_use` whose input holds it. So the record also holds paths the agent only typed or printed. `design.md:82` says "quotes it as saved output", and `verification.md:20-21` describes the record as holding a tool result reading "Full output saved to: <path>"; neither says which entries of the record count. How strongly M1 holds depends on that choice (see the generator question below). Running today's `check()` on `find ~ -path "*tool-results*"` returned `None` (not stopped), so a first user can get other agents' saved paths printed into its own record without naming `/.claude/projects`.

## Using the product as it is today, then reading the design, what that served you did the design take away?

Doing as written, this happened: today's `check()` (`first_user_history.py:40-50`), run from `/private/tmp`, printed:

- `Read` of `.../tool-results/bwmhpbxzp.txt` as `writ:first-user`: stopped, reason "writ: the first user does not read how the work was made (git history or Claude Code conversation records); use the work as it is."
- `Bash` `grep FAILED <that path>` as `writ:first-user`: stopped, same reason.
- `Read` of the same path as `general-purpose`: `None` (not stopped).

From the work I understood this: the design keeps every stop of today (git history commands, `design.md:80`; every other path under `.claude/projects`, any tool, `design.md:82`; agents other than `writ:first-user` untouched, `design.md:80`) and adds one new stop: a call is stopped when the hook cannot find or read the first user's own record (`design.md:82`, `verification.md:57-58`). That stop only applies to calls naming a path under `.claude/projects`, which today are all stopped anyway. I found nothing that serves the user today which the design takes away.

## Building a feature from the design as a generator would, what did you have to decide that is the user's to decide?

From the work I understood this: building the hook from `design.md:82`, I had to decide these, and the design does not say them:

1. Which entries of the record count as "quotes it as saved output": only the structured `toolUseResult.persistedOutputPath` of a tool result (as at my record's line 23), the text "Full output saved to: <path>" inside a tool result (`verification.md:20-21`), or any mention of the path anywhere in the record (line 44, 47 hold it too). The second and third let through a path the first user only printed or typed, such as another agent's output found with `find ~ -path "*tool-results*"` (not stopped today, as above), so this choice decides how far M1 holds. M1 is the user's criterion, so how strict it must be is theirs; the design's words "as saved output" lean to the first, but do not name it.
2. How to find the first user's own record from the hook input. `design.md:82` says "from `transcript_path` and `agent_id`". The test fixture's `transcript_path` is the session's own `.jsonl` (`test_pretooluse.py:20`), and on disk the record is `<dir of transcript_path>/<session>/subagents/agent-<agent_id>.jsonl`. The design does not give this form; I took it from the disk and the steering, not from the design. This is a generator's decision, not the user's.
3. Whether the same file named in another form (`~/.claude/projects/...` versus the absolute path quoted in the record, or with `..`) counts as the same path. The design does not say. A generator's decision.
4. For Bash, how to tell which words of the command are paths, and whether a glob such as `tool-results/*` counts as "a folder". `design.md:82` says "a folder included, whatever the tool". A generator's decision under that rule.

Only item 1 is one I would hand back to the user.

## Taking each scene of the verification document as the user it stands for, what of why they would choose the product would its pass show, and which scene or input showed nothing another did not?

From the work I understood this: there is one scene, A1 (`verification.md:28-42`). As the writ user it stands for, its pass shows that a first user handed a work whose output is too long still reports what the work printed (the three failed entries quoted from the saved file) without rerunning it another way, which is the "check by what happened in use" the README promises (`README.md:14`, `README.md:145`). The input is minimal: one script, one question. Three failed entries far into 40,000 lines (31207, 35880, 39114) sit past any preview, so a report naming them shows the whole file was read; one failure would show the same, but three with different reasons also show the quote came from the file. The scene says "If the output was not saved, or the first user never tried to read the saved file, the run showed nothing about A1; run it again" (`verification.md:41-42`). Nothing in the input makes the first user run the script plainly rather than, say, `python3 print_log.py | grep FAILED`, which would not be saved; how many reruns to try before stopping is not said.

Machine checks (`verification.md:53-60`) each map to A1, M1 or M2 and none repeats another. `verification.md:53` checks the let-through "by Read and by Bash"; the scene allows "Read, Grep or Bash" (`verification.md:39`), so Grep is let through in the scene only.

## Reading each document as its reader, which parts did you use to decide or act, and which did you read past?

From the work I understood this:

- Used: `design.md:80` (what is stopped and for whom), `design.md:82` (the whole rule, including its last sentence that it rests on one trial on 2.1.291 with a general-purpose subagent, which told me how far to trust that the record quotes the path before the read), `design.md:458`; `verification.md:3-60` all of it (start, run, scene, machine checks with the commands at `:46-51`); `README.md:46` and `README.md:145` to place the first user in the user's flow.
- Read past for this goal: the rest of `README.md` (examples, essentials, getting started) and of `design.md` (`:1-78`, `:84-456`, `:459-467`), which this goal does not change. Within `design.md:82`, the sentence "The folder and file names never say which agent wrote a file: a session's saved outputs ... share one folder beside the conversation records" I used once to see why a name check is not enough; the rest of `:82` I used to build.

## Conductor's Good and More

- Good A1: writ/docs/design.md:82 and writ/docs/verification.md:28-42 give the first user its own saved output by any reading tool, and the scene shows it reading the whole long output without a detour.
- Good M2: writ/docs/design.md:80 keeps the check to `writ:first-user` only, and writ/docs/verification.md:59 tests it.
- Good: nothing the product does today is taken away; every stop that exists today stays (report, "what did the design take away").
- More M1: writ/docs/design.md:82 "quotes it as saved output" does not say which entries of the own record count; a path the first user only typed or printed into its record would open another agent's file.
- More M1: writ/docs/design.md:82 does not say a path written another way (`~`, `..`, a symbolic form) is the same file; the generator would decide.
- More A1: writ/docs/verification.md:53 tests the let-through by Read and Bash only, while the scene allows Grep (verification.md:39).
- More M1: a first user can print other agents' saved paths with `find ~ -path "*tool-results*"`, since today's check stops only commands that name `/.claude/projects`.
- More A1: the scene does not say how many times to rerun when the first user pipes the output and nothing is saved.
