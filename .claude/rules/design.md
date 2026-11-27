---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
---

# Design of ccpm's plugins

These rules keep each part of a plugin, such as a role, a script, a skill, or a best practice, to
the vital few. Judge each part by them before you propose it or keep it.

- **Keep a part only where someone would be at a loss without it. Ask that of the part's
  responsibility. Its speed and its size don't decide it.**
  - Rationale: a part that no one needs spends the time and attention of whoever uses it or
    changes it, and draws in more parts.
- **Give each role, script, or check one responsibility. Split a part that holds two. In rn,
  the generator makes a deliverable, and the refactorer refactors it.**
  - Rationale: a reader understands and changes a part of one responsibility alone, and its result
    says what went wrong.
- **Search for a best practice or a common practice before you design a part, and take it where
  it fits. Put a practice that is the same every time in the prompt of the role that uses it, and
  keep in rn's best practices only what differs by a deliverable's kind.**
  - Rationale: many have tried a known practice, and no one has tried a part of one's own. rn
    chooses a best practice by a deliverable's kind, so a practice that never changes needs no
    choosing.
- **Write no step for what goes without saying, such as following the repository's rules. Name
  none of the repository's means either: its hooks, its check commands, or its other tools.**
  - Rationale: the repository holds its own rules and means, and a prompt that repeats them grows
    and drifts from them.
- **Make a hook or a script hold what must happen every time, in place of an instruction to a role
  or a restart of it.**
  - Rationale: a hook or a script runs the same way every time, while an instruction is only
    advice that a role may miss.
- **Tell a role the purpose and the intent of its work, not steps of work, and point to a file it
  must read by its path alone, with no word of its contents.**
  - Rationale: a role that knows why can meet a case that no step names. An AI that reads a summary
    works from it without opening the file.
- **Make no exception to a rule or a limit. Where one seems needed, find the missing step.**
  - Rationale: an exception makes the reader hold two rules in mind, and it hides the missing step
    that would make the rule hold.
- **Keep the terms already in use, such as generate and evaluate, and rename none.**
  - Rationale: a reader who meets a new name for a known thing takes it for a different thing.
