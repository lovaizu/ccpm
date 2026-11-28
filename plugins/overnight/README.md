# overnight

overnight is a Claude Code plugin with a command that runs the pieces of work, or works, that you
give it in Claude Code while you're away, one after another, and resumes each work by itself after
the usage limit or an error stops it.

In development, at 0.1.0: overnight runs the works one at a time, in the order you add them, and
starts the next when one ends. No work has yet run through a real night on this version.
overnight doesn't yet run more than one work at once or start a work at a given time.

overnight is for you when you hand Claude Code work that runs for hours and leave it running at
night. With it, you find each work done by morning, or recorded as failed with its log, without
getting up to type "continue" once the limit lifts or to start the next work.

## Non-goals

- overnight doesn't resume a conversation that you have open in Claude Code: it runs work that it
  starts itself. Give the work to overnight in place of your conversation. In the morning,
  `claude --resume <session_id>`, with the `session_id` from the work's `state.json`, opens the
  work's conversation.
- overnight doesn't run from a terminal outside Claude Code: Claude Code puts the command on the
  `PATH` of its own shell only. Start it from Claude Code, as `! overnight ...`.
- overnight doesn't keep your computer awake: before you leave, set the computer not to sleep while
  it's plugged in, such as by **Prevent automatic sleeping on power adapter when the display is
  off** in the Battery settings of a Mac laptop.

## Requirements

- macOS or Linux: `uname` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- Claude Code, logged in: `claude auth status` shows `"loggedIn": true`.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install overnight@ccpm
```

In Claude Code, `! overnight --version` shows `overnight 0.1.0`.

## Walkthrough

At the end, you have your tests moved to pytest and your blog's broken links fixed, each committed
by morning, from two commands that you typed the night before.

This run shows what overnight aims to do, not a night that someone recorded.

At 23:15, before you leave, you start the first work in Claude Code:

```console
! overnight --dir ~/work/shop \
    --allowed-tools "Read,Edit,Write,Bash(pytest:*),Bash(git add:*),Bash(git commit:*)" \
    "Move the tests in tests/unittest_old/ to pytest, run them until they pass, and commit"
overnight: work 20261128-231502 started in /home/you/work/shop
overnight: state and log in /home/you/.local/state/overnight/20261128-231502/
```

A minute later, you add the second work. It waits in the queue while the first runs:

```console
! overnight --dir ~/work/blog \
    --allowed-tools "Read,Edit,Bash(make linkcheck:*),Bash(git add:*),Bash(git commit:*)" \
    "Fix each broken link that make linkcheck reports, and commit"
overnight: work 20261128-231610 waits in the queue after 1 work, to run in /home/you/work/blog
overnight: state and log in /home/you/.local/state/overnight/20261128-231610/
```

Once overnight prints these lines, you close Claude Code.

In the morning, the first work's log shows it done, and your repository holds its commit:

```console
$ cat ~/.local/state/overnight/20261128-231502/log
23:15 run 1 started
01:42 run 1 stopped: 5-hour limit reached ∙ resets 4am. Retry 1 of 7 at 01:47.
01:47 run 2 started
01:47 run 2 stopped: 5-hour limit reached ∙ resets 4am. Retry 2 of 7 at 01:57.
01:57 run 3 started
01:57 run 3 stopped: 5-hour limit reached ∙ resets 4am. Retry 3 of 7 at 02:17.
02:17 run 4 started
02:17 run 4 stopped: 5-hour limit reached ∙ resets 4am. Retry 4 of 7 at 03:17.
03:17 run 5 started
03:17 run 5 stopped: 5-hour limit reached ∙ resets 4am. Retry 5 of 7 at 04:17.
04:17 run 6 started
05:03 run 6 done
work 20261128-231502 done after 6 runs
$ cat ~/.local/state/overnight/20261128-231502/state.json
{
  "status": "done",
  "dir": "/home/you/work/shop",
  "session_id": "8d1e5b7a-2c4f-4e0b-9a63-5f1d2e7c9b40",
  "runs": 6
}
$ git -C ~/work/shop log --oneline -1
3f9c2a1 Move the tests in tests/unittest_old to pytest
```

The second work started as the first ended, and its log shows it done too:

```console
$ cat ~/.local/state/overnight/20261128-231610/log
05:03 run 1 started
05:38 run 1 done
work 20261128-231610 done after 1 run
$ git -C ~/work/blog log --oneline -1
b72e04d Fix the broken links that make linkcheck reports
```

You typed two commands. The first work went on from where the limit stopped it, 17 minutes after
the limit lifted.

## How it works

overnight runs your works in Claude Code without you, one after another, and each time a run
stops short, it waits and asks Claude to go on in the same conversation, until the work is done
or the retries run out, then starts the next.

### "Do the works go on after you close Claude Code?"

Yes. overnight runs the works apart from the Claude Code session that you add them from, and
returns at once, so the works go on after you close Claude Code.

### "At the limit, the work waits until you're back to type 'continue'."

overnight types it for you. It runs the work with `claude -p`, Claude Code's non-interactive
mode. When a run stops, overnight waits, then asks Claude again to go on. The waits before the
retries are 5, 10, and 20 minutes, then 60 minutes each. The waits span the 5-hour limit, so the
work goes on within an hour after the limit lifts.

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

After 7 retries, which wait 4 hours and 35 minutes in all, overnight records the work as failed in
`state.json` and starts the next work, so one failed work doesn't stop the rest of the night. The
work's folder keeps `state.json` beside the log of each run. `--retries <count>` sets another
count, such as `--retries 10`.

### "If the computer restarts or overnight stops in the night, what becomes of the works?"

They wait for you, as the queue lives in a file. In Claude Code, `! overnight` with no work given
starts again on the works still waiting, in their order, and runs none that already ended. The work
that was running when overnight stopped goes on in its conversation, as a retry. Adding a work
with `overnight` starts the waiting works again too.

### "Does it stop at night to ask your permission?"

No. Claude uses only the tools that `--allowed-tools` names. Claude Code refuses any other tool
without asking, so no question waits for you.

## Documentation

- [Changelog](CHANGELOG.md): for you after an update, the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
