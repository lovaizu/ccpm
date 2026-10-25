# turn audit (2026-10-25, read-only, at 4b69a1d)

Checks all pass (171 tests, 100% line and branch, no duplicate code), yet four places bloated: run.py
does about six jobs in 751 lines; each reply's form is written in three places that disagree; two
Markdown readers and two readers of Claude Code's records beside lane's; documents drifted from the
code. `turn/hooks/lane` links to `lane/hooks/lane/`.

## 1. Size and structure

1. `turn/scripts/run.py` takes on about six things: the command line (`main`, `USAGE`, `shown`,
   `paged`, :59-91, :360-384); where the run's files go and what each role is given (`state_path`,
   `reply_path`, `records_folder`, `without_run_files`, `whole`, `checked_given`,
   `generator_given`, `reader_given`, :94-247); saving and loading the state (`running`, `save`,
   `write`, `going`, :387-397, :723-745); the progress lines (`DOES`, `JUDGES`, `AGAIN`, `told`,
   `judge`, `telling`, :37-57, :263-288); preparing the records for the learner (in `learn`,
   :657-667); the flow itself. Should be: `turn.py` the command line (takes `main`, `paged`; the
   8-line shim `turn.py:1-8` goes); `flow.py` the moves (the architecture's name); `state.py`
   saving, loading, resuming; `given.py` what each role is given and where its files are;
   `records.py` also writes the learner's text files. `records.split` and `PAGE`
   (`records.py:11-25`) only page what turn.py prints (`run.py:373`): move to the command line.
2. The run's stage is read from which keys the state holds, listed in three places in their own
   order: `SHOWN = ("check", "goods", "left")` (:31), the `JUDGES` dict (:45-51, whose order
   `next_step` depends on at :405), the if chain in `next_step` (:410-430). Should be one `stage`
   field and one table from stage to handler.
3. USER'S DECISION: `turn/agents/up.md` judges three things beside passing moves on: step 4 checks
   the CCS, step 5 checks the Goods by reading the whole work and running commands, step 6 words
   the questions — against base Principle 3 "Each job has a role of its own". The architecture
   (`dev/turn/architecture.md:110-116`) gives the Goods check to the orchestrator on purpose.
   Options: keep, or give step 5 to a role of its own (recommended, see 4.4).

## 2. Noise

- `forms.py:269` `for key in ("can", "good", "gets", ...)`: no form has `"gets"`; dead branch.
- `forms.py:28-34` `Grounds.work` never read; drop.
- `forms.py:179-181` `read=records.shown` exists for tests (`test_forms.py:595`); the comment
  explains a clash the code made (param `records` hides module `records`): rename, drop comment.
- `forms.py:200` `lines_problems(..., what)`: every caller passes `"lines of the work"` (:282,
  :284, :314); drop the parameter.
- `run.py:207-209` `each()` makes tuple keys; `forms.py:221` rebuilds dicts and calls `key_of`
  again: key once.
- `run.py:152-153` `if kept is None or not isinstance(result, str)` tests one condition twice.
- `call.py:63-67` a `for ... raise` loop used as "if the first"; `call.py:29` `EACH` and
  `scope in (EACH,)` (:94) repeat `SCOPES[1]`.
- No docstring (code.md F-1): `forms.span` (:75), `ground_problems` (:116), `lines_problems`
  (:200), `value_problems` (:267), `within_part` (:329), `records.shown` (:28), `records.write`;
  `records.WIDTH` mid-file (:59).
- `forms.py` form constants split (:20-21, :51-61, :145-147): one block.
- Comments telling how the work went: architecture.md:102-103 "since an edit told per item broke
  other items"; judge.py:5-6; test_forms.py:670 "as before".
- `shared.py:212` still ignores `.turn`, gone per the CHANGELOG.
- `trials/*/results.json` unexplained in `dev/turn/README.md`, quoting parts that no longer exist
  ("hand-on", "evaluator", "forms.py:220 ... "ran": []"): explain as records or leave to git.
- `hooks.json:5` matcher `".*|Bash|Write|..."`: all after `.*` pointless; lane:up's output, fix in
  lane.

## 3. Duplication

1. Each reply's form in three places: `turn/forms/*.json` (loose: `claim.json` requires only
   `checklist`, `item`); `forms.py` `CLAIM`/`FIRST_READING`/`LEARNT` and `WHOSE` (:25, repeats
   `learnt.json`'s enum); agents' prose (generator.md:58-70, first-user.md:117-128,
   learner.md:163-167). The orchestrator's `CHECK`, `HELD`, `LEFT` have no form file (forms.py and
   up.md:69-98 only). prompt.md: "its form is kept in a form file; the prompt names each of these
   files and does not say what they hold again". Should be: one full JSON Schema per reply, the
   orchestrator's three included; agents name the file only; forms.py keeps only what a schema
   cannot say (lines in the work, parts, quotes found in the records).
2. Markdown read three ways: `call.items` (call.py:139-142) and `forms.parts` (forms.py:345-352)
   track ``` fences only; lane's `template.headings` (lane/hooks/lane/template.py:31, :116)
   handles ``` and `~~~` and indented headings, and rn uses it by a link. Should be: turn links
   lane's `template` too.
3. Claude Code's records read twice: `records.find` (records.py:254-258) and `records.entries` vs
   lane's `record.path`/`entries`/`content`/`blocks` (lane/hooks/lane/record.py:50-95, "as Claude
   Code 2.1.306 writes it"). Should be one reader, in lane, linked into turn.
4. How an item is named, four times: `run.named` (:713), `forms.key_of` (:254), `helpers.named`
   (tests :322), the dict in `call.check` (:93). Keep one, in forms.
5. Instructions repeated in the agents: "run each command ... compare what it prints ... try each
   thing ... look up each file and link ... `mktemp -d`" at up.md:77-81, generator.md:50-53,
   first-user.md:103-105 and :114-116; Scope definitions at up.md:28-31, generator.md:30-34,
   first-user.md:107-112 beside `call.SCOPES`. Once per prompt.
6. generator.md:48-49 "`<result>` being `reply` without its last `.generator.json`" repeats
   `run.reply_path` (:101): give the generator the `parts` command or its result in its prompt, as
   `reader_given` does.
7. `roles.py:68-75` copies `forms.check(...)`'s arguments of `run.replied` (:451-458): factor out
   `run.reply_problems(run, agent, text)`.
8. `rn/scripts/forms.py` and `rn/scripts/call.py` link into turn but nothing shipped in rn uses
   them (rn.py imports only `records`, `template`; rn's learner and forms removed in dc45717); only
   rn's trials import `call`. rn ships ~560 unneeded lines; `dev/rn/cosmic-ray.toml:8-9` excludes
   them. Remove both links; rn's trials put `turn/scripts` on their path.

## 4. Inconsistency

1. README:62-65 shows "generator: will write README.md for the seven items, as MIT licensed, ...";
   `run.telling` (:283-286) prints "turn: … Next, turn:generator will make the work to give every
   item its Good, …, of README.md, for 7 items, round 1." (readme.md B-4, B-8). Show the real line.
2. README:100-101, architecture.md:34-35, ux.md:279 "with the same result"; `run.start` (:156-160)
   needs the same call, as CHANGELOG:154 and up.md:3 say. Say "same call" everywhere.
3. CHANGELOG:148 promises per item "its Good …, the question it waits on, or what the receiver gets
   once it has it and where it was not found"; the result is written only once every item has its
   Good (`ended` :622, `taught` :680-688). Rewrite.
4. USER'S DECISION (same as 1.3): architecture.md:104-109 (and up.md:21-23) say the orchestrator
   does not read the work ("its own reading there finds the Good the work meant"); :110-112 and
   up.md step 5 have it "Read the work whole" to check each Good.
5. "Principle 1" names two things: architecture.md:11-24 base "Principle 1 to 8", then turn's own
   1 and 2; "(Principle 1)" at :115 ambiguous. Label turn's own otherwise (rn uses "rn's
   Principle").
6. architecture.md:146-147 file tree: "`turn.py` the flow", "`*.py` … the parts"; the flow is in
   run.py, the parts in forms.py. The split in 1.1 makes it true.
7. One name for many things: `EACH` "each part" in call.py:29 but `("parts",)` in forms.py:21;
   `shown` a state key (call.py:96), a function in records.py:28 and run.py:360, `SHOWN` in
   run.py:31; `kept` a records folder (records.py:247), `KEPT`, locals; `run["records"]` holds
   agent IDs, `run["learnt"]` record paths (run.py:465, :659, :456); turn's `call.py`/`forms.py`
   share names with lane's (turn's cosmic-ray.toml:7-10 works around it). Rename turn's (e.g.
   `asked.py`, `replies.py`).
8. `dev/turn/README.md:5-9` stale: "`one` for the Flow trial" (no Flow scene; `trials/flow/flow.py`
   is it); leaves out `roles/roles.py`, `roles/kept.py`.
9. `shared.py:1-5` says it holds the flow trial's task with its check and a failing README; `CHECK`
   and `UNLICENSED` are used only by the role trials.
10. `plugin.json` description omits that turn is called from a plugin's step (README:7-8).

## 5. Other

- Prompts say a hook's sentence beside their own words for it: generator.md:27-29 "Read each file
  of `given` whole …" then "Read only `{given}`. Read `{given}` to its end."; also
  first-user.md:100-106, learner.md:157-159 (prompt.md B-4). The `{…}` sentences are lane's,
  checked word for word by `test_lanes.py:41-47`: drop the step's own wording.
- Line breaks from patched edits: README:5 cut short ("such as whether"); architecture.md:111
  (119 chars), up.md:99 (121), trial.py:43 too long.
- README "Why turn" first item (:92-96) repeats the opening (:8-10) (readme.md B-7).
