# Issue rules (ccpm)

How issues and pull requests are kept, so that each piece of work is decided in one place and
nothing piles up beside it.

## 1. One place for each piece of work

- **Before opening an issue, look for an open one that covers the work, and add to it instead.** A
  plugin being rebuilt has its rebuild issue; a request for it goes there as a section.
  - Rationale: two issues for one piece of work are decided apart and drift, and the extra one is
    left for someone to close.
- **When the plan changes, rewrite the issue and its pull request in place**, title included, so
  they say what is meant now.
  - Rationale: a new issue beside the old one leaves the reader to work out which still holds.
- **Close an issue opened by mistake with a line saying where its content went.**
  - Rationale: whoever finds it through a link reaches the place that holds it.

## 2. Form

- **Write an issue as the existing issues of its kind are written, in English.**
  - A fault: title `<plugin>: <what happens>`; `## What happened`, `## Why it matters`,
    `## What it should be` once it is known, and `## Seen in` with the plugin's version and commit,
    the Claude Code version and the session or pull request.
  - A piece of work: title `<plugin>: <what it should be>`; `## What it should be`, `## Why`,
    `## Order`, and `## Existing issues to judge once it is built` when there are any.
  - Rationale: the reader finds the same thing under the same heading in every issue.
- **Name each place a claim rests on as `path:line`, with the words quoted.**
  - Rationale: the reader checks the claim against the source without searching.
- **Keep only what holds now; how it was reached stays in the edit history and in git.**
  - Rationale: a reader acts on the current decision, and a history mixed in is read as part of it.
