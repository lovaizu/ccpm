"""Per-file scans over JSONL log files, one subcommand per question.

Usage: scan.py {spans|cwd|types|inversions|seam|handoff|escaping|hooks|hookraw|hookids|prompts}
               <file.jsonl>... [--tokens <dir>]

`--tokens <dir>` loads probe tokens the way walk.py does: hookraw masks their values out
of what it prints, prompts reports which of them each user entry holds.

Every scan parses entries rather than grepping lines, so a reported field is the field
an entry actually holds. Kept out of the evidence document so its command blocks stay
short; each subcommand is the exact measurement the section quoting it describes.
"""
import collections
import datetime
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
    """how many entries carry a `cwd`, and which paths they name."""
    for p in paths:
        es = load(p)
        print('%s entries=%-4d with_cwd=%-3d cwds=%s'
              % (os.path.basename(p)[:8], len(es), sum(1 for e in es if 'cwd' in e),
                 sorted({e['cwd'] for e in es if 'cwd' in e})))


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
        for i, e in enumerate(es, 1):
            v = e.get('version')
            if v and prev and v != prev:
                for x in es[i - 3:i + 1]:
                    print('%-22s v=%-8s ts=%-26s uuid=%s parent=%s'
                          % (x.get('type'), x.get('version'), x.get('timestamp'),
                             str(x.get('uuid'))[:8], str(x.get('parentUuid'))[:8]))
            if v:
                prev = v
        uu = {e['uuid'] for e in es if e.get('uuid')}
        print('entries whose parentUuid is absent from the file:',
              sum(1 for e in es if e.get('parentUuid') and e['parentUuid'] not in uu))


def _reports(path):
    """yield (line, conversation entry, task id, subagent's last entry) per handoff."""
    d, sid = os.path.dirname(path), os.path.basename(path)[:-6]
    for i, e in enumerate(load(path), 1):
        c = e.get('message', {}).get('content') if e.get('type') == 'user' else None
        if not isinstance(c, str) or '<task-notification>' not in c:
            continue
        tid = re.search(r'<task-id>(.*?)</task-id>', c).group(1)
        sub = '%s/%s/subagents/agent-%s.jsonl' % (d, sid, tid)
        if os.path.exists(sub):
            yield i, e, tid, load(sub)[-1]


def handoff(paths):
    """how long a subagent's final report takes to reach the conversation file."""
    for p in paths:
        for i, e, tid, rep in _reports(p):
            print('task %s  report %s -> user entry line %d %s (+%.0f ms)'
                  % (tid, rep['timestamp'], i, e['timestamp'],
                     (TS(e['timestamp']) - TS(rep['timestamp'])).total_seconds() * 1000))


def escaping(paths):
    """whether the <result> body equals the report, and which entities it holds."""
    for p in paths:
        for i, e, _, rep in _reports(p):
            text = rep['message']['content'][0]['text']
            body = re.search(r'<result>(.*?)</result>', e['message']['content'], re.S).group(1)
            print('line %-4d identical=%-5s unescape(result)==report=%-5s  &lt;=%d &gt;=%d &amp;=%d'
                  % (i, body.strip() == text.strip(), html.unescape(body).strip() == text.strip(),
                     body.count('&lt;'), body.count('&gt;'), body.count('&amp;')))


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
         'seam': seam, 'handoff': handoff, 'escaping': escaping, 'hooks': hooks,
         'hookraw': hookraw, 'hookids': hookids, 'prompts': prompts}

if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--tokens' in argv:
        k = argv.index('--tokens')
        TOKENS = load_tokens(argv[k + 1])
        argv = argv[:k] + argv[k + 2:]
    if len(argv) < 2 or argv[0] not in SCANS:
        raise SystemExit(__doc__)
    SCANS[argv[0]](argv[1:])
