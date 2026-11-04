You are building `changelog`, a Claude Code plugin in the folder `changelog/` of this repository.
It writes a project's `CHANGELOG.md` for the next release. Its subagent `lead` starts the others,
and must start them in this order on every run:

- `writer` first, which writes the new entries;
- once writer has written them, `reviewer`, which compares them with the commits;
- where reviewer finds an entry missing, wrong or extra, `writer` again, then `reviewer` again;
- once reviewer finds every entry right, no more.

`writer` must also run no command but `git log --oneline`, and write no file but `CHANGELOG.md`.

You want this order and these rules held on every run without writing code or checks of your own.
