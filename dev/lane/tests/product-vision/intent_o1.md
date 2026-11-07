You are building `changelog`, a Claude Code plugin in the folder `changelog/` of this repository.
It writes a project's `CHANGELOG.md` for the next release. Its skill `write`, typed as
`/changelog:write`, starts its subagents, and must start them in this order on every run:

- `writer` first, which writes the new entries;
- once writer has written them, `reviewer`, which compares them with the commits;
- where reviewer asks the person who runs the plugin about a commit, no one else until the person
  has answered and reviewer, given their answer as they wrote it, has gone on;
- where reviewer finds an entry missing, wrong or extra, `writer` again, then `reviewer` again;
- once reviewer finds every entry right, no more.

Each subagent must start with what `changelog/scripts/start.py`, given its name, prints for it,
word for word, so that nothing the main conversation adds or leaves out reaches it.

`writer` must also keep these on every run:

- run no command but `git log --oneline`, so it never commits or changes anything with git;
- write no file but `CHANGELOG.md`;
- carry out the practices of each intent that its start names under `intents`, in their order, as
  `changelog/domain/practices.json` keeps them.

You want this order and these rules held on every run without writing code or checks of your own.
