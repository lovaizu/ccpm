# overnight

overnight is a command-line tool, installed as a Claude Code plugin, that runs the commands you
leave it for the night, such as `claude -p` work, and runs each one that fails again until it
finishes.

In development, not yet released: overnight runs the commands one after another, and runs each
one that fails again until it succeeds, so it tries a command that never succeeds all night, and
the commands after it wait. It doesn't yet stop after a number of tries, start at a time you
set, or run commands side by side, and no real night at the usage limit has tried it yet.

overnight is for you when you leave work for Claude Code to do while you sleep, and the usage
limit stops it partway through the night. With it, you find in the morning all the work you left
finished, and how each piece ended.

## Non-goals

- overnight doesn't read when the usage limit lifts: it runs a failed command again, waiting
  longer each time, as How it works says.
- overnight doesn't tell a failure at the usage limit from any other failure: it runs again each
  command that ends with an exit status other than 0.
- overnight doesn't pick up a command where it stopped: it runs the same command again from the
  start. Write each piece so that a fresh run finishes it, such as a prompt that asks Claude to
  carry on from the files that an earlier run left.

## Requirements

- macOS or Linux: `uname` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- Claude Code, to install overnight: `claude --version` shows it.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install overnight@ccpm
```

Claude Code puts overnight in `~/.claude/plugins/cache/ccpm/overnight/0.1.0/`. Run it with its
help option:

```console
python3 ~/.claude/plugins/cache/ccpm/overnight/0.1.0/domain/scripts/overnight --help
```

It prints its usage, which starts with `usage: overnight`.

## Walkthrough

At the end, you have both pieces of work you left at night finished, and a report that says how
each ended, though the usage limit stopped the second piece at 02:20.

This run is the one that overnight's design gives. No recorded run of this version shows it yet.
In your repository, you write the night's work in `tonight.txt`, one command on each line:

```text
# The work for tonight, run in this order.
claude -p --permission-mode acceptEdits "Write a docstring for each public function in src/dates.py"
claude -p --permission-mode acceptEdits "Translate docs/guide.md into Japanese, as docs/guide.ja.md"
```

overnight skips blank lines and lines that start with `#`, and runs each other line as a shell
command in the folder you start it in. At 23:00, before you go to bed, you start it there:

```console
$ python3 ~/.claude/plugins/cache/ccpm/overnight/0.1.0/domain/scripts/overnight tonight.txt
Running 2 commands from tonight.txt. The report goes to tonight.txt.report.
```

You leave the terminal open. In the morning, the terminal shows the line that overnight printed
as it ended:

```text
Done: 2 of 2 commands. The report is in tonight.txt.report.
```

You open the report:

```console
$ cat tonight.txt.report
1. done after 1 try, 23:00 to 00:40
   claude -p --permission-mode acceptEdits "Write a docstring for each public function in src/dates.py"
   try 1  23:00 to 00:40  exit status 0
   output of try 1:
     I added a docstring to each of the 9 public functions in src/dates.py.

2. done after 7 tries, 00:40 to 03:31
   claude -p --permission-mode acceptEdits "Translate docs/guide.md into Japanese, as docs/guide.ja.md"
   try 1  00:40 to 02:20  exit status 1
   try 2  02:21 to 02:21  exit status 1
   try 3  02:23 to 02:23  exit status 1
   try 4  02:27 to 02:27  exit status 1
   try 5  02:35 to 02:35  exit status 1
   try 6  02:50 to 02:50  exit status 1
   try 7  03:05 to 03:31  exit status 0
   output of try 7:
     I translated docs/guide.md into Japanese, and wrote it to docs/guide.ja.md.
```

The usage limit stopped the second piece at 02:20, and lifted at 03:00. overnight ran it again
after 1, 2, 4, 8, and 15 minutes, and the try at 03:05 finished it. `src/dates.py` holds the
docstrings, and `docs/guide.ja.md` holds the translation.

## How it works

overnight runs each command you list, one after another, and runs a command that fails again,
waiting longer each time, until it succeeds.

### "Does it know when the usage limit lifts?"

No, and it doesn't need to. It runs a failed command again after 1 minute, then 2, 4, and 8, and
then every 15 minutes, so the work starts again within 15 minutes of the lift. A try that the limit
stops fails at once.

### "Does it work with commands other than `claude -p`?"

Yes. overnight reads only each command's exit status: 0 is a success, and any other is a failure.
So it runs any shell command, such as a script that runs Claude Code with your own options.

### "What if the computer goes to sleep?"

overnight runs only while your computer is awake and its terminal is open. Start it under a
command that keeps the computer awake, such as `caffeinate -i` on macOS or `systemd-inhibit` on
Linux, and leave the lid open.

### "Can Claude Code set up the night's work for you?"

Yes. The list is a plain text file of commands, so you can ask Claude Code to write `tonight.txt`
from the work you describe, and to start overnight as this README says.

### "Where does it say how each piece ended?"

In the report beside the list, named after it with `.report` added. overnight writes each piece
there as it ends, so the report holds each piece that ended even if the run stops partway.

## Documentation

- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](https://github.com/lovaizu/ccpm/blob/main/LICENSE)
