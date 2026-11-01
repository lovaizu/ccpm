# rn UX

## OKRs

- O1: A person who wants to hand a whole piece of work to an agent, even work of days, asks for it
  in rough words without preparing anything, only answers what they are asked, and their purpose is
  achieved.
  - KR1.1: The changes the person sends back at the sign-off on the finished work. Fewer is better,
    and none once O1 is reached.
  - KR1.2: The time the person spends from asking to their purpose achieved. Shorter is better, and
    once O1 is reached only the time spent answering is left.

KR1.1 comes before KR1.2: time saved on a finished work that misses the purpose is lost when it is
made again.

Key results have no target values. When a measure becomes a target, it stops being a good measure
(Goodhart's law). Use the key results to judge how close the objective is.

## Scenarios

The person is a person. rn is an AI: a Claude Code plugin that works in the person's conversation.
A sign-off is a stop where rn shows a proposal and waits: the person types `/rn:ty` to approve it,
or `/rn:gm <feedback>` to ask for a change.

### O1: From a request in rough words to a merged pull request

```mermaid
sequenceDiagram
  participant U as person (person)
  participant R as rn (AI)
  U->>R: /rn:up <what they want>
  loop one message per point to decide
    R->>U: the point, with what rn looked up and the answer it recommends
    U->>R: an answer
  end
  R->>U: the goal and the acceptance criteria, on a draft pull request
  U->>R: /rn:ty
  opt the purpose needs documents of what the person gets, or of how it is built
    R->>U: links to the documents, and each choice made without asking, with why
    U->>R: /rn:ty
  end
  opt the work takes days, and the person comes back another day
    U->>R: /rn:up, in a new conversation
    R->>U: the sign-off still waiting, or the next point to decide, asking nothing again
  end
  R->>U: the finished work, and each choice made without asking, with why
  U->>R: /rn:ty
  loop one message per learning
    R->>U: what the work taught, and where it would help later work
    U->>R: a question for that kind's checklist, an issue to rn's makers, or neither
  end
  R-->>U: the pull request marked ready
  Note over U: merges
```
