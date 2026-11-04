You are building `changelog`, a Claude Code plugin in the folder `changelog/` of this repository.
It writes a project's `CHANGELOG.md`. Its subagent `writer` must keep two rules on every run:

- run no command but `git log --oneline`, so it never commits or changes anything with git;
- write no file but `CHANGELOG.md`.

You want these rules held on every run without writing a check of your own.
