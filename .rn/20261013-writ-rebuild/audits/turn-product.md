# turn audit: the product and its documents (read-only, at c537dc3)

Scope: every file under `turn/` and the four files of `dev/turn/` outside `tests/` and `trials/`.
`python3 -m unittest discover -s dev/turn/tests`: 171 tests OK in 0.2 s; `ruff check` and
`ruff format --check` on `turn/scripts`: clean. One defect reproduced by running `turn.py start` (F1). 95 findings (F1, F3-F96; no F2).
"(D1)" marks a place the decision "only the first user looks for Good; the orchestrator's Good check
goes" touches; "(D4)" the `x in ("a",)` → `==` decision.

## Findings

### turn/scripts/call.py

- F1 `call.py:49-51` `for key in ("ccs", "kind", "result"): if key not in call` checks only that
  each key is present, not its type; `"result": 5` dies in `run.save` with `TypeError: unsupported
  operand type(s) for +: 'int' and 'str'`, `"ccs": ["x"]` in `read_ccs` with `TypeError: stat:
  path should be string` (both reproduced). defect, code.md B-2. Stop with `SHAPE` when `ccs` or
  `result` is not a non-empty string.
- F3 `call.py:131-134` `if line.startswith("```"): fenced = not fenced` (and the same at
  `forms.py:345-348`): only backtick fences at column 0; an item heading inside a `~~~` fence or an
  indented fence is taken as an item. defect + duplication, code.md B-5. Use lane's
  `template.headings` (`lane/hooks/lane/template.py:116`) through the link rn already takes.
- F4 `call.py:21` `EACH = "each part"` repeats `SCOPES[1]`, and `:86` `scope in (EACH,)`. noise,
  B-4 / (D4). `scope == "each part"` from `SCOPES`, drop `EACH`.
- F5 `call.py:55-59` `for name in sorted(set(kind) - set(KINDS)): raise Stop(...)`: a loop used as
  "if any, the first". complexity, B-3. `unknown = sorted(...); if unknown: raise`, as `:43-48`
  already does for the call's keys.
- F6 `call.py:39-89` `check` takes on four things: the call's shape, reading the CCS's kinds, the
  files being there, and laying out the run (`items`, `each`, `given`, `shown`). complexity, B-5.
  Split the call's check from the run's layout (see Structure).
- F7 `call.py:85-86` builds `{"checklist", "item"}` dicts that `run.named` (`run.py:713`) and
  `forms.key_of` (`forms.py:254`) build again. duplication, B-5. One item-naming function, in forms.

### turn/scripts/run.py

- F8 `run.py:1-751` takes on six things: the command line (`main`, `USAGE`, `shown`, `paged`,
  :59-91, :360-384), the run's files and what each role is given (:94-247), the state (`running`,
  `save`, `write`, `going`, :387-397, :723-745), the progress lines (`DOES`, `JUDGES`, `AGAIN`,
  `told`, `judge`, `telling`, :37-57, :263-288), the learner's record texts (`learn` :657-667) and
  the moves. complexity, B-5. Split as Structure says.
- F9 (D1) `run.py:31` `SHOWN = ("check", "goods", "left")`, `:48` `JUDGES["goods"]`, `:421-422`
  the `goods` branch, `:589-599` `first_read` (keeps `run["read"]` only for the check),
  `:602-615` `goods_checked`. Goes: `first_read` becomes `ended(run, goods, stops)` once the sends
  are spent; `run["read"]` goes with it.
- F10 `run.py:31`, `:45-51`, `:405`, `:410-430`: the run's stage is read from which keys the state
  holds, in three lists in their own order (`next_step` depends on `JUDGES`'s order at :405).
  complexity, B-5. One `stage` field and one table from stage to handler.
- F11 `run.py:45-51` `JUDGES` holds `"ask"` ("ask what only the user can decide") and `"returned"`
  ("return the result"), which are not judgments. inconsistency, B-3. Name it for what it is, the
  orchestrator's own moves.
- F12 `run.py:250` `def ask(...)` starts or messages a role, while `run["ask"]` (:412, :507) is
  the questions to put to the calling AI; `start`'s local `asked` (:150) is the call, `run["asked"]`
  the questions asked. one name for two things, B-5. Rename the function (e.g. `due`) and the local
  (`given_call`).
- F13 `run.py:139` `whole(paths)` means "absolute paths", beside `Scope: whole` and "read whole" in
  every prompt. one name for two things, B-5 / usability B-14. Rename (`absolute`).
- F14 `run.py:245`, `:579` and `parts` (:336) give the parts as `forms.parts(run["work"])`,
  relative to the call's folder, while every other path a role is given is absolute (`:225-229`,
  `:240-246`, `:578`), as `CHANGELOG.md:29` promises ("each AI of the run is given its files as
  whole paths"). inconsistency, B-5. Give the parts of `whole(run["work"])`.
- F15 `run.py:152-153` `kept = running(result) if isinstance(result, str) else None` then `if kept
  is None or not isinstance(result, str)`: the second test is the first again. noise, B-4. Goes with
  F1.
- F16 `run.py:207-209` `each()` turns `run["each"]` into key tuples; `forms.py:221` turns them back
  into dicts and calls `key_of` again. complexity, B-4. Pass the items, key once in forms.
- F17 `run.py:355` `if step in ("check",):` (D4). `==`.
- F18 `run.py:263-277` two `told` flags, `run["told"]` (a judgment told) and `step["told"]` (a role
  told), set and popped in `told`, `judge`, `next_step:414`, `resumed:202`. complexity, B-3. Goes
  with the single `stage` of F10.
- F19 `run.py:291-307` `moved` saves twice (:298, :302) around appending `since`. complexity, B-4.
  Save once after both.
- F20 `run.py:387-397` `going` also `os.chdir`s to the run's root; the name says only that it reads
  the run. B-3. Say it in the name or the docstring's first words, or chdir in `main`.
- F21 `run.py:354`, `:376` locals `shown` shadow the function `shown` (:360); `SHOWN`,
  `run["shown"]` (`call.py:88`) and `records.shown` are four more things of that name.
  inconsistency, B-5. Rename the state key (`reader_has`) and the records function (`as_text`).
- F22 `run.py:465` `run["records"]` holds agent IDs, `run["learnt"]` (:659) record paths, `KEPT`
  (:23) roles kept started, `records.kept()` the records folder, locals `kept` three other things.
  one name for many things, B-5. Rename (`agent_ids`, `record_paths`, `KEPT_STARTED`,
  `records.folder`).
- F23 `run.py:286` "for {len(run['items'])} items" prints "for 1 items" (seen). noise, B-3.
- F24 `run.py:166`/`:169-173` `start` prints `given` once, and the lane `4:read_whole:{given}`
  (`hooks.json:10`) takes `{given}` from that print (`lane/hooks/lane/started.py:1-6`); after an
  answer lays the run out anew, `judged` (:351-357) shows a new `given` "as an answer may name
  more", which the lane never sees. inconsistency, B-5 / prompt.md B-3. Have `turn.py next` print
  the new `given` as JSON the lane reads too, or say the lane holds only the first list.
- F25 `run.py:212`, `:250`, `:618`, `:631` `sent_back: list`, `-> dict`, `goods: list`: bare types
  where the rest of the file writes `dict[str, Any]`. B-3. Same form throughout.
- F26 `run.py:738` `write` has no docstring. F-1.

### turn/scripts/forms.py

- F27 (D1) `forms.py:57-59` `HELD`, `:276-280` the `"holds"` branch. Go.
- F28 `forms.py:37-47`, `:85-147`, `:172-197`: the learner's form is fitted into `Form` by
  `shapes=()`, `more=lessons` and `Grounds`; `check` takes seven parameters, three of them
  (`records`, `each`, `read`) for one form each, and its "not JSON" message hard-codes the
  learner's shape (:190 `'"lessons": [...], "checked": "..."'`). complexity, B-5. A `lessons_check`
  of its own for the learner; `check` for item forms only.
- F29 `forms.py:32` `Grounds.work` is never read. noise, B-4. Drop (or drop `Grounds` with F28).
- F30 `forms.py:269` `for key in ("can", "good", "gets", "did", "lacking")`: no form has `"gets"`.
  noise, B-4. Drop it.
- F31 `forms.py:200` `lines_problems(..., what)`: all three callers (:282, :284, :314) pass
  `"lines of the work"`. B-4. Drop the parameter.
- F32 `forms.py:177-181` the parameter `records` hides the module `records`, and a comment explains
  the clash; `read=records.shown` serves only a test. noise, B-3. Rename the parameter, drop the
  comment.
- F33 `forms.py:75-82` `span` and `:358-366` `in_files` each parse `<path>:<from>-<to>` with
  `LINES`. duplication, B-5. One parse, used by both.
- F34 `forms.py:25` `WHOSE = ("own", "general")` repeats `forms/learnt.json:22-25`. duplication,
  B-5. Held by the schema through lane's `in_form`; drop here (or with F28).
- F35 `forms.py:14-25`, `:49-61`, `:143-147`: the form constants in three blocks between functions.
  B-3. One block.
- F36 No docstring: `span` (:75), `ground_problems` (:116), `lines_problems` (:200),
  `value_problems` (:267), `within_part` (:329). F-1.

### turn/scripts/records.py

- F37 `records.py:15-20` `entries` runs `json.loads` on every line with no guard; one line that is
  not JSON, such as one half written in the orchestrator's own record, still being written while
  `learn` runs (`run.py:657-658`, `names` :110), ends `turn.py next` in a traceback, as `main`
  catches only `call.Stop`. lane's `record.entries` (`lane/hooks/lane/record.py:59-79`) skips such a
  line. defect + duplication, code.md B-2, B-5. Read through lane's `record`.
- F38 `records.py:81-85`, `:100-107`: the record's place (`<conversation>/subagents/agent-<ID>.jsonl`),
  `agentType` in `.meta.json`, the entry types, and `edited_text_file` attachments are Claude Code's
  undocumented layout, with no version named; lane's `record.py:5-6` says "read as Claude Code
  2.1.306 writes it". B-3, B-5. Keep the layout once, in lane, with its version.
- F39 `records.py:11-12` "A page of a record is short enough for one read to show it whole" and
  `split` (:23): nothing pages a record; `split` pages what `turn.py` prints (`run.py:373`).
  inconsistency, B-3 / B-5. Move `PAGE`/`split` to the command line and say what they page.
- F40 `records.py:28` `shown` has no docstring; `:60` `WIDTH` stands mid-file. F-1, B-3.
- F41 `records.py:74` `kept()` names the folder of Claude Code's records by a word used for three
  other things (F22). B-3.

### turn/scripts/turn.py

- F42 `turn.py:1-8` an 8-line shim whose only job is to give `run.py` the name the prompts and lanes
  use. complexity, B-4. Make the command-line module itself `turn.py` (F8).

### turn/agents/up.md

- F43 (D1) `up.md:3` "and each Good checked by running what it says"; `:23-24` "Once the first
  user's reading ends, you check each Good it gave ..."; `:55` `{"goods": [...]}`: go to step 5;
  `:75-91` step 5. Go; steps 6-7 become 5-6, so `hooks.json:10` `'7:as_printed:...'` and `:52`
  `'7:as_printed:...'` become `6:`.
- F44 (D1) `up.md:26-31` "You look only for each item's Good, judged by what the receiver gets ...
  never by whether the work matches its sources" and the definition of `each part`'s parts: once
  step 5 goes, the orchestrator reads no work, and only step 4 uses `Scope`. noise, prompt.md B-4.
  Keep the `Scope` words step 4 needs; the part definition (which `forms.parts` holds) goes.
- F45 `up.md:38-44` step 1 takes on the `turn.py` alias, the start, its output, the exit, how
  stdin is handed, and calls made one at a time. complexity, prompt.md B-3. Put the alias and the
  stdin convention in the Role or their own step; step 1 only starts.
- F46 `up.md:59-62` "Read each file of the `given` ... whole, each with `cat -n` ... Read `{given}`
  to its end.": the step's own words beside the lane's sentence for the same thing. prompt.md B-4.
  Keep the lane's sentence and only what it does not say (a folder: `ls`, then the files the
  receiver would use).
- F47 `up.md:3` description, 654 characters, and its "Use when ..." last. prompt.md B-1. Shorten to
  what it achieves and when, the Good check gone.
- F48 `up.md:99` 121 characters, unlike the 100-column wrap of the rest. usability B-19 (patched
  edit). Rewrap.
- F49 No lane holds "the orchestrator reads no work" (`dev/turn/architecture.md:104`): `turn:up`
  has no `read_only` (`hooks.json:10`). prompt.md B-3 "a bound ... held by no hook". After D1,
  consider `4:read_only:{given}`, if lane applies it to the whole agent; else say why none.

### turn/agents/generator.md

- F50 `generator.md:27-29` "Read each file of `given` whole, each with `cat -n` ..." then "Read only
  `{given}`. Read `{given}` to its end."; `:44` "Write only `{work}` or `{reply}`." beside step 4's
  own words. prompt.md B-4. The lane sentences alone, plus what they do not say.
- F51 `generator.md:58-70` the claim's shape in prose beside "in the form of
  `${CLAUDE_PLUGIN_ROOT}/forms/claim.json`" (:64); the form file holds only `checklist`/`item`
  required. duplication, prompt.md B-4. Make `claim.json` the whole form (`anyOf` of the three item
  shapes, `additionalProperties: false`, which lane's `schema.py:1-9` reads); the step names the file
  only; read_only already lets the role read its form (`lane/hooks/lane/lanes/read_only.py:3-4`).
- F52 `generator.md:48-49` "`<result>` being `reply` without its last `.generator.json`" repeats
  `run.reply_path` (`run.py:99-101`). duplication, prompt.md B-4. Give the full `parts` command in
  the prompt, as `reader_given` gives `parts`.
- F53 `generator.md:45-57` step 5 takes on re-reading, parts, running what the work tells, a
  missing file and a user's point. complexity, prompt.md B-3. Split check (read/run) from what
  waits on a question.
- F54 `generator.md:30-34`, `first-user.md:31-36`, `up.md:28-31`, `README.md:17-18`: the three
  `Scope` values defined four times; `generator.md:51-54`, `first-user.md:24-29`, `:37-40`,
  `up.md:76-81`: "run each command ... `mktemp -d` that the command removes" four times, twice in
  first-user. duplication, prompt.md B-4. Once per prompt (first-user step 4: "as in step 2").

### turn/agents/first-user.md

- F55 (D1) `first-user.md:15` "turn's orchestrator checks each Good you hand back." Goes.
- F56 `first-user.md:24-30` the step's own read-whole words beside "Read only `{given}`. Read
  `{given}` to its end."; `:44` "Write only `{reply}`." prompt.md B-4. As F50.
- F57 `first-user.md:41-52` the reading's shape in prose; `forms/reading.json` holds only
  `checklist`/`item`. duplication, prompt.md B-4. As F51.

### turn/agents/learner.md

- F58 (D1) `learner.md:12` "the orchestrator passed the moves of turn's flow and checked each Good".
  "and checked each Good" goes.
- F59 `learner.md:29-33` the lesson's shape in prose, all of it already in `forms/learnt.json`.
  duplication, prompt.md B-4. Name the file only.
- F60 `learner.md:23-25` "Read each file of `given` whole with Read, page by page ..." beside the
  two lane sentences. prompt.md B-4. Keep "page by page" alone beside them.

### turn/forms/*.json

- F61 `claim.json:23-36`, `reading.json:22-36` require only `checklist`, `item`, with no item shapes
  and no `additionalProperties: false`, so lane's `in_form` passes any item. inconsistency with what
  each agent's step says, prompt.md B-3. Whole forms (F51, F57).
- F62 The orchestrator's three forms (`CHECK`, `LEFT`, and `HELD` until D1) have no form file and
  are written in `up.md:69-74`, `:95-98` and `forms.py:54-61`. duplication, B-5. With `HELD` gone,
  either add `forms/check.json`/`left.json` for `forms.py` to read, or accept the prose (they come
  on stdin, which no lane holds); say which.

### turn/hooks/hooks.json

- F63 (D1) `hooks.json:10`, `:52` `'7:as_printed:turn.py questions'`: the step becomes 6 (F43).
- F64 `hooks.json:5` matcher `".*|Bash|Write|Edit|NotebookEdit|Agent|SendMessage"`: everything after
  `.*` matches nothing more. noise. lane:up's output; fix in lane (Cross-slice).
- F65 `hooks.json:10-50` `turn:learner` has no `hands_off` and `turn:up` no `read_only`/`write_only`,
  while `CHANGELOG.md:12` promises "Each AI of a run that reads beyond what your CCS gives it, writes
  beyond the work or its reply, or runs `git commit` or `git push`, is told its step again".
  inconsistency, usability B-21. Narrow the line to the roles, or lay the lanes.
- F66 The Python-version prelude is written out eight times, identical but for the agent and exit
  code. duplication; lane:up's output (Cross-slice).

### turn/README.md

- F67 (D1) `README.md:9-10` "and each Good it finds checked against what the work does"; `:67-70`
  "gets its Good ... only where `turn:up`, running what the Good says, also finds it holds";
  `:92-93` "each Good it finds is then run against what the work does". Go: the first user runs
  what the work tells (`first-user.md:37-40`), which is what to say.
- F68 `README.md:62-65` shows `generator: will write README.md for the seven items, as MIT
  licensed, ...`; `run.telling` (`run.py:285-286`) prints `turn: <done> Next, turn:generator will
  make the work to give every item its Good, and run what it gives as the receiver would, of
  README.md, for 7 items, round 1.` inconsistency, readme.md B-4, B-8. Show the real line.
- F69 `README.md:100-101` "calls turn again with the same result"; `run.start` (`run.py:156-160`)
  stops on another call with the same result. inconsistency, readme.md B-8. "the same call", as
  `CHANGELOG.md:17` and `up.md:3`.
- F70 `README.md:3-6` the opening's first sentence carries the mechanism ("what a machine can judge,
  such as whether / a reply has its form ... is checked by turn's scripts, not by an agent") and a
  line cut short at :5. readme.md B-1, usability B-19. Keep the idea and the gain; the scripts'
  checks belong to Why, if anywhere; rewrap.
- F71 `README.md:92-96` Why's first item says again the opening's `:8-10` ("read first by an AI
  that did not make it, in the place of its reader"). readme.md B-7. Say it once.
- F72 `README.md:100-103` "A run stopped anywhere ... goes on": the kind of benefit readme.md B-3
  names ("not losing work"). readme.md B-3. Drop from Why (it stays in the CHANGELOG).
- F73 `README.md:20`, `:50`, `:57` "the step's AI" and `:90` "your plugin's AI": two names for one.
  readme.md B-8. One name.
- F74 `README.md:77-80` the result shown without `work` and `checked`, which `run.taught`
  (`run.py:683-686`) writes, and with `"lines": ["README.md:3-4"]` where the first user, given
  absolute paths, likely names absolute ones; and `:78` "for CSV files" with no word before that the
  project is a CSV tool. readme.md B-2, B-4, B-6. Show the keys the result has and a project the
  example has introduced.
- F75 `README.md:108-111` git as a requirement, "a run cut off leaves its writing as changes git
  shows": turn runs no git; it is a convenience, not a requirement. readme.md B-4. Drop, or say it
  is for seeing what a cut-off run wrote.

### turn/CHANGELOG.md

- F76 (D1) Nothing under Unreleased names the orchestrator's Good check by itself, but `:16`
  "turn tells the main conversation, before each move of the run, its own check, decisions and
  return among them" counts it among the told moves; recheck the wording after D1. It is also
  garbled ("decisions and return among them"). usability B-19.
- F77 `CHANGELOG.md:11` "The result names, for every item, its Good ..., the question it waits on,
  or what the receiver gets once it has it and where it was not found": the result is written only
  once every item has its Good (`run.py:622-623`, `:671-691`); questions go out at once. stale,
  usability B-6, B-21. "every item's Good with its lines, and the lessons".
- F78 `CHANGELOG.md:24` "up to three times a round and two rounds — ... a run that does not settle
  ends": after two rounds the run asks a question and goes on with the answer, rounds counted anew
  (`run.py:26-29`, `:563-567`). inconsistency, B-21. "and an item still without Good becomes a
  question".
- F79 `CHANGELOG.md:34` Removed "the questions asked while the work goes on", against `:7` and
  `dev/turn/architecture.md:84-85` (questions sent "as soon as it is met, ... from the generator").
  inconsistency, B-21. Say what was removed: asking the user directly in a conversation.
- F80 `CHANGELOG.md:12` "Each AI of a run" wider than the lanes (F65).

### turn/.claude-plugin/plugin.json

- F81 `plugin.json:3` "make any work ... that passes your checklist: another AI reads it as the one
  it is for, and what does not pass yet is made again": 0.1.0's text; leaves out that turn is called
  from a plugin's step (`README.md:7-8`, `CHANGELOG.md:21`, `:34` "Asking in a conversation"
  removed). stale, usability B-6. Rewrite with the README's opening; the same text is in
  `.claude-plugin/marketplace.json:17` and `README.md:8` (Cross-slice).

### dev/turn/architecture.md

- F82 (D1) `architecture.md:8-9` "each time that reading ends, the orchestrator checks each Good
  holds, and only the items that do not are made again"; `:104-105` "Through that back and forth
  the orchestrator reads no work" (the qualifier goes: it reads none at all); `:110-116` the Good
  check bullet. Go. Add, once, under the CCS-check bullet (:79-83): the orchestrator judges what
  running the flow needs, the CCS check and the wording of questions, which is not a job of the
  work's and so not against base Principle 3.
- F83 `architecture.md:11-24` turn's own principles numbered 1 and 2 beside "named below Principle
  1 to 8"; `:87` "(Principle 2)" is base 2 but reads as turn's 2; `:115` "(Principle 1)" likewise.
  inconsistency, architecture.md B-8. Label turn's own apart (rn uses "rn's Principle").
- F84 `architecture.md:146-147` "`turn.py` the flow" and "`*.py` the call's check, the forms, the
  parts, the records": the flow is `run.py`, the parts are in `forms.py`. inconsistency,
  architecture.md B-4. True once Structure's split is made, or name `run.py` now.
- F85 `architecture.md:152-154` the work-folder tree names the result and the state only; the run
  also keeps `<result>.<role>.json` replies and `<result>.records/` beside it, whose naming
  `without_run_files` rests on (`run.py:109-117`). architecture.md B-4. Add them.
- F86 `architecture.md:63-64` "the guard acts in every role as it does in the generator, and the
  figure draws it once"; the figure draws it twice (`:59-60`, orchestrator and generator).
  inconsistency, B-6. "draws it for the orchestrator and the generator", or draw one arrow.
- F87 `architecture.md:101-103` "since an edit told per item broke other items": how the decision
  was reached. noise, architecture.md B-7. Drop.
- F88 `architecture.md:34-35` "call turn again with the same result". As F69.
- F89 `architecture.md:111` 119 characters. Rewrap.

### dev/turn/ux.md

- F90 `ux.md:65-68` "While turn runs": `T-->>C` then `C-->>U: passes each on`; turn sends each line
  to the main conversation itself (`run.py:288`, `architecture.md:53`, `:90-91`), and `:75-76` says
  "the lines reach the main conversation above it". figure against text, ux.md B-6. Draw turn →
  main conversation.
- F91 `ux.md:102` "calls it again with the same result". As F69.
- F92 `ux.md:27-28` KR1.2 says no value once G1 is reached. ux.md B-2. Add it (as short as one run
  of the generator and the first user allows, or what holds).

### dev/turn/README.md

- F93 `dev/turn/README.md:7-11` "`one` for the Flow trial and `readme` for the others": `one` is a
  task folder for `trial.py`; the flow trial is `trials/flow/flow.py`, and `trials/roles/roles.py`
  and `roles/kept.py` are not named; line breaks from patched edits (:9-11). stale, usability B-6,
  B-19. List each trial script and what it tries, one line each.

### dev/turn/cosmic-ray.toml

- F94 `cosmic-ray.toml:7-11` the comment works round turn's `call`/`forms` sharing module names with
  lane's (pyrefly reads both through `turn/hooks/lane`). inconsistency, code.md B-5. Rename turn's
  modules; the comment then goes.
- F95 (D4) No `# pragma: no mutate` reason is written here yet; when F4 and F17 become `==`, any
  mutant a test cannot tell apart gets the per-line pragma (cr-filter-pragma) and the reason once
  here.
- F96 `cosmic-ray.toml:6` `excluded-modules = []`: noise if Cosmic Ray does not need the key
  (not checked).

## Structure

| Module / prompt / document | Takes on | Split or reshape |
|---|---|---|
| `turn/scripts/run.py` (751) | command line, paging, run's files and role inputs, state, progress lines, records to text, moves | `turn.py`: `main`, `USAGE`, `shown`, `paged`, `split`/`PAGE` (shim goes); `flow.py`: the moves, one `stage` → handler table; `state.py`: `running`, `save`, `write`, `going`, `resumed`; `given.py`: `reply_path`, `records_folder`, `without_run_files`, `whole`, the three `*_given`; progress lines beside the moves table |
| `turn/scripts/call.py` `check` | call's shape, CCS's kinds, files there, run's layout | `check_call` (shape, types: F1) and `lay_out` (kinds, items, given, shown); `Stop` to the command line |
| `turn/scripts/forms.py` `check`/`Form` | item forms and the learner's lessons through one function | `check_items` (shapes, lines, parts, questions); `check_lessons` (grounds against records); shapes left to the JSON schemas where a schema can say them |
| `turn/scripts/records.py` | Claude Code's record layout, paging of prints, text for the learner | layout via lane's `record`; paging to `turn.py`; keep only "record as the learner reads it" |
| `turn/forms/*.json` + agents' step 6/5/4 | form said twice, the file loose | whole schemas; steps name the file only |
| `turn/agents/up.md` step 1 | alias, start, exit, stdin convention, serial calls | alias and stdin in Role; step 1 starts only |
| `turn/agents/generator.md` step 5 | re-read, parts, run, missing-file and user questions | step 5 check; step 6 what waits on a question |

## Cross-slice

- `dev/turn/trials/flow/replies/untrue.json`, `flow.py:1-15` ("the orchestrator's own check of a
  Good"), `roles/roles.py:4` ("the orchestrator's check"): (D1) go or change with the Good check.
- `lane` (lane:up): `hooks.json:5` matcher `.*|...` (F64) and the eight copied preludes (F66).
- `lane/hooks/lane/template.py:116` and `record.py:50-95` read Markdown fences and Claude Code's
  records better than turn's `call.items`/`forms.parts` (F3) and `records.entries` (F37); turn
  should take them through `turn/hooks/lane`.
- `rn/scripts/call.py` and `rn/scripts/forms.py` link to turn's, but `rn/scripts/rn.py:55-56`
  imports only `records` and `template`; only `dev/rn/trials/moves/stand.py` and
  `dev/rn/trials/flow/write.py` use them, and `dev/rn/cosmic-ray.toml:8-9` excludes them. rn ships
  them unused; renaming turn's modules (F94) breaks these links. rn uses only `records.kept`
  (`rn.py:1650`), touched by F41.
- `.claude-plugin/marketplace.json:17` and root `README.md:8` repeat `plugin.json:3`'s stale
  description (F81).
- `rn/checklists/usability.md` B-16 asks each box to carry its kind in angle brackets;
  `rn/checklists/product/architecture.md` F-1 asks the logical view's boxes to hold "its name
  alone". The kind's checklist decides, but the two disagree.

## Previous audit (`.rn/20261013-writ-rebuild/audits/turn.md`), points in this slice

Kept, verified (line numbers corrected above): 1.1 (F8, F42, F39), 1.2 (F10), 1.3/4.4 decided (D1),
2 noise items in forms/run/call (F30, F29, F32, F31, F16, F15, F4/F5, F36, F40, F35), architecture
history comment (F87), `hooks.json:5` (F64), 3.1 (F51, F57, F59, F34, F62), 3.2 (F3), 3.3 (F37,
F38), 3.4 (F7), 3.5 (F54), 3.6 (F52), 3.8 (Cross-slice), 4.1 (F68), 4.2 (F69, F88, F91), 4.3 (F77),
4.5 (F83), 4.6 (F84), 4.7 (F12, F21, F22, F94), 4.8 (F93), 4.10 (F81), 5 (F50, F56, F60, F70, F48,
F89, F71).
Corrected: `records.write` does not exist; it is `run.write` (F26). `up.md:3` said "same call"
already. Out of this slice, not checked: `judge.py:5-6`, `test_forms.py:670`, `shared.py`,
`roles.py:68-75`, `trials/*/results.json`.

## Read

`turn/README.md` 137; `turn/CHANGELOG.md` 40; `turn/.claude-plugin/plugin.json` 6;
`turn/agents/up.md` 101; `turn/agents/generator.md` 76; `turn/agents/first-user.md` 58;
`turn/agents/learner.md` 37; `turn/forms/claim.json` 54; `turn/forms/learnt.json` 53;
`turn/forms/reading.json` 32; `turn/hooks/hooks.json` 88; `turn/scripts/turn.py` 8;
`turn/scripts/run.py` 751; `turn/scripts/forms.py` 395; `turn/scripts/call.py` 165;
`turn/scripts/records.py` 118; `dev/turn/architecture.md` 177; `dev/turn/ux.md` 113;
`dev/turn/README.md` 11; `dev/turn/cosmic-ray.toml` 15.
Checklists and bases, whole: `rn/checklists/product/code.md` 202, `prompt.md` 150, `readme.md` 219,
`ux.md` 190, `architecture.md` 218, `rn/checklists/usability.md` 208, `dev/architecture.md` 411,
`.claude/rules/dev.md` 115, the previous audit 127.
In part, to check how turn uses them: `lane/hooks/lane/record.py` 1-120, `template.py` 1-40 and
110-140, `schema.py` 1-30, `started.py` 1-25, `lanes/in_form.py` 1-60, `lanes/read_only.py` 1-22,
`lanes/__init__.py` 127-248, the `WORDING` of each lane, the heads of `dev/turn/trials/*.py`,
`rn/scripts/rn.py` imports, `dev/rn/cosmic-ray.toml`.

## Not read

`turn/hooks/lane/` (lane's code, a link): not audited, as the brief says; only the parts above, for
how turn uses it.
