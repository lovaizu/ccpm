# rn that achieves a purpose from a request alone

## Goals

- G1: Whoever wants to hand a whole piece of work to an agent asks for it without preparing anything, only answers what they are asked, and their purpose is achieved; rn 0.10.0 brings this to them.

  Work that takes days then reaches a merged result with the user called only for their own decisions, deciding each sign-off from the proposal alone and going on from the record the next day, as issue #54 says.

## Acceptance criteria

- AC1: On real requests, the user sends back few changes at the deliverable sign-off, none once G1 is reached. Serves G1.

- AC2: On the same requests, the user spends little time from asking to their purpose achieved, with AC1 no worse. Serves G1.

## Tasks

- T41: turn rebuilt on the concept and roles agreed in turn-rebuild.md. Builds on none.

  - turn's UX, README and architecture are rewritten from turn-rebuild.md and agreed by the user, each written after its kind's template, the Format and the Checklist, is remade by planner's steps and the user has approved the kind's purpose and conditions. Serves AC1 and AC2.
  - turn's code, with its comments and docstrings, is written after the code template is remade the same way, and passes its questions. Serves AC1.
  - turn is built by .claude/rules/dev.md: check.sh turn 100%, mutate.sh turn 0 survivors, and its acceptance trials passing. Serves AC1.

- T47: lane's UX, README, architecture and code comments rewritten on the templates T41 makes. Builds on T41.

  - dev/lane/ux.md, plugins/lane/README.md, dev/lane/architecture.md and the comments and docstrings of lane's code each pass their template's questions and are agreed by the user; code is changed only where the rewritten documents show it must be, added to this task then. Serves AC1.

- T48: dev/architecture.md rewritten on the architecture template T41 makes. Builds on T41.

  - It passes the architecture template's questions and is agreed by the user: it holds what every plugin follows and why, the rules of making, testing and releasing moved to .claude/rules/dev.md or to the scripts that check them, the history of how it was reached gone, and no term of its own where a common word serves. Serves AC1.

- T42: rn's meta-checklist and every checklist remade as templates that turn's planner keeps. Builds on T41.

  - Each template holds a kind's Format and Checklist in JSON, and the user approved each kind's purpose and conditions. Serves AC1.

- T46: rn remade on T41's turn. Builds on T42.

  - A request in rough words reaches the plan sign-off with the user asked only the points that are theirs, one per message. Serves AC1 and AC2.
  - The user approves each sign-off from the proposal alone, and meets at the deliverable sign-off a finished work that does every acceptance criterion. Serves AC1 and AC2.
  - The steering holds only what is left and where the session stands, replanned from each move's facts; check.sh rn 100%, mutate.sh rn 0 survivors. Serves AC1.
  - rn's UX, README, architecture and the comments and docstrings of its code pass their templates' questions. Serves AC1.

- T43: rn drops a stopped task. Builds on T46.

  - dev/rn/architecture.md says it as intent and the case is derived from it, dev/rn/ux.md agreeing. Serves AC1.

- T44: rn's checklists back under Vale. Builds on T42.

  - Once the user has merged ccpm#64, plugins/rn/checklists/ pass Vale and .vale.ini's list is shrunk. Serves AC1.

- T34: rn's acceptance test, run whole as its user does on lovaizu/playground. Builds on T46.

  - The user is stood in for by an AI holding what the user truly wants, written beforehand and not shown to rn, and AC1 and AC2 are shown from the records. Serves AC1 and AC2.

- T14: AC1 and AC2 shown on a real request of about an hour. Builds on T34.

  - A command-line tool that tidies a Downloads folder, with its README, design and tests, run once by T34's test, then tried once by the user. Serves AC1 and AC2.

- T45: nothing left that no purpose needs. Builds on T14.

  - The result's work lists no __pycache__/*.pyc, rn's README shows a Walkthrough output from a real run, and plugins/rn/hooks/adapters/items-checklist.py is used or gone. Serves AC1 and AC2.

- T15: users who update get rn 0.10.0 and turn 0.2.0. Builds on T45.

  - Released on the user's instruction. Serves AC1 and AC2.

## Where it stands

Stage: build.

Next: T41: write turn's UX (dev/turn/ux.md), its O1 and KR1.1 to KR1.4 agreed and its scenario next, from .rn/20261013-rebuild/ux.json, the ux template the user approved on 2026-10-31: OKRs with no target values, and Scenarios with one main path per objective, checked by its four questions. Then remake the readme template the same way, just before turn's README, and the architecture template just before turn's architecture (.claude/rules/dev.md: work made before a checklist changed is read against the new one).

Open:

- Whether the design-tree way of thinking, wanted for every plan, task breakdown and way of going, is kept as a skill or a rule outside the plugins (the user, 2026-10-31: not a plugin matter).
- Whether turn's way of moving a work follows the plugin architecture as it stands (turn-rebuild.md, What turn takes and gives).
