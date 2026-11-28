# overnight

overnight is a Claude Code plugin with a command that runs a piece of work, or a work, that you
give it in Claude Code while you're away, and resumes it by itself after the usage limit or an
error stops it.

<!-- TODO: the queue and the next work's start: the first sentence says that overnight runs the
works you give it one after another, starting the next work when one ends. -->

overnight is in development, at version 0.1.0. What it does may still change, and no work has yet
run through a real night on this version.

overnight is for you when you hand Claude Code work that runs for hours and leave it running at
night. With it, you find the work done by morning, or recorded as failed with its log, without
getting up to type "continue" once the limit lifts.

<!-- TODO: the queue and the next work's start: the benefit says that you find each work that you
gave overnight carried through by morning, not only the first. -->

## Non-goals

- overnight doesn't resume a conversation that you have open in Claude Code: it runs work that it
  starts itself. Give the work to overnight in place of your conversation. In the morning, run
  `claude --resume <session_id>` to open the work's conversation, with the `session_id` from the
  work's `state.json`, which the [Walkthrough](#walkthrough) shows.
- overnight doesn't run from a terminal outside Claude Code: Claude Code puts the command on the
  `PATH` of its own shell only. Start it from Claude Code's bash mode, as `! overnight ...`.
- overnight doesn't keep your computer awake. Before you leave, set the computer not to sleep while
  it's plugged in, such as by **Prevent automatic sleeping on power adapter when the display is
  off** in the Battery settings of a Mac laptop.

## Walkthrough

<!-- TODO: the `overnight` command of bin/overnight runs this walkthrough as it's written. -->

At the end, you have your tests moved to pytest and committed by morning, from one command that you
typed before you left, though the usage limit stopped the work in the night.

This run shows what overnight aims to do, not a night that someone recorded.

At 23:00, before you leave, you give overnight the work in `~/work/shop`, with the tools that
Claude may use for it:

```console
! overnight --dir ~/work/shop \
    --allowed-tools "Read,Edit,Write,Bash(pytest:*),Bash(git add:*),Bash(git commit:*)" \
    "Move the tests in tests/unittest_old/ to pytest, run them until they pass, and commit"
overnight: work 20261128-230012 started in /home/you/work/shop
overnight: state and log in /home/you/.local/state/overnight/20261128-230012/
```

You close Claude Code and leave.

In the morning, the work's log shows where the limit stopped the work, and that the work went on
and ended as done:

```console
$ cat ~/.local/state/overnight/20261128-230012/log
23:00 run 1 started
01:42 run 1 stopped: 5-hour limit reached ∙ resets 4am. Retry 1 of 7 at 01:47.
01:47 run 2 started
01:47 run 2 stopped: 5-hour limit reached ∙ resets 4am. Retry 2 of 7 at 01:57.
01:57 run 3 started
01:57 run 3 stopped: 5-hour limit reached ∙ resets 4am. Retry 3 of 7 at 02:57.
02:57 run 4 started
02:57 run 4 stopped: 5-hour limit reached ∙ resets 4am. Retry 4 of 7 at 03:57.
03:57 run 5 started
03:57 run 5 stopped: 5-hour limit reached ∙ resets 4am. Retry 5 of 7 at 04:57.
04:57 run 6 started
05:43 run 6 done
work 20261128-230012 done after 6 runs
$ cat ~/.local/state/overnight/20261128-230012/state.json
{
  "status": "done",
  "dir": "/home/you/work/shop",
  "session_id": "8d1e5b7a-2c4f-4e0b-9a63-5f1d2e7c9b40",
  "runs": 6
}
$ git -C ~/work/shop log --oneline -1
3f9c2a1 Move the tests in tests/unittest_old to pytest
```

The work went on from where the limit stopped it, 57 minutes after the limit lifted.

<!-- TODO: the queue, the next work's start, a start time, and how many run at once: the
walkthrough puts the night's works in the queue with a start time, three of them run at once, and
each next work starts when one ends, so the morning's log shows each work done. -->

## How it works

<!-- TODO: the `overnight` command of bin/overnight works as this section says. -->

overnight runs your work in Claude Code without you, and each time a run stops short, overnight
waits and asks Claude to go on in the same conversation, until the work is done or the retries run
out.

<!-- TODO: the queue and the next work's start: the one way says too that once a work ends,
overnight starts the next work in its queue. -->

### "Does the work go on after you close Claude Code?"

Yes. overnight runs the work apart from the Claude Code session that you start it from, and
returns at once, so the work goes on after you close Claude Code.

### "At the limit, the work waits until you're back to type 'continue'."

overnight types it for you. It runs the work with `claude -p`, Claude Code's non-interactive
mode. When a run stops, overnight waits, then asks Claude again to go on. The waits before the
retries are 5 and 10 minutes, then 60 minutes each, so the work goes on within an hour after
the limit lifts, as long as it lifts before the retries run out.

### "Does it start the work over after a stop?"

No. Each retry goes on in the same conversation, by `claude -p --resume <session_id>`, so Claude
keeps what it has done and read.

### "Claude Code can exit with 0 at the limit. How does it know a run stopped short?"

overnight counts a run as done only when Claude Code exits with 0 and its result says no error.
Anything else, the usage limit or any other error, is a stop that it retries.

### "Does asking again and again while the limit holds do harm?"

No. A request while the limit holds only fails again. The growing waits keep the requests to a
few.

### "What if the limit lifts late, or an error keeps coming?"

overnight retries 7 times by default, and those retries wait 5 hours and 15 minutes in all. The
limit lifts at most 5 hours after a stop, so the 7 retries outlast it after any stop. To retry more
or fewer times, give `--retries <count>`.

Once the retries run out, overnight records the work as failed, with `"status": "failed"` in
`state.json`. In the morning, open the folder that overnight printed when the work started, such
as `~/.local/state/overnight/20261128-230012/`, not the folder that the work ran in. The printed
folder holds `state.json` and the work's one `log`, which shows where each run stopped.

### "Does it stop at night to ask your permission?"

No. Claude uses only the tools that `--allowed-tools` names. Claude Code refuses any other tool
without asking, so no question waits for you.

<!-- TODO: the next work's start: a doubt such as "When one work ends, does the next start without
me?", and how overnight starts it. -->

<!-- TODO: the queue: a doubt such as "Can I give it more works than one night's limit lets run?",
and how the queue holds any number of works. -->

<!-- TODO: a start time: a doubt such as "Can it wait to start until I've gone to bed?", and how a
work starts at the time you give, or right away. -->

<!-- TODO: how many run at once: a doubt such as "Do several works at once use up the limit
sooner?", and how overnight runs three at once by default, or as many as you give. -->

## Requirements

- macOS or Linux: `uname` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- Claude Code, logged in: `claude auth status` shows `"loggedIn": true`.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install overnight@ccpm
```

<!-- TODO: the `overnight` command of bin/overnight answers `--version` as this line says. -->
In Claude Code, `! overnight --version` shows `overnight 0.1.0`.

## Documentation

<!-- TODO: the `overnight` command of bin/overnight answers `--help` as this line says. -->
- `! overnight --help`, in Claude Code: for you when you start a work, every option of the command,
  whether it's required, and its default.
- [Changelog](CHANGELOG.md): for you after an update, the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
