---
name: guide
description: Has turn write SETUP.md, the guide a newcomer follows to start this repository's app. Takes an optional `<in> <out>` to go on from an earlier record.
---

With no arguments, write `.caller/1.yaml` with exactly this, unless it exists, and use `in:
.caller/1.yaml` and `out: .caller/2.yaml`. With arguments `$ARGUMENTS`, use the first as `in` and the
second as `out`.

```yaml
focal_entities:
  - work: "SETUP.md"
  - receiver: "今日入った新人。手順書だけでアプリを起動する"
goal_orientation:
  - acceptance: "新人が誰にも聞かずに、手順書どおりにアプリを起動し、app started と表示される"
  - use: "手順書を上から順に実行する"
constraints:
  - language: "日本語"
retrieved_artifacts:
  - source: "docs/ops.md"
```

Call the `turn:up` skill with three lines as its arguments: `in: <in>`, `out: <out>`, and
`domain: ${CLAUDE_PLUGIN_ROOT}/domain`.

When it returns, read only `<out>`, not the work, and act on its `next`:

- `done`: commit the work it names with the message `guide`, and say so.
- `ask the user`: show the user each `gap` and stop.
- `to the caller: ...` or `stopped: ...`: say what it says and stop.
