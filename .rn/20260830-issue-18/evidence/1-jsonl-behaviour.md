# Where an emitted string lands in Claude Code's conversation log

Measured 2026-09-06 against the live logs on this machine, under:

```
$ claude --version
2.1.263 (Claude Code)
```

Every fact here is about undocumented on-disk internals, so it is bound to that version and to this
machine's history. Each claim carries the command that produced it and the output that came back;
where output is shortened, the block says so.

## How this document names things

Claude Code's `sessionId` names **one conversation**, not an `rn` session — the pair this measurement
exists to keep apart.

- **session** — the `rn` session, `.rn/20260830-issue-18/`. Never used for a Claude Code log.
- **conversation** — one Claude Code log file, named for its `sessionId`. The conversation that emitted
  the probes is `ef482a21`; its file is the **conversation file**.
- **subagent file** — a subagent's own turns, two levels below the conversation file at
  `<conversation-uuid>/subagents/agent-*.jsonl`.
- **probe** — the act of emitting. **token** — the string emitted.
- **main checkout** — `/Users/kiyo/work/lovaizu/ccpm`. **worktree** — `…/.claude/worktrees/issue-18`.

Shorthand used in the command blocks:

```
PROJ_MAIN=~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm
PROJ_WT=~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18
CONV=$PROJ_WT/ef482a21-4765-41d3-9d74-aa4c8d40f5d8.jsonl
SUB=$PROJ_WT/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/subagents/agent-adcd0d76cf2237e15.jsonl
PROBE=/private/tmp/claude-501/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/scratchpad/probe
```

`$PROBE` holds one file per token, written before any probe was emitted. Token values are read from
those files and never typed into a command or into this document; they appear below elided as
`<p1>`…`<p4>`. That is not tidiness. This document is read back into the conversation it describes, so
any literal written here becomes a hit in every later grep of the log — a hazard measured, not
assumed, in *A substring grep is not a test for a structural link* below.

**When each figure was taken.** The probes and the first grep ran 2026-09-06 05:05–05:07Z in an earlier
round; those figures are quoted from the log as recorded and are labelled as such. Everything else was
re-measured 05:22–05:29Z for this document. The log is append-only and still growing, so re-running
any count now returns a larger number than the one printed here.

## The four emission points all land, each in the field its point predicts

Four probes were emitted from `ef482a21` at 05:05:18–05:05:27Z, one per candidate emission point.
Attribution is a walk over every string field of every parsed entry — not an eyeball over raw lines —
so each hit is reported at the JSON path it occupies. Re-measured 05:24Z:

```
$ python3 - "$CONV" "$PROBE" <<'PY'
import json,sys,os
toks={n:open(os.path.join(sys.argv[2],n)).read().strip() for n in ('p1','p2','p3','p4')}
def mask(s):
    for n,v in toks.items(): s=s.replace(v,'<%s>'%n)
    return s
for i,l in enumerate(open(sys.argv[1]),1):
    if not any(v in l for v in toks.values()): continue
    e=json.loads(l)
    print('line %-4d type=%-9s isSidechain=%-5s ts=%s'%(i,e.get('type'),e.get('isSidechain'),e.get('timestamp')))
    def walk(o,p=''):
        if isinstance(o,str):
            hs=[n for n,v in toks.items() if v in o]
            if hs: print('   %-6s @ %-38s %s'%(','.join(sorted(hs)),p,mask(repr(o))[:110]))
        elif isinstance(o,dict):
            for k,v in o.items(): walk(v,p+'.'+k)
        elif isinstance(o,list):
            for j,v in enumerate(o): walk(v,p+'[%d]'%j)
    walk(e)
PY
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

| Emission point | Landed | Entry `type` | JSONL field path | Detail |
|---|---|---|---|---|
| Assistant message text | yes | `assistant` | `message.content[0].text` | line 138 |
| Bash command string, no output | yes | `assistant` | `message.content[0].input.command` | line 139; the command `: <p2>` printed nothing |
| Bash command output | yes | `user` | `message.content[0].content` **and** `toolUseResult.stdout` | lines 142 and 134; two field paths in one entry |
| Non-Bash tool result (Read) | yes | `user` | `message.content[0].content` **and** `toolUseResult.file.content` | line 144; `message.content` carries the `1\t` line-number prefix, `toolUseResult.file.content` is the raw text |

Line 134 is the probing turn's own `cat` of the token files, run before the four probes. It is a
second, incidental instance of the "Bash command output" point landing, and it is why `p1` and `p2`
show two hits each; it is not counted as their intended landing.

**The negative column is empty, and that is a weak result rather than a strong one.** Four points were
tried and four landed; no method was tried that could plausibly fail — every candidate was an ordinary
part of a turn that Claude Code already records. The measurement shows these four work. It shows
nothing about where the boundary of "works" lies, because the boundary was never approached.

### Attribution rests on the field-path walk, and on a work order that names no token

The field-path walk above is the load-bearing guard. Each hit sits at the exact JSON path its emission
point predicts, in an entry the conversation itself produced (`isSidechain: false`, `type` matching the
point). A hit that were merely an echo of the request would sit in a prompt field of a `user` entry,
not in `message.content[0].input.command` of an `assistant` entry.

The second guard is that the requesting instruction contains no token value, so no hit above can be an
echo of it. The work order was passed to the probing subagent as the `Agent` tool's `prompt` input and
is recorded verbatim in the conversation file, so it can be counted directly. Re-measured 05:26Z:

```
$ python3 - "$CONV" "$PROBE" <<'PY'
import json,sys,os
toks={n:open(os.path.join(sys.argv[2],n)).read().strip() for n in ('p1','p2','p3','p4')}
wo=None
for l in open(sys.argv[1]):
    if 'toolu_017s36oLYcS6qDpAhZDgWvqZ' not in l: continue
    e=json.loads(l)
    if e.get('type')!='assistant': continue
    for b in e['message']['content']:
        if b.get('type')=='tool_use' and b.get('id')=='toolu_017s36oLYcS6qDpAhZDgWvqZ':
            wo=b['input']['prompt']
print('work order chars:',len(wo))
for n,v in toks.items(): print('  occurrences of %s in work order: %d'%(n, wo.count(v)))
PY
work order chars: 9697
  occurrences of p1 in work order: 0
  occurrences of p2 in work order: 0
  occurrences of p3 in work order: 0
  occurrences of p4 in work order: 0
```

The tokens were passed by file path only. All four counts are zero.

### Subagent turns are separated by file, and `isSidechain` agrees wherever it exists

Subagent turns are written two levels below the conversation file, not beside it. Re-measured 05:28Z;
the `grep` narrows the listing to the probing subagent, since four further subagents have run since:

```
$ find $PROJ_WT/ef482a21-4765-41d3-9d74-aa4c8d40f5d8 -type f | grep adcd0d76
/Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/subagents/agent-adcd0d76cf2237e15.jsonl
/Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/subagents/agent-adcd0d76cf2237e15.meta.json

$ cat $PROJ_WT/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/subagents/agent-adcd0d76cf2237e15.meta.json
{"agentType":"general-purpose","description":"Measure JSONL behaviour, task #1","toolUseId":"toolu_017s36oLYcS6qDpAhZDgWvqZ","spawnDepth":1}
```

Tallying `(type, isSidechain)` over both files, re-measured 05:25Z:

```
$ python3 - "$CONV" "$SUB" <<'PY'
import json,sys,collections
for path,label in ((sys.argv[1],'conversation file'),(sys.argv[2],'subagent file')):
    es=[json.loads(l) for l in open(path) if l.strip()]
    c=collections.Counter((e.get('type'), e.get('isSidechain')) for e in es)
    print('==',label,'entries',len(es))
    for k in sorted(c, key=lambda k:(str(k[0]),str(k[1]))): print('   ',k,c[k])
    has=[e for e in es if 'isSidechain' in e]
    print('    entries carrying isSidechain:',len(has),' all False:',all(e['isSidechain'] is False for e in has))
PY
== conversation file entries 268
    ('ai-title', None) 13
    ('assistant', False) 66
    ('atis-latch', None) 15
    ('attachment', False) 58
    ('file-history-snapshot', None) 4
    ('last-prompt', None) 14
    ('mode', None) 15
    ('permission-mode', None) 15
    ('pr-link', None) 16
    ('queue-operation', None) 8
    ('system', False) 8
    ('user', False) 36
    entries carrying isSidechain: 168  all False: True
== subagent file entries 75
    ('assistant', True) 37
    ('attachment', True) 19
    ('user', True) 19
    entries carrying isSidechain: 75  all False: False
```

Stated precisely: **every entry of the conversation file that carries `isSidechain` has it `false`.**
100 of its 268 entries carry no such field at all — `mode`, `permission-mode`, `atis-latch`,
`ai-title`, `last-prompt`, `pr-link`, `file-history-snapshot`, `queue-operation` — so "every entry is
`isSidechain: false`" would be wrong. Every entry of the subagent file has it `true`. The separation a
reader can rely on is the **file**; the field agrees wherever it is present.

## An emitted string is greppable in about eighty seconds — an upper bound, not a latency

The one recorded emission-to-readable interval comes from the probing round. Probes were emitted
between 05:05:18.632Z and 05:05:27.100Z (timestamps in the walk above). The first grep of the
conversation file is recorded in the subagent file as entry 15 (the command) and entry 16 (its
result), quoted from the log verbatim with the token literals masked:

```
$ python3 - "$SUB" "$PROBE" <<'PY'
import json,sys,os
toks={n:open(os.path.join(sys.argv[2],n)).read().strip() for n in ('p1','p2','p3','p4')}
def mask(s):
    for n,v in toks.items(): s=s.replace(v,'<%s>'%n)
    return s
for i,l in enumerate(open(sys.argv[1]),1):
    if i not in (15,16): continue
    e=json.loads(l); print('line',i,e.get('type'),e.get('timestamp'))
    for b in e['message']['content']:
        if b.get('type')=='tool_use':   print('  tool_use',b['name'],mask(json.dumps(b['input'])))
        if b.get('type')=='tool_result':print('  tool_result',mask(json.dumps(b.get('content'))))
    print()
PY
line 15 assistant 2026-09-06T05:06:46.799Z
  tool_use Bash {"command": "F=~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18/ef482a21-4765-41d3-9d74-aa4c8d40f5d8.jsonl; ls -la $F; echo \"lines:\"; wc -l < $F; echo \"=== token counts ===\"; for t in <p1> <p2> <p3> <p4>; do printf \"%s: %s\\n\" $t \"$(grep -c $t $F)\"; done", "description": "Check liveness and token hit counts"}

line 16 user 2026-09-06T05:06:46.849Z
  tool_result "-rw-------@ 1 kiyo  staff  325267  9\u6708  6 14:06 /Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18/ef482a21-4765-41d3-9d74-aa4c8d40f5d8.jsonl\nlines:\n     160\n=== token counts ===\n<p1>: 2\n<p2>: 2\n<p3>: 1\n<p4>: 1"
```

All four tokens were present on the first look; none needed a retry.

- Last probe 05:05:27.100Z → grep result entry 05:06:46.849Z: **79.7 s**.
- First probe 05:05:18.632Z → same: **88.2 s**.

**Both are upper bounds on the write-to-greppable delay, not measurements of it.** Nothing polled in
between; the interval is dominated by the probing turn doing other work. The true delay lies at or
below 79.7 s and this measurement does not narrow it. No tighter bound is recorded, because isolating
one would require emitting fresh probes from the conversation itself, which this round deliberately
did not do — a subagent's probes land in a subagent file, not where a marker must land.

### The entry for a tool call in flight is not necessarily on disk

An earlier draft claimed the opposite — that "the entry describing an action is flushed before that
action completes" — from a reading taken inside the subagent. The log refutes it. The command behind
that reading is recorded, and it read `$SUB`, the subagent file, not the conversation file; its own
output labels it as such:

```
line 41 assistant 2026-09-06T05:08:20.781Z
  tool_use Bash, `input.command` — lines 1-9 of 26, the rest unrelated to this figure:
 1| D=~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18
 2| SD=$D/ef482a21-4765-41d3-9d74-aa4c8d40f5d8/subagents/agent-adcd0d76cf2237e15.jsonl
 3| echo "now: $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
 4| echo "newest timestamp in live sidechain file:"
 5| python3 -c "
 6| import json
 7| ts=[json.loads(l)['timestamp'] for l in open('$SD',encoding='utf-8') if l.strip() and 'timestamp' in json.loads(l)]
 8| print(' entries:',len(ts),' newest:',max(ts))
 9| "

line 42 user 2026-09-06T05:08:20.888Z
  `toolUseResult.stdout` — lines 1-3 of 9:
 1| now: 2026-09-06T05:08:20.3NZ
 2| newest timestamp in live sidechain file:
 3|  entries: 40  newest: 2026-09-06T05:08:14.189Z
```

(`+%…%3NZ` is a GNU `date` extension; BSD `date` on this machine printed `.3NZ` literally, so the
recorded wall clock is `05:08:20`.)

What the reading actually saw: 40 entries on disk, newest timestamped 05:08:14.189Z. That entry is an
`assistant` entry whose first content block is `thinking`. The reading tool call is entry 41,
timestamped 05:08:20.781Z — **6.6 seconds later, and absent from disk when the maximum was computed.**
So the opposite of the earlier claim holds in this sample: the in-flight tool call's own entry was not
yet written. The six-second figure measures how stale the newest flushed entry happened to be after a
thinking pause. It is not a write delay, and it was not taken on the conversation file.

### The conversation's content is on disk while the conversation is open

The fact the criterion needs survives the correction and is re-runnable at any time. Re-measured
05:29Z, from inside the still-open conversation `ef482a21`:

```
$ python3 -c "
import json
ts=[json.loads(l).get('timestamp') for l in open('$CONV') if l.strip()]
ts=[t for t in ts if t]
print('entries on disk:  ', sum(1 for _ in open('$CONV')))
print('newest timestamp: ', max(ts))
"; date -u +'wall clock:        %Y-%m-%dT%H:%M:%SZ'
entries on disk:   268
newest timestamp:  2026-09-06T05:22:48.550Z
wall clock:        2026-09-06T05:29:03Z
```

268 entries, covering everything the conversation had written up to the moment it handed off to the
turn now reading it. **The 375-second age of the newest entry is not a flush delay**: the conversation
is idle while that turn runs, so nothing new has been produced. What is established is that the file
is readable and complete up to the handoff, and that it grows during the conversation rather than at
its end.

## A subagent's report lands in the conversation file — a fifth emission channel

A subagent's *intermediate* turns stay in its own file, as the tallies above show. Its **final report
does not**: it is delivered into the conversation file as a `user` entry. Re-measured 05:24Z, searching
the conversation file for the opening words of the probing subagent's report:

```
$ python3 - "$CONV" <<'PY'
import json,sys
needle="Task #1 done. All four probes landed; nothing came out negative"
for i,l in enumerate(open(sys.argv[1]),1):
    if needle not in l: continue
    e=json.loads(l)
    print('line',i,'type',e.get('type'),'isSidechain',e.get('isSidechain'),'ts',e.get('timestamp'))
    def walk(o,p=''):
        if isinstance(o,str):
            if needle in o: print('   path',p or '.','len',len(o))
        elif isinstance(o,dict):
            for k,v in o.items(): walk(v,p+'.'+k)
        elif isinstance(o,list):
            for j,v in enumerate(o): walk(v,p+'[%d]'%j)
    walk(e)
PY
line 162 type queue-operation isSidechain None ts 2026-09-06T05:11:20.076Z
   path .content len 3729
line 164 type user isSidechain False ts 2026-09-06T05:11:20.087Z
   path .message.content len 3729
```

The report's own entry in the subagent file is the last `assistant` entry there, at
2026-09-06T05:11:19.977Z. It reaches the conversation file 99 ms later as a `queue-operation` entry
and 110 ms later as the `user` entry the conversation actually reads.

The `user` entry in full, with strings over 100 characters truncated by the printer itself:

```
$ python3 - "$CONV" <<'PY'
import json,sys
for i,l in enumerate(open(sys.argv[1]),1):
    if i!=164: continue
    e=json.loads(l)
    def shrink(o):
        if isinstance(o,str): return o[:100]+('…[%d chars]'%len(o) if len(o)>100 else '')
        if isinstance(o,dict): return {k:shrink(v) for k,v in o.items()}
        if isinstance(o,list): return [shrink(v) for v in o]
        return o
    print(json.dumps(shrink(e),ensure_ascii=False,indent=1))
PY
{
 "parentUuid": "d6d86071-215e-43ea-b0d5-7358873d8de9",
 "isSidechain": false,
 "promptId": "f5be4693-9792-4b5f-87b8-f95accd5b271",
 "type": "user",
 "message": {
  "role": "user",
  "content": "<task-notification>\n<task-id>adcd0d76cf2237e15</task-id>\n<tool-use-id>toolu_017s36oLYcS6qDpAhZDgWvqZ…[3729 chars]"
 },
 "uuid": "99d3b1ff-68b4-4fa1-92c8-9b9f372fc8de",
 "timestamp": "2026-09-06T05:11:20.087Z",
 "permissionMode": "bypassPermissions",
 "origin": {
  "kind": "task-notification"
 },
 "promptSource": "system",
 "queueSkipAttachments": true,
 "userType": "external",
 "entrypoint": "cli",
 "cwd": "/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18",
 "sessionId": "ef482a21-4765-41d3-9d74-aa4c8d40f5d8",
 "version": "2.1.263",
 "gitBranch": "worktree-issue-18"
}
```

The wrapper's full tag sequence, taken from that same string with
`re.findall(r'</?[a-z-]+>', content)`, is `task-notification / task-id / tool-use-id / output-file /
status / summary / note / result / usage`; the report body sits inside `<result>`.

**Field paths for this channel:** `.content` on the `queue-operation` entry and `.message.content` on
the `user` entry, with `origin.kind == "task-notification"` and `promptSource == "system"`
distinguishing it from a human prompt. Both entries are in the conversation file; the `user` one is
`isSidechain: false`.

None of the four tokens reached the conversation file this way, but only by accident of wording — the
report elided them:

```
$ python3 - "$SUB" "$PROBE" <<'PY'
import json,sys,os
toks={n:open(os.path.join(sys.argv[2],n)).read().strip() for n in ('p1','p2','p3','p4')}
es=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]
rep=[e for e in es if e.get('type')=='assistant'][-1]['message']['content'][0]['text']
print('final report chars:',len(rep))
for n,v in sorted(toks.items()): print('  occurrences of %s in final report: %d'%(n, rep.count(v)))
PY
final report chars: 2962
  occurrences of p1 in final report: 0
  occurrences of p2 in final report: 0
  occurrences of p3 in final report: 0
  occurrences of p4 in final report: 0
```

Had the report quoted a token, that token would now sit in the conversation file at
`.message.content`, indistinguishable by grep from a coordinator emission. **Which agent is permitted
to emit a marker is therefore a live constraint**, not a settled one, and a subagent that merely
mentions a marker in its report emits it.

## A log file is filed by relocation target, not by the working directory of its entries

Each working directory has a project directory whose name is that path with `/` and `.` both replaced
by `-`. Six exist for this repository. Re-measured 05:28Z:

```
$ ls -d ~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm*
/Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm
/Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-aiya
/Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-hpate
/Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-17
/Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18
/Users/kiyo/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-techting
```

The name is reproducible with `tr`:

```
$ for p in /Users/kiyo/work/lovaizu/ccpm \
           /Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18; do
    printf '%s -> %s\n' "$p" "$(printf '%s' "$p" | tr '/.' '--')"
  done
/Users/kiyo/work/lovaizu/ccpm -> -Users-kiyo-work-lovaizu-ccpm
/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18 -> -Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18
```

**The mapping is lossy and does not guarantee distinct directories.** `/` and `.` map to the same
character, so two different paths produce one name:

```
$ printf '%s -> %s\n' "/a/b.c" "$(printf '%s' '/a/b.c' | tr '/.' '--')" \
                      "/a/b-c" "$(printf '%s' '/a/b-c' | tr '/.' '--')"
/a/b.c -> -a-b-c
/a/b-c -> -a-b-c
```

The six ccpm directories happen not to collide — a property of these six paths, not of the scheme.
Scope: all 24 project directories on this machine match `^[A-Za-z0-9-]*$`, so no other character class
was exercised, and nothing is known about how a space or a non-ASCII path segment is encoded.

### Three files prove the directory diverges from the `cwd` on every entry

The directory a file sits in is **not** decided by the `cwd` its entries record. The main checkout's
project directory holds three files whose every `cwd` is a worktree. Re-measured 05:22Z:

```
$ cd ~/.claude/projects
$ for d in ./-Users-kiyo-work-lovaizu-ccpm ./-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-*; do
    n=$(grep -l '"type":"relocated"' "$d"/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
    t=$(ls "$d"/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
    printf '%-56s %s / %s\n' "${d#./}" "$n" "$t"
  done
-Users-kiyo-work-lovaizu-ccpm                            3 / 4
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-aiya     0 / 31
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-hpate    0 / 5
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-17 0 / 4
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18 0 / 3
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-techting 0 / 15
```

Three of the four files in the main checkout's directory carry a `relocated` entry; none of the 58
files across the five worktree directories does. The entry names where the conversation went:

```
$ grep -h -o '"type":"relocated"[^}]*}' $PROJ_MAIN/5466c142-d1b4-4deb-ba67-bd19344e107c.jsonl | head -1
"type":"relocated","sessionId":"5466c142-d1b4-4deb-ba67-bd19344e107c","relocatedCwd":"/Users/kiyo/work/lovaizu/ccpm"}
```

All four files in that directory, characterised together. Re-measured 05:29Z:

```
$ python3 - $PROJ_MAIN/*.jsonl <<'PY'
import json,sys,os
for p in sys.argv[1:]:
    es=[json.loads(l) for l in open(p) if l.strip()]
    ts=[e['timestamp'] for e in es if e.get('timestamp')]
    ws=[e.get('worktreeSession') for e in es if e.get('type')=='worktree-state']
    cmds=[e['message']['content'] for e in es if e.get('type')=='user'
          and isinstance(e.get('message',{}).get('content'),str)
          and '<command-name>' in e['message']['content']]
    print(os.path.basename(p)[:8],'bytes=%-7d entries=%-3d relocated=%d'
          %(os.path.getsize(p),len(es),sum(1 for e in es if e.get('type')=='relocated')))
    print('   span   ',min(ts),'->',max(ts))
    print('   cwd    ',sorted(set(e['cwd'] for e in es if 'cwd' in e)))
    print('   assistant entries', sum(1 for e in es if e.get('type')=='assistant'))
    print('   command',[c.split('</command-name>')[0].split('>')[-1] for c in cmds])
    print('   worktreeSession.sessionId',[w['sessionId'] if w else None for w in ws])
PY
04319f87 bytes=3151    entries=11  relocated=2
   span    2026-08-16T12:09:36.320Z -> 2026-08-16T12:09:36.407Z
   cwd     ['/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/aiya']
   assistant entries 0
   command ['/clear']
   worktreeSession.sessionId ['6ff22937-755d-4f10-a4f3-178c8bab62b6', None]
10dcd188 bytes=4177    entries=13  relocated=2
   span    2026-08-30T14:21:59.216Z -> 2026-08-30T14:21:59.258Z
   cwd     ['/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-17']
   assistant entries 0
   command ['/clear']
   worktreeSession.sessionId ['6463aea8-e1eb-46b4-b8a6-13c65bcc66ac', None]
5466c142 bytes=3791    entries=13  relocated=2
   span    2026-08-30T14:19:43.762Z -> 2026-08-30T14:19:43.810Z
   cwd     ['/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18']
   assistant entries 0
   command ['/clear']
   worktreeSession.sessionId ['17080efa-bb3f-488c-a2e3-46794ddb2df2', None]
8dca6935 bytes=207465  entries=114 relocated=0
   span    2026-08-30T12:30:45.792Z -> 2026-08-30T13:59:14.084Z
   cwd     ['/Users/kiyo/work/lovaizu/ccpm']
   assistant entries 26
   command []
   worktreeSession.sessionId []
```

What the three relocated files are: 3–4 KB, 11–13 entries, spanning under 90 ms, containing a `/clear`
command entry, its empty `local-command-stdout` system entry, two `worktree-state` entries (the first
naming the worktree, the second `worktreeSession: null`), and two `relocated` entries. **None contains
any task work at all** — zero `assistant` entries. They are stubs.

**Established:** a file is placed by `relocatedCwd` when a `relocated` entry is present, and that
placement can differ from the `cwd` on every one of the file's own entries. **Not established — the
trigger.** All three stubs share the same three features: a `/clear`, a worktree-to-`null`
`worktree-state` transition, and a `relocatedCwd` equal to the checkout the worktree hangs off. This
material cannot separate "leaving a worktree relocates the file" from "`/clear` inside a worktree
relocates the file", and it says nothing about a relocated file that carries real work — no such file
exists on this machine to inspect.

**The consequence a marker reader needs: globbing one working directory's project directory can miss
conversations that belong to that working directory.** `5466c142` belongs to the issue-18 worktree by
every `cwd` and `gitBranch` it records, yet it is filed under the main checkout. The converse holds
too: grepping the main checkout's directory returns entries whose `cwd` is a worktree. Directory
membership and working directory are two different things and must not be conflated in a marker
search.

## One in-file pointer exists: it names the worktree's origin conversation, not a predecessor

The worktree's project directory holds three conversation files, all belonging to this one `rn`
session. Re-measured 05:29Z:

```
$ ls -la $PROJ_WT
total 2560
drwx------@  6 kiyo  staff     192  9月  6 14:06 .
drwx------@ 26 kiyo  staff     832  9月  6 14:03 ..
-rw-------@  1 kiyo  staff  350874  8月 30 23:19 17080efa-bb3f-488c-a2e3-46794ddb2df2.jsonl
-rw-------@  1 kiyo  staff  294284  9月  5 10:35 eded9b12-eb24-4601-9203-d893583ed99e.jsonl
drwxr-xr-x@  4 kiyo  staff     128  9月  6 14:15 ef482a21-4765-41d3-9d74-aa4c8d40f5d8
-rw-------@  1 kiyo  staff  640244  9月  6 14:22 ef482a21-4765-41d3-9d74-aa4c8d40f5d8.jsonl
```

```
$ python3 - $PROJ_WT/*.jsonl <<'PY'
import json,sys,os,collections
for p in sys.argv[1:]:
    es=[json.loads(l) for l in open(p) if l.strip()]
    ts=[e['timestamp'] for e in es if e.get('timestamp')]
    print(os.path.basename(p)[:8], 'entries=%-4d'%len(es), min(ts),'->',max(ts))
    print('   gitBranch',dict(collections.Counter(e['gitBranch'] for e in es if e.get('gitBranch'))))
    print('   cwd      ',dict(collections.Counter(e['cwd'] for e in es if e.get('cwd'))))
PY
17080efa entries=191  2026-08-30T14:01:09.992Z -> 2026-08-30T14:19:43.757Z
   gitBranch {'main': 94, 'worktree-issue-18': 34}
   cwd       {'/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18': 128}
eded9b12 entries=184  2026-08-30T14:20:31.090Z -> 2026-09-05T01:34:32.173Z
   gitBranch {'worktree-issue-18': 133}
   cwd       {'/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18': 133}
ef482a21 entries=268  2026-09-06T04:53:42.208Z -> 2026-09-06T05:22:48.550Z
   gitBranch {'worktree-issue-18': 168}
   cwd       {'/Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/issue-18': 168}
```

Note the shape of that tally: `17080efa` has 191 entries but only 128 carry a `cwd`, so "every entry
records the worktree as `cwd`" would overstate it — **every entry that carries a `cwd` does**, while 94
of those same entries still record `gitBranch: main`.

An in-file pointer to another conversation **does exist**. The `worktree-state` entry type carries
`worktreeSession.sessionId`, and in the stub `5466c142` that value is `17080efa` — a different
conversation. Scanned across all 62 ccpm conversation files, re-measured 05:31Z:

```
$ python3 - <<'PY'
import json, glob, os, collections
root=os.path.expanduser('~/.claude/projects')
dirs=[root+'/-Users-kiyo-work-lovaizu-ccpm']+sorted(glob.glob(root+'/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-*'))
tot=hit=0; by=collections.defaultdict(list)
for d in dirs:
    for f in sorted(glob.glob(d+'/*.jsonl')):
        tot+=1; me=os.path.basename(f)[:8]; ptr=set()
        for l in open(f):
            if '"worktree-state"' not in l: continue
            e=json.loads(l)
            ws=e.get('worktreeSession') if e.get('type')=='worktree-state' else None
            if ws and ws.get('sessionId'): ptr.add(ws['sessionId'][:8])
        if ptr:
            hit+=1; by[os.path.basename(d)].append((me, tuple(sorted(ptr))))
for d in sorted(by):
    rows=by[d]
    print('%-56s %2d file(s); targets %s; self-pointing %d'
          %(d, len(rows), sorted({r[1] for r in rows}), sum(1 for r in rows if r[1]==(r[0],))))
print('files carrying worktreeSession.sessionId: %d / %d'%(hit,tot))
PY
-Users-kiyo-work-lovaizu-ccpm                             3 file(s); targets [('17080efa',), ('6463aea8',), ('6ff22937',)]; self-pointing 0
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-aiya     11 file(s); targets [('6ff22937',)]; self-pointing 1
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-17  1 file(s); targets [('6463aea8',)]; self-pointing 1
-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-issue-18  1 file(s); targets [('17080efa',)]; self-pointing 1
files carrying worktreeSession.sessionId: 16 / 62
```

**How far the pointer goes.** It names the conversation that *created or entered the worktree*, not the
immediately preceding one. All eleven `aiya` conversations that carry it name the same target,
`6ff22937`, and one of the eleven is `6ff22937` itself. The pointer therefore partitions conversations
by which worktree entry they descend from; it does not chain, and it cannot order a session's
conversations. It is also usually absent — 46 of 62 files carry no `worktree-state` entry with a
non-null `worktreeSession`, including two of this session's own three conversations. Re-measured
05:28Z:

```
$ for f in 17080efa-bb3f-488c-a2e3-46794ddb2df2 \
           eded9b12-eb24-4601-9203-d893583ed99e \
           ef482a21-4765-41d3-9d74-aa4c8d40f5d8; do
    printf '%s: worktree-state entries = %s\n' "${f%%-*}" "$(grep -c '"type":"worktree-state"' $PROJ_WT/$f.jsonl)"
  done
17080efa: worktree-state entries = 9
eded9b12: worktree-state entries = 0
ef482a21: worktree-state entries = 0
```

Ordering this session's three conversations still needs outside knowledge — the directory listing, the
timestamps, and the session path each file mentions. The pointer does not supply it. `leafUuid` on
`last-prompt` entries resolves inside its own file only (all seven values in `ef482a21`, measured
05:07Z, name uuids in `ef482a21`), so it is not a cross-conversation link either.

### A substring grep is not a test for a structural link, and it no longer returns zero

The earlier check — grepping each of the three files for the other two conversation ids — is a raw
substring search over prose, not a test for a linkage field. It now returns non-zero, because this
very document quoting those ids was read back into the conversation. Re-measured 05:29Z:

```
$ A=17080efa-bb3f-488c-a2e3-46794ddb2df2
$ B=eded9b12-eb24-4601-9203-d893583ed99e
$ C=ef482a21-4765-41d3-9d74-aa4c8d40f5d8
$ for f in $A $B $C; do for id in $A $B $C; do
    [ "$f" = "$id" ] && continue
    printf 'in %s, substring hits for %s : %s\n' "${f%%-*}" "${id%%-*}" "$(grep -c -- "$id" $PROJ_WT/$f.jsonl)"
  done; done
in 17080efa, substring hits for eded9b12 : 0
in 17080efa, substring hits for ef482a21 : 0
in eded9b12, substring hits for 17080efa : 0
in eded9b12, substring hits for ef482a21 : 0
in ef482a21, substring hits for 17080efa : 6
in ef482a21, substring hits for eded9b12 : 1
```

All six hits in `ef482a21` are in `user`, `assistant` and `queue-operation` entries dated 05:11–05:22Z
— this document's own text and its review, not linkage. Two different claims are involved: **no
structural linkage field orders these three conversations** (measured above), and **a substring
occurrence of a conversation id is not evidence of a link** — nor is it stable, as the drift from 0 to
6 in fifteen minutes shows.

## Compaction stays in one file and replays earlier prose into it

An earlier draft left this undetermined. The answer is on disk: a conversation in the `techting`
worktree carries a compaction summary. Measured 05:27Z:

```
$ T=~/.claude/projects/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-techting/4b750c4a-e82a-4d1f-9dbd-cd1938cc4472.jsonl
$ grep -c '"isCompactSummary":true' $T
1
$ python3 - "$T" <<'PY'
import json,sys
es=[(i,json.loads(l)) for i,l in enumerate(open(sys.argv[1]),1) if l.strip()]
print('distinct sessionId in file:', set(e.get('sessionId') for i,e in es if e.get('sessionId')))
for i,e in es:
    if not e.get('isCompactSummary'): continue
    print('line',i,'type',e.get('type'),'ts',e.get('timestamp'),'isSidechain',e.get('isSidechain'))
    print('  keys:',sorted(e.keys()))
    c=e['message']['content']; s=c if isinstance(c,str) else json.dumps(c)
    print('  content chars:',len(s)); print('  head:',repr(s[:200]))
PY
distinct sessionId in file: {'4b750c4a-e82a-4d1f-9dbd-cd1938cc4472'}
line 307 type user ts 2026-08-22T06:21:18.412Z isSidechain False
  keys: ['cwd', 'entrypoint', 'gitBranch', 'isCompactSummary', 'isSidechain', 'isVisibleInTranscriptOnly', 'message', 'parentUuid', 'promptId', 'sessionId', 'session_id', 'slug', 'timestamp', 'type', 'userType', 'uuid', 'version']
  content chars: 10341
  head: 'This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.\n\nSummary:\n1. Primary Request and Intent:\n   The '
```

Compaction writes **one `user` entry with `isCompactSummary: true` into the same file, under the same
`sessionId`** — no new conversation, no new file, and so no predecessor record is needed. A reader
looking for a compaction boundary should look for that field, not for a second file.

**The duplication hazard is the consequence that matters for cutting an interval.** The summary is
10,341 characters of prose *about* the earlier part of the conversation, so text already in the file
reappears in it. Measured by extracting the backtick-quoted literals from the summary and testing each
against the portion of the file that precedes it (list trimmed to the first 6 of 27):

```
$ python3 - "$T" <<'PY'
import json,re,sys
lines=open(sys.argv[1]).read().splitlines()
es=[json.loads(l) for l in lines if l.strip()]
idx=[i for i,e in enumerate(es) if e.get('isCompactSummary')][0]
summ=es[idx]['message']['content']
before='\n'.join(lines[:idx])
toks=sorted(set(re.findall(r'`([^`\n]{8,60})`',summ)))
dup=[t for t in toks if t in before]
print('summary is entry index %d (line %d) of %d'%(idx,idx+1,len(es)))
print('distinct backtick-quoted strings in the summary: %d'%len(toks))
print('of those, also present verbatim earlier in the same file: %d'%len(dup))
for t in dup[:6]: print('   ',repr(t))
PY
summary is entry index 306 (line 307) of 405
distinct backtick-quoted strings in the summary: 39
of those, also present verbatim earlier in the same file: 27
    ' (approve) or '
    '## Fold-round re-review (coordinator, 2026-08-22)'
    '.claude-plugin/marketplace.json'
    '.rn/20260614-writ/checks/7.md'
    '.rn/20260614-writ/checks/8.md'
    '.rn/20260614-writ/steering.md'
```

27 of 39 quoted strings in the summary already appear earlier in the same file. **A marker quoted in
the conversation before a compaction therefore appears a second time, later in the file, inside the
summary entry** — and that second copy is timestamped at compaction time, minutes or hours after the
work it names. A reader cutting an interval on "the last occurrence of marker X" gets the summary's
copy, not the original emission.

## Multi-day gaps do not reveal whether a conversation was resumed

An earlier draft asserted that resume and continue "were never exercised". That is unsupported.
`eded9b12` spans 2026-08-30 to 2026-09-05 in one file, with two multi-day gaps between adjacent
entries. Re-measured 05:30Z, gap list trimmed to the three largest:

```
$ python3 - "$PROJ_WT/eded9b12-eb24-4601-9203-d893583ed99e.jsonl" <<'PY'
import json,sys,datetime,collections
def parse(t): return datetime.datetime.strptime(t,'%Y-%m-%dT%H:%M:%S.%fZ')
rows=[]
for i,l in enumerate(open(sys.argv[1]),1):
    if not l.strip(): continue
    e=json.loads(l)
    if e.get('timestamp'): rows.append((i,parse(e['timestamp']),e.get('type')))
es=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]
print('span',rows[0][1],'->',rows[-1][1],' entries with timestamp',len(rows))
print('distinct sessionId:',set(e.get('sessionId') for e in es if e.get('sessionId')))
print('isCompactSummary entries:',sum(1 for e in es if e.get('isCompactSummary')))
print('version tally:',dict(collections.Counter(e['version'] for e in es if e.get('version'))))
for g,a,b in sorted(((b[1]-a[1]).total_seconds(),a,b) for a,b in zip(rows,rows[1:]))[::-1][:3]:
    print('  %8.0f s (%5.1f h)  line %d %s %s -> line %d %s %s'%(g,g/3600,a[0],a[2],a[1],b[0],b[2],b[1]))
PY
span 2026-08-30 14:20:31.090000 -> 2026-09-05 01:34:32.173000  entries with timestamp 141
distinct sessionId: {'eded9b12-eb24-4601-9203-d893583ed99e'}
isCompactSummary entries: 0
version tally: {'2.1.251': 133}
    323426 s ( 89.8 h)  line 161 system 2026-09-01 07:43:18.353000 -> line 163 user 2026-09-05 01:33:44.711000
    147452 s ( 41.0 h)  line 49 system 2026-08-30 14:24:11.961000 -> line 51 user 2026-09-01 07:21:43.889000
       286 s (  0.1 h)  line 147 system 2026-09-01 07:34:31.650000 -> line 149 user 2026-09-01 07:39:17.527000
```

Nothing in the file marks either gap: one `sessionId`, no `isCompactSummary` entry, a single `version`
across all 133 entries that carry one, and a two-order-of-magnitude jump from the third-largest gap
(286 s) to the second (41 h).

**Whether this file was resumed cannot be decided from this material.** A restart would be visible if
Claude Code had been upgraded across a gap, since `version` is stamped per entry — but no file on this
machine spans two versions, so that discriminator is untested here too. Re-measured 05:31Z:

```
$ python3 - <<'PY'
import json, glob, os, collections
root=os.path.expanduser('~/.claude/projects')
dirs=[root+'/-Users-kiyo-work-lovaizu-ccpm']+sorted(glob.glob(root+'/-Users-kiyo-work-lovaizu-ccpm--claude-worktrees-*'))
tot=multi=0
for d in dirs:
    for f in sorted(glob.glob(d+'/*.jsonl')):
        tot+=1; vs=collections.Counter()
        for l in open(f):
            if '"version"' not in l: continue
            e=json.loads(l)
            if e.get('version'): vs[e['version']]+=1
        if len(vs)>1:
            multi+=1; print(os.path.basename(d)[:52], os.path.basename(f)[:8], dict(vs))
print('files with more than one distinct version: %d / %d'%(multi,tot))
PY
files with more than one distinct version: 0 / 62
```

A 90-hour gap in one file is equally consistent with `--resume` appending to the existing file and with
one conversation left open across four days. **The question stays open:** it is not known whether
`--resume` or `--continue` starts a new file, appends to the existing one, or writes any record at the
seam.

## Only 16-character lowercase hex was tested, so a real marker's character set is untested

All four tokens had the same shape. Measured 05:26Z:

```
$ for n in p1 p2 p3 p4; do v=$(cat $PROBE/$n)
    printf '%s: len=%d charclass=%s\n' $n ${#v} \
      "$(printf '%s' "$v" | grep -qE '^[0-9a-f]+$' && echo '[0-9a-f] only' || echo 'other')"
  done
p1: len=16 charclass=[0-9a-f] only
p2: len=16 charclass=[0-9a-f] only
p3: len=16 charclass=[0-9a-f] only
p4: len=16 charclass=[0-9a-f] only
```

No probe was emitted in this round, deliberately: a subagent's probes land in a subagent file, not
where a marker must land, so they would answer nothing about the four emission points. The measurement
therefore establishes those points **only for a bare alphanumeric run carrying no shell or JSON
metacharacter.**

The next task must not assume any of the following survives an emission point, because none was
tested: a **space** or any whitespace; `#`, `:`, `/`, `|`; a single or double **quote**; a
**backslash**; a **newline** inside the marker; **non-ASCII** characters; a marker long enough to be
truncated in a tool result; and a marker whose text is a substring of another marker. Two of the
landing paths are quoting-sensitive in ways a hex token could not expose:
`message.content[0].input.command` records the marker as it appeared on a shell command line, and
`toolUseResult.file.content` records it as file bytes.

## Line order and timestamp order disagree, so an interval's boundaries depend on the sort key

Measured 05:30Z over this session's three conversation files:

```
$ python3 - $PROJ_WT/*.jsonl <<'PY'
import json,sys,os,datetime
def parse(t): return datetime.datetime.strptime(t,'%Y-%m-%dT%H:%M:%S.%fZ')
for path in sys.argv[1:]:
    rows=[]
    for i,l in enumerate(open(path),1):
        if not l.strip(): continue
        e=json.loads(l); t=e.get('timestamp')
        if t: rows.append((i,parse(t),e.get('type')))
    inv=[(a,b) for a,b in zip(rows,rows[1:]) if b[1]<a[1]]
    print('%-12s entries_with_ts=%-4d adjacent_inversions=%-3d max_backstep=%.3fs'
          %(os.path.basename(path)[:8],len(rows),len(inv),
            max(((a[1]-b[1]).total_seconds() for a,b in inv), default=0)))
    for a,b in inv:
        print('   line %-4d %-18s %s  ->  line %-4d %-18s %s   (-%.3fs)'
              %(a[0],a[2],a[1].strftime('%H:%M:%S.%f')[:-3],
                b[0],b[2],b[1].strftime('%H:%M:%S.%f')[:-3],(a[1]-b[1]).total_seconds()))
PY
17080efa     entries_with_ts=134  adjacent_inversions=5   max_backstep=3.094s
   line 69   user               14:03:10.252  ->  line 70   attachment         14:03:10.251   (-0.001s)
   line 90   user               14:12:20.556  ->  line 91   attachment         14:12:20.555   (-0.001s)
   line 122  file-history-delta 14:18:04.903  ->  line 123  assistant          14:18:04.884   (-0.019s)
   line 145  pr-link            14:18:19.395  ->  line 146  assistant          14:18:16.301   (-3.094s)
   line 188  queue-operation    14:19:43.757  ->  line 189  assistant          14:19:43.732   (-0.025s)
eded9b12     entries_with_ts=141  adjacent_inversions=1   max_backstep=0.001s
   line 83   user               07:28:10.862  ->  line 84   attachment         07:28:10.861   (-0.001s)
ef482a21     entries_with_ts=192  adjacent_inversions=2   max_backstep=0.001s
   line 6    user               04:53:42.209  ->  line 7    attachment         04:53:42.208   (-0.001s)
   line 54   user               04:58:07.323  ->  line 55   attachment         04:58:07.322   (-0.001s)
```

Inversions occur in all three files. Most are 1 ms — a `user` entry written just ahead of its own
`attachment` — but one is **3.094 s**: a `pr-link` entry timestamped after the `assistant` entry that
follows it on the next line.

A second, larger ordering problem: **76 of the conversation file's 268 entries carry no `timestamp` at
all.** Re-measured 05:30Z:

```
$ python3 - "$CONV" <<'PY'
import json,sys,collections
es=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]
no=[e for e in es if not e.get('timestamp')]
print('entries with no timestamp: %d / %d'%(len(no),len(es)))
print(dict(collections.Counter(e.get('type') for e in no)))
PY
entries with no timestamp: 76 / 268
{'mode': 15, 'permission-mode': 15, 'atis-latch': 15, 'file-history-snapshot': 4, 'last-prompt': 14, 'ai-title': 13}
```

**Consequence for a marker reader: cutting an interval by line number and cutting it by timestamp give
different boundaries.** A timestamp sort silently drops the 76 untimestamped entries or must fall back
on line order for them; a line-number cut includes entries whose timestamps fall outside the interval,
by up to 3 seconds in the observed worst case. Whichever rule is chosen must be chosen explicitly, and
a marker landing within about 3 seconds of a boundary is not reliably on one side of it.

## What this still cannot answer

Open questions a marker-format decision must resolve some other way. They are handed forward, not
concealed.

- **How an emission is told apart from the text that defines it.** This document is read back into the
  conversation it measures, so its own text now sits in the conversation file at
  `.message.content[0].content` and `.toolUseResult.file.content` — the same field paths as the "Bash
  command output" and "Read result" emission points. The drift from 0 to 6 hits in the ordered-pair
  check above is exactly this effect. A marker whose format is described in a document that is later
  read, or quoted in a work order, is indistinguishable by grep from a real emission of it, and a
  field-path or entry-type discriminator does not help, because the defining text lands at the same
  paths.
- **Whether a marker containing a space, punctuation, a quote, a newline or non-ASCII survives an
  emission point.** Only 16-character lowercase hex was tested.
- **Whether a marker written in one turn is readable by a tool call in that same turn.** The tightest
  recorded bound is 79.7 s and is an upper bound; separately, an in-flight tool call's own entry was
  measured to be *absent* from disk at 05:08:20.781Z. Same-turn read-back is not established, and the
  one relevant sample points against it.
- **How to enumerate a session's conversations.** Globbing one project directory is unsound: a
  conversation belonging to a working directory can be filed under another, and
  `worktreeSession.sessionId` names the worktree's origin conversation rather than ordering the
  session's. No measured method enumerates a session's conversations completely.
- **Whether a marker survives compaction unduplicated.** It does not, if it is quoted in prose the
  summary reproduces — 27 of 39 quoted strings reappeared in the sample above. Whether a marker sitting
  in a Bash command string or a tool result is reproduced in a summary was not measured, and no way to
  suppress the duplicate is known.
- **What `--resume` and `--continue` write.** Untested, and the material on disk cannot distinguish a
  resumed conversation from a long-idle one.
