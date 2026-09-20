"""Whole-corpus scans over ~/.claude/projects, one subcommand per question.

Usage: corpus.py {versions|version-range|persist-bracket|no-timestamp|worktree-ptr|entry-types|
                  attachment-types|hook-entries}

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


def attachment_types():
    """every `attachment.type` on this machine, and how many carry a `content` string."""
    c, withtext = collections.Counter(), collections.Counter()
    for f in CONV + SUBS:
        for e in entries(f):
            a = e.get('attachment')
            if not isinstance(a, dict):
                continue
            c[a.get('type')] += 1
            if isinstance(a.get('content'), str):
                withtext[a.get('type')] += 1
    print('files scanned: %d conversation + %d subagent' % (len(CONV), len(SUBS)))
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
    print('files scanned: %d conversation + %d subagent' % (len(CONV), len(SUBS)))
    print('files holding a hook attachment: %d' % len(files))
    for k, n in sorted(c.items(), key=str):
        print('  entry type=%-11s attachment.type=%-20s hookEvent=%-16s %d' % (k + (n,)))
    for f in sorted(files):
        print('  %-24s entrypoint=%-20s version=%s'
              % (os.path.basename(f)[:24], sorted(files[f][0]), sorted(files[f][1])))
    print('other entries with `hookEvent` as a JSON key:        %d' % as_key)
    print('other entries with "hookEvent" only inside a string: %d' % as_text)


SCANS = {'versions': versions, 'version-range': version_range,
         'persist-bracket': persist_bracket, 'no-timestamp': no_timestamp,
         'worktree-ptr': worktree_ptr, 'entry-types': entry_types,
         'attachment-types': attachment_types, 'hook-entries': hook_entries}

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in SCANS:
        raise SystemExit(__doc__)
    SCANS[sys.argv[1]]()
