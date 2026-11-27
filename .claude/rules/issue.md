# Issue rules of ccpm

These rules say how to keep issues and pull requests, so that each request has one issue that
stays as it was asked, and nothing piles up in it or beside it.

## 1. One place for each piece of work

- **Before you open an issue, look for an open one that asks for the same, and open none if one
  does.** A request that an open issue's work covers goes in that work's steering. Any other
  request gets its own issue.
  - Rationale: two issues that ask for the same get two answers that drift apart, and an issue
    that grows a section for each new request stops reading as the request that started the
    work.
- **Once the work starts, leave its issue as it is, and write the aim as it changes in the run's
  steering and the pull request.**
  - Rationale: the issue is the request that started the work, and the reader finds what the work
    aims at now in one place beside the work.
- **Give work that a pull request's purpose doesn't need its own issue, and do it in a worktree
  of its own from main.** When the work comes up during development, propose its issue to the
  user, open it once they agree, and take its own pull request to main.
  - Rationale: the change reaches main without waiting for the other pull request, so several
    improvements go on at once, and each pull request holds only what its purpose needs. The user
    decides what work the repository takes on, and a talk with them goes on unbroken.
- **Close an issue opened by mistake with a line saying where its content went.**
  - Rationale: whoever finds it through a link reaches the place that holds its content.

## 2. Form

- **Write an issue in English with the title `<plugin>: <what it should be>`, or `<what it should
  be>` where no one plugin holds it, then two headings.**
  - `## Situation`: the trouble as it happened, and where it was seen, such as the plugin's version
    and commit, the Claude Code version, and the session or pull request.
  - `## Desired State`: the state wanted, for those it's for. No means, plan, or order: the
    development settles those, in the run's steering.
  - Rationale: an issue is the request that starts the work. The reader finds the same thing under
    the same heading in every issue, and the development stays free to choose the means.
- **Name each place a claim rests on as `path:line`, with the words quoted.**
  - Rationale: the reader checks the claim against the source without searching.
