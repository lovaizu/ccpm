#!/bin/sh
# Mutation testing of each plugin that has dev/<plugin>/cosmic-ray.toml, run from the top of the
# repository with the tools of dev/requirements.txt and dev/requirements-test-quality.txt; fails on any mutant no test catches.
# cr-rate is not used for that: it takes a limit of 0 as no limit.
# Given plugin names, such as `sh dev/mutate.sh rn`, it tests those alone, as while one plugin is
# changed; CI gives none and tests every plugin.
# Cosmic Ray changes the files it tests, so each worker runs on a copy of its own; one worker for
# each processor, as each mutant is tested on its own, each on a port free when the run starts, so
# two runs at once do not test each other's copies.
set -e

copy=$(mktemp -d)
pids=""
trap 'kill $pids 2>/dev/null || true; rm -rf "$copy"' EXIT
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
for port in $ports; do
  cp -R . "$copy/worker-$port"
  (cd "$copy/worker-$port" && exec cosmic-ray http-worker --port "$port") >/dev/null 2>&1 &
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
configs=""
for plugin in "$@"; do
  configs="$configs dev/$plugin/cosmic-ray.toml"
done
for config in ${configs:-dev/*/cosmic-ray.toml}; do
  db="$copy/mutants.sqlite"
  rm -f "$db"
  python3 - "$config" "$copy/config.toml" $ports <<'EOF'
import sys

# The config's distributor, its last table, is replaced by the workers.
source, target, ports = sys.argv[1], sys.argv[2], sys.argv[3:]
with open(source, encoding="utf-8") as f:
    text = f.read().split("[cosmic-ray.distributor]")[0]
urls = ", ".join(f'"http://localhost:{port}"' for port in ports)
with open(target, "w", encoding="utf-8") as f:
    f.write(f'{text}[cosmic-ray.distributor]\nname = "http"\n\n')
    f.write(f"[cosmic-ray.distributor.http]\nworker-urls = [{urls}]\n")
EOF
  cosmic-ray init "$copy/config.toml" "$db"
  # Cosmic Ray 8.7.0's http distributor asks asyncio for a loop that Python 3.14 no longer makes
  # on its own (sixty-north/cosmic-ray#608, fixed after 8.7.0), so one is set first.
  python3 -c 'import asyncio, sys
from cosmic_ray.cli import cli
asyncio.set_event_loop(asyncio.new_event_loop())
sys.exit(cli())' exec "$copy/config.toml" "$db"
  cr-report --surviving-only --show-diff "$db" | tee "$copy/report.txt"
  grep -q '^surviving mutants: 0 ' "$copy/report.txt"
done
