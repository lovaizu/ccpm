"""Whole-corpus scans over ~/.claude/projects, one subcommand per question.

Usage: corpus.py {versions|version-range|persist-bracket|no-timestamp|worktree-ptr|entry-types|
                  attachment-types|hook-entries|relocated|sidechain|continued-in|compaction|
                  projdirs|localcmd|handoffs|inversions|needle} [arg]

Every scan reads the whole population the section quoting it generalises to, and prints
that population as its first line, because a figure without its population is the defect
these scans exist to prevent. Conversation files are ~/.claude/projects/*/*.jsonl;
subagent files are ~/.claude/projects/*/*/subagents/*.jsonl. Scans that need only the
ccpm project directories say so in their own first line.
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.expanduser('~/.claude/projects')
CONV = sorted(glob.glob(ROOT + '/*/*.jsonl'))
SUBS = sorted(glob.glob(ROOT + '/*/*/subagents/*.jsonl'))
CCPM = sorted(glob.glob(ROOT + '/-Users-kiyo-work-lovaizu-ccpm*/*.jsonl'))
DIRS = sorted(d for d in glob.glob(ROOT + '/*') if os.path.isdir(d))


def entries(path):
    for line in open(path, encoding='utf-8', errors='replace'):
        if line.strip():
            yield json.loads(line)


def pop(conv=True, subs=False):
    if subs:
        print('files scanned: %d conversation + %d subagent' % (len(CONV), len(SUBS)))
    else:
        print('files scanned: %d conversation' % len(CONV))


def versions():
    """Files whose entries carry more than one distinct `version`."""
    pop()
    multi = 0
    for f in CONV:
        vs = collections.Counter(v for v in (e.get('version') for e in entries(f)) if v)
        if len(vs) > 1:
            multi += 1
            print(os.path.basename(os.path.dirname(f))[:52], os.path.basename(f)[:8], dict(vs))
    print('files with more than one distinct version: %d / %d' % (multi, len(CONV)))


def version_range():
    """First and last timestamp each `version` was written at, machine-wide."""
    pop()
    first, last = {}, {}
    for f in CONV:
        for e in entries(f):
            v, t = e.get('version'), e.get('timestamp')
            if v and t:
                first[v] = min(first.get(v, t), t)
                last[v] = max(last.get(v, t), t)
    for v in sorted(first):
        if v >= '2.1.250':
            print('  %-9s first=%s  last=%s' % (v, first[v], last[v]))


def persist_bracket():
    """Where the inline/side-file threshold sits, and what the side file leaves behind.

    Reported in bytes, because the cap is a byte cap: `persistedOutputSize` is bytes and
    a character count of the same text is smaller wherever the text is not ASCII.
    Non-stdout results are counted separately, because the cap applies to Bash stdout
    and not to every tool result.
    """
    pop(subs=True)
    inline = 0
    persisted = []
    big_other = []
    for f in CONV + SUBS:
        for line in open(f, encoding='utf-8', errors='replace'):
            if '"toolUseResult"' not in line:
                continue
            r = json.loads(line).get('toolUseResult')
            if not isinstance(r, dict):
                continue
            if r.get('persistedOutputSize'):
                persisted.append(r)
                continue
            if 'stdout' in r:
                inline = max(inline, len((r['stdout'] or '').encode()))
            else:
                f_ = r.get('file') if isinstance(r.get('file'), dict) else {}
                txt = f_.get('content') if isinstance(f_.get('content'), str) else (
                    r.get('content') if isinstance(r.get('content'), str) else None)
                if txt and len(txt.encode()) > 30000:
                    big_other.append((len(txt.encode()), r.get('type') or sorted(r)[:3]))
    print('largest Bash stdout kept inline:  %d bytes' % inline)
    print('smallest Bash stdout persisted:   %d bytes' % min(r['persistedOutputSize'] for r in persisted))
    kept = collections.Counter(len((r.get('stdout') or '').encode()) for r in persisted)
    print('persisted results: %d; bytes of stdout kept inline: min %d max %d'
          % (len(persisted), min(kept), max(kept)))
    on, head, tail = 0, 0, 0
    for r in persisted:
        p = r['persistedOutputPath']
        if not os.path.exists(p):
            continue
        on += 1
        raw = open(p, encoding='utf-8', errors='replace').read()
        s = r.get('stdout') or ''
        head += raw.startswith(s[:-1])
        tail += raw.endswith(s[1:])
    print('side file still on disk: %d; kept text is its head %d, its tail %d' % (on, head, tail))
    big_other.sort(reverse=True)
    print('non-stdout tool results over 30,000 bytes kept inline: %d (largest %s)'
          % (len(big_other), big_other[0] if big_other else '-'))


def no_timestamp():
    """Files that hold entries but carry no `timestamp` on any of them."""
    pop()
    for f in CONV:
        es = list(entries(f))
        if es and not any(e.get('timestamp') for e in es):
            print(os.path.basename(os.path.dirname(f))[:52], os.path.basename(f)[:8],
                  'entries', len(es), dict(collections.Counter(e.get('type') for e in es)))


def entry_types():
    """every distinct entry `type` on this machine, by frequency."""
    pop()
    c = collections.Counter()
    for f in CONV:
        for e in entries(f):
            c[e.get('type')] += 1
    print('distinct entry types:', len(c))
    print(', '.join('%s %d' % kv for kv in c.most_common()))


def worktree_ptr():
    """Which files carry worktreeSession.sessionId, and what they point at.

    Machine-wide: the pointer's shape — origin rather than predecessor, no chaining — is a
    claim about the field, not about one repository's directories.
    """
    pop()
    by = collections.defaultdict(list)
    for f in CONV:
        p = {e['worktreeSession']['sessionId'][:8] for e in entries(f)
             if e.get('type') == 'worktree-state' and (e.get('worktreeSession') or {}).get('sessionId')}
        if p:
            by[os.path.basename(os.path.dirname(f))].append((os.path.basename(f)[:8], tuple(sorted(p))))
    for d, rows in sorted(by.items()):
        print('%-56s %2d file(s); targets %s; self-pointing %d'
              % (d, len(rows), sorted({r[1] for r in rows}),
                 sum(1 for r in rows if r[1] == (r[0],))))
    print('files carrying worktreeSession.sessionId: %d / %d'
          % (sum(len(r) for r in by.values()), len(CONV)))


def attachment_types():
    """every `attachment.type` on this machine, and how many carry a `content` string."""
    pop(subs=True)
    c, withtext = collections.Counter(), collections.Counter()
    for f in CONV + SUBS:
        for e in entries(f):
            a = e.get('attachment')
            if not isinstance(a, dict):
                continue
            c[a.get('type')] += 1
            if isinstance(a.get('content'), str):
                withtext[a.get('type')] += 1
    print('distinct attachment.type: %d' % len(c))
    for t, n in c.most_common():
        print('  %-28s %6d  with .attachment.content: %d' % (t, n, withtext[t]))


def hook_entries():
    """hook attachments machine-wide, and where else the name `hookEvent` turns up."""
    def keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield k
                for x in keys(v):
                    yield x
        elif isinstance(o, list):
            for v in o:
                for x in keys(v):
                    yield x

    pop(subs=True)
    c, files, as_key, as_text = collections.Counter(), {}, 0, 0
    for f in CONV + SUBS:
        for e in entries(f):
            a = e.get('attachment') if isinstance(e.get('attachment'), dict) else {}
            if str(a.get('type', '')).startswith('hook'):
                c[(e.get('type'), a.get('type'), a.get('hookEvent'))] += 1
                files.setdefault(f, [set(), set()])
                files[f][0].add(e.get('entrypoint'))
                files[f][1].add(e.get('version'))
            elif 'hookEvent' in json.dumps(e):
                as_key += 'hookEvent' in set(keys(e))
                as_text += 'hookEvent' not in set(keys(e))
    print('files holding a hook attachment: %d' % len(files))
    for k, n in sorted(c.items(), key=str):
        print('  entry type=%-11s attachment.type=%-20s hookEvent=%-16s %d' % (k + (n,)))
    for f in sorted(files):
        print('  %-24s entrypoint=%-20s version=%s'
              % (os.path.basename(f)[:24], sorted(files[f][0]), sorted(files[f][1])))
    print('other entries with `hookEvent` as a JSON key:        %d' % as_key)
    print('other entries with "hookEvent" only inside a string: %d' % as_text)


def relocated():
    """Every file on this machine carrying a `relocated` entry, and how much work it holds."""
    pop()
    n = 0
    for f in CONV:
        es = list(entries(f))
        rel = [i for i, e in enumerate(es, 1) if e.get('type') == 'relocated']
        if not rel:
            continue
        n += 1
        ws = [(i, (e.get('worktreeSession') or {}).get('worktreePath'))
              for i, e in enumerate(es, 1) if e.get('type') == 'worktree-state']
        clear = [i for i, e in enumerate(es, 1) if '<command-name>/clear' in json.dumps(e)]
        cwds = sorted({e['cwd'] for e in es if e.get('cwd')})
        tgt = {e.get('relocatedCwd') for e in es if e.get('type') == 'relocated'}
        print('%-34s %s  entries=%-4d assistant=%-4d with_cwd=%-4d' %
              (os.path.basename(os.path.dirname(f))[:34], os.path.basename(f)[:8], len(es),
               sum(1 for e in es if e.get('type') == 'assistant'),
               sum(1 for e in es if 'cwd' in e)))
        print('    relocated at lines %s of %d; relocatedCwd %s' % (rel, len(es), sorted(tgt)))
        print('    cwd of its entries %s' % cwds)
        print('    worktree-state entries %d, first at line %d, last at line %d with worktreePath '
              '%s; /clear at lines %s'
              % (len(ws), ws[0][0], ws[-1][0], ws[-1][1], clear or 'none'))
        w0 = next(e for e in es if e.get('type') == 'worktree-state')['worktreeSession']
        print('    originalCwd==preEnterOriginalCwd==relocatedCwd: %s'
              % (w0['originalCwd'] == w0['preEnterOriginalCwd'] == sorted(tgt)[0]))
    print('files carrying a `relocated` entry: %d / %d' % (n, len(CONV)))


def sidechain():
    """Whether any conversation file holds a subagent-side entry."""
    pop()
    hit = [f for f in CONV if any(e.get('isSidechain') is True for e in entries(f))]
    print('conversation files holding an entry with isSidechain true: %d / %d' % (len(hit), len(CONV)))
    for f in hit:
        print('  ', os.path.basename(f)[:8])
    sub = sum(1 for f in SUBS[:40] if any(e.get('isSidechain') is True for e in entries(f)))
    print('subagent files holding one, of the first 40: %d' % sub)


def continued_in():
    """Every `continued-in` entry on this machine, and the pair it links."""
    pop()
    n = 0
    for f in CONV:
        for e in entries(f):
            if e.get('type') == 'continued-in':
                n += 1
                print('  %s -> %s  ts=%s' % (e['sessionId'][:8], e['continuedInSessionId'][:8],
                                             e.get('timestamp')))
    print('`continued-in` entries: %d, in %d / %d files' % (n, n, len(CONV)))


def compaction():
    """Compaction summaries machine-wide, and how likely an earlier string is to reappear.

    Conditioned on how often the string occurred before the summary, because a
    task-boundary marker occurs once per boundary and the unconditioned rate is
    dominated by strings that occurred many times.
    """
    pop()
    files = [f for f in CONV
             if any('"isCompactSummary":true' in l or '"isCompactSummary": true' in l
                    for l in open(f, encoding='utf-8', errors='replace'))]
    print('files carrying a compaction summary: %d / %d' % (len(files), len(CONV)))
    for f in files:
        lines = open(f, encoding='utf-8', errors='replace').read().splitlines()
        es = [json.loads(l) for l in lines if l.strip()]
        i = [k for k, e in enumerate(es) if e.get('isCompactSummary')][0]
        e = es[i]
        summ = e['message']['content']
        print('  %s line %d type=%s ts=%s isSidechain=%s summary chars=%d, file entries=%d, sessionIds=%s'
              % (os.path.basename(f)[:8], i + 1, e.get('type'), e['timestamp'], e.get('isSidechain'),
                 len(summ), len(es), sorted({x.get('sessionId') for x in es if x.get('sessionId')})))
        cnt = collections.Counter(re.findall(r'`([^`\n]{8,60})`', '\n'.join(lines[:i])))
        buckets = collections.defaultdict(list)
        for t, k in cnt.items():
            buckets['1' if k == 1 else ('2-4' if k < 5 else '5+')].append(t in summ)
        print('  backtick-quoted strings before the summary: %d' % len(cnt))
        for b in ('1', '2-4', '5+'):
            v = buckets[b]
            print('    occurring %-4s before the summary: %d of %d reproduced in it (%.0f%%)'
                  % (b, sum(v), len(v), 100.0 * sum(v) / len(v)))
        allv = [t in summ for t in cnt]
        print('    all:                                 %d of %d (%.0f%%)'
              % (sum(allv), len(allv), 100.0 * sum(allv) / len(allv)))


BANNER = re.compile(r'\A\[harness: subagent output matched instruction-shaped pattern\(s\): ([^.]*)\.', re.S)


def handoffs():
    """Every `<task-notification>` on this machine: its status, wrapper shape and neutralisation.

    The population for every channel-5 claim. A scan of one file's two handoffs cannot
    see the failed ones, the neutralised ones, or the second wrapper shape.
    """
    pop()
    tot = gone = gonef = 0
    c = collections.Counter()
    names = collections.Counter()
    files = set()
    for f in CONV:
        seen, queued = set(), collections.defaultdict(set)
        for e in entries(f):
            if e.get('type') == 'queue-operation':
                raw = json.dumps(e)
                m = (re.search(r'"taskId":\s*"([^"]+)"', raw)
                     or re.search(r'<task-id>(.*?)</task-id>', raw))
                if m:
                    queued[m.group(1)].add(e.get('operation') or e.get('op'))
            c_ = e.get('message', {}).get('content') if e.get('type') == 'user' else None
            if isinstance(c_, str) and '<task-notification>' in c_:
                seen.add(re.search(r'<task-id>(.*?)</task-id>', c_).group(1))
        n = sum(1 for t in queued if t not in seen)
        gone += n
        gonef += bool(n)
        for e in entries(f):
            c_ = e.get('message', {}).get('content') if e.get('type') == 'user' else None
            if not isinstance(c_, str) or '<task-notification>' not in c_:
                continue
            tot += 1
            st = re.search(r'<status>(.*?)</status>', c_, re.S)
            c[('status', st and st.group(1))] += 1
            c[('tool-use-id tag', '<tool-use-id>' in c_)] += 1
            m = re.search(r'<result>(.*?)</result>', c_, re.S)
            b = m and BANNER.match(m.group(1).strip())
            c[('neutralised', bool(b))] += 1
            if b:
                files.add(f)
                for t in b.group(1).split(','):
                    names[t.strip()] += 1
    print('task-notification entries: %d' % tot)
    print('queue-operation task ids enqueued but never reaching a `user` entry: %d in %d files'
          % (gone, gonef))
    for k, n in sorted(c.items(), key=str):
        print('  %-16s %-10s %d' % (k[0], k[1], n))
    print('files holding a neutralised report: %d' % len(files))
    for k, n in names.most_common():
        print('  neutralisation trigger %-24s %d' % (k, n))


def inversions():
    """Every adjacent pair on this machine whose timestamps run backwards.

    Machine-wide because the sentence quoting the largest backstep is about what a
    marker scheme may assume anywhere, not about one session's files.
    """
    pop()
    import datetime
    TS = lambda t: datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%fZ')
    c = collections.Counter()
    worst = []
    n = 0
    for f in CONV:
        rows = [(i, TS(e['timestamp']), e.get('type'))
                for i, e in enumerate(entries(f), 1) if e.get('timestamp')]
        for a, b in zip(rows, rows[1:]):
            if b[1] < a[1]:
                n += 1
                d = (a[1] - b[1]).total_seconds()
                c[(a[2], b[2])] += 1
                worst.append((d, os.path.basename(f)[:8], a[0], a[2], b[0], b[2]))
    print('backward-running adjacent pairs: %d' % n)
    print('the ahead-stamped entry, by (its type -> its successor\'s type):')
    for k, v in c.most_common():
        print('  %-20s -> %-20s %d' % (k + (v,)))
    print('largest backsteps:')
    for d, f, i, ta, j, tb in sorted(worst, reverse=True)[:5]:
        print('  %-8s line %-4d %-18s -> line %-4d %-18s  -%.3fs' % (f, i, ta, j, tb, d))


def needle(arg):
    """Where the first line of a given file turns up in the logs, machine-wide.

    The population is every log on this machine, because the sentence it backs is about
    any later read of the document, not about one session's files.
    """
    text = open(arg, encoding='utf-8', errors='replace').read().splitlines()[0]
    paths = collections.Counter()

    def walk(o, p=''):
        if isinstance(o, str):
            if text in o:
                paths[p] += 1
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, p + '.' + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p + '[N]')

    pop(subs=True)
    for grp, name in ((CONV, 'conversation'), (SUBS, 'subagent')):
        n = 0
        for f in grp:
            hit = False
            for line in open(f, encoding='utf-8', errors='replace'):
                if text not in line:
                    continue
                hit = True
                walk(json.loads(line))
            n += hit
        print('%s files holding that line: %d / %d' % (name, n, len(grp)))
    print('distinct field paths: %d' % len(paths))
    for k, v in paths.most_common():
        print('  %-44s %d' % (k, v))


def projdirs():
    """Every project directory on this machine, and whether the naming rule reproduces it."""
    print('project directories scanned: %d' % len(DIRS))
    odd = [d for d in DIRS if not re.match(r'^[A-Za-z0-9-]*$', os.path.basename(d))]
    print('directory names outside [A-Za-z0-9-]: %d' % len(odd))
    for d in odd:
        print('  ', os.path.basename(d))
    tr = lambda p: p.replace('/', '-').replace('.', '-')
    pairs, byfile = set(), []
    for f in CONV:
        ws = {e['cwd'] for e in entries(f) if e.get('cwd')}
        d = os.path.basename(os.path.dirname(f))
        pairs |= {(w, d) for w in ws}
        if ws:
            byfile.append((f, d, any(tr(w) == d for w in ws)))
    print('distinct (entry cwd, directory) pairs: %d; the rule reproduces the directory for %d'
          % (len(pairs), sum(1 for p, d in pairs if tr(p) == d)))
    print('files recording at least one cwd: %d; of those, the directory is reproduced by '
          'no cwd the file records: %d' % (len(byfile), sum(1 for _, _, ok in byfile if not ok)))
    for f, d, ok in byfile:
        if not ok:
            print('  %-8s filed under %-56s cwds %s'
                  % (os.path.basename(f)[:8], d[:56],
                     sorted({e['cwd'] for e in entries(f) if e.get('cwd')})[:2]))


def localcmd():
    """Slash-command output: `<local-command-stdout>` entries, and where their text sits."""
    pop(subs=True)
    c, paths = collections.Counter(), collections.Counter()

    def walk(o, p=''):
        if isinstance(o, str):
            if '<local-command-stdout>' in o:
                paths[p] += 1
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, p + '.' + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p + '[N]')

    files = 0
    for f in CONV + SUBS:
        seen = False
        for e in entries(f):
            if '<local-command-stdout>' in json.dumps(e):
                c[(e.get('type'), e.get('isSidechain'))] += 1
                walk(e)
                seen = True
        files += seen
    print('files holding a <local-command-stdout>: %d' % files)
    for k, n in c.most_common():
        print('  entry type=%-9s isSidechain=%-5s %d' % (k + (n,)))
    for k, n in paths.most_common():
        print('  %-40s %d' % (k, n))


SCANS = {'versions': versions, 'version-range': version_range,
         'persist-bracket': persist_bracket, 'no-timestamp': no_timestamp,
         'worktree-ptr': worktree_ptr, 'entry-types': entry_types,
         'attachment-types': attachment_types, 'hook-entries': hook_entries,
         'relocated': relocated, 'sidechain': sidechain, 'continued-in': continued_in,
         'compaction': compaction, 'projdirs': projdirs, 'localcmd': localcmd, 'inversions': inversions, 'needle': needle,
         'handoffs': handoffs}

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in SCANS:
        raise SystemExit(__doc__)
    SCANS[sys.argv[1]](*sys.argv[2:])
