"""Run one scenario of Claude Code on the throwaway plugin `rec` and keep each hook payload.

Usage: python3 record.py <scenario> <run-folder>

It sets up a throwaway git repository in <run-folder>/repo, starts
`claude -p --input-format stream-json --output-format stream-json --verbose --model haiku
--dangerously-skip-permissions --plugin-dir <plugin>` there, types each prompt of the scenario when
its condition holds, and closes the input once the scenario's end has come and the stream has been
quiet for QUIET seconds. It leaves hooks.jsonl (each payload, as log.py wrote it), stream.jsonl
(the stream that claude printed), and version.txt (`claude --version`) in <run-folder>. Each
scenario is named as the `<what>` of the record of dev/tests/recorded/ that it records again,
`claude-code-<version>-<what>.jsonl`, so that the compatibility test of Lane's architecture finds
the scenario of each record.
"""

import json
import os
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "plugin")
QUIET = 15
LIMIT = 300
TOLD = "Install nothing, and send nothing to any outside service."


def hooks(folder):
    path = os.path.join(folder, "hooks.jsonl")
    if not os.path.exists(path):
        return []
    with open(path) as log:
        return [json.loads(text)["payload"] for text in log if text.strip()]


def results(stream):
    return sum(1 for each in stream if each.get("type") == "result")


def stopped(folder, count):
    return (
        sum(
            1
            for each in hooks(folder)
            if each["hook_event_name"] == "SubagentStop" and each.get("agent_type") == "rec:sleeper"
        )
        >= count
    )


SLEEPER_ONE = (
    "Start the subagent rec:sleeper by the Agent tool with run_in_background set to true, the"
    ' description `Sleep then echo`, and the prompt: `Run the Bash command python3 -c "import'
    ' time; time.sleep(40)" in the foreground. Then run the Bash command echo after-sleep. Then'
    " reply with the word slept.` Don't wait for it. Reply with the word started. " + TOLD
)

SLEEPER_TWO = (
    "In one message, make two Agent calls at once, both to the subagent rec:sleeper with"
    " run_in_background set to true. The first has the description `Sleeper one` and the prompt"
    " `Run the Bash command echo one-first. Then run the Bash command echo one-second. Then reply"
    " with the word one.` The second has the description `Sleeper two` and the prompt `Run the"
    " Bash command echo two-first. Then run the Bash command echo two-second. Then reply with the"
    " word two.` Don't wait for them. Reply with the word started. " + TOLD
)

# Each scenario: its prompts, each with the condition on (folder, stream) that it waits for, and
# the condition of its end.
SCENARIOS = {
    "skill-command-while-subagent": (
        [
            ("/rec:start", lambda folder, stream: True),
            ("/rec:other", lambda folder, stream: results(stream) >= 1),
        ],
        lambda folder, stream: stopped(folder, 1) and results(stream) >= 3,
    ),
    "two-subagents": (
        [(SLEEPER_TWO, lambda folder, stream: True)],
        lambda folder, stream: stopped(folder, 2) and results(stream) >= 2,
    ),
    "compact-while-subagent": (
        [
            (SLEEPER_ONE, lambda folder, stream: True),
            ("/compact", lambda folder, stream: results(stream) >= 1),
        ],
        lambda folder, stream: stopped(folder, 1) and results(stream) >= 3,
    ),
}


def repository(folder):
    repo = os.path.join(folder, "repo")
    os.makedirs(repo)
    with open(os.path.join(repo, "README.md"), "w") as readme:
        readme.write("A throwaway repository.\n")
    for command in (
        ["git", "init", "-q", "-b", "main"],
        ["git", "add", "README.md"],
        [
            "git",
            "-c",
            "user.name=rec",
            "-c",
            "user.email=rec@example.invalid",
            "commit",
            "-qm",
            "start",
        ],
    ):
        subprocess.run(command, cwd=repo, check=True)
    return repo


def main(scenario, folder):
    prompts, end = SCENARIOS[scenario]
    os.makedirs(folder)
    repo = repository(folder)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True, check=True)
    with open(os.path.join(folder, "version.txt"), "w") as out:
        out.write(version.stdout)
    env = dict(os.environ, REC_LOG=os.path.join(folder, "hooks.jsonl"))
    claude = subprocess.Popen(
        [
            "claude",
            "-p",
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
            "--verbose",
            "--model",
            "haiku",
            "--dangerously-skip-permissions",
            "--plugin-dir",
            PLUGIN,
        ],
        cwd=repo,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    stream, last = [], [time.time()]

    def read():
        with open(os.path.join(folder, "stream.jsonl"), "w") as out:
            for text in claude.stdout:
                out.write(text)
                out.flush()
                last[0] = time.time()
                try:
                    stream.append(json.loads(text))
                except ValueError:
                    pass

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    start = time.time()
    pending = list(prompts)
    while time.time() - start < LIMIT:
        if pending and pending[0][1](folder, stream):
            prompt = pending.pop(0)[0]
            message = {"type": "user", "message": {"role": "user", "content": prompt}}
            claude.stdin.write(json.dumps(message) + "\n")
            claude.stdin.flush()
            last[0] = time.time()
        elif not pending and end(folder, stream) and time.time() - last[0] > QUIET:
            break
        time.sleep(0.5)
    else:
        print(f"{scenario}: the end didn't come in {LIMIT} seconds", file=sys.stderr)
    claude.stdin.close()
    try:
        claude.wait(timeout=60)
    except subprocess.TimeoutExpired:
        claude.kill()
    reader.join(timeout=5)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
