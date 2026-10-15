# Calling writ from a plugin's step

A plugin's step that needs a document calls writ, and gets back either the finished document with
its report, or the points only the step can decide, each with the answer writ recommends. writ
asks the user nothing when a step calls it, so the step may run where no one can answer, such as a
subagent.

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

- `decide`: `open` lists each point the request, the repository and the sources leave open and the
  document's purpose needs, as `{"point", "recommended"}`. Decide each, and call writ again with
  the same request, your decisions added to it in words, and a new `out`; writ then goes on as if
  they had been settled from the start.
- `done`: `document` lists each file of the document, written; `report` is the report, as writ
  shows it to a user: first what writ decided or left, each with its ground, then each item of the
  checklists, met with the lines that give it or not met.
- `stopped`: `reason` says why writ ended before the document was made, such as turn finding
  that a file where the document goes has changes the repository does not hold. The step puts the
  reason to the user.

When python3 or jq is missing, there is no `out` to read: writ says why in the conversation, and
the step puts that to the user.
