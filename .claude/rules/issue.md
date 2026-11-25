# Issue rules of ccpm

These rules say how to keep issues and pull requests, so that each piece of work has one place
where someone decides it, and nothing piles up beside it.

## 1. One place for each piece of work

- **Before you open an issue, look for an open one that covers the work, and add to it instead.**
  A plugin being rebuilt has its rebuild issue. A request for that plugin goes there as a section.
  - Rationale: two issues for one piece of work each get their own decisions, and the two drift
    apart. The extra one waits for someone to close it.
- **When what the work should be changes, rewrite the issue and its pull request in place**, title
  included, so they say what holds now.
  - Rationale: a new issue beside the old one leaves the reader to work out which still holds.
- **Close an issue opened by mistake with a line saying where its content went.**
  - Rationale: whoever finds it through a link reaches the place that holds its content.

## 2. Form

- **Write an issue in English with the title `<plugin>: <what it should be>`, then two headings.**
  - `## Situation`: the trouble as it happened, and where it was seen, such as the plugin's version
    and commit, the Claude Code version, and the session or pull request.
  - `## What it should be`: the state wanted, for those it's for. No means, plan, or order: the
    development settles those, in the run's steering.
  - Rationale: an issue is the request that starts the work. The reader finds the same thing under
    the same heading in every issue, and the development stays free to choose the means.
- **Name each place a claim rests on as `path:line`, with the words quoted.**
  - Rationale: the reader checks the claim against the source without searching.
- **Keep only what holds now. How you reached it stays in the edit history and in git.**
  - Rationale: a reader acts on the current decision, and reads any history mixed into it as part
    of that decision.
