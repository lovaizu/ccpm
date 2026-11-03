# Turn UX

## OKRs

- O1: A person who wants a piece of work gets one that meets their purpose well, soon after asking.
  - KR1.1: The share of requested works that the person puts to use as delivered, with no change
    that they ask for or make. Higher is better.
  - KR1.2: The lead time per work from the request to delivery, the person's answers and approvals
    included. Shorter is better.

KR1.1 comes first: KR1.2 is shortened only by a change that keeps KR1.1.

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
  T->>P: I have no Standard for press releases yet.<br/>Here is a new one, what a good press release is:<br/>Goal: a reporter decides from the release whether to write about it<br/>Parts: headline, lead, body, boilerplate, contact<br/>Checklist: Can a reporter tell from the headline what is new?<br/>Can a reporter tell from the lead who launches what, and when? ...<br/>Approve?
  P->>T: Approved
  T->>P: What is this release for?
  P->>T: To get RoomBook into trade magazines
  T->>P: When is the release date? I recommend 1 December:<br/>trade magazines plan their issues weeks ahead
  P->>T: 1 December
  T->>P: Design: a headline on RoomBook's launch,<br/>with three benefits and the PR contact from RoomBook's README. Approve?
  P->>T: Approved
  T->>P: The press release, which meets every question of the Standard
```
