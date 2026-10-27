# Where intents 1 to 5 of decisions/run-cost.decisions.md land

The impact map made 2026-10-27 at 66a0385, before any fix; line numbers hold at that commit.


Every intent is general to every plugin (decisions/run-cost.decisions.md), so each goes into dev/architecture.md first.

## `dev/architecture.md` places each intent touches

- **:16 and :42-45, Principle 1**, "The orchestrator holds the whole run and decides each move". Intent 5 has two roles settle a gap between them, so the line needs to say which moves stay with the orchestrator.
- **:17-18 Principle 2, :75-85 "Hearing until nothing is left to decide", :58-60 "a subagent cannot [ask the person]".** Intent 3: say that a technical choice is the maker's to settle and name, not to ask.
- **:19, :98-104, Principle 3**, "given only what the job needs". Intent 5 hands the generator the first user's gap and the first user the generator's answer.
- **:20-23 Principle 4 and :142-154 "Read by those who did not make it"**, "each reading it on its own", "each gives its verdict from its own reading alone", "A reader shown another's verdict finds what it was told".
  - Principle 4 decision and intent 5: limit this to the first reading, then allow the exchange about a gap.
  - Intent 4: add that the reader judges by whether the receiver can use the work, sends back only a gap that hinders that use, and runs per item what the maker ran.
  - Intent 1: :151-154 "Its maker checks it against its checklist" is the one place that states the shape of a maker's check.
- **:24-25 Principle 5**, "What a machine can judge is checked by a script or a hook at the moment it happens". Today it covers what the AI does. Intent 4 extends it to the work: formatter, linter and type checker.
- **:26-27 Principle 6, :172-175 "A run's state is kept…", :214-215** "what the run kept holds every send-back… as each move is kept before the next (Principle 6)".
  - Intent 3's "rn does not commit and push at each answer" goes against "each decision [is] kept before the next move".
  - The learnings read pushed history (:205-216).
- **:28-29 Principle 7 and :194-199** "A change is taken when the purpose is still met as fully; only then is time or cost cut". This bounds intents 1 to 3. No change; each change must be shown to keep KR1.1.
- **:156-170 "Where the course is kept"**, "turn's make–read–check rounds… kept in a script". Intent 2's count of moves is set here and in turn's flow.
- **:228-249 "Messages"**: the diagram (:230-243), "Roles do not message one another", "What passes between roles goes through the orchestrator". Intent 5 needs this rewritten, either as role-to-role messages or as orchestrator-relayed messages settled between the two roles.
- **:259-272 "The guard tells each role its steps again".** Intents 3 and 5 rely on hooks reading messages that come after the start (see `lane/` under intent 3).
- **`dev/who-does-what.svg`**, "starts it with its prompt, sends more work", "replies". No arrow runs between two roles; intent 5 adds one.

## Intent 1: the self-check is per item, pass and evidence; only items sent back are rewritten

**turn**
- `turn/forms/claim.json:2` "each item's Good with its lines…". Replace the prose shapes `good` (:47-79), `parts` (:80-134) and `waits` (:135-158) with per-item pass, the command run with what it printed or the lines, and a short note.
- `turn/forms/claim.json:13`, "one for each item of every checklist, or, before you have made anything, only the items that wait". Allow only the items sent back on a remake.
- `turn/scripts/forms.py:27` `WORDED = ("can", "good", "did", "lacking")`. Add the new evidence keys.
- `turn/scripts/forms.py:59-61` `CLAIM = Form(shapes(...claim.json), asks=True, asks_first=True, chooses=True)`. Needs a mode where a remake gives only the items sent back.
- `turn/scripts/forms.py:125` `every = not (form.asks_first and data["questions"])` and :181-186 "is left out; give every item judged here". These force the whole claim every round.
- `turn/scripts/forms.py:227-266` `parts_problems`. Holds a Good per part for `each part` items; decide its evidence shape.
- `turn/scripts/flow.py:372-374` `claim_problems(...run["items"]...)`. On a remake, check against the items sent back.
- `turn/scripts/flow.py:255-262` "its reply is written anew", `os.remove(reply)`. Today the whole claim goes away each time.
- `turn/scripts/flow.py:473-481` `made`, `run["chosen"] = reply["chosen"]`. With a partial claim, merge the choices rather than replace them.
- `turn/prompts/generator.md:9-13` "Your Goods are your claim… you name in your claim with why"; recast the role.
- `turn/prompts/generator.md:33-35` step 3 "For every item, set its Good".
- `turn/prompts/generator.md:44-53` step 5, "For every item find the lines that give its Good". Make it per item: the command run and what it printed.
- `turn/prompts/generator.md:58-62` step 7, "Write your claim to `reply` anew… each time, as the file is gone by then". Rewrite only the items sent back.
- `turn/agents/generator.md:3` "claims each Good with the lines that give it".
- `turn/hooks/lanes.json:112-121` `in_form {reply} claim.json`. The schema it holds changes; lay it again with `lay.py`.
- `dev/turn/architecture.md:83-90` "the generator is sent back the items…". `:109-114` "The generator names in its claim each choice…" stays, with the new form named.
- `dev/turn/architecture.md:186-189` "Each role writes its reply to a file… in a JSON form of its own".

**turn tests and trials that assert today's behavior**
- `dev/turn/tests/helpers.py:86-95` `GOOD`, `CLAIM`, `WAITS`, and `:321-326` `made()`.
- `dev/turn/tests/test_forms.py`
  - :256 `test_a_claim_of_every_item_good_or_waiting_passes`
  - :263 `test_a_claim_names_each_choice…`
  - :287 `test_a_claim_asking_before_any_work_is_made_gives_the_items_waiting_alone`
  - :575, :581, :596, :607: the form-file and schema tests.
- `dev/turn/tests/properties.py:32` `FORMS = (forms.CHECK, forms.CLAIM, ...)`.
- `dev/turn/tests/test_made.py:189` `test_a_claim_leaving_an_item_out_or_without_its_questions_is_sent_back`.
- `dev/turn/tests/test_rounds.py:53` and `:64` (choices of the last claim).
- `dev/turn/trials/orchestrator/replies.py:53-54, :63-98`: the claims of the stand-in generator.

**rn**
- `rn/forms/claim.json` is a link to turn's form and follows it.
- `dev/rn/architecture.md:241` names it.
- `rn/prompts/orchestrator.md:145-147` "answer each item of the checklists at the lines of the part that give it". This is the orchestrator's own check of the plan and the learnings; apply the same evidence form if the rule becomes general.

## Intent 2: about eight moves for two rounds; the user is told only at a role's start and end, a question and the result

**turn's flow**
- `turn/scripts/flow.py:169-185` `tell()`, a `SendMessage` move to `MAIN` made before every move. It is called from:
  - `due` (:194-207)
  - `judge` (:188-191)
  - `to_judge` (:221-223)
  - `asking_now` (:226-232)
  - `returning` (:235-242)
  - `role` (:245-252)

  Cut it to the role start, role end, question and result, and carry the line inside the role's move, not as a move of its own.
- `turn/scripts/flow.py:33-56` `DOES`, `OWN` ("check", "ask", "left", "returned") and `AGAIN`. `OWN`'s check and left lines go away.
- `turn/scripts/flow.py:29-30` `WAIT = 100`, `:311-327` `awaited`, `:292-293` `return {"waiting": agent}`. Polling turns into extra moves for every role that gets a message.
- `turn/scripts/flow.py:281-291`, the `{"agent_id"}` hand-back, one move for each role started.
- `turn/scripts/flow.py:86` `stage="check"` and `:383-401` `checked`: the AI check of the CCS before any work. `:90-106` `resumed` sets `told=False` and shows the check again after a restart. Drop the check or make it a script, and do not repeat it.
- `turn/scripts/flow.py:23-28` `SENDS = 3`, `MORE = 1`. They bound rounds and sends; set them to the budget.
- `turn/scripts/turn.py` (`USAGE`, `printed`) prints `line` with the move and changes with it.

**turn's prompts, lanes and documents**
- `turn/prompts/orchestrator.md`
  - :12-18 and :20-23: the check of the CCS before any work.
  - :37-38: "Load SendMessage with ToolSearch".
  - :42-46: "a line for the user and then the tool call…", `{"waiting"}`.
  - :48: `{"check"...}` leads to step 4.
  - :52-67: step 4, "Check the CCS. Read each file of the `given`…".
- `turn/hooks/lanes.json:36-50`, `read_only` and `read_whole` on `{given}` at the orchestrator's step 4. These go away with the check.
- `dev/turn/architecture.md`
  - :30-31 user story "I want the user told, as the run goes, what it will do and what is done".
  - :64-70: the orchestrator's check.
  - :77-82: "The flow makes a line for the user before each move and after each outcome".
  - :184-185 and :190-199: roles that get a message and the record read for their end.
- `dev/turn/ux.md:270-276`, "loop each of turn's agents… what it will do, how far and how, then what is done and what comes next", and :278-280.
- `dev/turn/logical-view.svg:58` "tells progress".
- `turn/README.md:47-50` "turn first checks that the CCS holds everything…", :58-64 "turn tells the main conversation… before each of its agents starts…", and the example line at :63.
- `turn/CHANGELOG.md:7` (the CCS check before work) and :18 ("turn tells the main conversation, before each move of the run…").

**turn tests and trials**
- `dev/turn/tests/test_told.py`, the whole file (:22, :42, :53, :63, :82, :104, :115, :123).
- `dev/turn/tests/helpers.py:268-278` `heard`/`due` expect a `SendMessage` to `main` before each move, and :292-299 `started` hands over a check.
- `dev/turn/tests/test_check.py`, the whole file.
- `dev/turn/tests/test_resumed.py:30` `…at_its_check_shows_the_check_again`.
- `dev/turn/tests/test_round.py:79` and :107 (the wait and `waiting`).
- `dev/turn/trials/roles/kept.py:59-69` skips "A SendMessage whose `to` is `main`".
- `dev/turn/trials/orchestrator/orchestrator.py:69` "turn sends you a line before each move".
- `dev/turn/trials/trial.py:39` "turn sends you a line before each move and after each…".

**rn**
- `rn/prompts/orchestrator.md:164-166` "A message from one of its agents, a line beginning `turn:`: reply with that line alone".
- `dev/rn/architecture.md:166-169` "passes each line turn tells on to the user".
- `dev/rn/architecture.md:25-26` user story "told before and after each step what rn does".
- `dev/rn/ux.md:137-139` "what it will do, how far and how / what is done and what comes next".
- `rn/README.md:135-137` "Before each step, rn tells you in a line…".
- `rn/CHANGELOG.md:12` "rn says before each step what it will do…".
- rn's own lines from `rn.py state` "tell" (`rn/scripts/session.py:437`) are rn's step lines, not turn's. They are touched only if the general rule applies to rn too.
- `dev/rn/trials/moves/stand.py:107-115` makes up the line "turn: Next, turn:first-user will…".
- `dev/rn/trials/moves/cases.py:899-902` `TURN_LINE`, used in the "task" case (around :1100).
- The acceptance trial (`dev/rn/trials/acceptance/acceptance.py:228-298`, costs and minutes) is the measure of improvement and needs no change.

**`lane/`**
- `lane/hooks/lane/lanes/follow_next.py:26-39` holds the orchestrator to every move printed. It is general and needs no change, but every line turned into a move is a move this lane enforces.

## Intent 3: only the user's points are asked; turn goes on where it stood; no commit and push at each answer

**Generator asking about technical choices**
- `turn/prompts/generator.md:5-8` "what they leave open that only the user can decide, you hand back as a question".
- `turn/prompts/generator.md:36-38` step 3, "the item waits on a question".
- `turn/prompts/generator.md:54-57` step 6, "Where a Good needs a file the work does not hold… the item waits on a question whether to add that file". This is the source of the questions about test paths and ignore files. Make it "add it, name it in `chosen`".
- `turn/prompts/generator.md:12-13` and :58-61: `chosen` is already the place for such choices.
- `turn/prompts/orchestrator.md:57-60` "or what the receiver has lacks something, the item waits on a question", and :68-74 step 5.
- `turn/scripts/forms.py:56` `CHECK`, :59-61 `CLAIM` with `asks`, and :65 `LEFT`. These are the forms that carry questions.
- `turn/scripts/flow.py:529-541` `left_asked`: an item two rounds leave becomes a user question even when the gap is technical. Intent 5 should settle these first.
- `dev/turn/ux.md:296-297` "turn asks where the CCS lacks what the run needs, making the work meets a point…".
- `turn/docs/calling.md:58-69`.
- `turn/README.md:47-57`, the license example. It stays: the license is a user point.
- `rn/checklists/product/prompt.md:363-374` B-6. It already says only the user's choice goes to the user; keep it consistent.
- `rn/checklists/product/code.md:159-164` (B-6, "a survivor of mutation testing… with nothing… saying that the user decided it and why"). This item asks for a decision by the user about each gap left out of the checks, which pushes generators to ask the user about surviving mutants. Recast it as the maker's named choice.

**Going on where it stood instead of starting anew**
- `turn/scripts/flow.py:417-430` `answered` sets `stage = "anew"`, and :433-440 `anew` returns `{"anew"}` when `laid_out_anew`.
- `turn/scripts/flow.py:109-121` `laid_out_anew` and `again` (begun again at the check), and :74-75 in `start`.
- `turn/scripts/flow.py:443-445` `checked_again` (the check made again), :448-454 `sent_answer`, :457-461 `left_answered`.
- `turn/scripts/call.py:84-117` `laid_out` (the `given`/`readable` lists).
- `turn/prompts/orchestrator.md:47` `{"anew": "<result>"}`: go to step 1.
- `dev/turn/architecture.md:97-99` "an answer whose CCS lays the run out anew has the orchestrator start the run again, and the lane takes the files the CCS now names". That is the stated cause, and it lies in lane (next point).
- `lane/hooks/lane/started.py:1-5` "The JSON a subagent starts from is the one place a plugin hands it the files of its run". The same is in `dev/lane/architecture.md:87-92`, and the guard reads values only from the start (`lane/hooks/lane/guard.py:166-171`). For `{given}` to grow while a role stays started, lane must read values from later messages too, or turn must hand the files another way. This is a change to lane with its tests: `dev/lane/tests/test_started.py`, `test_guard.py`, `test_start_with.py`.
- Tests:
  - `dev/turn/tests/test_check.py:67`, :82 `test_an_answer_laying_the_run_out_anew_has_the_run_started_again`, :95, :114
  - `dev/turn/tests/test_made.py:121` `…lays_the_work_out_anew_has_the_ccs_checked_again`
  - `dev/turn/tests/test_resumed.py:39`
  - `dev/turn/tests/helpers.py:249-253` `laid_out_anew`

**rn's commit and push at each answer**
- `rn/prompts/orchestrator.md:167-177`: "first keep the move with `rn.py state`… so turn's run waiting on them is pushed before anything is asked"; "run `rn.py ccs` for the work again…"; "each answer kept with `rn.py decide`".
- `rn/prompts/orchestrator.md:41-44`: every keep "committing every change with `--message` and pushing it".
- `rn/scripts/ccs.py:355-396` `decide` ends in `session.keep` (commit and push). `rn/scripts/session.py:198-208` `keep` runs `repo.git(["commit"...])` and `repo.push()`.
- `rn/scripts/ccs.py:429` `repo.pushed()` makes `rn.py ccs` refuse unless everything is pushed, and :467-471 keeps the call.
- `rn/scripts/repo.py:118-139` `pushed`.
- `dev/rn/architecture.md`
  - :166-175 "it keeps the questions in the steering before it asks the first… so it is pushed with the questions before the user is asked"
  - :176-180 "the orchestrator answers by writing the CCS again"
  - :186-187 "Every decision, answer, feedback and approval is pushed before the move after it"
  - :208-212 and :268-272 (the record kept by a commit and a push)
- `rn/CHANGELOG.md:17` "every decision is pushed before the work after it".
- `rn/checklists/session/learnings.md:383-384` (B-4, "a question turn asked while it ran… an answer added to a work's decisions during the run") and :389-390. These rely on that history.
- `rn/prompts/learnings.md:167-173` (`rn.py history` from commits).
- Tests:
  - `dev/rn/tests/test_ccs.py:404` `test_turns_files_at_the_root_are_kept_with_the_move` ("When: the orchestrator keeps a decision while turn asks")
  - `dev/rn/tests/test_ccs.py:983`, :996, :1006 (`ccs` stops when not pushed)
  - `dev/rn/tests/test_session.py:430`, :463, :473
  - `dev/rn/trials/moves/cases.py:1076-1093`, case "asks": "kept in Open and pushed… the answer kept", `KEPT` after the answer
  - `dev/rn/trials/moves/place.py:78-81` `ALL_KEPT`

## Intent 4: tools for what a machine sees, Good judged by use, the same run for maker and reader

**rn's code checklist**
- `rn/checklists/product/code.md:20-22` "The development rules are the project's own rules… the checks every change passes". Add an item that the project has a formatter, a linter and a type checker set up and run. Today only `:182-183` (B-7) checks one "the development rules name… already failing".
- Move what tools catch out of the reader's hunt:
  - F-1 (:33-43): the docstring and type shape, which a linter or type checker holds.
  - B-1 (:57-58): imports and language features beyond what the rules name.
  - B-3 (:96-97): idiom and layout, the formatter's and linter's.
  - B-4 (:111): a parameter every caller gives the same value.
  - B-5 (:131-132): `__pycache__/` and the ignore file.
  - B-6 (:157-164): coverage and mutation, checks that are run, not read.
- Recast every "Look for:" list in code.md (B-1 to B-9) from defects to hunt into what the receiver must be able to do.

**Every other checklist, judged for the hunting pattern**

Each list of defects sets a reader hunting counterexamples:
- `rn/checklists/checklist.md:64-65`, the template "Look for: <the signs a deliverable falls short of it, each a thing to be found in the deliverable…>". This is the root that every checklist copies. Also :16-18 "the ways a deliverable meets that thing are the signs under the item" and B-5 :173-175. Change the template first.
- `rn/checklists/usability.md:15-17` already says "answered by what the reader has and does". Its lists at :66-70, :84-86, :114-115, :138-141, :163-164, :176, :189-190 are defect hunts.
- `rn/checklists/fix.md:220-222`, :233-234, :246-249, :261-263: hunts.
- `rn/checklists/product/architecture.md:97-99`, :111-112, :125-132, :146-147, :160-164, :177-179, :192-199, :213-219: hunts. B-6 and B-7 ("every…") are the strongest.
- `rn/checklists/product/prompt.md:282-283`, :295-296, :309-321 (B-3, eight signs), :333-341, :352-358, :369-371, :382-383: hunts.
- `rn/checklists/product/readme.md:88-93`, :106-110, :122-123, :137-143, :157-162, :175-182, :194-201, :216-222 (B-8 "every statement holds"): hunts.
- `rn/checklists/product/ux.md:319-321`, :333-340, :354-359, :374-375, :386-391, :403-411: hunts.
- `rn/checklists/session/deliverable.md:32-38`: partly framed by use already (:17-21 "serves the user by what it does when used").
- `rn/checklists/session/issue.md:108-111`, :123-126, :137: hunts.
- `rn/checklists/session/trial.md:170-173`, :187-191, :203-206, :218-222, :234: hunts.
- `rn/checklists/session/research.md:268-271`, :284-291, :304-307, :319-323, :335: hunts.
- `rn/checklists/session/plan.md:81-82`, :95-99, :114-123, :136-146, :162-167, :181-187, :205-218, :235-243, :254-263: hunts. Several are machine checks rn's scripts already hold, such as the F-1 form and the IDs at B-9 :258-260.
- `rn/checklists/session/learnings.md:326-331`, :343-350, :362-365, :377-387 (B-4 "Every shortfall"): hunts.

**Same check for maker and reader**
- `turn/prompts/generator.md:44-53` (step 5) and `turn/prompts/first-user.md:19-24` and :32-35 (steps 2 and 4) each describe running on their own words. The checklist item must name what is run and how far, so that both run it, or the claim's evidence must hand the commands on. The new place would be the `checklist.md:31-68` template, such as a line beside `Judged on:` (:60).
- `turn/docs/calling.md:6-27` (checklist form) and `turn/scripts/call.py:126-128` and :153-172 (`SCOPES`, item parsing) only if a new line is read.
- `rn/scripts/ccs.py:35-39` `BUILT` is the precedent for such a line.

**Send back only a gap that hinders use**
- `turn/prompts/first-user.md:3-10`: Role, "Where you find none, you hand back…".
- `turn/forms/reading.json:317-353` `stop` (places/did/lacking): add how it hinders the use.
- `turn/prompts/orchestrator.md:16-18`.
- `dev/turn/architecture.md:14-18` turn's Principle 1, "looks only for each item's Good".

**The one test command**
- `rn/scripts/ccs.py:232-247` `test_of`: the one command from the task's `Test:` line.
- `rn/checklists/session/plan.md:55` and :121-122.
- `turn/docs/calling.md:52-53` "joining every check into one".
- `turn/hooks/lanes.json:103-108` `test_after`.

The formatter, linter and type checker must sit inside that command, or a plan item must ask a task to set them up. `rn/checklists/session/plan.md` B-3 and B-6 are the natural places.

## Intent 5: generator and first user settle a gap by messages

**turn's flow and forms**
- `turn/scripts/flow.py:484-496` `first_read` sends the gaps one way. `:46-51` `AGAIN` ("sent_back", "remade") and `:499-502` `sending`/`SENDS` count one-way sends.
- `turn/scripts/flow.py:473-481` `made` gives the first user `prompts.remade(run)` only.
- `turn/scripts/flow.py:564-566` `good()`. An item "outside the purpose" needs a state of its own: who closes it, and what the result holds.
- `turn/scripts/flow.py:505-517` `ended` and `:529-541` `left_asked`: once the two roles talk, decide what still becomes a user question.
- `turn/scripts/flow.py:544-552` `finished`, where the result is written.
- `turn/scripts/prompts.py:100-107` `remade` gives work, parts and reply only; add the generator's answer for each gap.
- `turn/scripts/prompts.py:63-81` `generator`: `sent_back` at :76.
- `turn/forms/reading.json:317-353` `stop`: add "how it hinders the purpose".
- `turn/forms/claim.json`: add, per item sent back, "mended (evidence)" or "outside the purpose (why)". This combines with intent 1.

**turn's prompts and lanes**
- `turn/prompts/first-user.md:8-10` "the work is then made again aimed at it, and you read it again".
- `turn/prompts/first-user.md:39-41` step 6, the `remade` message only. Add reading the generator's answer, and holding or dropping the gap.
- `turn/prompts/generator.md:35`, :41 and :64-66: step 8 takes only `sent_back` and `answers`.
- `turn/agents/first-user.md:3` "sent the work made again, reads it again". `turn/agents/generator.md:3`.
- `turn/hooks/lanes.json:137-204` (first user: `write_only {reply}`, `end_when`) and :65-134 (generator). New message steps need their lanes laid and `dev/turn/tests/test_lanes.py:36` and :45 run again.

**turn's documents and tests**
- `dev/turn/architecture.md:6-9` "through which the generator and the first user go back and forth", and :83-90 "the generator is sent back the items… and the first user is sent the work made again".
- `dev/turn/logical-view.svg`: no arrow between generator and first user (labels "replies" at :72 and :76).
- `turn/CHANGELOG.md:29` "made again aimed at where it stopped… with no other reading between".
- Tests:
  - `dev/turn/tests/test_round.py:58` (sent the stop by message), :193, :200 `test_the_first_user_sends_back_three_times_a_round_at_most`, :211
  - `dev/turn/tests/test_rounds.py:38`, :142, :150, :172
  - `dev/turn/tests/test_parts.py:37`
- Trials: `dev/turn/trials/orchestrator/roles/generator.md:16-17` and `roles/first-user.md:41-42` (message shapes); `dev/turn/trials/roles/kept.py`.

## Principle 4 decision: the first reading without the claim, then talk

- `dev/architecture.md:20-23` and :142-149: change to "the first reading is on its own". See the general section.
- `dev/turn/architecture.md:91-97` "the first user is not given the generator's reply… a reader shown the maker's claim finds the Good it was told to find (Principle 4)". Keep it for the first reading and add the exchange after.
- `turn/scripts/prompts.py:84-87` `reader`, "not the CCS nor the generator's reply". Keep it. `:29-36` and :37-53 `without_run_files` with `apart` keep the CCS and the replies from the first user; keep them for the first reading.
- `dev/turn/architecture.md:200-201` "The flow gives no role the run's own files, nor the first user the CCS". Keep it; the generator's answers go to the first user by message, not as files it reads.
- `turn/prompts/first-user.md:6-8` "you did not make the work, so you find only the Good its lines give". Keep it for step 2.
- `dev/turn/tests/test_given.py:228` `test_the_first_user_is_given_neither_the_ccs_nor_the_generator_s_reply_nor_the_state` stays true for the first reading.

## Where intents pull against each other or against a written principle

1. **Intent 5 against `dev/architecture.md:247-249`** ("Roles do not message one another… goes through the orchestrator") and Principle 1 (:16). Either the orchestrator relays every message, which costs moves against intent 2, or the principle changes. Direct messages between roles also need lane to read values from messages.
2. **Intent 5 and the Principle 4 decision against `dev/architecture.md:147-149`** ("A reader shown another's verdict finds what it was told"). After the first reading, the first user is shown the generator's reasons for "outside the purpose", which is the exact risk that line names. Today nothing bounds how far the first user may be argued down.
3. **Intent 3 ("rn does not commit and push at each answer") against Principle 6** (`dev/architecture.md:26-27`, "each decision [is] kept before the next move") and `dev/rn/architecture.md:186-187`. It also takes away what the learnings read (`dev/architecture.md:205-216`, `rn/checklists/session/learnings.md:383-384`).
4. **Intent 3 ("a CCS added to, not starting again") against lane's design** (`lane/hooks/lane/started.py:1-5`, `dev/lane/architecture.md:87-92`, "the JSON it starts from is the one place"). turn starts anew only because a lane's files are fixed at start (`dev/turn/architecture.md:97-99`). The cause sits in lane, so the fix belongs there or in how turn hands files over.
5. **Intent 2 (about eight moves) against keeping roles started** (`turn/scripts/flow.py:304-306`): every message to a kept role costs a `waiting` poll (:311-327). It also pulls against intent 5's extra messages. Starting roles fresh avoids polls but loses what they have already read.
6. **Intent 2 dropping the CCS check against `dev/turn/architecture.md:64-70`** ("A Good the CCS cannot give, the generator cannot give either") and `turn/CHANGELOG.md:7`. With intent 3, the generator's named choices take over most of what the check caught. A missing user decision then shows only once the generator meets it.
7. **Intent 1 (only items sent back rewritten) against the result.** The result takes the first user's Goods (`flow.py:544-552`), so no conflict there. But `chosen` is replaced whole each claim (`flow.py:479`) and must be merged.
8. **Intent 4 against `rn/checklists/checklist.md:16-18` and :64-65**, the template every checklist inherits ("signs… each a thing to be found"). Every checklist's lists come from there, so changing code.md alone leaves the pattern in the other eleven.
9. **Intent 4 ("what a machine sees is left to tools") against `code.md` B-6 :162-164**, which asks for a user decision about each gap left out of the checks. That item breeds the technical questions intent 3 removes.
10. **Intent 2 against rn's own user story** "told before and after each step" (`dev/rn/architecture.md:25-26`, `dev/rn/ux.md:137-139`, `rn/README.md:135-137`). That holds for rn's steps; only turn's per-move lines are cut. If the rule is made general, rn's step lines need the same judgment.

## Read whole, and only grepped

**Read whole**
- `.rn/20261013-writ-rebuild/decisions/run-cost.decisions.md`
- `dev/architecture.md`
- turn
  - `turn/prompts/` (all three), `turn/agents/` (all three)
  - `turn/docs/calling.md`, `turn/README.md`, `turn/CHANGELOG.md`
  - `turn/scripts/`: `flow.py`, `forms.py`, `prompts.py`, `state.py`, `call.py`, `turn.py`
  - `turn/forms/claim.json`, `turn/forms/reading.json`
  - `turn/hooks/lanes.json`, `turn/hooks/adapters/items-checklist.py`
- `dev/turn/architecture.md`, `dev/turn/ux.md`, `dev/turn/README.md`
- `dev/turn/tests/helpers.py` lines 205-357
- `dev/turn/trials/orchestrator/roles/generator.md` and `roles/first-user.md`
- lane's lane checks: `lane/hooks/lane/lanes/` `follow_next`, `wait_for`, `end_when`, `in_form`, `every_item`, `write_only`, `hands_off`, `__init__`
- rn
  - `rn/prompts/`: `orchestrator.md`, `build.md`, `design.md`, `plan.md`, `messages.md`, `feedback.md`, `approval.md`, `learnings.md`
  - `rn/scripts/ccs.py`
  - every checklist under `rn/checklists/` (12 files)
- `dev/rn/architecture.md`

**Only grepped or read in part**
- turn: `turn/hooks/hooks.json`; `turn/scripts/items.py`, `parts.py`, `record.py`, `template.py` (not read)
- `dev/turn/tests/test_*.py` (test names), `properties.py`
- `dev/turn/trials/` other scripts, `dev/turn/logical-view.svg` (text labels), `dev/who-does-what.svg`, `dev/rn/logical-view.svg`
- rn
  - `rn/README.md` (:100-230), `rn/CHANGELOG.md` (:1-30 and grep)
  - `rn/scripts/repo.py` (:90-140), `session.py`, `rn.py`
- `dev/rn/ux.md` (grep and :128-150)
- `dev/rn/tests/test_ccs.py` (:400-430, :980-1015), `dev/rn/tests/test_session.py` (test names)
- `dev/rn/trials/moves/cases.py` (:885-910, :1065-1120), `stand.py` (:100-135), `place.py`, `moves.py`
- `dev/rn/trials/acceptance/acceptance.py` and `user.md`
- lane
  - `lane/hooks/lane/started.py` (:1-30), `guard.py`, `step.py`, `ports.py`
  - `dev/lane/architecture.md` (:86-94)
  - `dev/lane/tests` (file names only)

**Not opened**
- `.claude/rules/dev.md`
- the turn trials' `results.json` files
- `dev/rn/tests/` other than the two above
- the rest of lane's hook code