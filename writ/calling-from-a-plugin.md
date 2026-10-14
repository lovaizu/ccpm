# Calling writ from a plugin's step

A plugin's step that needs a document calls writ, and gets back either the finished document with
its report, or the points that only the step can decide, each with the answer writ recommends. writ
asks the user nothing when a step calls it, so the step may run where no one can answer.

## The call

Call the `writ:up` skill with the request in words, then a line naming the file writ writes back:

```text
Write the release notes for 1.4 at docs/releases/1.4.md, from the merged pull requests.
out: .tasks/notes-back.json
```

Name `writ` in `dependencies` in your plugin's `.claude-plugin/plugin.json`, so that installing your
plugin installs writ, and turn with it.

## What writ writes back

A JSON object at `out`, whose `next` says what the step does next:

- `decide`: `open` lists each point the request, the repository and the sources leave open, as
  `{"item", "question", "recommended"}`. Decide each, write your decisions in a file, in words, and
  call writ again with the same request, a new `out`, and a line `decisions: <that file>`.
- `done`: the document is at `document`, and every item of its checklists is met; `report` is the
  file that gives, for each item, the lines that meet it.
- `not met`: the document is at `document`, but the job ended, at the user's word, before every
  item was met; `not met` lists those items, and there is no report.
