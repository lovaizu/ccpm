# Issue rules of ccpm

These rules say how to keep issues and pull requests, so that each piece of work has one place
where someone decides it, and nothing piles up beside it.

## 1. One place for each piece of work

- **Before you open an issue, look for an open one that covers the work, and add to it instead.**
  A plugin being rebuilt has its rebuild issue. A request for that plugin goes there as a section.
  - Rationale: two issues for one piece of work each get their own decisions, and the two drift
    apart. The extra one waits for someone to close it.
- **Once the work starts, leave its issue as it is, and write the aim as it changes in the run's
  steering and the pull request.**
  - Rationale: the issue is the request that started the work, and the reader finds what the work
    aims at now in one place beside the work.
- **Give work that a pull request's purpose doesn't need its own issue, and do it in a worktree
  of its own from main.** Open the issue when the work comes up during development, and take its
  own pull request to main.
  - Rationale: the change reaches main without waiting for the other pull request, so several
    improvements go on at once, and each pull request holds only what its purpose needs.
- **Close an issue opened by mistake with a line saying where its content went.**
  - Rationale: whoever finds it through a link reaches the place that holds its content.

## 2. Form

- **Write an issue in English with the title `<plugin>: <what it should be>`, then two headings.**
  - `## Situation`: the trouble as it happened, and where it was seen, such as the plugin's version
    and commit, the Claude Code version, and the session or pull request.
  - `## Desired State`: the state wanted, for those it's for. No means, plan, or order: the
    development settles those, in the run's steering.
  - Rationale: an issue is the request that starts the work. The reader finds the same thing under
    the same heading in every issue, and the development stays free to choose the means.
- **Name each place a claim rests on as `path:line`, with the words quoted.**
  - Rationale: the reader checks the claim against the source without searching.
- **Keep only what holds now. How you reached it stays in the edit history and in git.**
  - Rationale: a reader acts on the current decision, and reads any history mixed into it as part
    of that decision.
