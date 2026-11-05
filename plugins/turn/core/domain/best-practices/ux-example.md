# Turn UX

## Roles

- **requester**: one who asks Turn for a work, such as a README, and decides what is theirs.

## OKRs

- O1: The requester gets a work they put to use as handed over, having decided only what is theirs.
  - KR1.1: Of the works the requester asks for, the share they did not put to use as handed over,
    or for which they were asked a point that was not theirs. Lower is better.
  - KR1.2: The time from the requester's request to a work they put to use. Shorter is better.

KR1.1 comes first: a change that improves KR1.2 is kept only if KR1.1 does not get worse. Key
results have no targets, as a measure made a target stops being a good measure (Goodhart's
law). They show whether a change brought its objective closer.

## Scenarios

### O1: The requester has a README made for tidy

```mermaid
sequenceDiagram
  participant R as requester
  participant T as Turn
  R->>T: a README for tidy, which sorts a Downloads folder
  T->>R: purpose: a newcomer installs tidy and sorts their folder, yes?
  R->>T: yes
  loop until no decision is open
    T->>R: found: tidy --dry-run shows what it would move, right?
    R->>T: right
    T->>R: the walkthrough runs --dry-run, then tidy, yes?
    R->>T: yes
  end
  T->>R: the design, to approve
  R->>T: yes
  opt a decision of the requester's comes up while the README is made
    T->>R: the decision, with a recommendation
    R->>T: the answer
  end
  T->>R: README.md, not committed
```

- If the run stops before the README is handed over: the requester types `/turn:up` with the
  run's folder, and Turn goes on from where it stopped, asking nothing again.
- If the requester wants the README changed: they type `/turn:up` with the run's folder and the
  change, and get the README made again with the change.
- If Turn stops on a fault of its own: the requester gets the fault, to send to Turn's makers.
