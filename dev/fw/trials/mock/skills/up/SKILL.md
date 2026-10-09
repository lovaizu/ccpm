---
name: up
description: This skill should be used when the user asks mock to answer questions for a friend, or types /mock:up. It is a trial plugin for fw.
---

Call the `fw:flow` skill with these arguments, exactly as they are:

```
record: .mock
domain: ${CLAUDE_PLUGIN_ROOT}/fw
issues: lovaizu/ccpm
request: $ARGUMENTS
```
