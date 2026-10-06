Agreed design points, waiting for writ (writ/README.md, writ/docs/design.md, writ/docs/verification.md).

- The check tells the first user's own saved output by its own transcript. Inside a subagent the hook
  input carries `transcript_path` (the main conversation's `<project>/<session>.jsonl`) and
  `agent_id`; the subagent's own transcript is `<project>/<session>/subagents/agent-<agent_id>.jsonl`.
  When Claude Code saves a long result, it writes into that transcript, before the agent's next tool
  call, a tool result reading `Full output saved to: <path>`. A path under `.claude/projects` is let
  through only when it is exactly such a path quoted in the first user's own transcript.
  - Checked on this machine, Claude Code 2.1.291: a general-purpose subagent ran `seq 1 40000`, then
    Read the saved file; at the Read's PreToolUse the own transcript existed and held
    `saved to: <that path>`.
  - Why: the folder and file names never say which agent wrote a file, and only the agent that made
    the call is told the path, so its own transcript is the one record that shows the file is its own.
- Every path under `.claude/projects` in a tool call's input must be such a path, whatever the tool
  (Read, Grep, Bash). A call that names any other path there, a folder included, is stopped as now.
  - Why: A1 lets the first user read its own output the way it reads anything else; M1 keeps every
    other path closed, so one own path cannot open another beside it.
- When the own transcript cannot be found or read, the call is stopped, as now.
  - Why: M1; a check that cannot show the file is the first user's own does not open it.
- Agents other than `writ:first-user` are not checked, as now (M2).
- `writ/docs/design.md` ("The roles are kept apart by the agent definitions") and
  `writ/agents/first-user.md` (its "Do not read how the work was made" item) say that the first user
  may read the output its own calls saved, and that the hook opens only those.
- writ/README.md does not speak of the hook, so it changes only if writ finds the reader needs it.
- The verification document is new: its A1 scene has a first user run a command whose output is too
  long, then read the saved file; it passes when the read is not stopped and the first user goes on
  with the work's output in hand. Its machine checks are the unittest run of `dev/writ/tests/` with
  every line run, covering own saved path let through (Read and Bash), another agent's saved path,
  a conversation record, and a path beside an own one stopped, and other agents not checked.
