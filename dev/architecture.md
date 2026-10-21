# How a plugin works

A ccpm plugin is called in rough words, asks the user what only they can decide, and has the work
done by agents that each do one job, so the same request gives the same work each time.

```mermaid
sequenceDiagram
  actor U as user #lt;person#gt;
  participant M as main #lt;skill#gt;
  participant O as orchestrator #lt;agent#gt;
  participant S as script #lt;code#gt;
  participant R as role #lt;agent#gt;
  U->>M: calls the plugin in rough words
  loop hearing, until nothing only the user can decide is left
    M->>U: asks one point
    U->>M: answers
  end
  M->>O: hands over what was settled
  loop execution, until the script says the work is done
    O->>S: asks for the next step
    S-->>O: the role to start and its prompt
    O->>R: starts the role with that prompt
    R-->>O: its result
  end
  Note over O,R: hooks keep each agent to its steps
  O-->>M: the work, or questions only the user can answer
  M->>U: shows the work, or asks
```

- main talks with the user and does no work of its own.

  An agent cannot ask the user, and main's hooks cannot tell which skill it runs, and last the
  whole session once a skill has started.
- Each job is done by an agent made for it.

  An agent starts with its own steps and tools alone, and its hooks know they run in it, so it does
  the job the same way each time.
- The script decides the next step, and the orchestrator does what it prints.

  Code decides the order the same way each time.
- The hooks are in the plugin's `hooks/hooks.json`, each acting only in the agents it names.

  Claude Code reads no hooks from a plugin agent's own file.
