# Check: writ/docs/design.md

Target: writ/docs/design.md (the paragraph at line 82, saved output under `.claude/projects`)
Receiver and purpose: builders and maintainers of writ, who build writ from this design and weigh a change by what it costs the user; here they build the hook check that lets the first user read only the output its own calls saved.
Aim: A builder reading the paragraph knows how the hook picks paths out of a call: every path under `.claude/projects` named anywhere in the call is taken, in a Bash command too, whatever word it sits in, such as `F=<path>` or a quoted path, and the call is let through only when each one is the first user's own saved output; so a command like `F=<saved path>; wc -l $F; grep -n FAILED $F; cd <repo> && git status --short` (the call stopped in issue #36) is let through when the path is the first user's own saved output, and stopped when any such path is not. The builder also knows how far the rule's ground is checked: three runs of the A1 scene with `writ:first-user` itself as a subagent on Claude Code 2.1.291, in each of which the first user's own record quoted the saved path in the `<persisted-output>` wrapper before the read. Earlier Goods to keep: Read, Grep or Bash may read its own saved file; only a path Claude Code recorded as saved output in the first user's own record opens, typed or printed paths do not; `~` and `..` are compared as the same file; the wrapper is relied on over persistedOutputPath; a record that cannot be read stops the call.

This recheck covers only the two questions below; no other question of doc.md or design.md was asked of this first user.

## doc.md: In trying to decide or act, what was not in the document, so that you could only guess or ask someone?

Report: Below are the points where I had to choose something in code and found nothing in the document to base it on.

1. **How to get from the hook input to the first user's own record.** design.md:82 says the record is "found from `transcript_path` and `agent_id` in the hook's input". It does not say:
   - whether `transcript_path` inside a subagent points to the subagent's record or to the parent session's record;
   - how `agent_id` is combined with it (a file name pattern, a subfolder, or filtering lines inside one file).

   I would have to guess a path layout, or go and inspect real records, which the first user's definition forbids.

2. **The exact shape of a "tool result whose text begins with … `<persisted-output>`".** The document does not say:
   - whether the tool result content in the JSONL is a string or an array of content blocks, and which block's text counts as the start;
   - where the path after `Full output saved to: ` ends (end of line, whitespace, or the closing tag).

   It gives no sample line. I would guess "up to the newline".

3. **Telling a forged wrapper from a real one.** The document says "Claude Code itself recorded it as saved output", and "printed by a command, does not count". But the stated test is text-based: the result "begins with" the wrapper. If the first user runs a command whose output itself begins with `<persisted-output>\nFull output saved to: <other path>`, I could not tell from the document whether that tool result passes. I also did not know what in the record separates it from a real one.

4. **What counts as "a path under `.claude/projects`".** These were all left to guessing:
   - whether this means only `~/.claude/projects` or any `.claude/projects` directory;
   - how to treat `$HOME/...`, relative paths after `cd ~/.claude`, globs, and environment variables. Only "`~` is expanded" is stated.
   - how to treat a call that names `~/.claude` (the parent folder), e.g. `find ~/.claude`. Such a call is not "under" `.claude/projects`, and by the document's own reasoning `find` "could print the paths of other agents' saved outputs".

5. **What "normalized" and "the same file" mean.** The document does not say whether this is lexical normalization (normpath) or resolving symlinks (realpath / inode compare).

6. **Ordering.** design.md:82 reports that the wrapper appeared "before the read of it was attempted", but does not say whether the hook must require the record entry to come before the call. I would guess "anywhere in the record".

7. **Mechanics of stopping.** Line 82 and line 80 do not say:
   - which hook event this is (I assumed PreToolUse);
   - how a stop is expressed (exit code or JSON decision);
   - what message the first user gets when stopped.

   Line 80 does give the gating condition: "only when it is `writ:first-user`".

- Good: `writ/docs/design.md:82` The builder takes every `.claude/projects` path from any word of a Bash command, `F=<path>` and quoted paths included, and lets the call through only when each is the first user's own saved output; no gap was reported on how paths are picked out of a call.
  - Evidence (work): "in a Bash command whatever word it sits in, such as `F=<path>` or a quoted path, and lets the call through only when each one is the first user's own saved output"
- Good: `writ/docs/design.md:82` The builder knows a record that cannot be found or read stops the call, and that `~` is expanded before comparing.
  - Evidence (work): "When the hook cannot find or read that record, it stops the call"
- More: `writ/docs/design.md:82` The builder cannot tell whether a command whose own output begins with the wrapper text would pass the check, so the rule that printed paths do not count may not hold in the code they write.
  - Evidence (report): "If the first user runs a command whose output itself begins with"
  - Left because: to the user — outside the two points this fix was asked to change; it bears on M1 (printed paths must not count), so the rn conductor decides whether the design needs a line on it.
- More: `writ/docs/design.md:82` The builder cannot get from `transcript_path` and `agent_id` to the first user's own record without guessing the layout or inspecting real records.
  - Evidence (report): "I would have to guess a path layout, or go and inspect real records"
  - Left because: outside the two points asked; this is how the hook is built, settled in the build task and its unittest cases planned after the Design sign-off (steering.md "Not yet specified"), while the design states what must hold.
- More: `writ/docs/design.md:82` The builder has to guess the record line's shape: string or content blocks, and where the path after `Full output saved to: ` ends.
  - Evidence (report): "It gives no sample line. I would guess"
  - Left because: outside the two points asked; this is how the hook is built, settled in the build task and its unittest cases planned after the Design sign-off (steering.md "Not yet specified"), while the design states what must hold.
- More: `writ/docs/design.md:82` The builder cannot tell what counts as under `.claude/projects`: `$HOME`, relative paths, globs, variables, or a call naming the parent `~/.claude` such as `find ~/.claude`.
  - Evidence (report): "how to treat a call that names `~/.claude` (the parent folder), e.g. `find ~/.claude`."
  - Left because: outside the two points asked; this is how the hook is built, settled in the build task and its unittest cases planned after the Design sign-off (steering.md "Not yet specified"), while the design states what must hold.
- More: `writ/docs/design.md:82` The builder has to guess whether "the same file" is a lexical normalization or resolves symlinks.
  - Evidence (report): "The document does not say whether this is lexical normalization (normpath) or resolving symlinks (realpath / inode compare)."
  - Left because: outside the two points asked; this is how the hook is built, settled in the build task and its unittest cases planned after the Design sign-off (steering.md "Not yet specified"), while the design states what must hold.
- More: `writ/docs/design.md:82` The builder has to guess whether the record entry must come before the call.
  - Evidence (report): "does not say whether the hook must require the record entry to come before the call"
  - Left because: outside the two points asked; this is how the hook is built, settled in the build task and its unittest cases planned after the Design sign-off (steering.md "Not yet specified"), while the design states what must hold.
- More: `writ/docs/design.md:80-82` The builder has to guess the hook event, how a stop is expressed, and what the first user is told when stopped.
  - Evidence (report): "which hook event this is (I assumed PreToolUse)"
  - Left because: outside the two points asked; this is how the hook is built, settled in the build task and its unittest cases planned after the Design sign-off (steering.md "Not yet specified"), while the design states what must hold.

## doc.md: How certain did you take each statement you relied on to decide or act?

Report: **Taken as checked, with the reach stated:**
- "it was in the records of all four versions checked, 2.1.278 to 2.1.291" (design.md:82). I took this as checked across four versions only. How many records per version were checked is not stated.
- "records made by 2.1.285 lack `persistedOutputPath`" (design.md:82). Checked for that version. This made me treat the wrapper as the primary test and `persistedOutputPath` as secondary.
- "three runs of the A1 scene … on Claude Code 2.1.291 … the first user's own conversation record quoted the saved path in the `<persisted-output>` wrapper before the read of it was attempted" (design.md:82). Taken as checked: three runs, one version.
- "By the official hooks documentation, a plugin's hooks also run on a subagent's tool calls, and inside a subagent the hook's input carries `agent_type`" (design.md:80). Taken as resting on documentation, not on a trial.

**Stated flatly, with no check shown; I took them as true but could not tell whether they were checked:**
- "Claude Code saves it to a file under `.claude/projects` and tells only the agent that made the call where it is". The whole design rests on "only".
- "The folder and file names never say which agent wrote a file: a session's saved outputs, from the main conversation and from every subagent, share one folder beside the conversation records."
- That `transcript_path` and `agent_id` are both in the hook's input and together locate the first user's own record.

**Taken as reasoning or prediction, not a fact:**
- "stopped there, it would spend a step finding another way to see it".
- "with `find` it could print the paths of other agents' saved outputs".
- "A path the hook missed would either stop the first user's own read or let another file through".

**Taken as design decisions to implement:**
- let through only paths recorded as the first user's own saved output;
- take every `.claude/projects` path in any tool call and any word;
- stop if any other path is named, folders included;
- compare after `~` expansion and normalization;
- stop when the record cannot be found or read.

- Good: `writ/docs/design.md:82` The builder takes the rule's ground as exactly three runs of the A1 scene on one version, 2.1.291, and does not stretch it further.
  - Evidence (report): "Taken as checked: three runs, one version."
- Good: `writ/docs/design.md:82` The builder relies on the wrapper over `persistedOutputPath`, knowing why and on which versions it was seen.
  - Evidence (report): "This made me treat the wrapper as the primary test and `persistedOutputPath` as secondary."
- Good: `writ/docs/design.md:82` The builder sets the path rules apart as design decisions to implement, not as facts.
  - Evidence (report): "take every `.claude/projects` path in any tool call and any word"
- More: `writ/docs/design.md:82` The builder relies on statements the whole design rests on, that only the calling agent is told the saved path and that `transcript_path` and `agent_id` locate its own record, without knowing whether they were checked.
  - Evidence (report): "The whole design rests on"
  - Left because: outside the points asked; steering.md "Assumptions" records both as facts checked on this machine (Claude Code 2.1.291, and dev/writ/tests/test_pretooluse.py:17-31).
- More: `writ/docs/design.md:82` The builder cannot tell how many records per version back the four-version claim about the wrapper.
  - Evidence (report): "How many records per version were checked is not stated."
  - Left because: outside the points asked; the sentence was not changed by this fix.
