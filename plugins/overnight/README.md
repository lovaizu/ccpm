# overnight

overnight is a Claude Code plugin that resumes work stopped at the usage limit, from where it
stopped.

In development: it resumes the stopped work, but doesn't yet tell you whether the work reached its
end.

overnight is for you when you leave Claude Code working through the night, and the usage limit can
stop it. With it, you find the work done in the morning, not stopped since the small hours.

## Non-goals

- overnight doesn't go on in the window you left: it resumes in the background, and
  `claude --continue` shows it.
- overnight doesn't answer permission prompts: start the night's work in a mode that asks nothing,
  such as `auto`.
- overnight doesn't resume work stopped for another reason, such as a failed login.
- overnight doesn't keep your computer awake: leave it on, such as with `caffeinate` on macOS.

## Requirements

- macOS or Linux: `uname` shows it.
- Claude Code 2.1.332 or later: `claude --version` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install overnight@ccpm
```

`claude plugin details overnight@ccpm` shows `Hooks (1)  StopFailure`.

## Walkthrough

At the end, you have in the morning the work you gave Claude Code at night, done to its end.

This run is the one that overnight's design draws. No end-to-end run of this version records it
yet. At night, at your repository's root, you start Claude Code in a mode that asks nothing for the
work:

```console
claude --permission-mode auto
```

You give it a task of several steps, and go to bed:

```text
Write unit tests for each module in src/, and commit after each module.
```

Claude Code commits the tests of the first modules. In the night, the usage limit stops its turn:

```text
API Error: Rate limit reached
```

You do nothing. Every 15 minutes, overnight resumes the session, and each try stops at the limit
again until it lifts. Once it lifts, the session goes on from the module it stopped at. In the
morning, the window you left still shows the stop. You quit it with `/exit`, and look at your
repository:

```console
git log --oneline
```

A commit for each module of `src/` is there, those after the stop too. To see what the resumed work
did, you open the session:

```console
claude --continue
```

After the stop, the session shows the prompt that overnight gave it, and the work that followed:

```text
Your last turn stopped at the usage limit, which has now lifted. Go on with the work from where it
stopped, and carry it on to its end.
```

## How it works

When the usage limit stops a turn, overnight resumes that session every 15 minutes until the limit
lifts.

### "Does the night's work have to start some other way?"

No: Claude Code runs overnight's hook each time the limit stops a turn, so you give the work as
always.

### "Does the work start over?"

No: overnight resumes the very session that stopped, with its whole conversation, and prompts it to
go on.

### "When does the work start again after the limit lifts?"

Within 15 minutes: overnight tries every 15 minutes, and each try that meets the limit waits for
the next. To try at another interval, set `OVERNIGHT_INTERVAL_SECONDS` to its seconds before you
start Claude Code.

### "Does it do more than the session's permission mode allows?"

No: overnight resumes the session in the permission mode it last ran in, as its transcript records
it.

## Documentation

- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
