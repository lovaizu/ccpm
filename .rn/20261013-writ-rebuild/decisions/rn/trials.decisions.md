# What rn's trials do

rn's prompts are tried one move at a time, as `dev/architecture.md`'s Unit tests: prompts says:
each case one move the steps of rn's skills take, from a session state made beforehand by rn's own
commands, in `dev/rn/trials/moves/`; how to run it is in `dev/rn/README.md`, the cases in
`cases.py`.

## Form

- Each case runs in a fresh repository whose origin is a bare repository beside it, not on
  `lovaizu/playground`, as a move needs no real GitHub; the cases run side by side, each in a folder
  of its own, and nothing is removed, so each record can be read after.
- Each message is sent by lane's `dev/lane/trials/trying.py` `Conversation`, on Opus, the messages
  of one conversation to one live run of Claude Code, a fresh conversation a new run, as
  `claude -p --resume` dropped the last reply on Claude Code 2.1.309.
- What each move must leave is checked by script, and the records are read against the skills'
  steps, as only they show where a move went wrong.
- Code in `dev/rn/trials/` is out of the line count, mutation testing and property tests, its run
  being its check; Python 3 with the standard library alone, checked by ruff and the type checker.

## The stand-ins

- turn's `turn:up`: an agent in the copy of turn, on the model it inherits as the real one does,
  passing on what the case set for the call's work, the line turn sends `main` and its reply, so the
  move judged is the orchestrator's alone; its lanes are left out, as it keeps none of the real
  steps.
- `gh`: a script first on the PATH, keeping the pull request, the issues and every command in a
  file of the case's.
- The user: the case's messages, each answer in the user's own words, as rn orders its options as
  it judges and a letter would pick a decision the stand-in's reply was not made from.
