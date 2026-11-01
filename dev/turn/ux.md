# turn UX

## OKRs

- O1: A person who wants a piece of work spends effort only on what only they can decide, and gets a
  work that fully meets their purpose.
  - KR1.1: The changes the person asks for after delivery; fewer is better.
  - KR1.2: The times the person is asked something they did not need to decide; fewer is better.
  - KR1.3: The time the person spends answering questions and giving approvals; shorter is better.
  - KR1.4: The time from the request to delivery; shorter is better.

Key results have no target values. When a measure becomes a target, it stops being a good measure (Goodhart's law). Use the key results to judge how close the objective is.

## Scenarios

The participants are the person who wants the work; turn, a plugin; and the internet, where turn researches.

### O1: A press release for a new meeting-room booking app

```mermaid
sequenceDiagram
  participant User as Person (person)
  participant turn as turn (plugin)
  participant Web as Internet
  User->>turn: Write a press release for our new meeting-room booking app
  turn->>User: Is this a release for the press?
  User->>turn: Yes
  turn->>Web: Research how good press releases are written
  Web-->>turn: Guides and examples
  turn->>User: Format: headline, lead, body, boilerplate, contact<br/>Checklist: Can a reporter tell from the headline what is new?<br/>Can a reporter tell from the lead who starts what and when? ...<br/>Approve?
  User->>turn: Approved
  turn->>User: What is the release for?
  User->>turn: To get it into trade magazines
  turn->>User: When is the release date? I recommend the 1st of next month
  User->>turn: The 1st of next month
  turn->>User: Key points: headline, three benefits, the PR department as contact. Approve?
  User->>turn: Approved
  turn->>User: The press release
```
