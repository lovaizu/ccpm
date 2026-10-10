---
name: guide
description: Has turn write SETUP.md, the guide a newcomer follows to start this repository's app.
---

Write `.caller/1.yaml` with exactly this, unless it exists:

```yaml
focal_entities:
  - work: "SETUP.md"
  - receiver: "今日入った新人。手順書だけでアプリを起動する"
goal_orientation:
  - acceptance: "新人が誰にも聞かずに、手順書どおりにアプリを起動し、app started と表示される"
  - use: "手順書を上から順に実行する"
constraints:
  - language: "日本語"
```

Then call the `turn:up` skill with these three lines as its arguments:

```
in: .caller/1.yaml
out: .caller/2.yaml
domain: ${CLAUDE_PLUGIN_ROOT}/domain
```

When it returns, read only `.caller/2.yaml`, not the work, and say in one line what you do next:
finish, ask the user its `gap`, or call `turn:up` again.
