# rn audit (2026-10-25, read-only, at 4b69a1d)

rn.py (1,895 lines) takes on about eight jobs; two linked files shipped and unused; some knowledge
in two or three places; about a dozen contradictions, four changing what rn does.

## 1. Size and structure

rn.py split (no import cycles):

| Module | Takes on | Functions | Lines |
|---|---|---|---|
| `stop.py` | the stop, checking values given | `Stop`, `named`, `given`, `joined` | ~40 |
| `repo.py` | git, gh, files | `ran`, `git`, `gh`, `AS_GIT_SAYS`, `at_top`, `default_branch`, `base`, `RUN_FILES`, `changed`, `at`, `push`, `pushed`, `read_text`, `write_text`, `write_json` | ~150 |
| `steering.py` | the steering's text, F-1 form, edits; no git | form constants (`TITLE`..`TICK`, `KEYS`, `VALUES`, `HEADINGS`), `keys_of`, `sections`, `trimmed`, `Item`, `items_of`, `Task`, `task_of`, `tasks_of`, `all_ticked`, `out_of_form`, `keys_out`, `body_out`, `listed`, `task_out`, `open_out`, `Steering`, `parsed`, `render`, `opened`, `tick`, `ticked`, `pruned`, `put_plan`, `decided` (merged into `items_of`, 3.5) | ~450 |
| `session.py` | the session's record on the branch | path and work constants, `session`, `current`, `*_path`, `held_form`, `kept_steering`, `keep`, `Call`, `calls`, `latest`, `next_number`, `numbered_on`, `part_of`, `moved`, `learnings_of`, `put_learnings`, `write_learnings` | ~280 |
| `ccs.py` | a work's CCS | `ENTRIES` and keys, `worked`, `own`, `checklists`, `held`, `finished_work`, `served`, `done_made`, a CCS builder out of `run_ccs` | ~170 |
| `proposal.py` | the sign-offs | `SIGNOFFS`, `WORKS_SHOWN`, `ANSWER`, `MOST`, `LONGEST`, `Shown`, `simple`, `blob`, `shown_works`, `shown_at`, `changes`, `compared`, `proposed`, `ready` | ~220 |
| `conversations.py` | Claude Code's records of the conversations | `NAME_LENGTH`, `COMMANDS`, `project_folders`, `begun`, `conversations`, `since`, `told`, `typed` (on `records.entries`) | ~100 |
| `stretch.py` | what the learnings are made from | the records place (`learning()` now), `stretch`, `history`, `session_files`, `turns_learnings` | ~110 |
| `rn.py` | the command entry | short docstring, `Parser`, `parser`, `main`, `version`, thin `run_*` | ~300 |

- `rn` uses all; `ccs`, `proposal`, `stretch` use `session`, `steering`, `repo`; `session` uses
  `repo`, `steering`, `template`; `steering` uses `template`, `stop`; `conversations` uses
  `records`, `top` and `branch` passed in.
- `run_ccs` (75 lines), `run_start` (63), `run_proposal` (53), `body_out` (49) each do several
  things. Callees far from callers: `joined` :1365 used :529, `decided` :1354 used :1227,
  `learning` :1635 used :1124. Constants mid-file: `RUN_FILES` :290, `CHANGED_TASK` :980, `Shown`
  :1410, `COMMANDS` :1579.
- `test_rn.py` (2,948 lines) splits the same way; `cosmic-ray.toml` keeps `module-path =
  rn/scripts`.

`rn/skills/up/SKILL.md` (301 lines), what to cut:
- Fixed receiver, use, kind strings (up :216-219, :249-250, :154-156; ty :63-65): rn.py defaults
  for its own works (`plan`, `deliverable`, `learnings`, `checklist-<kind>`).
- Next texts after each approval (ty :49-52, up :111, :233): `rn.py answer approved` sets Next
  from `APPROVED`.
- Decision lookup (up :124, `grep -l '"work": "<work>"' … | tail -n 1`) redoes `latest()` and
  depends on `write_json`'s indent: an rn.py subcommand prints a work's decisions.
- Session layout (up :25-33) also in rn.py :8-22 and the architecture: keep only paths the AI
  reads.

ty :16-30 and gm :91-106 copy up's Role conventions nearly word for word: keep once, point to it.

plan.md opening second paragraph (:19-37, 19 lines) restates architecture :101-112, and B-3, B-4,
B-5, B-8 say it again: cut to the idea of links each checked against the one above.

## 2. Noise

1. `rn/scripts/call.py`, `rn/scripts/forms.py` links imported by nothing in rn (trials use turn's,
   `stand.py:164`, `write.py:19`); installed on users' machines; in `cosmic-ray.toml:8-9`. Remove,
   or use `call.py` (3.1) and remove `forms.py`.
2. README :240 "and jq": nothing runs jq (rn.py :896 uses gh's `--jq`; turn README :108 asks none).
3. `dev/rn/trials/moves/moves.py:4` "on Claude Code's default model": `dev/lane/trying.py:42`
   passes `--model opus`.
4. CHANGELOG :15 "rn's own learner": none exists now.
5. rn.py docstring :1-34 restates the architecture and drifted (no research/trial results): say
   what the module does and why.
6. rn.py :1302-1309 comment restates the CCS layout (architecture :124-132) and says "turn's
   generator holds [fix] whenever it changes a work", which generator.md does not say.
7. Mixed idiom: `in (x,)` 35 times beside `==`/`!=` ~10 (:353, :518, :553, :637, :695, :805,
   :1070, :1469, :1505, :1678); reason given only at :1891-1893. One idiom, reason once.
8. `done_made` docstring :1244-1245 "a research result made before a decision among them" unclear.
9. `served` :1227-1229 computes `said` before returning `{}` for the plan.

## 3. Duplication

1. CCS reading: `entry` (:765), `decisions_of` (:808), the dict check in `calls` (:786-796) redo
   turn's `call.entries` (call.py:120), `read_ccs` (:92).
2. `lines_of` (:1658) is `records.entries` (records.py:15) without its type filter.
3. `CALL` regex (:73) spells `ccs.json|result.json|steering.md|learnings.md` beside `CCS`,
   `RESULT` (:74-75), `PART` (:87), `STEERING`/`LEARNT` (:68-69): build it from them;
   `place.py:69-70` copies again.
4. Project-folder naming re-derived in tests: `properties.py:170-173`, `test_rn.py:2525` (code.md
   B-6, expected value from the code): fixed examples.
5. Two list-item readers: `items_of`/`task_of` (:428-481) and `item`/`by_id`/`decided`
   (:1332-1362): keep one.
6. `LEARNING` (:157) and `NUMBERED` (:162) the same prefix.
7. Sign-offs listed several times: `VALUES["signoff"]` :118, `APPROVED` :120, `SIGNOFFS` :174;
   `ANSWERS` (:186) is `COMMANDS`' keys (:1579); `ANSWER` (:187) spells both commands; front
   matter keys as literals (`"signoff"`, `"pr"` at :530, :827, :880, :1544, :1615, :1628) beside
   `STAGE`, `KEYS`.
8. Session layout in four places (rn.py :8-22, up :25-33, ty :16-18 / gm :91-93, architecture
   :197-208); what a CCS holds in three (architecture :124-132, rn.py :1302-1309, turn README
   :20-33).

## 4. Inconsistency

1. USER'S DECISION: "work" means two things. One call per output makes a task's research, trial
   and document each a call on `t<n>` (up :197): `decide`/`ccs` carry the latest call's decisions
   into the next (:1152, :1294), so research decisions flow into the document's call; `shown_at`
   (:1440) shows only the latest call's paths; plan.md :161 names "two actions of turn's on the
   same work" a fault. Each output its own work name, or change the sign.
2. `session_files` (:1707-1712) gives the learnings' maker the steering, learnings, `turn/*` only;
   research and trial results in `<session>/` (up :198, architecture :203) left out, though ty
   :60-61 says "the session's files".
3. The learnings part rn cuts opens `## Learnings` (rn.py :1296; `cases.py:363`), stripped by
   `put_learnings` (:1012); learnings.md F-1 (:212) has no heading, so turn's first user checks
   F-1 against a file opening with one. Cut an empty part, or show the heading in F-1.
4. `served` (:1230-1231) gives `learnings` and `checklist-<kind>` the goal and every criterion;
   they serve no criterion of the user's work.
5. USER'S DECISION: `done_made` passes every returned call of each done task; redesign.md said "the
   latest call's CCS and result"; architecture :130 says "the calls of each done task" (= code).
6. Plan-stage tasks: plan.md :27 "that reach the criteria"; architecture :103-104, up :220-221
   "only the research or trials a gap calls for". ux.md :49 calls research a task; plan.md :31-35
   makes it an action.
7. Architecture logical view: `orch -->|adds each learning the user takes to| cl` (:50) vs up :295
   (turn makes the checklist) and :145 ("No work turn returns is fixed by the orchestrator");
   `guard` (:43) absent from the physical view; physical view (:194, :211) omits the links to
   turn's `records.py` and lane's `template.py`.
8. CHANGELOG Unreleased omits the design sign-off left out without documents (README :134, ux
   :20-21); 0.9.0 :54 "There is always a Design sign-off" stands.
9. `moved` to build (:1076-1083) counts any non-plan call at the design stage as a document, a
   research call included; architecture :119 holds the sign-off only where a document is needed.
10. Action form: plan.md F-1 two forms (:72-73); rn.py's stop text a third, `<what is done>. <who
    does it>` (:623-624).
11. One name, several things: CCS key `deliverable` (`ENTRIES`, :92) holds every work's paths,
    beside the finished work and a kind (turn README :26 leaves the key's name to the plugin);
    `learning()` (:1635) returns the folder the records are shown in; `held()` (:1195) checks a
    has-path beside `held_form` (:679); local `shown` holds commits (:1556), a `Shown` (:1558),
    (name, text) pairs (:1760).

## 5. Other

- plan.md B-8 (:175) sits between B-4 and B-5 (checklist.md F-4): renumber while unreleased.
- `properties.py:31` "an unit test".
