"""Report the JSON path of every string field of a JSONL entry that contains a needle.

Usage:
    walk.py <file.jsonl> --tokens <dir>          needles = token files in <dir>
    walk.py <file.jsonl> --needle-file <path>    needle  = first line of <path>

Attribution needs the exact field a hit sits in, not a raw-line grep, so every entry
is parsed and every string field is visited. Printed values are masked (token values
never appear) and TRUNCATED TO 110 CHARACTERS; the path and the entry header are not.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from masktok import load, mask

TRUNCATE = 110


def walk(obj, tokens, path=''):
    if isinstance(obj, str):
        hits = sorted(n for n, v in tokens.items() if v and v in obj)
        if hits:
            print('   %-6s @ %-38s %s'
                  % (','.join(hits), path, mask(repr(obj), tokens)[:TRUNCATE]))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, tokens, path + '.' + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, tokens, path + '[%d]' % i)


def main(argv):
    path, flag, arg = argv[1], argv[2], argv[3]
    if flag == '--tokens':
        tokens = load(arg)
    elif flag == '--needle-file':
        tokens = {'needle': open(arg).read().splitlines()[0]}
    else:
        raise SystemExit(__doc__)
    for i, line in enumerate(open(path, encoding='utf-8', errors='replace'), 1):
        if not any(v and v in line for v in tokens.values()):
            continue
        entry = json.loads(line)
        print('line %-4d type=%-9s isSidechain=%-5s ts=%s'
              % (i, entry.get('type'), entry.get('isSidechain'), entry.get('timestamp')))
        walk(entry, tokens)


if __name__ == '__main__':
    main(sys.argv)
