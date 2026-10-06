# First user report: design, scene A1

## What I read, used, and did not look at

- Read: `.rn/20261006-writ-first-user-saved-output/steering.md` (goal, A1, M1, M2);
  `writ/docs/verification.md:1-49` (intro, "Where a run starts", "How a run goes", scene A1);
  the viewpoint file `rn/0.9.0/references/essentials/design.md` and `report.md`;
  `writ/agents/first-user.md` (to know what the agent is handed); `dev/writ/trials/run.py`
  (to see how a trial starts `claude -p`).
- Used: I set up scene A1 as `verification.md:33-43` writes it and ran it once, against the writ
  on this branch as it is today (the fix is not built yet), as `verification.md:9-27` writes a run.
- Not looked at: `writ/README.md`, `writ/docs/design.md`, the hook code, the tests, git history,
  earlier reports. The other scenes and the machine checks are outside this question.

## Taking each scene of the verification document as the user it stands for, what of why they would choose the product would its pass show, and which scene or input showed nothing another did not?

### From the work I understood this

- The user A1 stands for is whoever runs a writ check whose first user meets a long output
  (`steering.md` Goal: today "it spends a step finding another way"; A1: it "reads the whole of
  what its own tool calls returned ... and goes on using the work without a detour").
- The pass (`verification.md:45-49`) asks for four things: Claude Code saved the run to a file;
  the first user read that file by Read, Grep or Bash on its path; writ's hook did not stop it; and
  the report names the three failed entries, quoting the saved output, without running the script
  again another way. The last two are the "no detour" and "reads what its calls returned" of A1.
  The pass accepts any one of Read, Grep or Bash, so a pass shows the one tool the first user
  happened to choose; the other two are left to the machine check `verification.md:60`.
- The pass says nothing about M1 or M2; the scene does not show a stop of anything (those are the
  machine checks, `verification.md:61-71`).
- "How a run goes" (`verification.md:19-21`) says the trial "starts the `writ:first-user` agent
  directly, without running `/writ:pith` first". It does not say whether that is
  `claude -p --agent writ:first-user` (the agent is the main session) or a session that starts it as
  a subagent, as pith does. I took the first; the next section shows where its record then lands.

### Doing as written, this happened

Setup, in `/private/tmp/.../scratchpad/a1scene/repo` (a fresh git repository outside ccpm): I wrote
`print_log.py` as `verification.md:33-37` describes (40,000 lines, three `FAILED` entries after
30,000 picked from seed 20261006) and `essentials.md` with the one question of `verification.md:38-40`.
Running it myself printed `40000  628991` (lines, bytes) and the answer:

```
entry 31333: FAILED: quota socket error code 901
entry 34696: FAILED: socket disk error code 210
entry 38107: FAILED: disk socket error code 219
```

Run: `claude -p "Work: print_log.py in this repository. Receiver and purpose: someone who runs it to
find which entries failed. Essentials file: essentials.md. Write your report in English." --agent
writ:first-user --plugin-dir <worktree>/writ --permission-mode auto --output-format json`, Claude
Code 2.1.291. It exited 0. What happened:

- The output was saved. The first user's report quotes `Output too large (614.2KB). Full output saved
  to: .../d2b5c39c-.../tool-results/b1p5u1mtq.txt`, with a 2KB preview ending at `entry 150: ok`.
  The record `<project>/d2b5c39c-9f91-47b9-bda9-f2a4a377b86b.jsonl` holds the same "Full output
  saved to:" tool result.
- The first user tried to read the saved file with Bash (a search for lines not ending in `: ok`),
  and writ's hook stopped it: `writ: the first user does not read how the work was made (git history
  or Claude Code conversation records); use the work as it is.` The record holds that reason twice.
- The first user did not rerun the script another way; its report says adding `| grep FAILED` "would
  break the 'nothing added to the command' condition". It named no failed entry and wrote
  "Which entries failed" under "What I don't know".
- It read `print_log.py` and reported from the source that failures come from entries 30001 to
  40000 (`print_log.py:4`) and their format (`print_log.py:8`), but not which entries or reasons.

So against today's writ the run met the conditions that make it count ("the output was saved", "the
first user tried to read the saved file", `verification.md:48-49`) and failed the pass at "writ's
hook does not stop the read". The scene's input reproduced #36 on its first run.

Where the record landed: with `--agent writ:first-user` the first user's own record is the session's
main record `<project>/<session>.jsonl`; the project folder held only that file and
`<session>/tool-results/b1p5u1mtq.txt`, with no `subagents/` folder. `grep -c '"agentId"'` on the
record printed `0`; the record carries `"agentSetting":"writ:first-user"` three times. When pith runs
the first user it runs as a subagent, whose record `steering.md` (Assumptions) places at
`<session>/subagents/agent-<id>.jsonl`. A pass from a direct `--agent` start therefore shows the
first user reading its saved output where its record is the main one, not where it is a subagent's.

On inputs showing nothing another does not:

- The preview ended at `entry 150: ok`. "All after entry 30,000" and "40,000 entries" each keep the
  failures out of the preview; with the output 614.2KB and the preview at 150 entries, any position
  after 150 kept them out in this run.
- "A different reason each" and "a fixed random seed ... so neither shows in its source": the first
  user did read the source and got the range and format from it, but not the entries or reasons, so
  the answer still came only from the output.
- "Run ... with nothing added to the command" in `essentials.md`: the first user cited it as why it
  did not rerun with a filter, so in this run it is what kept a detour from hiding the stop.
- A1 is the only scene; there is no other scene to compare it with.

Cleanup: I deleted `/private/tmp/.../scratchpad/a1scene` and the project folder the run made under
`~/.claude/projects/`, each by its exact path. The ccpm repository was not touched apart from this file.

## Conductor's Good and More

- Good A1: writ/docs/verification.md:38-40 has the first user run the script as written; it did, the output was saved, and it named "nothing added to the command" as why it took no detour.
- Good A1: writ/docs/verification.md:35-37 keeps the answer out of the source; the first user read the source and could not name the entries or reasons.
- Good A1: writ/docs/verification.md:33-37 keeps the failures past the inline preview, which ended at entry 150.
- More A1: writ/docs/verification.md:19-21 "starts the `writ:first-user` agent directly" lets a maintainer start it as the main session (`--agent`), where its record is the session's own and the hook input carries no `agent_id`; writ always runs it as a subagent, so such a pass would not show the first user reading its saved output as it does in use.
