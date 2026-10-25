#!/bin/sh
# Mutation testing of each plugin that has dev/<plugin>/cosmic-ray.toml, run from the top of the
# repository with the tools of pyproject.toml's dev and test-quality groups; fails on any mutant no
# test catches.
# cr-rate is not used for that: it takes a limit of 0 as no limit.
# Given plugin names, such as `sh dev/mutate.sh rn`, it tests those alone, as while one plugin is
# changed; CI gives none and tests every plugin. Given `--since <commit>` first, it tests only the
# mutants on lines changed since that commit, files not yet added to git among them, by Cosmic
# Ray's own git filter, as before a push.
# Each mutant is to be caught by the unit tests, which dev/check.sh runs, as the mutation testing
# checks that they are enough; the property tests are left out of it.
# Cosmic Ray changes the files it tests, so each worker runs on a copy of its own; one worker for
# each processor, as each mutant is tested on its own, each on a port free when the run starts, so
# two runs at once do not test each other's copies. The copies of each plugin's run are in
# <plugin>/<yyyymmdd>-mutate-<random>/ in the system's temporary folder (dev/architecture.md, Where
# a plugin writes its files), removed when the run ends, and the system's temporary folder the
# workers' tests are given is in it, so what a test killed on its timeout leaves goes with it.
set -e

since=""
if [ "$1" = "--since" ]; then
  since=$2
  shift 2
fi

plugins="$*"
if [ -z "$plugins" ]; then
  for config in dev/*/cosmic-ray.toml; do
    plugin="${config#dev/}"
    plugins="$plugins ${plugin%/cosmic-ray.toml}"
  done
fi
tmp=$(python3 -c 'import tempfile; print(tempfile.gettempdir())')
copy=""
pids=""
trap 'kill $pids 2>/dev/null || true; [ -z "$copy" ] || rm -rf "$copy"' EXIT
for plugin in $plugins; do
  mkdir -p "$tmp/$plugin"
  copy=$(mktemp -d "$tmp/$plugin/$(date +%Y%m%d)-mutate-XXXXXX")
  mkdir "$copy/tmp"
  ports=$(python3 - "$(getconf _NPROCESSORS_ONLN)" <<'EOF'
import socket
import sys

# Each socket is held until all are bound, so no two ports are the same.
found = [socket.socket() for _ in range(int(sys.argv[1]))]
for s in found:
    s.bind(("localhost", 0))
print(" ".join(str(s.getsockname()[1]) for s in found))
EOF
  )
  # The virtual environment uv makes in .venv is left out of the copies: the workers run the tools
  # from where it is, and the files Python writes in it while the first workers start would be
  # copied half made.
  for port in $ports; do
    mkdir "$copy/worker-$port"
    tar -cf - --exclude=./.venv . | tar -xf - -C "$copy/worker-$port"
    (cd "$copy/worker-$port" && exec env TMPDIR="$copy/tmp" cosmic-ray http-worker --port "$port") \
      >/dev/null 2>&1 &
    pids="$pids $!"
  done
  python3 - $ports <<'EOF'
import socket
import sys
import time

for port in sys.argv[1:]:
    for _ in range(300):
        try:
            socket.create_connection(("localhost", int(port))).close()
            break
        except OSError:
            time.sleep(0.1)
EOF
  db="$copy/mutants.sqlite"
  python3 - "dev/$plugin/cosmic-ray.toml" "$copy/config.toml" "$since" $ports <<'EOF'
import sys

# The config's distributor, its last table, is replaced by the workers; the git filter is given the
# commit the changed lines are counted from.
source, target, since, ports = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
with open(source, encoding="utf-8") as f:
    text = f.read().split("[cosmic-ray.distributor]")[0]
urls = ", ".join(f'"http://localhost:{port}"' for port in ports)
with open(target, "w", encoding="utf-8") as f:
    f.write(f'{text}[cosmic-ray.distributor]\nname = "http"\n\n')
    f.write(f"[cosmic-ray.distributor.http]\nworker-urls = [{urls}]\n")
    f.write(f'\n[cosmic-ray.filters.git-filter]\nbranch = "{since}"\n')
EOF
  cosmic-ray init "$copy/config.toml" "$db"
  # A line marked `# pragma: no mutate` has no mutant a test can tell apart, for the reason the
  # plugin's cosmic-ray.toml gives (dev/architecture.md, Unit tests: code).
  cr-filter-pragma "$db"
  # The git filter reads the lines changed from `git diff`, which leaves out a file not yet added
  # to git, such as a check just written; each is marked as to be added in a copy of the index, the
  # index git uses itself left as it is, so all its lines count as changed.
  if [ -n "$since" ]; then
    cp "$(git rev-parse --git-path index)" "$copy/index"
    git ls-files --others --exclude-standard | while read -r file; do
      GIT_INDEX_FILE="$copy/index" git add --intent-to-add -- "$file"
    done
    GIT_INDEX_FILE="$copy/index" cr-filter-git --config "$copy/config.toml" "$db"
  fi
  # Cosmic Ray 8.7.0's http distributor asks asyncio for a loop that Python 3.14 no longer makes
  # on its own (sixty-north/cosmic-ray#608, fixed after 8.7.0), so one is set first.
  python3 -c 'import asyncio, sys
from cosmic_ray.cli import cli
asyncio.set_event_loop(asyncio.new_event_loop())
sys.exit(cli())' exec "$copy/config.toml" "$db"
  cr-report --surviving-only --show-diff "$db" | tee "$copy/report.txt"
  grep -q '^surviving mutants: 0 ' "$copy/report.txt"
  # The workers are stopped before their copies are removed, and the next plugin's run takes ports
  # of its own.
  kill $pids 2>/dev/null || true
  wait $pids 2>/dev/null || true
  pids=""
  rm -rf "$copy"
  copy=""
done
