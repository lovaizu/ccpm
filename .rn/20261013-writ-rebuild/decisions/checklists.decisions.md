# What rn makes and judges, and the checklist of each

The map T24 rests on (`.rn/20261013-writ-rebuild/steering.md:121`): each thing rn makes or judges,
who receives it and for what, when it is made and judged, and which of rn's checklists holds its
items. `rn/checklists/checklist.md` is then written to tell, from this map, where each item goes.

Sources, cited as `<key>:<line>`: D `dev/rn/design.md`, U `dev/rn/ux.md`, R `rn/README.md`, and
each checklist by its path under `rn/checklists/`.

## The map

The first sixteen rows are the works D:4 and D:100 name, their parts, and what the lessons bring
(D:143-147); the rest are what rn keeps, shows or reads along the way.

| Work | Receiver, and for what | Made | Judged, when and by whom | Checklist |
|---|---|---|---|---|
| Plan's goal `G1` | The user, to approve a purpose they recognize as theirs (session/plan.md:8-10, 89-97); the conductor and turn later, to judge each move by it (session/plan.md:10-13) | From the points confirmed, before the plan sign-off (D:70-72, D:118) | First reader, then the conductor reads each Good (D:96-98, D:106); the user at the plan sign-off (D:25-27); a later change is a point to confirm (D:116-117) | session/plan.md |
| Acceptance criteria | The user, to approve; turn, making each result for them; the maker, using the finished work for each (session/plan.md:147-149, D:141) | With the goal (D:17-19, session/plan.md:25-26) | As the goal | session/plan.md |
| Plan's list of documents | The conductor, to have each made (D:133-135) | After the plan sign-off, settled with the user as a point (D:133) | Unsettled: D:133-135 has the user answer the point, and names no other judge | session/plan.md, F-1 only (session/plan.md:64-66) |
| Tasks | turn, making each result in one run; the conductor, accepting it by its criteria (session/plan.md:147-149, 186-187) | After the design sign-off, written by the conductor (D:136-138); a lacking checklist or environment becomes a task first (D:112-113) | Unsettled: the conductor writes them, not the maker (D:136), so no first reader, and no sign-off follows (D:25-27) | session/plan.md |
| UX | Whoever builds the product, to build it to the experience (product/ux.md:8-9) | First of the documents, after the plan sign-off (D:133-135) | First reader and the conductor (D:96-98, D:106); the user at the design sign-off (D:26-27) | product/ux.md, usability.md |
| README | Someone meeting the product, to decide and reach a first result (product/readme.md:8-10) | Second of the documents (D:134); its second stage, once built (product/readme.md:10-12, 25-31), is unsettled: D:133-135 has no such time | As the UX | product/readme.md, usability.md |
| Design | Whoever builds or changes the product, to build it to the mechanism (product/design.md:8-10) | Third of the documents (D:134-135) | As the UX | product/design.md, usability.md |
| Another document the purpose needs | Unsettled: D:133 and U:20 say only "such as" | After the plan sign-off (D:133) | As the UX | None in rn; the user's addition, made to checklist.md (D:102-103) |
| A task's result | Unsettled: D:137-138 says it is "used for those criteria" and names no receiver | During the tasks, by the maker (D:137) | First reader, for its criteria (D:96-98, D:137-138); the conductor accepts and ticks it (session/plan.md:30-31) | The checklist of its kind, below, or the user's addition |
| Code | Whoever runs it, for its behavior; whoever maintains it, to change it with trust (product/code.md:8-10) | As a task's result (R:152-153 names code as a kind) | As a task's result | product/code.md, usability.md |
| Prompt, a skill or an agent | An AI, to achieve its purpose from it alone (product/prompt.md:8-10) | Unsettled: D, U and R name no prompt; only product/prompt.md:8 does | As a task's result | product/prompt.md, usability.md |
| Finished work | The user, using it for every criterion (D:141-142, U:21) | When the tasks are done (D:141) | The maker uses it as the user would, for each criterion (D:141-142); the user at the deliverable sign-off (D:26-27) | The checklists of its kinds (U:85-86); none for the whole, where the criteria are the measure (session/plan.md:108-110) |
| The user's checklist for a kind | Whoever makes or judges a work of the kind (checklist.md:8-10): turn and its first reader, through the CCS (D:189-192) | As a task, before the task that needs it, for a kind rn has none for (D:102-103, D:112-113) | As a task's result (D:100) | checklist.md, usability.md (checklist.md:25-27) |
| An addition to the user's checklists | As the checklist it goes into | After the deliverable sign-off, on the user's answer to a lesson (D:143-147) | The user decides where it goes (U:165, U:173); its content: unsettled, D:143-147 names no first reader | checklist.md for an item's shape (checklist.md:31-67); which checklist it goes into: none yet |
| Lesson | The user, to decide where it goes (U:163-166, R:154-156) | Returned by the maker with each work (D:63, D:104-105), kept as it comes (D:149-150) | The user, one per message, after the deliverable sign-off, with the conductor's recommendation (D:143-146, U:170-173) | None yet |
| Issue to rn's makers | rn's makers, to make rn better for every user (U:171-173) | After the user's yes, with `gh` on `lovaizu/ccpm` (D:145-146, D:216-217, R:174) | The user decides whether it goes (U:173); its content: unsettled | None yet |
| Decisions of a work | The maker, making the work from them (D:61, D:96); the next conversation, going on from them (D:89) | After each answer, before the work that follows (D:81-82) | A guard stops a work begun before its decision is kept (D:92); the trials read each decision against the answer (D:246) | None yet |
| CCS, `ccs/<work>.json` | turn's `turn:up`, to make the work (D:189-192) | By rn's script, before each work is made (D:202-203) | The script's tests (D:231-234) | None yet |
| `state.json` | The conductor in the next conversation, to go on (D:84-86, D:152-153) | Whole, after each move (D:85, D:110-111) | The script's tests (D:231); the trials, on resting only on the move's facts (D:246-247) | None yet |
| Message of the points to decide | The user, to answer one point (D:74-77, U:116-120) | By the conductor, while asking and whenever a point comes up (D:70-72, D:140) | The trials, on its form (D:245-246) | None yet |
| Proposal | The user, to decide at a sign-off from it alone (D:122-127, U:76-82) | By rn's script, from turn's result and the record (D:126, D:203) | The user at the sign-off; the trials, on saying only what the result and record hold (D:247-248); the conductor makes the work again where its core decisions do not fit a few lines (U:81-82) | None yet |
| Commit messages | The user or a teammate later, for why each decision was taken (U:83-84, U:189-190, R:209-211) | By the conductor, at each commit (D:209-210) | Unsettled: no source names a judge | None yet |
| Pull request | The user, to see every work and merge (D:120-121) | Opened with the plan, marked ready after the lessons (D:118, D:146-147) | The user, by merging (D:151) | None yet; its description is unsettled, no source says what it holds |
| turn's result: each item's Good with its lines, questions, lessons | The conductor, to judge the work and put the proposal together (D:104-109) | By turn, with each work (D:63, D:192) | The conductor reads each Good at its lines (D:106-107, D:194-195) | None in rn; turn is checked by its own design (D:253) |

## Works with no checklist

- Plan's list of documents: only the template's line holds it; no item asks whether the list fits
  the purpose.
- Another document the purpose needs: by design (D:102-103), the user's addition is the whole
  checklist.
- Finished work as a whole: the criteria are its measure; whether a checklist should hold more is
  unsettled.
- Lesson: nothing asks what a lesson must give the user to decide where it goes.
- Issue to rn's makers: only `.claude/rules/plugin.md:45-46` gives a point (the need alone, nothing
  of the user's project), and that file is the builders' rule, not rn's checklist.
- Placing an addition: which checklist an item goes into is what T24 is to settle.
- Decisions of a work: the maker and the next conversation rest on them, and no checklist says
  what they hold.
- CCS, `state.json`, proposal: made by rn's scripts, checked by their tests (D:231), so they may
  need none.
- Message of the points, commit messages, pull request: the user reads each, and only the design's
  prose or the trials say what they hold.
- turn's result: judged under turn's design, not rn's checklists.

## Checklists that serve no work in the map

- None wholly. Two serve a work only in part:
- product/prompt.md: its work is named by no source of rn's flow (D, U, R); it serves only a
  task's result that happens to be a prompt.
- product/readme.md steps 5-7 (product/readme.md:25-31) and the items drawn from them, B-5, B-8,
  B-6, B-7: they are answered once the product is built, and rn's flow makes the README only
  before the design (D:133-135).

## Items that may belong to another work, to judge with checklist.md

- session/plan.md B-4 (session/plan.md:125-133): answered in the plan's decisions, not the plan;
  it asks what the decisions hold.
- session/plan.md step 5's last sentence (session/plan.md:31-32), not an item: it says what
  `state.json` holds.
- product/code.md B-24 (product/code.md:325-335): answered on each README and guide, for their
  readers, not the code's.
- product/prompt.md B-19 (product/prompt.md:195-205): its receiver is the user, and it is answered
  on scripts and hooks.
- product/prompt.md B-17, B-25, B-26 (product/prompt.md:184-193, 317-345): answered on scripts and
  hooks, which are code.
- product/prompt.md B-27 (product/prompt.md:130-141): serves the hooks that read the AI's tool
  calls, not the AI that reads the prompt.
