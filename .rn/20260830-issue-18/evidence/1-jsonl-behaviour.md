# Where an emitted string lands in Claude Code's conversation log

Task #2 has to choose the textual form of a task-boundary marker and the method `rn` uses to write it
into the conversation log. This document records what the log actually does, so that choice rests on
measurement rather than on reasoning. Every claim carries the command that produced it and the output
that came back; anything not measured is labelled as an inference, with its basis named.

Measured 2026-09-10 on this machine, under:

```
$ claude --version
2.1.267 (Claude Code)
```

Figures taken on 2026-09-06 under version 2.1.263 are labelled where they are quoted, as are the
hook-channel figures taken on 2026-09-20 under 2.1.278. All of this is undocumented on-disk
internals, so it is bound to those versions and to this machine's history.

## What this establishes

| # | Finding | Section |
|---|---|---|
| 1 | The conversation file is complete on disk while the conversation is open, and an entry reaches disk about 0.1 s after its own timestamp. | [Liveness](#the-conversation-file-is-live-and-lags-its-own-entries-by-about-01-s) |
| 2 | Six channels put an arbitrary string into the conversation file; each lands at the field path its channel predicts. | [Six channels land](#six-channels-put-a-string-into-the-conversation-file) |
| 3 | A plugin hook's stdout is filed as an entry of its own kind — `type: "attachment"` with `attachment.type: "hook_success"` — carrying a string the hook computes at run time. | [Channel 6](#channel-6-a-plugin-hooks-stdout-is-filed-as-an-entry-of-its-own-kind) |
| 4 | That entry shape **is** a discriminator: machine-wide, `hookEvent` occurs as a JSON key only inside a hook attachment, while the same marker quoted in prose stays in the message fields. It is the one thing the other five channels do not offer. | [The discriminator](#the-hook-entry-tells-an-emission-from-a-quotation) |
| 5 | Two candidate methods do **not** land: a subagent's own turns never reach the conversation file, and a tool result over about 30 KB is written to a side file instead of into the JSONL. | [Two methods do not land](#two-candidate-methods-do-not-land) |
| 6 | Two hook placements do **not** land either: a `SessionEnd` hook's output is filed nowhere, and a hook firing inside a subagent reaches the subagent file only. | [Hook events that do not land](#two-hook-placements-fire-without-reaching-the-conversation-file) |
| 7 | A string emitted in one turn is readable by a later tool call in that same turn. | [Same-turn read-back](#same-turn-read-back-works) |
| 8 | Only 16-character lowercase hex was emitted on channels 1–5, so nothing is known there about spaces, quotes, newlines, non-ASCII — or about `<` and `>`, which one channel escapes to `&lt;` and `&gt;`. Channel 6 additionally carried a space and uppercase ASCII. | [Character set](#only-16-character-lowercase-hex-was-emitted) |
| 9 | A conversation file is placed by its relocation target, so globbing one working directory's project directory both misses and over-returns. | [Placement](#a-file-is-placed-by-relocation-target-not-by-the-working-directory-of-its-entries) |
| 10 | The set of files in a project directory changes while the session is open: three files became five between the two measurement rounds. | [The file set moves](#the-file-set-changes-while-the-session-is-open) |
| 11 | A conversation can continue into a **new file under a new `sessionId`** that replays every earlier entry verbatim, so a marker emitted before the continuation exists twice on disk. A `continued-in` entry links the pair. | [Continuation by replay](#a-conversation-can-continue-into-a-new-file-that-replays-the-old-one) |
| 12 | A restart can instead append into the existing file, leaving no seam record other than a change of `version` mid-file. | [Restart in place](#a-restart-can-append-into-the-existing-file-marked-only-by-the-version-stamp) |
| 13 | Compaction stays in one file and reproduces earlier prose into a summary entry, so a marker quoted in prose can appear a second time under a later timestamp. | [Compaction](#compaction-stays-in-one-file-and-replays-earlier-prose-into-it) |
| 14 | Line order and timestamp order disagree; the largest observed backstep is 13,429.9 s, and 76 of one file's entries carry no timestamp at all. | [Ordering](#line-order-and-timestamp-order-disagree) |

What this does **not** do is choose the marker. Section [What this still cannot answer](#what-this-still-cannot-answer)
lists what task #2 has to settle some other way.

## Terms

`sessionId` names one Claude Code conversation, not an `rn` session — the pair this measurement exists
to keep apart. The vocabulary used throughout:

- **session** — the `rn` session, `.rn/20260830-issue-18/`. Never used for a Claude Code log.
- **conversation** / **conversation file** — one Claude Code log file, named for its `sessionId`.
- **subagent file** — a subagent's own turns, two levels below the conversation file at
  `<conversation-uuid>/subagents/agent-*.jsonl`.
- **entry** — one JSON object, one line of a JSONL file. Every entry carries a `type`; nineteen types
  are in use on this machine, inventoried in [Ordering](#line-order-and-timestamp-order-disagree).
- **marker** — the string task #2 will design for `rn` to write at a task boundary. Nothing in this
  document is a marker; the strings measured here stand in for one.
- **emission channel** — one way of getting a string into a log file: a place in a turn where the
  string can be put, plus the entry and field path it ends up in. Six are measured, and *channel* is
  the only word this document uses for them.
- **probe** — one act of emitting a stand-in string through one channel. **token** — the string
  emitted. A probe is performed; a token is emitted.
- **coordinator** — the main agent of a conversation, whose entries are `isSidechain: false`. The
  channel 1–5 probes were performed by the coordinator of conversation `ef482a21`, never by a
  subagent; the channel 6 probes were performed by a hook script in three headless conversations of
  their own, one of whose hooks fired inside a subagent. Which agent emits is load-bearing and is
  named everywhere below.
- **hook** — a command Claude Code runs at a named point of a turn. A plugin declares its hooks in
  `<plugin>/hooks/hooks.json`; the string the hook prints on stdout is what channel 6 emits.
- **main checkout** — `/Users/kiyo/work/lovaizu/ccpm`. **worktree** — `…/.claude/worktrees/issue-18`.

Paste these assignments into a shell before running any command block below. They are inputs, not
output:

```sh
PROJ_MAIN=~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm
PROJ_WT=~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18
CONV=$PROJ_WT/ef482a21-4765-41d3-9d74-aa4c8d40f5d8.jsonl
SUB=$PROJ_WT/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/subagents/agent-adcd0d76cf2237e15.jsonl
PROBE=/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/scratchpad/probe
TOOLS=.rn/20260830-issue-18/evidence/tools
LIVE=$PROJ_WT/c763d0be-78f2-4036-a80b-3d5d95c07065.jsonl          # the conversation writing this document
AGENT=$PROJ_WT/c763d0be-78f2-4036-a80b-3d5d95c07065/subagents/agent-a39f6e288d6277a88.jsonl
S=/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18/c763d0be-78f2-4036-a80b-3d5d95c07065/scratchpad
HOOKPROJ=~/.claude/projects/-private-tmp-claude-501--Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18-c391e411-3a1d-49ce-84fb-a082334e2143-scratchpad-pcwd
HBASE=/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18/c391e411-3a1d-49ce-84fb-a082334e2143/scratchpad
HTOK=$HBASE/tokall
```

`$PROBE` holds one file per token, written before any probe ran, and `$HTOK` does the same for the
three channel-6 tokens. Token values are read from those files and never typed into a command or into
this document; they appear below elided as `<p1>`…`<p4>` and `<h1>`…`<h3>`, and `$TOOLS/masktok.py`
is what performs the elision. The rule is deliberate: this document is read
back into the conversation it describes, so any token literal written here would become a hit in every
later grep of the log — the hazard measured in [The self-reference hazard](#the-self-reference-hazard-is-measured-not-assumed).

Four shared scripts live in `evidence/tools/` so the command blocks stay short:

- `masktok.py` — loads tokens from a directory and replaces each value with `<name>`.
- `corpus.py <scan>` — the eight whole-machine scans (`versions`, `version-range`, `persist-bracket`,
  `no-timestamp`, `worktree-ptr`, `entry-types`, `attachment-types`, `hook-entries`), each reading
  every conversation file on this machine; `persist-bracket`, `attachment-types` and `hook-entries`
  read every subagent file too, and `worktree-ptr` reads only the ccpm project directories.
- `scan.py <scan> <file>… [--tokens <dir>]` — the eleven per-file scans (`spans`, `cwd`, `types`,
  `inversions`, `seam`, `handoff`, `escaping`, `hooks`, `hookraw`, `hookids`, `prompts`). Each
  subcommand is the exact measurement the section quoting it describes; `--tokens` loads probe
  tokens the way `walk.py` does, so `hookraw` can mask them and `prompts` can report them.
- `walk.py` — parses every entry of a JSONL file and reports the JSON path of each string field
  containing a needle. Printed values are masked and **truncated to 110 characters**; paths and entry
  headers are printed in full. It parses rather than grepping raw lines because attribution needs the
  exact field a hit occupies: a hit at `.message.content[0].input.command` of an `assistant` entry
  cannot be an echo of a prompt, and a raw-line grep cannot tell the two apart.

## Part 1 — What lands

### The conversation file is live, and lags its own entries by about 0.1 s

The file is complete on disk up to the moment it is read, while the conversation is still open:

```
$ python3 -c "
import json
ts=[json.loads(l).get('timestamp') for l in open('$CONV') if l.strip()]
print('entries on disk:  ', sum(1 for _ in open('$CONV')))
print('newest timestamp: ', max(t for t in ts if t))
"; date -u +'wall clock:        %Y-%m-%dT%H:%M:%SZ'
entries on disk:   268
newest timestamp:  2026-09-06T05:22:48.550Z
wall clock:        2026-09-06T05:29:03Z
```

That block is quoted from the 2026-09-06 round. The 375 s between the newest entry and the wall clock
is idle time, not flush delay: the conversation was suspended while the reading turn ran.

Flush delay itself is small. Comparing the file's mtime against the newest entry it contains, from
inside a running Bash command, measured 2026-09-10 11:09:01Z:

```
$ python3 - "$AGENT" <<'PY'
import json,sys,os,datetime
p=sys.argv[1]; M='<m>'                       # a random literal placed in this very command
es=[(i,json.loads(l)) for i,l in enumerate(open(p),1) if l.strip()]
mt=datetime.datetime.utcfromtimestamp(os.stat(p).st_mtime)
i,e=max(((i,e) for i,e in es if e.get('timestamp')), key=lambda x:x[1]['timestamp'])
print('newest entry:             line %d type=%s ts=%s'%(i,e.get('type'),e['timestamp']))
print('file mtime:               %sZ'%mt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])
print("this command's own entry: %s"%('present' if any(M in json.dumps(x) for _,x in es) else 'not yet written'))
PY
newest entry:             line 190 type=assistant ts=2026-09-10T11:09:00.965Z
file mtime:               2026-09-10T11:09:01.067Z
this command's own entry: not yet written
```

`<m>` is elided for the same reason token values are. The mtime runs 0.102 s behind the newest entry's
own timestamp, and two facts follow:

- **An entry reaches disk about 0.1 s after the timestamp it carries.**
- **The entry describing an in-flight tool call is not on disk while that call runs.** An earlier draft
  claimed the opposite; a reading taken at 2026-09-06T05:08:20.781Z inside a subagent found 40 entries
  on disk, newest 05:08:14.189Z, with the reading call's own entry absent — the same result, six
  seconds staler because a thinking pause preceded it.

Both readings were taken on files the running agent writes to. The 0.1 s figure is measured on a
subagent file; the cross-agent measurement in [Same-turn read-back](#same-turn-read-back-works)
bounds the conversation file at 11.1 s and is consistent with it.

Every re-measured figure in this document also rests on the log being **append-only**, so that is
tested rather than assumed — the same file hashed and counted twice, 105 seconds apart:

```
$ date -u +'t %Y-%m-%dT%H:%M:%SZ'
$ printf 'bytes=%s lines=%s prefix40=%s\n' "$(wc -c < $AGENT|tr -d ' ')" \
    "$(wc -l < $AGENT|tr -d ' ')" "$(head -n 40 $AGENT | shasum -a 256 | cut -c1-16)"
t 2026-09-10T11:04:23Z
bytes=554921 lines=126 prefix40=809e0c5fd3437c3a
t 2026-09-10T11:06:08Z
bytes=610859 lines=150 prefix40=809e0c5fd3437c3a
```

The file grew by 55,938 bytes and 24 lines while the hash of its first 40 lines stayed identical.
Content already written is not rewritten; a count re-run later returns a larger number, never a
different prefix.

### Six channels put a string into the conversation file

Four tokens were emitted by the **coordinator** of conversation `ef482a21` between 05:05:18Z and
05:05:27Z on 2026-09-06, one per channel. Re-run 2026-09-10 with the shared walker:

```
$ python3 $TOOLS/walk.py "$CONV" --tokens "$PROBE"
line 134  type=user      isSidechain=False ts=2026-09-06T05:05:18.632Z
   p1,p2  @ .message.content[0].content            'HEAD=6bb155d\np1=<p1>\np2=<p2>\n(p3 and p4 deliberately not printed)'
   p1,p2  @ .toolUseResult.stdout                  'HEAD=6bb155d\np1=<p1>\np2=<p2>\n(p3 and p4 deliberately not printed)'
line 138  type=assistant isSidechain=False ts=2026-09-06T05:05:24.735Z
   p1     @ .message.content[0].text               'Probe P1 (assistant message text): `<p1>`'
line 139  type=assistant isSidechain=False ts=2026-09-06T05:05:25.443Z
   p2     @ .message.content[0].input.command      ': <p2>'
line 142  type=user      isSidechain=False ts=2026-09-06T05:05:26.915Z
   p3     @ .message.content[0].content            '<p3>'
   p3     @ .toolUseResult.stdout                  '<p3>'
line 144  type=user      isSidechain=False ts=2026-09-06T05:05:27.100Z
   p4     @ .message.content[0].content            '1\t<p4>\n2\t'
   p4     @ .toolUseResult.file.content            '<p4>\n'
```

Line 134 is the coordinator's own `cat` of the token files, run before the probes; it is a second,
incidental instance of the Bash-output channel and is why `p1` and `p2` show two hits each.

| # | Emission channel | Lands | Entry `type` | Field path |
|---|---|---|---|---|
| 1 | Assistant message text | yes | `assistant` | `message.content[0].text` (line 138) |
| 2 | Bash command string, no output | yes | `assistant` | `message.content[0].input.command` (line 139; `: <p2>` printed nothing) |
| 3 | Bash command output | yes | `user` | `message.content[0].content` **and** `toolUseResult.stdout` (lines 142, 134) |
| 4 | Non-Bash tool result (Read) | yes | `user` | `message.content[0].content` **and** `toolUseResult.file.content` (line 144; `message.content` carries the `1\t` line-number prefix, `toolUseResult.file.content` the raw text) |
| 5 | A subagent's final report | yes | `queue-operation` and `user` | `.content` and `.message.content`, inside `<result>` — see below |
| 6 | A plugin hook's stdout | yes | `attachment` | `.attachment.content` and `.attachment.stdout`, under `attachment.type: "hook_success"` — [see below](#channel-6-a-plugin-hooks-stdout-is-filed-as-an-entry-of-its-own-kind) |
| — | A subagent's own turn | **no** | — | reaches the subagent file only; [evidence](#two-candidate-methods-do-not-land) |
| — | Bash output over ~30 KB | **no** | `user` | replaced by a `<persisted-output>` preview; full text goes to `tool-results/<id>.txt`; [evidence](#two-candidate-methods-do-not-land) |
| — | A `SessionEnd` hook's stdout | **no** | — | the hook runs; its output is filed nowhere; [evidence](#two-hook-placements-fire-without-reaching-the-conversation-file) |
| — | A hook firing inside a subagent | **no** | `attachment` | reaches the subagent file only, like the subagent's own turns; [evidence](#two-hook-placements-fire-without-reaching-the-conversation-file) |

Channels 1–4 are ordinary parts of a turn that Claude Code already records, so four positives out of
four attempts would be a weak result on its own: no method was tried there that could plausibly fail.
The four negatives at the foot of the table are what give it a boundary, and all four are measured
rather than assumed.

#### Channel 5: a subagent's final report crosses into the conversation file

A subagent's intermediate turns stay in its own file. Its final report does not: it arrives in the
conversation file about 100 ms later as a `user` entry wrapped in a `<task-notification>` element,
preceded by a `queue-operation` entry carrying the same text. Measured 2026-09-10 over two handoffs:

```
$ python3 $TOOLS/scan.py handoff $PROJ_WT/555280be-*.jsonl
task a78cb9340f4ca0e62  report 2026-09-06T08:37:32.037Z -> user entry line 242 2026-09-06T08:37:32.156Z (+119 ms)
task a1acd223789ed6dda  report 2026-09-06T08:42:10.340Z -> user entry line 278 2026-09-06T08:42:10.406Z (+66 ms)
```

The `user` entry is `isSidechain: false`, carries `origin.kind == "task-notification"` and
`promptSource == "system"` — which is what distinguishes it from a human prompt — and its content is a
tag sequence `task-notification / task-id / tool-use-id / output-file / status / summary / note /
result / usage`, with the report body inside `<result>`.

**That body is HTML-entity-escaped.** Comparing each report against the `<result>` it arrives in:

```
$ python3 $TOOLS/scan.py escaping $PROJ_WT/555280be-*.jsonl
line 242  identical=False unescape(result)==report=True   &lt;=4 &gt;=4 &amp;=0
line 278  identical=False unescape(result)==report=True   &lt;=12 &gt;=11 &amp;=6
```

`html.unescape()` of the `<result>` body equals the report exactly, and `<`, `>` and `&` are the
characters that differ. **Channel 5 does not carry a marker verbatim if the marker contains an angle
bracket or an ampersand.** No other channel was shown to transform its payload.

The `<output-file>` named in the wrapper is a symlink back to the subagent's own JSONL, not a copy of
the report:

```
$ ls -la /private/tmp/claude-501/…-issue-18/555280be-…/tasks/
lrwxr-xr-x 1 kiyo wheel 162 a1acd223789ed6dda.output -> …/555280be-…/subagents/agent-a1acd223789ed6dda.jsonl
```

#### Channel 6: a plugin hook's stdout is filed as an entry of its own kind

The five channels above are places in a turn; this one is a program Claude Code runs. A throwaway
plugin was built under `$HBASE` — a `plugin.json`, and a `hooks/hooks.json` registering one script
against five events, extended to nine for the third run — and three headless conversations were run
with it loaded, on 2026-09-20 under
2.1.278, from a scratch working directory of their own so their logs land in a project directory
nothing else writes to, `$HOOKPROJ`. The script is what emits:

```sh
#!/bin/bash                                    # $1 is the event name
BASE=$HBASE
TOK=$(cat "$BASE/tok/h")                       # read at run time, not baked into the script
cat > /dev/null                                # the event payload arrives on stdin
printf '%s %s\n' "$(date -u +%H:%M:%S.000)" "$1" >> "$BASE/fired.log"
printf 'HOOKPROBE %s %s\n' "$1" "$TOK"
exit 0
```

The plugin and the scratch working directory were deleted once the runs were over. What stays, as
this section's evidence, is the three conversation files those runs wrote, plus the one subagent
file under the third:

```
$ python3 $TOOLS/scan.py spans $HOOKPROJ/*.jsonl
11b1c7b5 entries=38   with_ts=31   2026-09-20T04:25:47.775Z -> 2026-09-20T04:25:56.089Z
495aaa7b entries=37   with_ts=30   2026-09-20T04:26:54.551Z -> 2026-09-20T04:27:00.891Z
7e75075d entries=37   with_ts=30   2026-09-20T04:27:51.856Z -> 2026-09-20T04:27:59.629Z
```

`hooks.json` points every registered event at that one script, in the shape a plugin declares:

```json
"Stop": [{"hooks": [{"type": "command",
                     "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/emit.sh\" stop"}]}]
```

The first run, with a token freshly generated by `openssl rand -hex 8` into the file the script
reads, and kept for later scans as `$HTOK/h1`:

```
$ cd $HBASE/pcwd && claude -p "Run exactly this Bash command and then reply with only its output:
    grep -c -F -f $HBASE/tok/h $HOOKPROJ/*.jsonl" --plugin-dir $HBASE/hookprobe --allowedTools Bash
2
```

The `2` is the grep's own answer: the glob matched the one file the run had just created, so
`grep -c` printed a bare count. The prompt names the token *file*, never its contents, so no hit on
the token can come from the instruction. That is measured rather than asserted — every `user` entry
of the three probe conversations and of the one subagent file, with the tokens it holds:

```
$ python3 $TOOLS/scan.py prompts $HOOKPROJ/*.jsonl $HOOKPROJ/*/subagents/*.jsonl --tokens $HTOK
11b1c7b5-1768-407c-991 line 4   chars=386   tokens=-
11b1c7b5-1768-407c-991 line 26  chars=109   tokens=-
495aaa7b-918a-4f8a-841 line 4   chars=252   tokens=-
495aaa7b-918a-4f8a-841 line 25  chars=124   tokens=['h2']
7e75075d-29fb-4c06-886 line 4   chars=175   tokens=-
7e75075d-29fb-4c06-886 line 25  chars=908   tokens=-
agent-a76a62b028a410a1 line 1   chars=59    tokens=-
agent-a76a62b028a410a1 line 13  chars=110   tokens=-
```

Line 4 of each conversation is its prompt and line 1 of the subagent file is its work order; none of
the four holds a token. The single `user` entry that does is run 2's line 25 — the `cat` this
document deliberately asked for, to give the next section a quotation to tell apart from an emission.
All five events the first run registered put the token into the conversation file:

```
$ python3 $TOOLS/walk.py $HOOKPROJ/11b1c7b5-*.jsonl --tokens $HTOK
line 3    type=attachment isSidechain=False ts=2026-09-20T04:25:47.775Z
   h1     @ .attachment.content                    'HOOKPROBE sessionstart <h1>'
   h1     @ .attachment.stdout                     'HOOKPROBE sessionstart <h1>\n'
   h1     @ .rendered[0].content                   '<system-reminder>\nSessionStart:startup hook success: HOOKPROBE sessionstart <h1>\n</system-reminder>'
line 14   type=attachment isSidechain=False ts=2026-09-20T04:25:50.252Z
   h1     @ .attachment.content                    'HOOKPROBE userpromptsubmit <h1>'
   h1     @ .attachment.stdout                     'HOOKPROBE userpromptsubmit <h1>\n'
   h1     @ .rendered[0].content                   '<system-reminder>\nUserPromptSubmit hook success: HOOKPROBE userpromptsubmit <h1>\n</system-reminder>'
line 25   type=attachment isSidechain=False ts=2026-09-20T04:25:54.931Z
   h1     @ .attachment.content                    'HOOKPROBE pretooluse <h1>'
   h1     @ .attachment.stdout                     'HOOKPROBE pretooluse <h1>\n'
line 27   type=attachment isSidechain=False ts=2026-09-20T04:25:55.073Z
   h1     @ .attachment.content                    'HOOKPROBE posttooluse <h1>'
   h1     @ .attachment.stdout                     'HOOKPROBE posttooluse <h1>\n'
line 35   type=attachment isSidechain=False ts=2026-09-20T04:25:56.088Z
   h1     @ .attachment.content                    'HOOKPROBE stop <h1>'
   h1     @ .attachment.stdout                     'HOOKPROBE stop <h1>\n'
```

The entry is neither a message nor a tool result. Line 3 whole, with `rendered` dropped and the token
masked:

```
$ python3 $TOOLS/scan.py hookraw $HOOKPROJ/11b1c7b5-*.jsonl --tokens $HTOK
{
 "parentUuid": null,
 "isSidechain": false,
 "attachment": {
  "type": "hook_success",
  "hookName": "SessionStart:startup",
  "toolUseID": "5729eee6-ec9f-462f-99d7-af03ef7481ac",
  "hookEvent": "SessionStart",
  "content": "HOOKPROBE sessionstart <h1>",
  "stdout": "HOOKPROBE sessionstart <h1>\n",
  "stderr": "",
  "exitCode": 0,
  "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/emit.sh\" sessionstart",
  "durationMs": 20
 },
 "type": "attachment",
 "uuid": "b6514e54-33df-4157-8f7e-a9928bc74cd3",
 "timestamp": "2026-09-20T04:25:47.775Z",
 "userType": "external",
 "entrypoint": "sdk-cli",
 "cwd": "…/scratchpad/pcwd",
 "sessionId": "11b1c7b5-1768-407c-991a-f954cb7ca5dd",
 "version": "2.1.278",
 "gitBranch": "HEAD"
}
```

`content` is the hook's stdout with its trailing newline stripped and `stdout` is the raw bytes, in
all 18 hook entries the three runs wrote — `scan.py hooks` reports `content==stdout.strip()=True` on
every one of them. The emitted string carried a **space** and **uppercase ASCII** through unaltered,
which makes channel 6 the only one measured over more than bare lowercase hex. In all three probe
conversations, `SessionStart` and `UserPromptSubmit` additionally get a `rendered` copy wrapped in a
`<system-reminder>` and the other events do not; that is the only difference between the landings.

**The string is computed at run time.** The token file was overwritten with a fresh
`openssl rand -hex 8` between runs, and each run's value kept as `$HTOK/h1`, `h2`, `h3`. Counting
each token in each conversation:

```
$ for t in h1 h2 h3; do printf '%s: ' $t
    for f in $HOOKPROJ/11b1c7b5-*.jsonl $HOOKPROJ/495aaa7b-*.jsonl $HOOKPROJ/7e75075d-*.jsonl; do
      printf '%s ' "$(grep -c -F -f $HTOK/$t $f)"; done; echo; done
h1: 5 0 0
h2: 0 7 0
h3: 0 0 5
```

Each conversation carries only the value that was in the file at the moment it ran, so **what a hook
emits is decided at run time and can name the session and the task** rather than being fixed when the
plugin is installed. (Run 2's seven is five hook entries plus two quotations; the next section is
about those.)

**The entry is on disk before the conversation ends.** The `2` printed above is the probe's own grep,
recorded in the conversation that produced it:

```
$ python3 -c "
import json,sys
for i,l in enumerate(open(sys.argv[1]),1):
    e=json.loads(l)
    if i in (24,26): print(i, e['type'], e['timestamp'], e['message']['content'][0].get('content',''))
" $HOOKPROJ/11b1c7b5-*.jsonl
24 assistant 2026-09-20T04:25:54.897Z
26 user 2026-09-20T04:25:55.073Z 2
```

The Bash call ran between 04:25:54.897Z and 04:25:55.073Z and counted the two hook entries that
preceded it, stamped 04:25:47.775Z and 04:25:50.252Z — so a hook emission was greppable from inside
its own conversation, twelve entries and two further hook events before that conversation ended (the
file closed at 38 lines). The newer of the two was on disk within 4.8 s of its own timestamp, which
is an upper bound set by the agent's latency rather than a flush time: the `PreToolUse` entry at
line 25, stamped at most 0.18 s before the read, was *not* counted, which is the 0.1 s flush lag of
[Liveness](#the-conversation-file-is-live-and-lags-its-own-entries-by-about-01-s) seen from the other
side.

#### The hook entry tells an emission from a quotation

Run 2 asked for the token file to be `cat`-ed and its contents repeated in the reply, so the same
string reached one conversation twice: once because the hook printed it, once because the
conversation quoted it.

```
$ python3 $TOOLS/walk.py $HOOKPROJ/495aaa7b-*.jsonl --tokens $HTOK
line 3    type=attachment isSidechain=False ts=2026-09-20T04:26:54.551Z
   h2     @ .attachment.content                    'HOOKPROBE sessionstart <h2>'
   h2     @ .attachment.stdout                     'HOOKPROBE sessionstart <h2>\n'
   h2     @ .rendered[0].content                   '<system-reminder>\nSessionStart:startup hook success: HOOKPROBE sessionstart <h2>\n</system-reminder>'
line 14   type=attachment isSidechain=False ts=2026-09-20T04:26:56.480Z
   h2     @ .attachment.content                    'HOOKPROBE userpromptsubmit <h2>'
   h2     @ .attachment.stdout                     'HOOKPROBE userpromptsubmit <h2>\n'
   h2     @ .rendered[0].content                   '<system-reminder>\nUserPromptSubmit hook success: HOOKPROBE userpromptsubmit <h2>\n</system-reminder>'
line 24   type=attachment isSidechain=False ts=2026-09-20T04:26:59.312Z
   h2     @ .attachment.content                    'HOOKPROBE pretooluse <h2>'
   h2     @ .attachment.stdout                     'HOOKPROBE pretooluse <h2>\n'
line 25   type=user      isSidechain=False ts=2026-09-20T04:26:59.421Z
   h2     @ .message.content[0].content            '<h2>'
   h2     @ .toolUseResult.stdout                  '<h2>'
line 26   type=attachment isSidechain=False ts=2026-09-20T04:26:59.421Z
   h2     @ .attachment.content                    'HOOKPROBE posttooluse <h2>'
   h2     @ .attachment.stdout                     'HOOKPROBE posttooluse <h2>\n'
line 33   type=assistant isSidechain=False ts=2026-09-20T04:27:00.837Z
   h2     @ .message.content[0].text               'QUOTED <h2>'
line 34   type=attachment isSidechain=False ts=2026-09-20T04:27:00.890Z
   h2     @ .attachment.content                    'HOOKPROBE stop <h2>'
   h2     @ .attachment.stdout                     'HOOKPROBE stop <h2>\n'
```

Lines 25 and 33 are channels 3 and 1 carrying the identical string, 0.1 s either side of a hook
entry. Nothing about the string separates them; the entry does:

| | a hook emission | the same string quoted |
|---|---|---|
| entry `type` | `attachment` | `user` (line 25), `assistant` (line 33) |
| `attachment.type` | `hook_success` | the entry has no `attachment` key |
| field path | `.attachment.content`, `.attachment.stdout` | `.message.content[0].content`, `.toolUseResult.stdout`, `.message.content[0].text` |

The separation is not local to this file. Machine-wide, over every conversation and subagent file
under `~/.claude/projects/`, at 2026-09-20T05:03Z:

```
$ python3 $TOOLS/corpus.py hook-entries
files scanned: 156 conversation + 394 subagent
files holding a hook attachment: 7
  entry type=attachment  attachment.type=hook_success         hookEvent=PostToolUse      4
  entry type=attachment  attachment.type=hook_success         hookEvent=PreToolUse       4
  entry type=attachment  attachment.type=hook_success         hookEvent=SessionStart     3
  entry type=attachment  attachment.type=hook_success         hookEvent=Stop             3
  entry type=attachment  attachment.type=hook_success         hookEvent=SubagentStop     1
  entry type=attachment  attachment.type=hook_success         hookEvent=UserPromptSubmit 3
  entry type=attachment  attachment.type=hook_system_message  hookEvent=PostToolUse      4
  ca75e7c4-22b8-46d6-bac7- entrypoint=['cli']              version=['2.1.239']
  4b750c4a-e82a-4d1f-9dbd- entrypoint=['cli']              version=['2.1.239']
  720ab230-dc70-47b1-a6e4- entrypoint=['cli']              version=['2.1.233']
  11b1c7b5-1768-407c-991a- entrypoint=['sdk-cli']          version=['2.1.278']
  495aaa7b-918a-4f8a-8418- entrypoint=['sdk-cli']          version=['2.1.278']
  7e75075d-29fb-4c06-8860- entrypoint=['sdk-cli']          version=['2.1.278']
  agent-a76a62b028a410a1c. entrypoint=['sdk-cli']          version=['2.1.278']
other entries with `hookEvent` as a JSON key:        0
other entries with "hookEvent" only inside a string: 43
```

**Across those 550 files, `hookEvent` occurs as a JSON key only inside a hook attachment.** The 43
other entries hold the word only inside a string — prose about hooks, written on this machine while
this measurement was being made, which is precisely the class of hit
[the self-reference hazard](#the-self-reference-hazard-is-measured-not-assumed) is about. That count
rises every time this document is edited or read; the key count does not. A substring test counted 43
false positives at 05:03Z; the structural test counted none.

The field path alone is not the test. Over the same 156 + 394 files, keeping only the attachment
types that carry a `content` string:

```
$ python3 $TOOLS/corpus.py attachment-types | grep -v 'content: 0$'
files scanned: 156 conversation + 394 subagent
distinct attachment.type: 32
  skill_listing                   529  with .attachment.content: 529
  hook_success                     18  with .attachment.content: 18
  hook_system_message               4  with .attachment.content: 4
```

Three of the 32 attachment types carry a `.attachment.content` string, and one of them,
`skill_listing`, holds each available skill's own description verbatim — so a marker documented in a
skill description would land at the same path. It is `attachment.type` that discriminates, not the
path.

Two limits of the discriminator, both measured rather than argued:

- The entry identifies the **emitter, not the provenance of the text**. `attachment.content` is
  whatever the hook printed, so a hook that echoed something it had read would file quoted text under
  `hook_success`. What pins a hit to one plugin's hook is `attachment.command`, which records the
  hook's own command line — `bash "${CLAUDE_PLUGIN_ROOT}/hooks/emit.sh" <event>` in all 18 entries
  above.
- All 18 `hook_success` entries on this machine sit in the four probe files listed above, written
  under `entrypoint: "sdk-cli"`. The four hook attachments this measurement did not write are the
  `hook_system_message` entries in the three `cli` files — Claude Code's own notices, carrying
  `content, hookEvent, hookName, toolUseID, type` and no `stdout`, `exitCode` or `command`. So hook
  attachments are filed in interactive sessions too, but **a plugin hook's stdout has been observed
  only headless**.

#### Two hook placements fire without reaching the conversation file

Run 3 registered four further events and asked for a subagent, to find where the channel stops. The
script appends a line to its own log before printing, so a firing is recorded whether or not its
output lands:

```
$ cat $HBASE/fired.log
04:27:51.000 sessionstart
04:27:53.000 userpromptsubmit
04:27:55.000 pretooluse
04:27:57.000 pretooluse
04:27:57.000 posttooluse
04:27:58.000 subagentstop
04:27:58.000 posttooluse
04:27:59.000 stop
04:27:59.000 sessionend
```

`Notification` and `PreCompact` are registered in the same `hooks.json` and do not appear: the run
gave them no occasion, so they are untested rather than negative. Of the nine firings, five reached
the conversation file, three reached the subagent file only, and one reached nothing at all.

**A `SessionEnd` hook's output is filed nowhere.** The script ran — it wrote its line at 04:27:59,
the same second the conversation file took its last write, at 04:27:59.649 — and printed the same
string the eight landing firings printed. It appears in none of the four files of the probe project
directory:

```
$ grep -c 'HOOKPROBE sessionend' $HOOKPROJ/*.jsonl $HOOKPROJ/*/subagents/*.jsonl | sort
…/11b1c7b5-1768-407c-991a-f954cb7ca5dd.jsonl:0
…/495aaa7b-918a-4f8a-8418-28abc9a4933d.jsonl:0
…/7e75075d-29fb-4c06-8860-207335cfd428.jsonl:0
…/7e75075d-29fb-4c06-8860-207335cfd428/subagents/agent-a76a62b028a410a1c.jsonl:0
```

**A hook that fires inside a subagent reaches the subagent file only.** The run's `SubagentStop`,
and the `PreToolUse`/`PostToolUse` pair around the subagent's own Bash call, are in the subagent
file; the conversation file holds only the events of the coordinator's own turn:

```
$ python3 $TOOLS/scan.py hooks $HOOKPROJ/7e75075d-*.jsonl $HOOKPROJ/7e75075d-*/subagents/*.jsonl
7e75075d-29fb-4c06-8860- line 3    hook_success  SessionStart:startup exit=0   content==stdout.strip()=True  keys=…
7e75075d-29fb-4c06-8860- line 14   hook_success  UserPromptSubmit     exit=0   content==stdout.strip()=True  keys=…
7e75075d-29fb-4c06-8860- line 24   hook_success  PreToolUse:Agent     exit=0   content==stdout.strip()=True  keys=…
7e75075d-29fb-4c06-8860- line 26   hook_success  PostToolUse:Agent    exit=0   content==stdout.strip()=True  keys=…
7e75075d-29fb-4c06-8860- line 34   hook_success  Stop                 exit=0   content==stdout.strip()=True  keys=…
agent-a76a62b028a410a1c. line 12   hook_success  PreToolUse:Bash      exit=0   content==stdout.strip()=True  keys=…
agent-a76a62b028a410a1c. line 14   hook_success  PostToolUse:Bash     exit=0   content==stdout.strip()=True  keys=…
agent-a76a62b028a410a1c. line 22   hook_success  SubagentStop         exit=0   content==stdout.strip()=True  keys=…
```

The three subagent-side entries are `isSidechain: true`, the five conversation-side ones
`isSidechain: false`. `SubagentStop` is the obvious place to mark the end of a dispatched task, and
it lands on the far side of the same boundary
[a subagent's own turns](#two-candidate-methods-do-not-land) land on. What does reach the
conversation file for that same dispatch is `PostToolUse` on the `Agent` call, and it is tied to the
dispatch by id:

```
$ python3 $TOOLS/scan.py hookids $HOOKPROJ/7e75075d-*.jsonl $HOOKPROJ/7e75075d-*/subagents/*.jsonl
## 7e75075d-29fb-4c06-8860-
 line 3   SessionStart:startup toolUseID=3ac2d64d-b321-47bc-b1d1-8489c8791595
 line 14  UserPromptSubmit     toolUseID=708d872d-30cd-45f7-bdc5-3087bbb57516
 line 23  tool_use Agent    id=toolu_01NUQwpHhgcXk1gfJEpuVysV
 line 24  PreToolUse:Agent     toolUseID=toolu_01NUQwpHhgcXk1gfJEpuVysV
 line 26  PostToolUse:Agent    toolUseID=toolu_01NUQwpHhgcXk1gfJEpuVysV
 line 34  Stop                 toolUseID=e51d2363-5dd2-4b4a-a947-2bd6e07d9808
## agent-a76a62b028a410a1c.
 line 11  tool_use Bash     id=toolu_011UMEmif2dkF9HYV96ChCoo
 line 12  PreToolUse:Bash      toolUseID=toolu_011UMEmif2dkF9HYV96ChCoo
 line 14  PostToolUse:Bash     toolUseID=toolu_011UMEmif2dkF9HYV96ChCoo
 line 22  SubagentStop         toolUseID=75eb66bd-cd7e-47c2-b9ea-23ea0ecb37a7
```

A `PreToolUse` or `PostToolUse` entry carries the id of the call it brackets — `toolu_01NUQ…` on
lines 24 and 26 is the `tool_use` at line 23 — while the other four events carry a uuid that is not a
tool-call id at all. So a task boundary marked on `SubagentStop` is invisible to the conversation,
while the same boundary marked on `PostToolUse` of the `Agent` call is both visible and attributable
to the dispatch that ended.

### Attribution: the tokens post-date every instruction that could have echoed them

A hit only counts as a landing if it came from the emission and not from the text that requested it.
For channels 1 to 5, three facts establish that, and each is measured on conversation `ef482a21`;
channel 6's tokens are accounted for in its own section above.

**The field paths.** Each hit sits at the exact path its channel predicts, in an entry the
conversation itself produced (`isSidechain: false`, `type` matching the channel). An echo of a request
would sit in a prompt field of a `user` entry, not at `message.content[0].input.command` of an
`assistant` entry.

**The tokens did not exist until after the last human instruction.** The last typed prompt before the
probes is line 122, three characters long; the tokens were generated in-conversation at line 127:

```
$ python3 -c "
import json
for i,e in ((i,json.loads(l)) for i,l in enumerate(open('$CONV'),1)):
    if i<140 and e.get('type')=='user' and (e.get('origin') or {}).get('kind')=='human':
        print('line %-4d ts=%s chars=%d'%(i,e['timestamp'],len(e['message']['content'])))"
line 5    ts=2026-09-06T04:53:42.209Z chars=76
line 54   ts=2026-09-06T04:58:07.323Z chars=12
line 94   ts=2026-09-06T05:01:04.033Z chars=1
line 122  ts=2026-09-06T05:03:52.631Z chars=3

$ # line 127, 2026-09-06T05:05:18.258Z, the command that created the tokens:
for n in 1 2 3 4; do openssl rand -hex 8 > "$PROBE/p$n"; done
```

The longest human prompt before the probes is 76 characters and the immediately preceding one is 3;
none could hold a 16-hex token, and no token existed until 05:05:18.258Z, 86 seconds after the last of
them.

**The work order could not have been the source.** It was passed to a subagent at 05:06:30.864Z —
after every hit at 05:05:24–27Z — and the hits are coordinator emissions (`isSidechain: false`) whose
own instruction is the human prompt above. Counting token occurrences in that work order, as an
earlier draft did, measures a text that post-dates what it is supposed to guard.

### Same-turn read-back works

A marker is only useful if the same turn that writes it can read it back. A token was emitted into
Bash stdout and grepped by the next tool call of the same turn, 2026-09-10:

```
$ openssl rand -hex 8 > "$S/q1"; cat "$S/q1"        # emitting call, entry ts 11:07:47.607Z
$ grep -c -F -f "$S/q1" "$AGENT"                    # reading call,  entry ts 11:07:59.006Z
1
$ grep -c -F -f "$S/q1" "$LIVE"
0
```

The token was on disk and greppable **11.4 s** after the entry carrying it, without leaving the turn.
`-F -f <file>` keeps the token out of the command line, so the hit cannot be an echo of the grep
itself; `walk.py` places it at `.message.content[0].content` and `.toolUseResult.stdout` of a `user`
entry, exactly as channel 3 predicts.

The 11.4 s is dominated by the agent's own latency between two tool calls, not by the writer: the
flush measurement above puts the write itself at about 0.1 s. The independent cross-agent figure
agrees. On 2026-09-06 the coordinator emitted an `assistant` text entry at 05:06:35.762Z (line 159 of
`$CONV`); a subagent running concurrently listed the file at 05:06:46.849Z and counted 160 lines:

```
$ python3 $TOOLS/walk.py "$SUB" --tokens "$PROBE"   # entry 16, 2026-09-06T05:06:46.849Z
  tool_result "…\nlines:\n     160\n=== token counts ===\n<p1>: 2\n<p2>: 2\n<p3>: 1\n<p4>: 1"
```

160 lines means line 159 was on disk, so a coordinator emission was greppable by another agent
**11.1 s** after its timestamp. All four tokens were present on that first look; none needed a retry.
The same read gives a loose 82.1 s bound from the first probe (05:05:24.735Z) — that figure is an
artefact of the emitting turn doing other work in between and is not used anywhere below.

### Two candidate methods do not land

**A subagent's own turns never reach the conversation file.** This is the method an `rn`
implementation is most likely to reach for — have the expert subagent emit the marker — and it does
not work. While this document was being written, the writing subagent's own file grew by 24 entries
while the conversation file stayed byte-identical:

| `wc -c` / `wc -l` | 11:04:23Z | 11:06:08Z |
|---|---|---|
| subagent file `agent-a39f6e28…` | 554,921 B, 126 lines | 610,859 B, 150 lines |
| conversation file `c763d0be…` | 578,631 B, 167 lines | 578,631 B, 167 lines |

The probe of the previous section confirms it directly: `grep -c` for the emitted token returns 1 in
the subagent file and **0** in the conversation file. The separation is by file, and the `isSidechain`
field agrees wherever it exists:

```
$ python3 $TOOLS/scan.py types $LIVE $AGENT
c763d0be-78f2-40 entries 167  | no isSidechain field: 48
    {'assistant/False': 38, 'atis-latch/None': 10, 'attachment/False': 55, 'file-history-snapshot/None': 2, 'last-prompt/None': 9, 'mode/None': 10, 'permission-mode/None': 10, 'pr-link/None': 7, 'system/False': 2, 'user/False': 24}
agent-a39f6e288d entries 332  | no isSidechain field: 0
    {'assistant/True': 158, 'attachment/True': 90, 'user/True': 84}
```

Every entry of the conversation file that carries `isSidechain` has it `false`, and 48 of its 167
entries carry no such field at all — so "every entry is `isSidechain: false`" would overstate it.
Every entry of the subagent file has it `true`. **What does cross the boundary is the subagent's final
report** — channel 5 — and nothing else.

**A tool result over about 30 KB is not written into the JSONL at all.** The conversation directory has
a second child besides `subagents/`:

```
$ ls $PROJ_WT/ef482a21-*/ $PROJ_WT/ef482a21-*/tool-results/
…/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/:            …/tool-results/:
subagents                                           bxs03q1mk.txt
tool-results
```

Above the threshold the entry's `message.content` carries a `<persisted-output>` notice —
`Output too large (30.5KB). Full output saved to: …/tool-results/<id>.txt` — followed by a preview,
and the full text goes to that file:

```
$ python3 -c "                        # the first such entry on this machine
import json,glob,os
for f in glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl')):
    for l in open(f):
        if 'persistedOutputPath' not in l: continue
        r=json.loads(l).get('toolUseResult') or {}
        if 'persistedOutputPath' not in r: continue
        print('toolUseResult keys:',sorted(r.keys()))
        print('persistedOutputSize %d, file on disk %d, stdout kept in the entry %d chars'%(
              r['persistedOutputSize'],os.path.getsize(r['persistedOutputPath']),len(r['stdout'])))
        raise SystemExit"
toolUseResult keys: ['interrupted', 'isImage', 'noOutputExpected', 'persistedOutputPath', 'persistedOutputSize', 'stderr', 'stdout']
persistedOutputSize 41731, file on disk 41731, stdout kept in the entry 15250 chars
```

The threshold was bounded by scanning every `toolUseResult` carrying a `stdout` across all 137
conversation files and every subagent file on this machine:

```
$ python3 $TOOLS/corpus.py persist-bracket
largest result kept inline: 29067 chars
smallest result persisted:  30044 bytes
```

**The threshold lies between 29,067 and 30,044 characters of output**, consistent with a 30,000-character
cap; the corpus contains no result between those sizes, which is how far the material on disk bounds
it. Two consequences: the Bash-output channel silently stops writing into the JSONL for large output,
and `tool-results/<id>.txt` is a further place on disk where an emitted string can end up — one no
grep of the JSONL will find.

### Only 16-character lowercase hex was emitted

All seven tokens were `openssl rand -hex 8` output: 16 characters, `[0-9a-f]` only. The measurement
therefore establishes the six channels **only for a bare alphanumeric run carrying no shell, JSON or
markup metacharacter**. Channel 6 reaches a little further, because what its hook printed was
`HOOKPROBE <event> <token>`: a **space** and **uppercase ASCII** arrived verbatim at
`.attachment.content`, and the only transformation seen anywhere on that channel was the trailing
newline being stripped from `content` while `stdout` kept it.

Task #2 must not assume any of the following survives a channel, because none was tested: a **space**
or any whitespace on channels 1 to 5; `#`, `:`, `/`, `|`; a single or double **quote**; a
**backslash**; a **newline** inside the marker; **non-ASCII** characters; a marker long enough to be
truncated or persisted out of the JSONL; and a marker whose text is a substring of another marker.
An interior space is the one item channel 6 has evidence for. Two channels are quoting-sensitive
in ways a hex token cannot expose — channel 2 records the marker as it appeared on a shell command
line, channel 4 as file bytes — and channel 5 is *known* to transform `<`, `>` and `&`.

## Part 2 — What a later reader can rely on

### A file is placed by relocation target, not by the working directory of its entries

Each working directory has a project directory whose name is that path with `/` and `.` both replaced
by `-` (`printf '%s' "$p" | tr '/.' '--'` reproduces it). Six exist for this repository — the main
checkout plus `aiya`, `hpate`, `issue-17`, `issue-18` and `techting` — listed by
`ls -d ~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm*` on 2026-09-10.

The mapping is not injective, so "each worktree gets its own directory" is a property of these paths
rather than of the scheme: `/` and `.` both become `-`, so `/a/b.c` and `/a/b-c` both name `-a-b-c`.
All 32 project directories on this machine match `^[A-Za-z0-9-]*$`, so no other character class has
been exercised and nothing is known about a space or a non-ASCII path segment.

Directory membership is not decided by the `cwd` an entry records. The main checkout's project
directory holds three files that carry a `relocated` entry; none of the 69 files across the five
worktree directories does. Measured 2026-09-10:

```
$ for d in $PROJ_MAIN ~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-*; do
    printf '%-56s %s / %s\n' "$(basename $d)" \
      "$(grep -l '"type":"relocated"' "$d"/*.jsonl 2>/dev/null | wc -l|tr -d ' ')" \
      "$(ls "$d"/*.jsonl 2>/dev/null | wc -l|tr -d ' ')"
  done
-Users-kiyo-work-lovaizu-ccpm                            3 / 4
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-aiya     0 / 31
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-hpate    0 / 13
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-17 0 / 5
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18 0 / 5
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-techting 0 / 15
```

The `relocated` entry names where the conversation went — `"relocatedCwd":"/Users/kiyo/work/lovaizu/ccpm"`
in all three — while the entries of those same files record a worktree. How far that goes is bounded
by how few entries carry a `cwd` at all:

```
$ python3 $TOOLS/scan.py cwd $PROJ_MAIN/*.jsonl
04319f87 entries=11   with_cwd=3   cwds=['/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/aiya']
10dcd188 entries=13   with_cwd=3   cwds=['/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-17']
5466c142 entries=13   with_cwd=3   cwds=['/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18']
8dca6935 entries=114  with_cwd=76  cwds=['/Users/kiyo/work/lovaizu/ccpm']
```

**Three files diverge from their directory on every entry that records a `cwd` — but only 3 of 11 to
13 entries record one.** The divergence is real and the sample inside each file is small.

The three divergent files are stubs of 3–4 KB and 11–13 entries spanning under 90 ms, with **zero**
`assistant` entries — no task work at all. A tally of their entry types shows what they share: a
`/clear` command entry with its empty `local-command-stdout` system entry, one `mode`, two
`file-history-snapshot`, one `last-prompt`, two `worktree-state` (the first naming the worktree, the
second `worktreeSession: null`) and two `relocated`. They do not share everything — two of the three
carry two `cost-state` entries and `04319f87` carries none. In each, `worktreeSession.originalCwd`,
`preEnterOriginalCwd` and `relocatedCwd` are the same path, the checkout the worktree hangs off, so
the relocation target is the recorded origin rather than anything computed at relocation time.

**Relocation happens mid-file**: the two `relocated` entries sit at lines 7 and 10 of 11 in
`04319f87`, and at lines 7 and 12 of 13 in the other two, with entries before and after. A path
resolved earlier in a session therefore stops being the file's location partway through, which rules
out caching a conversation's location once.

**Not established — the trigger.** All three stubs pair a `/clear` with a worktree-to-`null`
`worktree-state` transition, so this material cannot separate "leaving a worktree relocates the file"
from "`/clear` inside a worktree relocates the file", and no file on this machine carries real work
*and* a `relocated` entry.

**The consequence for a marker reader: globbing one working directory's project directory both misses
and over-returns.** `5466c142` belongs to the issue-18 worktree by every `cwd` and `gitBranch` it
records, yet it is filed under the main checkout; conversely, grepping the main checkout's directory
returns entries whose `cwd` is a worktree.

### The file set changes while the session is open

The 2026-09-06 round recorded three conversation files for this session. There are now five:

```
$ python3 $TOOLS/scan.py spans $PROJ_WT/*.jsonl
17080efa entries=191  with_ts=134  2026-08-30T14:01:09.992Z -> 2026-08-30T14:19:43.757Z
555280be entries=296  with_ts=266  2026-09-06T04:53:42.208Z -> 2026-09-06T08:43:11.345Z
c763d0be entries=167  with_ts=126  2026-09-10T10:52:57.852Z -> 2026-09-10T10:58:50.352Z
eded9b12 entries=184  with_ts=141  2026-08-30T14:20:31.090Z -> 2026-09-05T01:34:32.173Z
ef482a21 entries=370  with_ts=270  2026-09-06T04:53:42.208Z -> 2026-09-06T08:34:49.927Z
```

Files appear while the session is open, and existing files keep growing — `ef482a21` was 268 entries
when the first round measured it and is 370 now. **Any enumeration of a session's conversations is a
snapshot**, and this is exactly the condition a task-boundary mechanism has to work under.

Nor does an entry's own metadata identify where its file sits. Pairing `cwd` with `gitBranch` per
entry in `17080efa` shows every `cwd`-carrying entry naming the issue-18 worktree while 94 of them
record `gitBranch: main`, and 63 of the file's 191 entries carry neither field:

```
$ python3 -c "
import json,sys,collections
es=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for k,v in sorted(collections.Counter((e.get('cwd'),e.get('gitBranch')) for e in es).items(),key=str):
    print('  cwd=%s gitBranch=%s -> %d'%(k[0],k[1],v))" $PROJ_WT/17080efa-*.jsonl
  cwd=/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18 gitBranch=main -> 94
  cwd=/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18 gitBranch=worktree-issue-18 -> 34
  cwd=None gitBranch=None -> 63
```

A timestamp-ordered sweep can also drop a whole file. One file on this machine carries entries but no
`timestamp` anywhere:

```
$ python3 $TOOLS/corpus.py no-timestamp
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-tech a08bd6fc entries 1 {'bridge-session': 1}
```

`555280be` was in that state too when it first appeared during the previous review round — 10 entries,
no timestamps, its `file-history-snapshot` entries replaying another file's `messageId`s — before it
grew into the 296-entry file above. A file with no timestamps is invisible to a timestamp-ordered
sweep and can grow into a substantive conversation later.

### A conversation can continue into a new file that replays the old one

`555280be` and `ef482a21` share a start timestamp because the first is a continuation of the second,
written as a **new file under a new `sessionId` that replays every earlier entry verbatim**:

```
$ python3 -c "
import json,sys
L=lambda p:[json.loads(l) for l in open(p) if l.strip()]
a,b=L(sys.argv[1]),L(sys.argv[2])
ua={e['uuid'] for e in a if e.get('uuid')}; ub={e['uuid'] for e in b if e.get('uuid')}
print('ef482a21 uuids',len(ua),'555280be uuids',len(ub),'shared',len(ua&ub))
print('555280be sessionIds', {e.get('sessionId') for e in b if e.get('sessionId')})
print('sessionId on the replayed entries:', {e.get('sessionId') for e in b if e.get('uuid') in ua})" \
    $PROJ_WT/ef482a21-*.jsonl $PROJ_WT/555280be-*.jsonl
ef482a21 uuids 229 555280be uuids 256 shared 229
555280be sessionIds {'555280be-6a99-451d-a64b-f48c62d964df'}
sessionId stamped on the replayed entries: {'555280be-6a99-451d-a64b-f48c62d964df'}
```

All 229 of the predecessor's entries reappear in the successor with their original `uuid` and original
`timestamp`, but restamped with the new `sessionId`; 27 further entries follow, the earliest at
08:37:32.156Z, 2 m 42 s after the predecessor's last entry. Every entry of the successor carries
`sessionKind: "bg"`, which the predecessor never carries — so what was measured is Claude Code's
background-session continuation, not necessarily what `--resume` or `--continue` do.

**The pair is linked by a structural field.** The predecessor's last entry is a type this document had
not previously recorded:

```
$ grep -h '"type":"continued-in"' $PROJ_WT/*.jsonl
{"type":"continued-in","timestamp":"2026-09-06T08:34:49.927Z","sessionId":"ef482a21-4765-41d3-9d74-aa4c8d40f5d8","continuedInSessionId":"555280be-6a99-451d-a64b-f48c62d964df"}
```

It appears in 1 of the 137 conversation files on this machine — the only continuation of this kind in
the corpus — and it is a forward pointer only: the successor carries no field naming the predecessor.

Two consequences for a marker reader:

- **A marker emitted before the continuation exists twice on disk**, in two files, under identical
  `uuid`s and identical original timestamps. Deduplicating by `uuid` works; treating each file as a
  distinct stretch of history does not. The four probe tokens show it — the same hit counts in the
  predecessor and in the successor, and nothing in the other three files:

  ```
  $ for f in $PROJ_WT/*.jsonl; do printf '%s: ' "$(basename $f | cut -c1-8)"
      for n in p1 p2 p3 p4; do printf '%s=%s ' $n "$(grep -c -F -f $PROBE/$n $f)"; done; echo; done
  17080efa: p1=0 p2=0 p3=0 p4=0
  555280be: p1=2 p2=2 p3=1 p4=1
  c763d0be: p1=0 p2=0 p3=0 p4=0
  eded9b12: p1=0 p2=0 p3=0 p4=0
  ef482a21: p1=2 p2=2 p3=1 p4=1
  ```
- **`continued-in` orders that pair**, which is more than the worktree pointer below can do — but n=1,
  and it says nothing about the other four files of this session.

### A restart can append into the existing file, marked only by the version stamp

Scanning every conversation file on this machine for a change of `version` within one file:

```
$ python3 $TOOLS/corpus.py versions
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-hpat f96e5843 {'2.1.261': 75, '2.1.263': 129}
-Users-kiyo-work-lovaizu-dotfiles--claude-worktrees- 1b4dd5b8 {'2.1.239': 488, '2.1.240': 16}
files with more than one distinct version: 2 / 137
```

Both seams look the same. Printing `(line, type, version, timestamp, uuid, parentUuid)` around the
version change in `1b4dd5b8`:

```
$ python3 $TOOLS/scan.py seam ~/.claude/projects/-Users-kiyo-work-lovaizu-dotfiles--claude-worktrees-herdr4mac/1b4dd5b8-*.jsonl
system                 v=2.1.239  ts=2026-08-24T00:10:29.358Z   uuid=c7b6b082 parent=271452ce
bridge-session         v=None     ts=None                       uuid=None parent=None
user                   v=2.1.240  ts=2026-08-24T00:24:29.842Z   uuid=1f14e004 parent=c7b6b082
user                   v=2.1.240  ts=2026-08-24T00:24:29.842Z   uuid=aea67ec7 parent=1f14e004
entries whose parentUuid is absent from the file: 0
```

One `sessionId` throughout, no compact-summary entry, a 14-minute gap, and an unbroken `parentUuid`
chain across the seam (`1f14e004`'s parent is the pre-seam `c7b6b082`; zero entries in the file carry
a `parentUuid` absent from it). `f96e5843` matches: same `sessionId`, no summary, 16 m 8 s gap,
`52192322`'s parent is the pre-seam `2c62a778`.

A running process cannot change the version string it stamps, so **a restart appended into the existing
file under the same id, leaving no seam record other than the version change** — an inference from the
version stamp, with nothing else in the file marking the seam. The `bridge-session` entry sitting next
to both seams is not that record: it appears in 25 of 137 files and 14 times inside `f96e5843` alone.

So there are two observed continuation shapes: this one, and the new-file replay above. Neither is
attributable to a specific command-line flag from the material on disk.

**The version stamp does not work as a general discriminator**, because several versions are in use at
once. Taking the first and last timestamp of each version across every file on this machine:

```
$ python3 $TOOLS/corpus.py version-range
  2.1.251   first=2026-08-30T12:27:16.653Z  last=2026-09-06T04:43:55.344Z
  2.1.252   first=2026-09-01T07:25:21.343Z  last=2026-09-06T05:37:14.089Z
  2.1.261   first=2026-09-05T11:54:27.870Z  last=2026-09-06T08:52:03.322Z
  2.1.263   first=2026-09-06T04:53:17.428Z  last=2026-09-10T11:17:22.090Z   ← still running: `last` advances on every re-run
  2.1.265   first=2026-09-10T10:51:05.750Z  last=2026-09-10T10:58:50.352Z
  2.1.267   first=2026-09-10T10:54:32.431Z  last=2026-09-10T10:55:44.508Z
```

The version ranges overlap heavily — `2.1.265` and `2.1.267` were both written within four minutes
today — so an old stamp after a long gap means only that the writing process is old, not that it was
never restarted. That is why `eded9b12`'s 90-hour gap, listed under
[What this still cannot answer](#what-this-still-cannot-answer), stays undecided.

### Compaction stays in one file and replays earlier prose into it

Exactly one conversation file on this machine carries a compaction summary, so everything in this
section is n=1:

```
$ printf 'machine: %s / %s\n' \
    "$(grep -l '"isCompactSummary":true' ~/.claude/projects/*/*.jsonl 2>/dev/null | wc -l|tr -d ' ')" \
    "$(ls ~/.claude/projects/*/*.jsonl | wc -l|tr -d ' ')"
machine: 1 / 137
```

In that file, compaction writes one `user` entry with `isCompactSummary: true` into the same file under
the same `sessionId` — no new conversation, no new file:

```
$ T=~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-techting/4b750c4a-*.jsonl
$ python3 -c "
import json,sys
es=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]
print('entries %d, distinct sessionId %s'%(len(es),{e.get('sessionId') for e in es if e.get('sessionId')}))
for i,e in enumerate(es,1):
    if not e.get('isCompactSummary'): continue
    c=e['message']['content']
    print('line %d type=%s ts=%s isSidechain=%s chars=%d'%(i,e.get('type'),e['timestamp'],e.get('isSidechain'),len(c)))
    print('head:',repr(c[:90]))" $T
entries 405, distinct sessionId {'4b750c4a-e82a-4d1f-9dbd-cd1938cc4472'}
line 307 type=user ts=2026-08-22T06:21:18.412Z isSidechain=False chars=10341
head: 'This session is being continued from a previous conversation that ran out of context. The '
```

A reader looking for a compaction boundary should look for that field, not for a second file.

**The duplication hazard is what matters for cutting an interval.** The summary is 10,341 characters of
prose *about* the earlier conversation, so some earlier text reappears in it. The decision-relevant
direction is how likely a given earlier string is to be reproduced — not how much of the summary is
old text:

```
$ python3 - "$T" <<'PY'
import json,re,sys
lines=open(sys.argv[1]).read().splitlines()
es=[json.loads(l) for l in lines if l.strip()]
i=[k for k,e in enumerate(es) if e.get('isCompactSummary')][0]
summ=es[i]['message']['content']; before='\n'.join(lines[:i])
earlier=sorted(set(re.findall(r'`([^`\n]{8,60})`',before)))
print('backtick-quoted strings appearing before the summary: %d'%len(earlier))
print('of those, reproduced in the summary: %d'%sum(1 for t in earlier if t in summ))
PY
backtick-quoted strings appearing before the summary: 194
of those, reproduced in the summary: 35
```

**35 of 194 earlier quoted strings — about 18% — were reproduced in the summary.** (The converse
tally, 27 of the summary's 39 quoted strings being older text, describes what the summary is made of
and says nothing about the odds facing any particular marker.) A marker quoted in prose before a
compaction therefore has a material chance of appearing a second time, later in the file, timestamped
at compaction time rather than at the boundary it names — so "the last occurrence of marker X" can
return the summary's copy. Whether a marker sitting in a Bash command string or a tool result is
reproduced was not measured.

### Line order and timestamp order disagree

Measured 2026-09-10 across this session's five conversation files, listing every adjacent pair whose
timestamps run backwards:

```
$ python3 $TOOLS/scan.py inversions $PROJ_WT/*.jsonl
17080efa  line 69   user               -> line 70   attachment          -0.001s
17080efa  line 90   user               -> line 91   attachment          -0.001s
17080efa  line 122  file-history-delta -> line 123  assistant           -0.019s
17080efa  line 145  pr-link            -> line 146  assistant           -3.094s
17080efa  line 188  queue-operation    -> line 189  assistant           -0.025s
555280be  line 12   queue-operation    -> line 13   user                -13429.938s
555280be  line 14   user               -> line 15   attachment          -0.001s
555280be  line 52   user               -> line 53   attachment          -0.001s
555280be  line 249  queue-operation    -> line 250  assistant           -30.169s
555280be  line 254  queue-operation    -> line 255  attachment          -8.590s
c763d0be  line 6    user               -> line 7    attachment          -0.001s
eded9b12  line 83   user               -> line 84   attachment          -0.001s
ef482a21  line 6    user               -> line 7    attachment          -0.001s
ef482a21  line 54   user               -> line 55   attachment          -0.001s
ef482a21  line 321  queue-operation    -> line 322  system              -0.060s
```

The entry stamped ahead of its successor is always a bookkeeping type — `queue-operation`, `pr-link`,
`file-history-delta`, or a `user` entry running 1 ms ahead of its own `attachment`. No `assistant`
entry was ever the ahead-stamped one. But the backstep is not small: **13,429.9 s (3 h 43 m)** at
`555280be` line 12, where resume-time bookkeeping precedes the replayed prefix described above, and
30.2 s at line 249.

**That figure is a running maximum observed at 2026-09-10T11:00Z, not a bound.** It was 3.094 s when
the previous round measured three files and grew to 13,429.9 s when two more appeared. No marker
scheme should treat any number from this measurement as a safe separation.

A second ordering problem: **76 of `ef482a21`'s 268 entries carried no `timestamp` at all** when the
first round measured it, and 100 of 370 do now:

```
$ python3 -c "
import json,collections
es=[json.loads(l) for l in open('$CONV') if l.strip()]
no=[e for e in es if not e.get('timestamp')]
print('%d / %d'%(len(no),len(es)), dict(collections.Counter(e.get('type') for e in no)))"
100 / 370 {'mode': 19, 'permission-mode': 19, 'atis-latch': 19, 'last-prompt': 18, 'ai-title': 17, 'file-history-snapshot': 5, 'cost-state': 3}
```

Which types those are is the whole inventory in use on this machine:

```
$ python3 $TOOLS/corpus.py entry-types
distinct entry types: 19
attachment 9194, assistant 7350, user 4779, mode 1457, last-prompt 1450, pr-link 1443, atis-latch 1241,
system 1093, queue-operation 962, ai-title 836, file-history-snapshot 762, permission-mode 454,
worktree-state 374, bridge-session 272, file-history-delta 82, cost-state 73, relocated 14,
agent-name 4, continued-in 1
```

**Consequence: cutting an interval by line number and cutting it by timestamp give different
boundaries.** A timestamp sort silently drops the untimestamped entries or must fall back on line order
for them; a line-number cut includes entries whose timestamps fall hours outside the interval. The rule
has to be chosen explicitly.

### Cross-conversation pointers: one forward chain, one worktree-origin pointer, no ordering

Besides `continued-in`, one in-file pointer to another conversation exists: `worktree-state` entries
carry `worktreeSession.sessionId`. Scanned across the 73 ccpm conversation files, 2026-09-10:

```
$ python3 $TOOLS/corpus.py worktree-ptr
-Users-kiyo-work-lovaizu-ccpm                             3 file(s); targets [('17080efa',), ('6463aea8',), ('6ff22937',)]; self-pointing 0
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-aiya     11 file(s); targets [('6ff22937',)]; self-pointing 1
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-17  1 file(s); targets [('6463aea8',)]; self-pointing 1
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18  1 file(s); targets [('17080efa',)]; self-pointing 1
files carrying worktreeSession.sessionId: 16 / 73
```

It names the conversation that *created or entered the worktree*, not the immediately preceding one:
all eleven `aiya` conversations name the same target and one of them is that target. It partitions
conversations by worktree origin, does not chain, and is usually absent — 57 of 73 files carry no
`worktree-state` entry with a non-null `worktreeSession`, including four of this session's five
conversations (only `17080efa` has any, nine of them).

`leafUuid` on `last-prompt` entries is not a cross-conversation link either: every value resolves
inside its own file.

```
$ python3 -c "
import json
es=[json.loads(l) for l in open('$CONV') if l.strip()]
lp=[e.get('leafUuid') for e in es if e.get('type')=='last-prompt']
uu={e['uuid'] for e in es if e.get('uuid')}
print('last-prompt %d, distinct leafUuid %d, resolving in this file %d'%(
      len(lp),len(set(lp)),sum(1 for v in set(lp) if v in uu)))"
last-prompt 18, distinct leafUuid 18, resolving in this file 18
```

Eighteen, where the 2026-09-06 round recorded seven at 05:07Z: the file grew. Every count in this
document is the count at its stated time.

### The self-reference hazard is measured, not assumed

A substring grep for a conversation id is not a test for a link between conversations, and it does not
return a stable answer. Counting each of this session's five ids inside the other four files:

```
$ python3 -c "
import glob,os,sys
files=sorted(glob.glob(sys.argv[1])); ids=[os.path.basename(f)[:-6] for f in files]
for f,me in zip(files,ids):
    raw=open(f,encoding='utf-8',errors='replace').read()
    print(' in %s: %s'%(me[:8],{o[:8]:raw.count(o) for o in ids if o!=me}))" '$PROJ_WT/*.jsonl'
 in 17080efa: {'555280be': 0, 'c763d0be': 0, 'eded9b12': 0, 'ef482a21': 0}
 in 555280be: {'17080efa': 9, 'c763d0be': 0, 'eded9b12': 2, 'ef482a21': 254}
 in c763d0be: {'17080efa': 0, '555280be': 0, 'eded9b12': 0, 'ef482a21': 0}
 in eded9b12: {'17080efa': 0, '555280be': 0, 'c763d0be': 0, 'ef482a21': 0}
 in ef482a21: {'17080efa': 10, '555280be': 1, 'c763d0be': 0, 'eded9b12': 2}
```

The `17080efa` count inside `ef482a21` was 0 in the first round, 6 in the second, and is 10 now: every
increment is this document being read back into the conversation it describes. Only one of those 254
hits is structural — the `continued-in` entry.

The text lands in the same fields an emission does. Running the walker with the document's own first
line as needle, over every conversation and subagent file of this session:

```
$ sed -n '1p' .rn/20260830-issue-18/evidence/1-jsonl-behaviour.md > $S/needle
$ for f in $PROJ_WT/*.jsonl $PROJ_WT/*/subagents/*.jsonl; do
    python3 $TOOLS/walk.py "$f" --needle-file $S/needle; done
```

Nine distinct field paths came back at 2026-09-10T11:30Z — `.message.content[0].content`,
`.message.content[0].input.command`, `.message.content[0].input.content`, `.toolUseResult`,
`.toolUseResult.content`, `.toolUseResult.file.content`, `.toolUseResult.stdout`,
`.toolUseResult.structuredPatch[N].lines[M]` and `.attachment.snippet` — reached by reading the file
with `Read`, reading it with `cat` or `grep`, writing it, editing it, and naming its first line on a
command line. Eleven subagent files carry the text and two conversation files do, the latter through a
`git log` whose commit subject quotes the document. The list keeps growing as the document is worked
on, which is itself the point.

Four of those nine — `.message.content[0].content`, `.message.content[0].input.command`,
`.toolUseResult.stdout` and `.toolUseResult.file.content` — are exactly where channels 2, 3 and 4 land.
**A marker whose format is described in a document that is later read, or quoted in a work order, is
indistinguishable by grep from a real emission of it on channels 1 to 5**, and for those five neither
a field-path nor an entry-type discriminator separates the two, because the defining text lands at
the same paths. This is why token values are elided throughout.

Channel 6 is the exception, and it is the reason the channel was probed at all: a hook emission is an
`attachment` entry of type `hook_success`, a shape the nine paths above do not include and quoted text
cannot produce — measured in
[The hook entry tells an emission from a quotation](#the-hook-entry-tells-an-emission-from-a-quotation).
A marker emitted through a hook can therefore be described in this document, and quoted in a work
order, without either mention counting as a landing.

## What this still cannot answer

- **How an emission on channels 1 to 5 is told apart from the text that defines it.** Measured above;
  no discriminator found for those five. Channel 6 has one, so this constrains the marker's form only
  if task #2 chooses a channel other than the hook.
- **Whether a marker containing punctuation, a quote, a newline or non-ASCII survives a channel.**
  Channels 1–5 were measured on 16-character lowercase hex only, channel 6 on the same alphabet plus
  a space and uppercase ASCII. `<`, `>` and `&` are known to be escaped on channel 5 and untested
  elsewhere.
- **What a hook emits on `Notification` and `PreCompact`.** Both were registered; neither fired in
  the probe runs, so both are untested. Nor was an interactive session measured: every
  `hook_success` entry on this machine was written headless, under `entrypoint: "sdk-cli"`.
- **What `--resume` and `--continue` write.** Two continuation shapes were measured — a new file
  replaying the old one under a new `sessionId` with `sessionKind: "bg"`, and a restart appending into
  the existing file across a version change — but neither can be attributed to a particular flag from
  the material on disk. The version stamp does not help decide which happened in a given file: on
  2026-09-05, when `eded9b12` resumed after a 90-hour gap stamped `2.1.251`, this machine's files
  carried `2.1.251`, `2.1.252` and `2.1.261` on the same day, so several versions were in concurrent
  use and an old stamp after a gap discriminates nothing.
- **How to enumerate a session's conversations completely.** Globbing one project directory is unsound
  in both directions, the file set moves while the session is open, `continued-in` covers one pair, and
  `worktreeSession.sessionId` names a worktree origin rather than an order. No measured method is
  complete.
- **What the relocation trigger is**, and how a relocated file that contains real work behaves — no
  such file exists on this machine.
- **Whether a marker in a command string or tool result survives compaction unduplicated.** Only
  backtick-quoted prose was measured, at n=1, at about 18%.

## Which blocks re-run and which are frozen records

- **Re-runnable at any time** on this machine: every block under "Part 2 — what a later reader can
  rely on", plus the append-only test. They read only the logs, so their figures come back larger,
  never different in kind.
- **Frozen records.** Every block that depends on `$PROBE` — the whole of
  [Six channels land](#six-channels-put-a-string-into-the-conversation-file) except its channel-6
  subsections,
  [Attribution](#attribution-the-tokens-post-date-every-instruction-that-could-have-echoed-them)
  and the cross-agent figure in [Same-turn read-back](#same-turn-read-back-works). `$PROBE` is a
  per-conversation scratchpad directory belonging to conversation `ef482a21`. It still existed on
  2026-09-10 and every block above was re-run against it that day, but nothing keeps it alive; once it
  is cleaned up, those blocks cannot be re-run and the outputs quoted here are the only record. The
  same-turn probe and the flush measurement are one-shot for the same reason — they were emitted by
  the agent that wrote this document, into that agent's own file.
- **The channel-6 blocks sit in between.** The three probe conversations —
  `11b1c7b5-…`, `495aaa7b-…` and `7e75075d-…`, plus `7e75075d-…/subagents/agent-a76a62b028a410a1c` —
  are ordinary log files and stay at `$HOOKPROJ`, so every scan over them (`walk.py`, the four
  `scan.py` hook subcommands, the two `corpus.py` censuses, the `grep` counts) re-runs as long as
  those files exist. What does not come back is the plugin: it was a throwaway under `$HBASE` and was
  deleted once the runs were over, so a *new* hook probe means building one again, and the script's
  own `$HBASE/fired.log` went with it. `$HTOK` keeps the three token values so the masked blocks can
  be re-derived; it is a scratchpad directory and dies with the scratchpad, exactly as `$PROBE` does.
  The two machine-wide censuses grow with the corpus, so their figures are stamped with the minute
  they were taken.
- Re-running the frozen blocks would mean emitting fresh tokens from a coordinator turn, which is a
  measurement task #2 can commission if it needs a channel this document did not test.
