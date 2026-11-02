# Turn UX

## OKRs

- O1: A person who wants a piece of work gets one that meets their purpose well, for effort spent
  only on what only they can decide.
  - KR1.1: The share of requested works that the person puts to use as delivered, with no change
    that they ask for or make. Higher is better.
  - KR1.2: The questions per work that the person judges they did not need to decide. Fewer is
    better.
  - KR1.3: The time per work that the person spends answering questions and giving approvals.
    Shorter is better.
  - KR1.4: The time per work from the request to delivery. Shorter is better.

Where two key results of O1 move against each other:

- KR1.1 comes before KR1.2, KR1.3 and KR1.4: a work that the person cannot use as delivered is no
  gain, whatever it saved them.
- KR1.2 and KR1.3 come before KR1.4: O1 limits the person's effort, not Turn's time, so Turn does
  not save its own time with the person's.

Key results have no target values. When a measure becomes a target, it stops being a good measure
(Goodhart's law). Use the key results to judge how close the objective is.

## Scenarios

The person who wants the work is a person. Turn is an AI: a Claude Code plugin.

### O1: The person gets a press release by answering only their own points

```mermaid
sequenceDiagram
  participant P as Person (person)
  participant T as Turn (AI)
  P->>T: Write a press release for RoomBook, our new meeting-room booking app.<br/>Its README is in this repository
  T->>P: This is a press release, a document. Right?
  P->>T: Yes
  T->>T: Finds no best practice for press releases,<br/>and reads guides and examples of good ones on the web
  T->>P: Purpose: a reporter decides from the release whether to write about it<br/>Format: headline, lead, body, boilerplate, contact<br/>Checklist: Can a reporter tell from the headline what is new?<br/>Can a reporter tell from the lead who launches what, and when? ...<br/>Approve?
  P->>T: Approved
  T->>P: What is this release for?
  P->>T: To get RoomBook into trade magazines
  T->>P: When is the release date? I recommend 1 December:<br/>trade magazines plan their issues weeks ahead
  P->>T: 1 December
  T->>P: Design: a headline on RoomBook's launch, three benefits and the PR contact,<br/>both from RoomBook's README. Approve?
  P->>T: Approved
  loop until every question of the checklist is met
    T->>T: Writes the release
    T->>T: Reads it as a reporter would, against each question
  end
  T->>P: The press release
```
