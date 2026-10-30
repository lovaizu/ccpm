#!/bin/sh
# Installs Vale into .venv/bin, beside the tools uv sets up, and the Google style package Vale reads
# into dev/vale/styles/Google/, which git ignores, for dev/prose.sh, run from the top of the
# repository. Neither is on PyPI, so each is downloaded from its GitHub release and checked against a
# sha256 kept here before it is unpacked: a binary or a style run before anything checks it is what
# a lock is there to stop. Vale's are the lines it published in its release's checksums.txt; the
# Google package publishes none, so its sha256 is the one its release file had when it was first
# taken (#63). To move to another version, change the version and its sha256 lines together.
set -e

version=3.25.1
sums='4bf5c5176b682b1da0830f471584d3494f1c2e27ee3029e1ad6f6661d4962182  vale_3.25.1_Linux_64-bit.tar.gz
2a69755b68118c612c455fc0c5ea1b9438519aa1c852e3fb303b3ad97141bbb0  vale_3.25.1_Linux_arm64.tar.gz
e27097e84a812d45546de8d6a4ffa75538cab39c96f79b153b601240f8cefaf9  vale_3.25.1_macOS_64-bit.tar.gz
fbcaa68d9b9e229b9c8dc918f209e93572ce943039700b7e04a423ff12f684cd  vale_3.25.1_macOS_arm64.tar.gz'

google=0.7.1
google_sum='4b67fca1f2a88595b2a578ab98bbf3017a23af677b04f93e862843f3ea1a9a0b  Google.zip'

if command -v sha256sum >/dev/null 2>&1; then
  check="sha256sum -c"
else
  # macOS, which has no sha256sum.
  check="shasum -a 256 -c"
fi
# Each download goes into a folder of its own, removed however the script ends, so a download cut
# off or refused leaves nothing behind.
dir=$(mktemp -d)
trap 'rm -rf "$dir"' EXIT

# Downloads $2 from $1 into $dir and checks it against the sha256 line $3, or stops.
fetch() {
  curl -fsSL -o "$dir/$2" "$1/$2"
  echo "$3" > "$dir/sum"
  if ! (cd "$dir" && $check sum >/dev/null); then
    echo "vale.sh: $2 does not match the sha256 kept for it; nothing is installed" >&2
    exit 1
  fi
}

styles=dev/vale/styles/Google
if [ "$(cat "$styles/version" 2>/dev/null)" != "$google" ]; then
  fetch "https://github.com/vale-cli/Google/releases/download/v$google" Google.zip "$google_sum"
  rm -rf "$styles"
  (cd "$dir" && unzip -q Google.zip)
  mv "$dir/Google" "$styles"
  echo "$google" > "$styles/version"
fi

bin=.venv/bin/vale
if [ -x "$bin" ] && [ "$("$bin" --version)" = "vale version $version" ]; then
  exit 0
fi

case $(uname -s) in
  Linux) os=Linux ;;
  Darwin) os=macOS ;;
  *) echo "vale.sh: no Vale archive is kept for $(uname -s); install Vale $version" \
    "(https://vale.sh/docs/install) as $bin" >&2; exit 1 ;;
esac
case $(uname -m) in
  x86_64 | amd64) arch=64-bit ;;
  arm64 | aarch64) arch=arm64 ;;
  *) echo "vale.sh: no Vale archive is kept for $(uname -m); install Vale $version" \
    "(https://vale.sh/docs/install) as $bin" >&2; exit 1 ;;
esac
archive=vale_${version}_${os}_${arch}.tar.gz
fetch "https://github.com/errata-ai/vale/releases/download/v$version" "$archive" \
  "$(echo "$sums" | grep " $archive\$")"
tar -xzf "$dir/$archive" -C "$dir" vale
mkdir -p .venv/bin
mv "$dir/vale" "$bin"
