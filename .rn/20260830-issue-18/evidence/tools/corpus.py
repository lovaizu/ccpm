"""Whole-corpus scans over ~/.claude/projects, one subcommand per question.

Usage: corpus.py {versions|version-range|persist-bracket|no-timestamp|worktree-ptr|entry-types}

Each scan reads every conversation file on the machine (and, for persist-bracket, every
subagent file too), so its figures grow as the logs grow. Kept out of the evidence
document so the document's command blocks stay short.
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.expanduser('~/.claude/projects')
CONV = sorted(glob.glob(ROOT + '/*/*.jsonl'))
SUBS = sorted(glob.glob(ROOT + '/*/*/subagents/*.jsonl'))
CCPM = sorted(glob.glob(ROOT + '/-Users-kiyo-work-lovaizu-ccpm*/*.jsonl'))


def entries(path):
    for line in open(path, encoding='utf-8', errors='replace'):
        if line.strip():
            yield json.loads(line)


def versions():
    """Files whose entries carry more than one distinct `version`."""
    multi = 0
    for f in CONV:
        vs = collections.Counter(v for v in (e.get('version') for e in entries(f)) if v)
        if len(vs) > 1:
            multi += 1
            print(os.path.basename(os.path.dirname(f))[:52], os.path.basename(f)[:8], dict(vs))
    print('files with more than one distinct version: %d / %d' % (multi, len(CONV)))


def version_range():
    """First and last timestamp each `version` was written at, machine-wide."""
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
    """Largest tool result kept inline vs smallest written out to tool-results/."""
    mx, mn = 0, None
    for f in CONV + SUBS:
        for e in entries(f):
            r = e.get('toolUseResult')
            if not isinstance(r, dict) or 'stdout' not in r:
                continue
            if r.get('persistedOutputSize'):
                mn = min(mn or 1 << 30, r['persistedOutputSize'])
            else:
                mx = max(mx, len(r['stdout'] or ''))
    print('largest result kept inline: %d chars' % mx)
    print('smallest result persisted:  %d bytes' % mn)


def no_timestamp():
    """Files that hold entries but carry no `timestamp` on any of them."""
    for f in CONV:
        es = list(entries(f))
        if es and not any(e.get('timestamp') for e in es):
            print(os.path.basename(os.path.dirname(f))[:52], os.path.basename(f)[:8],
                  'entries', len(es), dict(collections.Counter(e.get('type') for e in es)))


def entry_types():
    """every distinct entry `type` on this machine, by frequency."""
    c = collections.Counter()
    for f in CONV:
        for e in entries(f):
            c[e.get('type')] += 1
    print('distinct entry types:', len(c))
    print(', '.join('%s %d' % kv for kv in c.most_common()))


def worktree_ptr():
    """Which ccpm files carry worktreeSession.sessionId, and what they point at."""
    by = collections.defaultdict(list)
    for f in CCPM:
        p = {e['worktreeSession']['sessionId'][:8] for e in entries(f)
             if e.get('type') == 'worktree-state' and (e.get('worktreeSession') or {}).get('sessionId')}
        if p:
            by[os.path.basename(os.path.dirname(f))].append((os.path.basename(f)[:8], tuple(sorted(p))))
    for d, rows in sorted(by.items()):
        print('%-56s %2d file(s); targets %s; self-pointing %d'
              % (d, len(rows), sorted({r[1] for r in rows}),
                 sum(1 for r in rows if r[1] == (r[0],))))
    print('files carrying worktreeSession.sessionId: %d / %d'
          % (sum(len(r) for r in by.values()), len(CCPM)))


SCANS = {'versions': versions, 'version-range': version_range,
         'persist-bracket': persist_bracket, 'no-timestamp': no_timestamp,
         'worktree-ptr': worktree_ptr, 'entry-types': entry_types}

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in SCANS:
        raise SystemExit(__doc__)
    SCANS[sys.argv[1]]()
