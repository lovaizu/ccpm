"""Per-file scans over JSONL log files, one subcommand per question.

Usage: scan.py {spans|cwd|types|inversions|seam|handoff|escaping|replay|leaf|selfref|
                hooks|hookraw|hookids|prompts}
               <file.jsonl>... [--tokens <dir>]

`--tokens <dir>` loads probe tokens the way walk.py does: hookraw masks their values out
of what it prints, prompts reports which of them each user entry holds.

Every scan parses entries rather than grepping lines, so a reported field is the field
an entry actually holds. Each subcommand is the exact measurement the section quoting it
describes, and each is meant to be pointed at the whole population that section
generalises to — a glob of one directory where the sentence says one directory, and of
every file where it says this machine.
"""
import collections
import datetime
import glob
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from masktok import load as load_tokens, mask

TOKENS = {}

TS = lambda t: datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%fZ')


def load(path):
    return [json.loads(l) for l in open(path, encoding='utf-8', errors='replace') if l.strip()]


def spans(paths):
    """entries, entries carrying a timestamp, and the span they cover."""
    for p in paths:
        es = load(p); ts = [e['timestamp'] for e in es if e.get('timestamp')]
        print('%s entries=%-4d with_ts=%-4d %s -> %s'
              % (os.path.basename(p)[:8], len(es), len(ts), min(ts), max(ts)))


def cwd(paths):
    """how many entries carry a `cwd`, which paths they name, and with which gitBranch."""
    for p in paths:
        es = load(p)
        print('%s entries=%-4d with_cwd=%-4d cwds=%s'
              % (os.path.basename(p)[:8], len(es), sum(1 for e in es if 'cwd' in e),
                 sorted({e['cwd'] for e in es if 'cwd' in e})))
        c = collections.Counter((e.get('cwd'), e.get('gitBranch')) for e in es)
        for (w, b), n in sorted(c.items(), key=str):
            print('    cwd=%s gitBranch=%s -> %d' % (w, b, n))


def types(paths):
    """(type, isSidechain) tally, and how many entries carry no isSidechain at all."""
    for p in paths:
        es = load(p)
        c = collections.Counter((e.get('type'), e.get('isSidechain')) for e in es)
        print('%-16s entries %-4d | no isSidechain field: %d'
              % (os.path.basename(p)[:16], len(es), sum(1 for e in es if 'isSidechain' not in e)))
        print('   ', {'%s/%s' % k: v for k, v in sorted(c.items(), key=str)})


def inversions(paths):
    """adjacent entry pairs whose timestamps run backwards."""
    for p in paths:
        rows = [(i, TS(e['timestamp']), e.get('type'))
                for i, e in enumerate(load(p), 1) if e.get('timestamp')]
        for a, b in zip(rows, rows[1:]):
            if b[1] < a[1]:
                print('%-9s line %-4d %-18s -> line %-4d %-18s  -%.3fs'
                      % (os.path.basename(p)[:8], a[0], a[2], b[0], b[2],
                         (a[1] - b[1]).total_seconds()))


def seam(paths):
    """entries around a change of `version` within one file, plus parentUuid integrity."""
    for p in paths:
        es = load(p); prev = None
        print('## %s  entries=%d' % (os.path.basename(p)[:8], len(es)))
        for i, e in enumerate(es, 1):
            v = e.get('version')
            if v and prev and v != prev:
                for x in es[i - 4:i + 1]:
                    print('%-22s v=%-8s ts=%-26s uuid=%s parent=%s'
                          % (x.get('type'), x.get('version'), x.get('timestamp'),
                             str(x.get('uuid'))[:8], str(x.get('parentUuid'))[:8]))
            if v:
                prev = v
        uu = {e['uuid'] for e in es if e.get('uuid')}
        print('sessionIds in the file: %s; compact summaries: %d' %
              (sorted({e.get('sessionId') for e in es if e.get('sessionId')})[:1] or '-',
               sum(1 for e in es if e.get('isCompactSummary'))))
        print('entries whose parentUuid is absent from the file:',
              sum(1 for e in es if e.get('parentUuid') and e['parentUuid'] not in uu))


BANNER = re.compile(r'\A\[harness:.*?\]\n\n', re.S)


def _subfile(conv_path, tid, body):
    """The subagent's own JSONL for one handoff, found the way the entry itself points.

    The <output-file> tag is a symlink to it. That indirection matters: a continued
    conversation's task symlinks point back into the PREDECESSOR's directory, so
    building the path from the reading file's own sessionId misses them.
    """
    m = re.search(r'<output-file>(.*?)</output-file>', body, re.S)
    if m and os.path.exists(m.group(1)):
        return os.path.realpath(m.group(1))
    d, sid = os.path.dirname(conv_path), os.path.basename(conv_path)[:-6]
    local = '%s/%s/subagents/agent-%s.jsonl' % (d, sid, tid)
    if os.path.exists(local):
        return local
    g = glob.glob(os.path.expanduser('~/.claude/projects/*/*/subagents/agent-%s.jsonl' % tid))
    return g[0] if g else None


def _report(sub):
    """(last assistant text of the subagent file, whether it died on an error entry).

    NOT the file's last entry: an agent that died on a session limit has an error entry
    last, and taking it as the report reports a mismatch that is the script's own.
    """
    es = load(sub)
    died = bool(es[-1].get('isApiErrorMessage'))
    for e in reversed(es):
        if e.get('type') != 'assistant':
            continue
        c = (e.get('message') or {}).get('content')
        if isinstance(c, list):
            t = [b.get('text') for b in c if b.get('type') == 'text']
            if t:
                return e, '\n'.join(t), died
    return None, None, died


def _reports(path):
    """yield (line, entry, task id, status, subagent path, report entry, report text, died)."""
    for i, e in enumerate(load(path), 1):
        c = e.get('message', {}).get('content') if e.get('type') == 'user' else None
        if not isinstance(c, str) or '<task-notification>' not in c:
            continue
        tid = re.search(r'<task-id>(.*?)</task-id>', c).group(1)
        st = re.search(r'<status>(.*?)</status>', c, re.S)
        sub = _subfile(path, tid, c)
        if sub is None:
            yield i, e, tid, st and st.group(1), None, None, None, None
            continue
        rep, text, died = _report(sub)
        yield i, e, tid, st and st.group(1), sub, rep, text, died


def handoff(paths):
    """how long a subagent's final report takes to reach the conversation file."""
    for p in paths:
        for i, e, tid, status, sub, rep, text, died in _reports(p):
            if sub is None:
                print('task %s  status=%-9s subagent file NOT FOUND' % (tid, status))
                continue
            print('task %s  status=%-9s report %s -> user entry line %-4d %s (+%.0f ms)%s'
                  % (tid, status, rep['timestamp'], i, e['timestamp'],
                     (TS(e['timestamp']) - TS(rep['timestamp'])).total_seconds() * 1000,
                     '  [agent died on an error entry]' if died else ''))


def escaping(paths):
    """what the <result> body does to the report: entities, harness banner, tag shape."""
    for p in paths:
        for i, e, tid, status, sub, rep, text, died in _reports(p):
            c = e['message']['content']
            body = re.search(r'<result>(.*?)</result>', c, re.S).group(1).strip()
            tags = re.findall(r'<([a-z-]+)>', c)
            ban = BANNER.match(body)
            stripped = body[len(ban.group(0)):] if ban else body
            un = html.unescape(stripped).strip()
            print('line %-4d status=%-9s banner=%-4d identical=%-5s unescape==report=%-5s '
                  'undo-neutralisation==report=%-5s  &lt;=%-3d &gt;=%-3d &amp;=%-3d tool-use-id=%s'
                  % (i, status, len(ban.group(0)) if ban else 0,
                     body == (text or ''), un == (text or '').strip(),
                     un.replace('<\\', '<').replace('[\\', '[') == (text or '').strip(),
                     body.count('&lt;'), body.count('&gt;'), body.count('&amp;'),
                     'tool-use-id' in tags))


def replay(paths):
    """predecessor vs successor of a continuation: what is copied, dropped and restamped."""
    a, b = load(paths[0]), load(paths[1])
    na, nb = (os.path.basename(p)[:8] for p in paths[:2])
    ua = {e['uuid'] for e in a if e.get('uuid')}
    ub = {e['uuid'] for e in b if e.get('uuid')}
    msg = {e['uuid']: json.dumps(e.get('message'), sort_keys=True) for e in a if e.get('uuid')}
    raw_b = {l.strip() for l in open(paths[1], encoding='utf-8', errors='replace') if l.strip()}
    print('%s entries=%-4d uuid-carrying=%-4d uuid-less=%d' % (na, len(a), len(ua), len(a) - len(ua)))
    print('%s entries=%-4d uuid-carrying=%-4d uuid-less=%d' % (nb, len(b), len(ub), len(b) - len(ub)))
    print('uuids shared: %d; new in %s: %d' % (len(ua & ub), nb, len(ub - ua)))
    print('replayed entries whose .message is byte-identical: %d / %d'
          % (sum(1 for e in b if e.get('uuid') in msg
                 and json.dumps(e.get('message'), sort_keys=True) == msg[e['uuid']]), len(ua & ub)))
    nou = [l for l in open(paths[0], encoding='utf-8', errors='replace')
           if l.strip() and not json.loads(l).get('uuid')]
    print('uuid-less entries of %s copied byte-identically into %s: %d / %d %s'
          % (na, nb, sum(1 for l in nou if l.strip() in raw_b), len(nou),
             dict(collections.Counter(json.loads(l).get('type') for l in nou
                                      if l.strip() in raw_b))))
    print('sessionKind in %s: %s' % (nb, dict(collections.Counter(e.get('sessionKind') for e in b))))
    print('sessionKind in %s: %s' % (na, dict(collections.Counter(e.get('sessionKind') for e in a))))
    last = max(i for i, e in enumerate(b, 1) if e.get('uuid') in ua)
    print('last replayed entry at %s line %d of %d; entries after it: %d'
          % (nb, last, len(b), len(b) - last))
    sid = collections.Counter((str(e.get('session_id'))[:8], e.get('uuid') in ua) for e in b)
    print('%s (session_id, is a replayed entry): %s' % (nb, dict(sid)))
    print('%s entries carrying session_id: %d, all naming %s: %s'
          % (na, sum(1 for e in a if e.get('session_id')),
             na, {str(e.get('session_id'))[:8] for e in a if e.get('session_id')}))
    print('replayed entries whose session_id equals their own sessionId: %d'
          % sum(1 for e in b if e.get('uuid') in ua and e.get('session_id') == e.get('sessionId')))


def selfref(paths):
    """every string field of one file that contains another file's sessionId."""
    needle = os.path.basename(paths[0])[:-6]
    paths = paths[1:]
    c = collections.Counter()

    def walk(o, p=''):
        if isinstance(o, str):
            if needle in o:
                c[p] += o.count(needle)
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, p + '.' + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p + '[N]')

    for p in paths:
        c.clear()
        for e in load(p):
            walk(e)
        raw = open(p, encoding='utf-8', errors='replace').read().count(needle)
        print('%s inside %s: %d raw substring hits, %d in parsed string fields'
              % (needle[:8], os.path.basename(p)[:8], raw, sum(c.values())))
        for k, n in c.most_common():
            print('   %-40s %d' % (k, n))


def leaf(paths):
    """whether `last-prompt` leafUuid values resolve inside their own file."""
    for p in paths:
        es = load(p)
        lp = [e.get('leafUuid') for e in es if e.get('type') == 'last-prompt']
        uu = {e['uuid'] for e in es if e.get('uuid')}
        print('%s last-prompt %d, distinct leafUuid %d, resolving in this file %d'
              % (os.path.basename(p)[:8], len(lp), len(set(lp)),
                 sum(1 for v in set(lp) if v in uu)))


def _hook_entries(path):
    for i, e in enumerate(load(path), 1):
        a = e.get('attachment') or {}
        if str(a.get('type', '')).startswith('hook'):
            yield i, e, a


def hooks(paths):
    """every hook attachment: its event, its exit code, and where its text sits."""
    for p in paths:
        for i, e, a in _hook_entries(p):
            print('%-24s line %-4d %-13s %-20s exit=%-3s content==stdout.strip()=%-5s keys=%s'
                  % (os.path.basename(p)[:24], i, a.get('type'), a.get('hookName'),
                     a.get('exitCode'), (a.get('stdout') or '').strip() == (a.get('content') or '').strip(),
                     ','.join(sorted(a))))


def hookraw(paths):
    """the first hook attachment of each file, whole, minus its `rendered` copy."""
    for p in paths:
        for i, e, _ in _hook_entries(p):
            body = json.dumps({k: v for k, v in e.items() if k != 'rendered'}, indent=1)
            print(mask(body, TOKENS))
            break


def hookids(paths):
    """hook attachments and tool calls in line order, with the ids that link them."""
    for p in paths:
        print('##', os.path.basename(p)[:24])
        for i, e in enumerate(load(p), 1):
            a = e.get('attachment') or {}
            c = (e.get('message') or {}).get('content')
            if str(a.get('type', '')).startswith('hook'):
                print(' line %-3d %-20s toolUseID=%s' % (i, a.get('hookName'), a.get('toolUseID')))
            elif isinstance(c, list) and c and c[0].get('type') == 'tool_use':
                print(' line %-3d tool_use %-8s id=%s' % (i, c[0].get('name'), c[0].get('id')))


def prompts(paths):
    """every user entry: how long it is, and which probe tokens it holds."""
    for p in paths:
        for i, e in enumerate(load(p), 1):
            if e.get('type') != 'user':
                continue
            c = (e.get('message') or {}).get('content')
            c = c if isinstance(c, str) else json.dumps(c)
            print('%-22s line %-3d chars=%-5d tokens=%s'
                  % (os.path.basename(p)[:22], i, len(c),
                     [n for n, v in TOKENS.items() if v and v in c] or '-'))


SCANS = {'spans': spans, 'cwd': cwd, 'types': types, 'inversions': inversions,
         'seam': seam, 'handoff': handoff, 'escaping': escaping, 'replay': replay,
         'selfref': selfref, 'leaf': leaf, 'hooks': hooks, 'hookraw': hookraw,
         'hookids': hookids, 'prompts': prompts}

if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--tokens' in argv:
        k = argv.index('--tokens')
        TOKENS = load_tokens(argv[k + 1])
        argv = argv[:k] + argv[k + 2:]
    if len(argv) < 2 or argv[0] not in SCANS:
        raise SystemExit(__doc__)
    SCANS[argv[0]](argv[1:])
