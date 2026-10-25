# lane: the product and its documents — audit (2026-10-25, read-only, at c537dc3)

Scope: every file of `git ls-files lane`, and `dev/lane/{architecture.md,ux.md,README.md,cosmic-ray.toml,testing.py,trying.py}`.
`python3 -m unittest discover -s dev/lane/tests`: 504 tests, OK. `lay.py print` run on a scratch copy of the README's
example plugin (removed after) to check the example's output. 100 findings (8 defects first).

## Defects

1. `lane/README.md:40-44` shows the print as
   "`write: Write only \`CHANGELOG.md\`.                 hook write_only`" and the step wrapped
   "`… Do not run \`git commit\`` / `   or \`git push\`.`"; `lay.py print` on that very proposal gives two blanks before
   `hook` (`lay.py:256` `f"  {action:<{wide}} {sentence:<{long}}  {hook}\n"`) and the step on one line
   (`lay.py:209` `" ".join([last, *added])`). Defect, readme.md B-4 ("the example, run as written, giving other output")
   / B-8. Should be: the README shows the print exactly as it comes out.
2. `lane/CHANGELOG.md:22` "`lane:up` first brings the copy … and says so in its first reply"; `lane/agents/up.md:24-26`
   "its print begins your first reply in step 5, or, where no point is left open, your reply in step 9". With no point
   open the first reply is step 7's proposal, held by as_printed (one heading line allowed, `as_printed.py:51-60`), so
   the note comes only after the OK. Defect, usability B-21. Should be: `lay.py print` carries the bring-up note, or
   the CHANGELOG says "before it writes". (Previous audit's defect 3: kept, the up.md wording moved but the gap holds.)
3. `lane/agents/up.md:16-17` Role "Its plugin changes only by `lay.py write`, after that OK." against step 1
   `lay.py up <the folder>`, which writes `hooks/hooks.json` and `hooks/lane/` before any point is sent
   (`lay.py:527-528`). Inconsistency, prompt.md B-5 ("two instructions that cannot both be followed"). Should be: the
   Role names the bring-up as the one change before the OK. Same in `dev/lane/architecture.md:57`
   "nothing is written into the plugin before the approval", true only with `:60-63` beside it.
4. `lane/hooks/lane/lanes/start_with.py:2` "such as turn's `scripts/turn.py given`" and `lane/CHANGELOG.md:8`
   "`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/turn.py" given`": turn.py has no `given` command
   (`turn/scripts/run.py:60` "usage: turn.py start …"). Stale, code.md B-3 / usability B-6. Should be `turn.py start`,
   or an example of lane's own.
5. `lane/hooks/lane/lanes/hands_off.py:1-2` "`git commit` held for the orchestrator once the building AI has read the
   work": at run time the plugin's user reads the work (`README.md:33` "once you have read it"); the building AI only
   builds the plugin. Inconsistency, code.md B-3 ("a comment that says something else"). Should be "once the user has
   read the work".
6. `lane/scripts/lay.py:126-133` a manifest that holds no JSON (`except ValueError: given = None`) is stopped with
   "names the plugin by no name of letters, digits and -._". Defect, code.md B-2 ("a stop that does not name the
   condition that was wrong"). Should be: its own stop, "holds no JSON".
7. `lane/docs/lanes.md:23` test_after "Told when the subagent | goes on with a change not yet passed": it is held only
   at the end (`test_after.py:19` `EVENTS = ("SubagentStop",)`). Inconsistency, usability B-21. Should be "ends with a
   change not yet passed".
8. `lane/agents/up.md:63-65` "each thing a lane takes written as `docs/lanes.md` says … wait_for takes the approval
   first, then each command it holds back": `docs/lanes.md` gives wait_for `<approval>` alone, and never says in_form's
   form must be written `${CLAUDE_PLUGIN_ROOT}/<path in the plugin>`, which `in_form.py:29-32` and `lay.py:182-189`
   stop on. Inconsistency, prompt.md B-3 ("a form of what a step hands on set neither in the step nor in a form file
   it names"). Should be: `docs/lanes.md` says what each lane takes, held commands and form path included; step 6
   points to it alone.

## lane/agents/up.md

- `:28-34` (step 3) "the word after it is the subagent as `<plugin>:<subagent>`, and each word after that a lane laid
  before as `<step>:<lane>:<what it takes, joined by commas>`; one in both entries is one lane": the AI parses what
  `lay.laid_before` (`lay.py:485-510`) already parses. Duplication, prompt.md B-3 / B-4 ("what a script holds said
  again"). Should be: `lay.py up` prints the lanes laid before; the step drops the format. (Previous 3.3: kept.)
- `:41-42` (step 4) "each lane laid before whose step no longer says its sentence": the AI decides what `step.holds`
  (`step.py:55-63`) decides. Complexity, prompt.md B-3 ("an operation that must give the same result every run
  worked out by the AI"). Should be: `lay.py up` prints each such lane.
- `:77` (step 9) "Run `lay.py write <proposal>`. Do not go on until `OK`.": the wait sentence, appended at the step's
  end by the layer, reads after the action it holds back, and the OK was taken in step 8. Inconsistency, prompt.md B-5.
  Should be: lay wait_for on step 8, or place a held sentence before the commands it holds. (Previous 5.1: kept.)
- `:23`, `:66` "Run … `lay.py up <the folder>` alone" vs "Run `lay.py print <proposal>` as the whole command": one
  instruction, two phrasings. Inconsistency, prompt.md B-5 ("one thing under two names"). Should be one wording.
- `:67` "Hand on `lay.py print` as it is." sits mid-step, while the layer puts sentences "at the end of its step"
  (`lay.py:12-14`, `CHANGELOG.md:21`). Inconsistency, usability B-21. Harmless to `step.holds`; say "in its step".
- `:28` (step 3): the bound ("the whole of what you read of the plugin") and step 2's whole read held by no lane;
  lane:up lays only as_printed and wait_for (`lane/hooks/hooks.json:10`). prompt.md B-3 ("a bound … held by no hook").
  Should be: read_only/read_whole on steps 2-3 where they apply, or the bound dropped as unneeded.
- `:77-78` "Where it exits with 1, reply with its print as a fact as in step 5 and go on by the answer": which step
  follows the answer is not said. prompt.md B-3. Should name the step to go to.

## lane/README.md

- `:35-36` "each under the action it keeps"; `docs/lanes.md:3` and `dev/lane/ux.md:73` "the action it watches".
  Inconsistency, readme.md B-8 / usability B-13. One verb. (Previous 4.3: kept.)
- `:5-6` "a step being one line of what a subagent … is told to do": a step is a numbered item with its lines
  (`step.py:1-3`, `span`). Inconsistency, readme.md B-8 ("a promise narrower than what the product does"). Should be
  "one numbered item of its Steps".
- `:68-70` "Each check is written and tested once, in lane. / Your plugin takes no misreadings of a command of its
  own.": the explanation does not say the gain. readme.md B-6. Should say: your plugin has no check of its own to
  write, test and get wrong.
- `:34-36` "each under the action it keeps: begin, read, write, run, test, hand on, wait or end; with its hook, and the
  step as it would read": the list breaks the sentence. readme.md B-6. Should be two sentences, or a pointer to the
  print below.
- `:77-83` the fourth Why item repeats `dev/architecture.md:206-213` (hooks of agent files, skill hooks lasting the
  session) at length. readme.md B-7 ("a part meant for someone other than the reader"). Should keep the gain ("each
  lane acts only in its subagent") and one line of why.
- `:104-105` "In a plugin of ccpm itself, the code is a link to lane's.": for ccpm's makers, not a newcomer.
  readme.md B-7. Should go to the architecture, which has it (`architecture.md:141-144`).

## lane/docs/lanes.md

- `:24` as_printed `Hand on \`<input>\` as it is.`: what it takes is a command whose print is handed on
  (`as_printed.py:1-2`, up's `lay.py print`). Inconsistency, usability B-14. Should be `<command>`.
- `:25` follow_next listed under the action "hand on": it watches every call for the move a script printed
  (`follow_next.py:20` `TOOLS = (".*",)`), and its module says so (`follow_next.py:17` `ACTION = "hand on"`). One name
  for two things, usability B-14. Should be its own action, such as "follow", in the module and the table.
- `:26` wait_for "goes on without it": what is held back is the commands it takes, which the page never names.
  usability B-3. Should be "runs a command it holds back without it".
- `:12-13` "Write only `{work}`. holds a subagent to …": a sentence opening with a sentence. usability B-11. Should be
  "The sentence `Write only {work}.` holds …".
- The page does not say which lanes are told on a call and which as the subagent ends, though "Told when" depends on
  it (`EVENTS` of end_when, every_item, test_after, as_printed). usability B-3. Should add a column or a line.

## lane/CHANGELOG.md

- `:8` see Defect 4. `:22` see Defect 2.
- `:12` in_form's line carries the whole schema keyword story ("a JSON Schema of the keywords Anthropic's structured
  outputs accept …"), which `docs/lanes.md` does not have at all. usability B-7 / B-19: the user-facing account of what
  in_form reads belongs in `docs/lanes.md`, the CHANGELOG line pointing to the gain.

## lane/hooks/lane/lanes/__init__.py

- Five jobs in one module: the registry (`LANES`), the wording (`slots`, `shown`, `sentence`, `alone`, `fits`), the
  command format both ways (`word`, `hook_words`, `read`, `laid`), reading hooks.json (`taken`, `texts`), and the
  runner (`Laid`, `main`). Complexity, code.md B-5. See Structure. (Previous 1.2: kept.)
- `:159-160` `if self.lane in ("read_only",): each = [[*inputs, *self.forms()] …]` and `:167-172` `run_values` on
  start_with's rules: one lane's rule in the runner. Complexity, code.md B-5. Should be an optional hook in the lane's
  module (e.g. `extra(laid)`), called for any lane. (Previous 1.3: kept.)
- `:135-165` `Laid.check` takes on five rules (end let through, step no longer says it, run values not yet given,
  read_only's forms, the told text). code.md B-5. (Previous 5.2: kept.)
- `:182-200` `taken` reads `hooks/hooks.json` itself, apart from `lay.hooks_read` (`lay.py:299-318`); `:203-209`
  `texts` walks every string of it. Duplication, code.md B-5. One reader in the command-format module. (Previous 3.2:
  kept.)
- `:122-124` `word`, `:212-247` `hook_words`/`laid`/`read` read the format `lay.py:52-58`, `:268-277` writes;
  `dev/lane/testing.py:136-149` parses it a third time. Duplication, code.md B-5. (Previous 3.1: kept.)
- Every lane's `Laid.check` re-reads the record (`call.read` → `record.entries`, then `started.texts` →
  `record.entries` again), the agent file (`step.holds`) and hooks.json (`taken`) on every call, once per lane.
  Complexity, code.md B-5 (one reading of an input in several places). Should be: `main` reads the event's call, record
  and step once and hands it to each lane.
- `:116-118` "Told by membership in the counts it takes …" and `:141`, `:159`, `:199` `in ("…",)`: decision taken —
  plain `==` / comparison, `# pragma: no mutate` where needed, reason once in `dev/lane/cosmic-ray.toml`.
- `:67` `LANE` (a regex of a laid lane) vs `lay.py:38` `LANE` (lane's folder); `:65` `NAME` (a name pattern) vs
  `step.py:14` `NAME` (frontmatter's name regex); `:81` `shown` (how many takes a sentence shows) vs `call.py:189`
  `shown` (lines numbered in a result) vs `schema.py:74` `shown` (a value cut short); `:203` `texts` vs
  `started.py:28` `texts`. One name for several things, code.md B-5. (Previous 4.4: kept, made specific.)
- `:224` `laid(..., held: str = "PreToolUse")`: the default is used by `taken` alone. code.md B-4. Pass it there.

## lane/hooks/lane/hook.py

- `:41` `agent: str | None = None` and `:59` its `None` branch: the only product caller (`lanes/__init__.py:263`)
  always passes it; the default serves `dev/lane/tests/test_hook.py:48` alone. `:1-3` "for a hook acting in one
  subagent alone, such as a lane's" implies hooks of other kinds that do not exist. code.md B-4. Make `agent` required.
  (Previous 2.2: kept.)
- `:12-15` `STOPPED = 2`, `UNREAD = 1` and their meaning, and `lay.py:59-63` `EVENTS = {"PreToolUse": 2,
  "SubagentStop": 1}` with its own comment on the same exit codes. Duplication, code.md B-5. Should be: lay takes the
  codes from `hook`.
- `:15` `UNREAD` (an exit code) vs `template.py:22` `UNREAD` (value prefixes not read) vs `schema.py:44` `Unread`
  (an error). code.md B-5.

## lane/hooks/lane/call.py

- `:1-12` the module opening retells `Call` (`:41-50`) and every function. Noise, code.md B-3/B-4. Should be what and
  why in two or three lines. (Previous 2.3: kept.)
- `:40-63` `Call` has 12 fields for two things: the call being made (`before`, `text`, `heard`) and one made before
  (`result`, `failed`, `ends`). Complexity, code.md B-5. Two types. (Previous 1.5: kept.)
- `:33-35`, `record.py:31-34` `REPLY, SAID = "", "text"`: a reply is read as a call of a tool named `""` with input
  `{"text": …}`, while `Call.action == ""` (`:41`, `:154`) means "no action". Complexity, code.md B-3 (roundabout way;
  `""` for two things). Should be a reply kind of its own.
- `:160-171` `runs` (each command of a shell command) vs `lanes/start_with.py:29` `runs` (whether a call runs a script
  taken); `:109` `text` vs `record.py:95` `text` vs `every_item.py:49` `text`. One name for several things, code.md
  B-5.
- `:137` `alone`: the name says less than "read without the calls before it". code.md B-3.
- `:114`, `:118`, `:134`, `:179`, `:197` `in ("…",)`: decision taken (plain `==`).

## lane/hooks/lane/record.py

- `:147-172` `done` keys one dict by entry numbers (replies) and by tool-use ids (calls). Complexity, code.md B-3.
  Should be two lists merged in order.
- `:60-63` "read from the file once for every reading of it below": each lane re-reads it (see `lanes/__init__`).
  code.md B-3 ("a comment that says what the code does not do").
- `:99`, `:111-112`, `:131`, `:195`, `:212`, `:215` `in ("…",)`: decision taken.
- Claude Code's record format is read here, again in `turn/scripts/records.py:15-20` (rn links it) and in
  `dev/lane/trying.py:57`, `:73`. Duplication, code.md B-5; see Cross-slice. (Previous 3.7: kept.)

## lane/hooks/lane/started.py

- `:50-66` `objects`/`loaded` find JSON in a script's print; `lanes/follow_next.py:34-46` `printed` does it again.
  Duplication, code.md B-5. (Previous 3.8: kept.)
- `:92` `told` (the line giving a run's value) vs `record.py:120` `told` (whether a stop hook told the subagent).
  code.md B-5.

## lane/hooks/lane/shell.py

- `:163-171` `git_statement` works out the folder each `-C` moves to, but its only caller keeps the words alone
  (`call.py:169` `shell.git_statement(here, words)[1]`); the folder serves only `dev/lane/tests/test_shell.py:391-407`.
  Noise, code.md B-4. Should return the words alone, or a caller should use the folder.
- One module for the tokenizer (`PIECE`, `words`, `heredocs_end`), statements and cd (`statements`, `path`), the
  program run (`after_env`, `git_statement`) and what each reader/writer reads (`written`, `reads`, `*_lines`).
  Complexity, code.md B-5; see Structure.
- `:104-107` "A kind is told by membership rather than `==` …" and `:110-128`, `:249`, `:262`, `:292`, `:301`
  `in ("…",)`: decision taken.

## lane/hooks/lane/step.py

- `:11-14` own `FRONT`, `NAME` regexes read frontmatter that `template.closing`/`keys`/`text_of`
  (`template.py:56-113`) read, more strictly. Duplication, code.md B-5. `agent_file` should use `template`.
  (Previous 3.6: kept.)

## lane/hooks/lane/template.py, schema.py, forms.py

- `schema.py:117-301` twenty `*_read`/`*_out` functions with no docstring. Format, code.md F-1 ("for each function
  what it takes in, what it gives back"). One line each, or one comment over `KEYWORDS` naming the two signatures.
- `schema.py:108-112` the stop lists the keywords read ("type, properties, required, …") beside `KEYWORDS`
  (`:306-320`) and the module opening (`:1-3`). Duplication, code.md B-5. Build the list from `KEYWORDS`.
- `template.py:175-176` "Told by membership, as `is` tells small numbers apart …", `:102`, `:106`; `forms.py:30`:
  decision taken.
- `forms.py:39`, `template.py:143`, `schema.py:197` `held` (the point out by) vs `lay.py:260` `held` (what a hook
  holds beyond its sentence) vs `lanes.laid(held=…)` (an event). code.md B-5.

## lane/hooks/lane/lanes/*.py

- `as_printed.py:12`, `follow_next.py:15`, `wait_for.py:14` `from lanes.start_with import runs`: one lane used as the
  library of three. Complexity, code.md B-5. "Does a call run the command a step names" belongs in `call.py`.
  (Previous 1.4: kept.)
- `hands_off.py:16` `c.split()`, `test_after.py:29` `t.split()` read a take by blanks; `start_with.runs` reads it by
  `shell.words` with interpreter and path matching. Duplication/inconsistency, code.md B-5: a quoted take matches
  differently. One function in `call.py`. (Previous 3.4: kept.)
- A take turned into a path four ways: `write_only.py:21`, `in_form.py:46` `os.path.realpath(t)`;
  `read_only.py:21`, `read_whole.py:24`, `test_after.py:26` `shell.path(os.getcwd(), t)`; `end_when.py:23`,
  `every_item.py:32` `shell.paths`. They differ on `$`, `~` and an empty take. Duplication, code.md B-5. One helper.
  (Previous 3.5: kept.)
- `every_item.py:49-55`, `read_whole.py:40`, `call.py:122` read a file with `errors="replace"` three times.
  Duplication, code.md B-5. (Previous 3.8: kept.)
- `write_only.py:17-20` "as turn's generator does": names another plugin's role unexplained. code.md B-3.
- `in_form.py:59` (116 chars), `in_form.py:3`, `wait_for.py:2`, `:19`: over the 100 the repository wraps at, as are
  `call.py:30`, `:190`, `forms.py:3`, `schema.py:3`, `:22`, `template.py:1`, `lanes/__init__.py:1`, `lay.py:5`, `:49`,
  `:261`, `dev/lane/trying.py:1` (15 lines). `ruff.toml:2-3` says 100 "The width this repository's documents wrap at"
  but E501 is not selected. Inconsistency, code.md B-3 (layout unlike the code around it). Select E501.
  (Previous 2.4: kept.)
- `hands_off.py:17-18`, `read_whole.py:31-33`, `test_after.py:36-38`, `write_only.py:23-24` the same membership
  comment four times; `as_printed.py:30`, `:45`, `in_form.py:48`, `start_with.py:37`: decision taken.

## lane/scripts/lay.py

- Seven jobs (536 lines): the proposal read and checked (`:95-189`), the step text (`:192-228`), the print
  (`:231-265`), hook commands (`:52-63`, `:268-296`), hooks.json edited (`:299-345`, `:395-423`), lane's code placed
  with VERSION (`:348-392`, `:463-482`), the bring-up (`:485-529`). Complexity, code.md B-5; see Structure.
  (Previous 1.1: kept.)
- `:1-25` the opening retells `written` (`:426`) and `brought_up` (`:513`). Noise, code.md B-4. (Previous 2.3: kept.)
- `:273`, `:280` `event: str = "PreToolUse"` defaults: product callers always pass it (`:292`, `:341`); only
  `test_python_check.py:31`, `test_in_form.py:219`, `test_write_only.py:161` lean on it. code.md B-4. Drop.
  (Previous 2.2: kept.)
- `:182` `if known in ("in_form",): in_form.form(…)`: in_form's rule in the layer. code.md B-5. Same optional hook as
  `Laid` (`check_takes(root, takes)`). (Previous 1.3: kept.)
- `:268` `run(event)` gives a command text; `hook.run` runs checks. code.md B-5 (one name, two things). Name it
  `script_command`.
- `:363-365`, `:532-535` membership comments and `:291`: decision taken (`__name__ == "__main__"` with a pragma).

## dev/lane/architecture.md

- `:129` "lane runs on Claude Code, python3 3.9 or later, git and jq": nothing in `lane/` runs git or jq (grep of
  `lane/scripts`, `lane/hooks/lane`); `README.md:87-88` lists Claude Code and Python. Inconsistency, architecture.md
  B-6. Should be "Claude Code and python3 3.9 or later". (Previous 4.1: kept.)
- `:12-13` own Principle 1 "The AI is made to notice its drift … and is told the step again" restates base Principle 5
  (`dev/architecture.md:31-32` "tells the role its step again"). architecture.md B-1 ("a principle of what it is built
  on written again"). Should be linked; keep only what lane adds (the AI finds its way back itself).
- `:14` own Principle 2 "A lane is a sentence of a step together with the hook …" is a definition, not a principle.
  architecture.md B-1. Should move to the opening's account of how lane is put together.
- `:9-10` "named below Principle 1 to 8, and its own: 1. … 3." then `:58` "(Principle 2)": lane's own are numbered 1-3
  too, so "Principle 2" names two things. architecture.md B-8. Number lane's own L1-L3.
- `:53-59` "The arrows run in this order: `lane:up` reads the plugin, sends … every point open at once …" retells the
  UX scene Laying lanes (`ux.md:62-80`). architecture.md B-7. Link it. (Previous 4.5: kept.)
- `:136-138` "as tried on Claude Code 2.1.306": how it was reached. architecture.md B-7. (Previous 4.5: kept.)
- `:154-157` the record's path `<transcript_path without .jsonl>/subagents/agent-<agent_id>.jsonl`: behavior held in
  `record.py:50-57`. architecture.md B-7. Keep only "the guard reads the subagent's own record". (Previous 4.5: kept.)
- `:152` "Claude Code reads no hooks from a plugin subagent's own file" says again `dev/architecture.md:208`.
  architecture.md B-7. Link it.
- `:36-41` the logical view's boxes have no kind (`building AI`, `lane:up`, `layer`, `building AI's plugin`, `guard`,
  `subagent` are an AI, an agent, a script, files, code and an AI). usability B-16 ("each box holds its name, with its
  kind beside it"), as `dev/architecture.md:11-14` does.
- `:46` the guard's only arrow is to the subagent; it also reads the plugin's step, hooks.json and the subagent's
  record (`:71-78`). architecture.md B-3 ("what a component does with what it is handed" left to guess). Add
  `guard -->|reads the steps and hooks of| plugin`.
- `:97-117` the tree leaves out `lanes/__init__.py` (registry, wording, command format, runner),
  `.claude-plugin/plugin.json` (the version `:143` reads) and `CHANGELOG.md`; several places have no kind
  (`pretooluse.py`…`started.py` inherit, `docs/lanes.md`, `README.md`). architecture.md B-4.
- `:161-165` (previous 4.5 said in_form's forms belong to the code): dropped — which forms in_form reads, with the
  standard library alone, is a decision the approval rests on, not a case's behavior.
- `:169` "lane is tested as Test says": `dev/lane/testing.py` and `dev/lane/trying.py`, which every plugin's tests and
  trials stand on, are lane's to keep; the base names testing.py (`dev/architecture.md:255-256`) and nothing names
  trying.py. architecture.md B-5 ("what this product's checks need that the project's rules do not give"). Name both.

## dev/lane/ux.md

- `:73` "the action it watches": see README.
- `:50` participant `subagent<br/>#lt;AI, with its hooks#gt;` and `:90` `subagent<br/>#lt;AI#gt;`; `:91`
  `hook<br/>#lt;lane's#gt;` ("lane's" is whose, not a kind). ux.md B-3 ("kind … as one short word"), B-6 (one thing,
  two descriptions). Should be `<AI>` and `<hook>`.
- `:41-42` "The building AI, `lane:up` and a subagent … take part": the hook of scene 3 is not named there. ux.md B-6.
- `:101-102` "On a machine without Python …, the hooks stop the calls they watch": the end-of-subagent case (tells the
  user, lets it end), which the architecture's story 4 (`architecture.md:26-28`) and README hold, is missing.
  ux.md B-6 ("an idea given in part").
- `:108` Benefit "Hooks stay few, laid only where a step alone is not sure to hold.": what the product does, not the
  gain. ux.md B-4. Should be the gain (a plugin carries only the checks its steps need, so little to read or keep).
- `:82` "Lane's code" vs "lane's code" everywhere else. usability B-13 (trivial).

## dev/lane/README.md

- `:6` lists the unit tests alone; `dev/architecture.md:226-227` says it "says how to run its tests and trials once
  they exist", and `dev/lane/trials/` exists; the property tests and `cosmic-ray.toml` are not named either.
  Inconsistency, usability B-3. Add the trial, property and mutation commands (or link `dev/README.md`).
  (Previous 4.2: kept.)
- Names neither `testing.py` nor `trying.py`, which every plugin's tests and trials import. usability B-3.

## dev/lane/cosmic-ray.toml

- Decision taken: the reason for `# pragma: no mutate` (a mutant no test can tell apart) is written here once; today
  it is in the nine comments listed above. Missing now; the filter (cr-filter-pragma) is not configured.
- `:6` `excluded-modules = []`: not checked whether Cosmic Ray needs the key; if it is its default, noise (code.md B-4).

## dev/lane/testing.py

- `:136-149` `laid` parses hook commands by `rpartition("; exec ")`, `words[2:]`, `split(":", 2)`: the format
  `lanes.hook_words`/`lanes.read` own. Duplication, code.md B-5. Should call them. (Previous 3.1: kept.)
- `:117-133` `lane_code` exists because lane's `call.py`/`forms.py` share names with turn's unrelated
  `turn/scripts/call.py`/`forms.py`. Complexity, code.md B-5. Renaming one side removes it. (Previous 4.4: kept.)

## dev/lane/trying.py

- `:1-2` "What every plugin's trials stand on" but it lies outside `dev/lane/trials/`, where
  `dev/architecture.md:339-340` puts trial code, and no README names it. Inconsistency, usability B-21.
  (Previous 4.2: kept.)
- `:57` `~/.claude/projects/*/{session}/subagents/*.jsonl` and `:73` `"Stop hook feedback"` (= `record.TOLD`,
  `record.py:20`): Claude Code's record format again. Duplication, code.md B-5. (Previous 3.7: kept.)
- `:20`, `:55` return types `dict`, `list` say nothing of what is in them. code.md F-1/B-3.
- `:52` `json.loads(done.stdout.strip().splitlines()[-1])` raises IndexError on an empty print with exit 0. code.md B-2.
- `:22-24` "wait is the minutes … which it stops waiting for after 10 by default": whose default (Claude Code's) is
  left to guess. code.md B-3.

## Previous audit points outside this slice

Not judged here (other slices): defect 1 (`dev/changed.sh`, still true at `dev/changed.sh:18`), defect 2
(`dev/lane/trials/trial.py`), 1.6, 2.5, 3.9. 2.1 is now the maintainer's decision (above).

## Structure

| Module / document | Takes on | Split or reshaping |
|---|---|---|
| `lane/scripts/lay.py` | proposal, step text, print, hook commands, hooks.json, code placement, bring-up | `lay.py` the command line over `proposal.py` (read, check), `steps.py` (step text, print), `hooks_file.py` (hooks.json read/edit, sharing the command format), `code.py` (link/copy, VERSION, bring-up) |
| `lane/hooks/lane/lanes/__init__.py` | registry, wording, command format, hooks.json reading, runner | `lanes/__init__.py` the registry; `wording.py` (`slots`, `shown`, `sentence`, `alone`, `fits`); `command.py` the hook command both ways, with lay's `CHECK`/`run`/`command` and `hook_words`/`read`/`laid`/`taken`, used by lay and `testing.py`; `guard.py` (`Laid`, `main`) reading the call once |
| `Laid.check` | five rules incl. read_only's and start_with's | lane-module hooks (`extra`, `check_takes`) called for any lane; the runner keeps only "step still says it" and "run values given" |
| `lane/hooks/lane/call.py` `Call` | the call being made and calls made before | `Call` (the call now: `before`, `text`, `heard`) and `Made` (`result`, `failed`, `ends`); a reply its own kind, not tool `""`; `runs_command(call, take)` moved here from `start_with` |
| `lane/hooks/lane/shell.py` | tokenizing, statements and cd, the program run, reads/writes | `shell.py` (words, statements, path) and `effects.py` (what each command reads and writes) |
| take to path (5 lanes) | four ways | one `call.path_of(take)` |
| `lane/agents/up.md` steps 3-4 | parsing hook commands, finding stale lanes | `lay.py up` prints lanes laid before, stale and left-out ones; the steps read its print |
| `dev/lane/architecture.md` | principles mixed with a restated base principle and a definition | opening defines a lane; own principles L1-L2 only what lane adds; lines that retell the UX or the base linked |

## Cross-slice

- `dev/changed.sh:17-18` `'^(lane/hooks/lane/(hook|shell)\.py|dev/lane/testing\.py)$'` and `dev/README.md:9`, `:17`
  "the tests of `hook.py` and `shell.py`, the hook code the plugins share": turn links all of `hooks/lane`
  (`turn/hooks/lane -> ../../lane/hooks/lane`), rn links `template.py` (`rn/scripts/template.py`), and
  `dev/turn/tests/test_lanes.py:8` imports lane's `lanes`, `step`. A change to any lane module runs only lane's checks
  before push.
- `turn/scripts/records.py:15-20` reads Claude Code's records apart from `lane/hooks/lane/record.py`; rn links it.
- `turn/scripts/call.py`, `turn/scripts/forms.py` (and rn's links to them) share names with lane's `call.py`,
  `forms.py` (`dev/lane/testing.py:117-133` works around it).
- `turn/scripts/run.py:60` turn.py's commands are `start`/`next`/`questions`/`parts`; lane's `start_with.py:2` and
  `CHANGELOG.md:8` still name `given`.
- `dev/architecture.md:206-213` and `lane/README.md:77-83`, `dev/lane/architecture.md:152` say the same about agent
  files and skill hooks.
- `dev/architecture.md:339-340` (trial code in `dev/<plugin>/trials/`) against `dev/lane/trying.py`; it is imported by
  `dev/turn/trials/shared.py:22` and `dev/rn/trials/moves/moves.py:36`.
- `ruff.toml:2-3` line-length 100 with E501 unselected (repository-wide).
- Decision on the membership idiom: 38 `in (x,)` sites in lane's code, nine explaining comments; rn.py has its own
  (rn auditor). Decision on turn's Good check: no place in this slice touches it (`follow_next.py:2`'s
  `turn.py next` still exists).

## Read

| File | Lines |
|---|---|
| lane/README.md | 120 |
| lane/CHANGELOG.md | 24 |
| lane/.claude-plugin/plugin.json | 6 |
| lane/docs/lanes.md | 36 |
| lane/agents/up.md | 78 |
| lane/hooks/hooks.json | 28 |
| lane/hooks/lane/call.py | 198 |
| lane/hooks/lane/forms.py | 63 |
| lane/hooks/lane/hook.py | 66 |
| lane/hooks/lane/lanes/__init__.py | 263 |
| lane/hooks/lane/lanes/as_printed.py | 60 |
| lane/hooks/lane/lanes/end_when.py | 27 |
| lane/hooks/lane/lanes/every_item.py | 55 |
| lane/hooks/lane/lanes/follow_next.py | 54 |
| lane/hooks/lane/lanes/hands_off.py | 21 |
| lane/hooks/lane/lanes/in_form.py | 62 |
| lane/hooks/lane/lanes/read_only.py | 22 |
| lane/hooks/lane/lanes/read_whole.py | 54 |
| lane/hooks/lane/lanes/start_with.py | 52 |
| lane/hooks/lane/lanes/test_after.py | 43 |
| lane/hooks/lane/lanes/wait_for.py | 36 |
| lane/hooks/lane/lanes/write_only.py | 26 |
| lane/hooks/lane/pretooluse.py | 12 |
| lane/hooks/lane/record.py | 216 |
| lane/hooks/lane/schema.py | 320 |
| lane/hooks/lane/shell.py | 319 |
| lane/hooks/lane/started.py | 96 |
| lane/hooks/lane/step.py | 69 |
| lane/hooks/lane/subagentstop.py | 13 |
| lane/hooks/lane/template.py | 185 |
| lane/scripts/lay.py | 536 |
| dev/lane/README.md | 6 |
| dev/lane/architecture.md | 169 |
| dev/lane/ux.md | 108 |
| dev/lane/cosmic-ray.toml | 13 |
| dev/lane/testing.py | 149 |
| dev/lane/trying.py | 79 |
| Checklists: rn/checklists/product/{code,prompt,readme,ux,architecture}.md, rn/checklists/usability.md | 202, 150, 219, 190, 218, 208 |
| dev/architecture.md, .claude/rules/dev.md, .rn/20261013-writ-rebuild/audits/lane.md | 411, 115, 118 |

Consulted in part for cross-checks: `dev/changed.sh:1-30`, `dev/README.md`, `turn/scripts/turn.py`,
`turn/scripts/run.py:60-100`, `turn/scripts/records.py:1-40`, `ruff.toml`, `pyproject.toml` (ruff part).

## Not read

None of the slice.
