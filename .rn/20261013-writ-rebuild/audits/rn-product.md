# rn product audit (read-only, at c537dc3)

Slice: rn/README.md, rn/CHANGELOG.md, rn/.claude-plugin/, rn/skills/{up,ty,gm}, rn/scripts/ (rn.py and
its four links), dev/rn/{architecture.md,ux.md,README.md,cosmic-ray.toml}. 52 findings; one is a
defect verified by running it (F1). The unit tests pass (191, 3.5 s).

## rn/scripts/rn.py

1. `rn/scripts/rn.py:1076-1077` `if stage in (BUILD,): made = [c.work for c in calls(folder) if c.stage in (DESIGN,) and c.work not in (PLAN,)]`.
   Kind: defect (code.md B-6, B-2). `/rn:ty` at the plan sign-off moves the stage to design (ty step 2) and
   then makes the learnings call (ty step 3), so that call carries `stage: design`. When the user then
   says no document is needed, `rn.py state --stage build` (up :232) stops with "the design stage made
   learnings, which go to the design sign-off", and the stop's own action, `rn.py proposal design`,
   shows a design sign-off with nothing to approve. Verified with a scratch test on the StateTest
   fixtures (calls 0001 plan/plan, 0002 learnings/design). This breaks README :134, ux :20-21 and
   architecture :119-123. Fix: count only document works (`t<n>`, `checklist-<kind>`), or the works
   that `WORKS_SHOWN[DESIGN]` shows, and add the test the suite lacks (test_rn.py:1000-1011 has no
   learnings call).
2. `:82` `TASK_WORK = re.compile(r"t[0-9]+")`, `:84` `WORKS`, `:220-226` `worked`, `:1230-1238` `served`,
   `:182-185` `WORKS_SHOWN`, `:1413-1422` `shown_works`, `:1449` `label = work.upper()`, `:1152` and
   `:1294` (each new call takes the latest call's decisions).
   Kind: inconsistency, the user's decision. Every turn call of a task goes under one work, `t<n>`, so a
   research call's decisions are carried into the document's call, and `shown_at` (:1440-1457) shows
   only the paths of the latest call. It should be one work per output, as architecture :124-126 says:
   each research result, trial result, document and task result named on its own.
3. `:1241-1254` `done_made`: "For each call on a task's work whose task the plan no longer holds, done, in the order made, its CCS and its result ..."; also `:1262-1263` in the `run_ccs` docstring and `:1300-1301`.
   Kind: inconsistency, the user's decision. The plan's CCS gets every CCS and result of each done task.
   It should hold, for each done task, only what it served, decided and made. Its docstring's tail, "a
   research result made before a decision among them", says nothing clear (code.md B-3).
4. `:765` `entry`, `:808` `decisions_of`, `:786-796` (the dict check inside `calls`).
   Kind: duplication (code.md B-5). This redoes turn's `call.entries` and `call.read_ccs`
   (rn/scripts/call.py:120, :92), which rn ships as a link but never imports. Use one or the other (see
   #22).
5. `:1658-1661` `lines_of`, used by `begun` :1667, `conversations` :1678 and `typed` :1591, beside `told` :1732 using `records.entries`.
   Kind: duplication (code.md B-5). There are two readers of the same JSONL, one without the type
   filter. Use one reader: the `user` and `assistant` entries carry `cwd`, `gitBranch` and `timestamp`.
6. `:1295-1298` writes the cut part (`write_text(part, cut + "\n")`) before `:1318` `checklists(kind, root)`, which can stop.
   Kind: defect (code.md B-2). A stop there leaves an uncommitted `<nnnn>-steering.md` or
   `-learnings.md`. The next `rn.py ccs` then stops in `pushed()` and sends the AI to `rn.py state`,
   and `rn.py decide` commits the stray file. Check the kind before writing anything.
7. `:1569` `waits = f"Wait at the {signoff} sign-off for the user's answer: {ANSWER}"`; also up :297-298 (Next after `--stage finished`).
   Kind: inconsistency (prompt.md B-5). up :61-62 sets Next as `Step <n> of /rn:up on <work>: <what is
   left of it>`, and plan.md F-1 has "the step of /rn:up to take next, by its number". The script writes
   another form itself. Use one form.
8. `:118` `VALUES = {"stage": STAGES, "signoff": (NONE, PLAN, DESIGN, DELIVERABLE)}`, `:120` `APPROVED`, `:174` `SIGNOFFS`, `:186` `ANSWERS = ("approved", "feedback")`, `:187` `ANSWER = "/rn:ty to approve, /rn:gm <feedback> ..."`, `:1579` `COMMANDS`.
   Kind: duplication (code.md B-5). The sign-offs are listed in three places, and the answers in three.
   The front-matter keys appear as literals (`"signoff"`, `"pr"`, `"stage"` at :118, :530, :827, :880,
   :891, :914, :1451, :1505, :1544, :1572, :1615, :1628) beside `STAGE` and `KEYS`. Derive each from one
   table.
9. `:73` `CALL = re.compile(r"([0-9]{4})-(ccs\.json|result\.json|steering\.md|learnings\.md)")`.
   Kind: duplication (code.md B-5). It spells out `CCS` and `RESULT` (:74-75) and `PART` (:87) again.
   Build it from them.
10. `:428-481` `items_of`/`task_of` and `:1332-1362` `item`/`by_id`/`decided`.
    Kind: duplication (code.md B-5). These are two readers of the steering's list items, with two rules
    for where an item ends. Keep `items_of`.
11. `:157` `LEARNING = re.compile(r"- (?P<id>L[0-9]+): \S.*")` and `:162` `NUMBERED = re.compile(r"- L[0-9]+: ")`; `:84` `WORKS` spells out the work patterns of :79-83.
    Kind: duplication (code.md B-5). Derive each from the other.
12. `:623-624` `expected action {number} of {task.id} as \`  - [ ] {number}. <what is done>. <who does it>\``.
    Kind: inconsistency (code.md B-2/B-5). This is a third action form beside the two of plan.md F-1
    (:72-73). The stop should quote those two.
13. `:1-34` (module docstring).
    Kind: noise (code.md B-3/B-5). It restates the session layout and the CCS shape from the
    architecture, and has drifted: it lists steering, learnings and `turn/`, but not the research and
    trial results at `<session>/<path>`. Say only what the module does and why.
14. `:1302-1309` "rn's checklist for a fix, which turn's generator holds whenever it changes a work already there"; also dev/rn/architecture.md:93-94 "each passing rn's plan checklist and its checklist for a fix".
    Kind: inconsistency (code.md B-3; architecture.md B-6). fix.md goes to turn as a `fix` constraint
    (:1322), not as a `checklist` entry, so no first user judges it, and turn/agents/generator.md never
    names it. The comment also restates the CCS layout of architecture :124-132. Either hand fix.md as a
    checklist, or say in both places what holds it.
15. `in (x,)` membership, 35 times: `:402, 498, 531, 553, 659, 877, 880, 969, 1012, 1040, 1076, 1077, 1085, 1110, 1123, 1228, 1251, 1296, 1300, 1319, 1420, 1434, 1435, 1450, 1512, 1520, 1545, 1557, 1568, 1594, 1616, 1629, 1687, 1799, 1894`, beside `==`/`!=` at :353, 518, 553, 637, 695, 805, 1070, 1469, 1505, 1678. The reason is given only at :1891-1893.
    Kind: complexity, the user's decision (code.md B-3). Make each a plain `==`; give each mutant that
    truly cannot be told apart `# pragma: no mutate`, with the reason written once in cosmic-ray.toml
    (#27).
16. `:1707-1712` `session_files`: "the steering, the learnings, and each file of its calls to turn".
    Kind: inconsistency (code.md B-5). It leaves out the research and trial results in `<session>/`
    (architecture :203), though ty :60-61 and architecture :175 hand the learnings' maker "the
    session's files". List every file under the session folder.
17. `:1296` `f"## {LEARNINGS}"` (stripped again at :1012).
    Kind: inconsistency. The part turn makes opens with a heading, but learnings.md F-1 shows none ("the
    list left empty"), so turn's first user checks F-1 against a file that differs from it. Cut an empty
    part, or show the heading in F-1.
18. `:1230-1231` `if not TASK_WORK.fullmatch(work): return said`.
    Kind: inconsistency (judgement). `learnings` and `checklist-<kind>` get the goal and every criterion
    as `serves`, though they serve no criterion of the user's work. Give `serves` to the deliverable
    alone. Noise in the same place: `:1227` computes `said` before `:1228-1229` returns `{}` for the plan.
19. Names (code.md B-3/B-5):
    - The CCS key `deliverable` (`ENTRIES["work"]`, :92) holds every work's paths, beside `DELIVERABLE`,
      which is a work, a stage, a sign-off and a kind.
    - `learning()` (:1635) returns a folder, beside `learnings_of`, `LEARNINGS` (a heading),
      `LEARNINGS_WORK` (used as a stage in `STAGES` :116) and `LEARNT` (a file).
    - `held()` (:1195) is a has-path check, beside `held_form` (:679).
    - `shown` names commits (:1556), the alias `Shown` (:1410) and (name, text) pairs (:1760).
    - `kept` names a commit, a folder (`records.kept`) and a time (:1718).
    - The parameters `entry_` (:1715) and `at_` (:1332) are renamed only to avoid shadowing functions.
20. `:845-852` `gh()`: "then run `rn.py start` again with the same arguments".
    Kind: inconsistency (code.md B-3). A general name carries the stop text of one caller. Give `run_start`
    the action, or rename the function.
21. Layout (code.md B-3):
    - Constants sit mid-file: `RUN_FILES` :290, `CHANGED_TASK` :980, `Shown` :1410, `COMMANDS` :1579.
    - Callees sit far from their callers: `joined` :1365 is used at :529, `decided` :1354 at :1227,
      `learning` :1635 at :1124.
    - The top-of-repository and branch lookups are repeated at :877, :1403, :1587-1588 and :1755-1756.
    - Every `run_*` takes `(args, root, today)`, though `today` is used only by `run_start` (code.md B-4,
      low).

## rn/scripts links

22. `rn/scripts/call.py` and `rn/scripts/forms.py` (links into turn/scripts).
    Kind: noise (code.md B-4). rn.py imports only `records` and `template` (:55-56); no file under
    dev/rn/tests imports them. The trials' `import call` (dev/rn/trials/moves/stand.py:31,
    flow/write.py:19) runs from the stand-in turn's scripts folder (place.py:112, flow.py:153). Both
    links are installed on users' machines and excluded in cosmic-ray.toml:8-9. Remove both, or keep
    `call.py` only if #4 is fixed by using it. `records.py` (`kept`, `entries`, `said`, `wrapped`) and
    `template.py` (`keys`, `body`, `headings`) are used.

## rn/skills/up/SKILL.md

23. `:174-185` "read the result whole, then each item's `good` at its `lines` in the work. A Good its lines fall short of, or an item without one, is a point behind it ...".
    Kind: inconsistency, the user's decision. rn's orchestrator re-judges each Good. This goes against
    architecture :151-153 ("it judges none of turn's lines") and the decision that only the first user
    looks for Good. On `returned`, keep the move and go on; drop step 4's "and check what it returns"
    (:145).
24. `:31-33` "`t<n>` for what task T<n> makes outside the steering", `:190` "The task's work is `t<n>`", `:197` "one call, step 4 on the task's work".
    Kind: inconsistency, the user's decision (#2). Name each output's work on its own.
25. Fixed strings left to the AI:
    - receiver, use, kind and `--has` for `plan` (:216-219), `deliverable` (:248-250) and
      `checklist-<kind>` (:154-156), and in ty :63-65 for `learnings`;
    - Next strings at up :111-112 and :232-233, ty :49-52 and gm :127-128.

    Kind: complexity (prompt.md B-3 "an operation that must give the same result every run worked out by
    the AI", B-4). rn.py should default these for its own works, and set Next from `APPROVED` and the
    step.
26. `:123-126` `grep -l '"work": "<work>"' <session>/turn/*-ccs.json | tail -n 1`.
    Kind: complexity (prompt.md B-3). This redoes `latest()` and depends on `write_json`'s indent (:389).
    Have an rn.py subcommand print a work's decisions.
27. `:158-161` "Reply in one line that the work is being made ..." and `:190-193` "before it, tell the user in one line what it will do, how far and how, and after it ...".
    Kind: complexity (prompt.md B-6 "what the user must see while the AI works left to the AI's words").
    User story 4 (architecture :25-26) rests on lines written on some runs only. Have the script print
    them (`rn.py ccs`, `rn.py state`).
28. `:120-122`, `:130-133`, `:283` take the "Points to decide" and "Learnings to decide" forms from the README's Example.
    Kind: complexity and duplication (prompt.md B-3/B-4; usability.md B-7). The newcomers' README serves
    as the prompt's form file, and the same form is described again in ux :122-126. Keep the form in one
    form file, which up names and the README shows, or have a script print the map of points from the
    decisions.
29. `:272` "Have each work it touches made again, step 4, as the step that made it gave it".
    Kind: complexity (prompt.md B-3). In a fresh conversation the AI must rebuild the kind, receiver, use
    and `--has` of the earlier call. Have rn.py remake a call from the work's last CCS.
30. `:50-59` restates what `decide` and `state` do, which rn.py's docstrings hold. `:25-33` restates the session layout, also at rn.py :8-22, ty :16-18, gm :91-93 and architecture :197-208.
    Kind: duplication (prompt.md B-4). Keep the command shapes, what each prints, and only the paths the
    AI reads.
31. `:297` `gh pr ready <the steering's pr>`, then `rn.py state --stage finished`.
    Kind: complexity (prompt.md B-3, low). A fixed command should be done by `state --stage finished`
    itself.

## rn/skills/ty/SKILL.md, rn/skills/gm/SKILL.md

32. `ty :16-30` and `gm :91-106` are nearly word for word the same, and both restate up :42-79. Step 1 is the same at `ty :37-44`, `gm :113-120` and `up :87-90`.
    Kind: duplication (prompt.md B-4 "one thing said in two places"). Keep these conventions once (one
    file that each skill reads first, or have the script print what is needed). The copies have also
    drifted: ty/gm say the steering is "the plan and where the session stands", while up :26 says "what
    is left to reach the goal and where the session stands" (prompt.md B-5).
33. The heredoc instruction appears in three wordings: up :68-75 (a code block), ty :27-29 and gm :103-104 (inline).
    Kind: duplication (prompt.md B-4). Say it once.
34. `ty :60-67` "Run `rn.py records` ... a `--has` for each path `rn.py records` printed".
    Kind: complexity (prompt.md B-3). The AI copies the script's output into another command, and also
    gives the fixed receiver and use. `rn.py ccs learnings` should gather the records itself.

## rn/README.md

35. `:240` "Python 3.9 or later, run as `python3`, and jq, the command-line JSON tool."
    Kind: noise (readme.md B-8). Nothing runs jq: rn.py :896 uses gh's own `--jq`, and turn/README.md:108
    asks only for Python and git.
36. `:123-128` "design: https://github.com/you/app/blob/typescript/docs/design.md" followed by untitled bullets; `:144-149`.
    Kind: inconsistency (readme.md B-4 "the example, run as written, giving other output than the README
    shows"). rn.py prints `T<n>: <url>` (:1449, :1457) and each decision as `- <title>: <says>` (:1468).
    At the deliverable sign-off it also prints each build task's decisions (:1458-1459), which the example
    leaves out. Make the example match the output, or make the output match the example.

## rn/CHANGELOG.md

37. `:15` "rn's own learner reads what led there".
    Kind: inconsistency (usability.md B-13). There is no such role. The learnings are a work that turn
    makes (architecture :171-173).
38. `:23` (Unreleased) does not say that the design sign-off is left out where no document is needed (README :134, ux :20-21), and `:54` (0.9.0) "There is always a Design sign-off" stands with nothing under Unreleased replacing it.
    Kind: inconsistency (usability.md B-21). Add the change.
39. `:14` "Each sign-off shows the link to each work and its core decisions"; also dev/rn/ux.md:82-85 "At the sign-off rn shows the link to each work and its core decisions ... and nothing else".
    Kind: inconsistency (usability.md B-21). The plan sign-off shows the goal and the criteria, with no
    decisions, and the deliverable sign-off shows the criteria and the tasks' decisions, with no links
    (rn.py:1434-1459, README examples). Say what each sign-off shows.

## rn/.claude-plugin/plugin.json

40. `:3` "calls you only at the plan, design and deliverable sign-offs".
    Kind: inconsistency (low). The design sign-off comes only where a document is needed.

## dev/rn/architecture.md

41. `:50` `orch -->|adds each learning the user takes to| cl`.
    Kind: inconsistency (architecture.md B-6). up :295-296 has turn make the checklist, and :145 says
    "No work turn returns is fixed by the orchestrator". The arrow should run from turn.
42. Logical view `:34-54`.
    Kind: complexity (architecture.md B-3/B-4; usability.md B-16).
    - "rn's scripts" are missing from it, though the text has them act at :68, :78, :86, :94, :129,
      :162, :172 and :220.
    - Claude Code's conversation records, which `typed` and the learnings read (:162-163, :175-176), are
      missing too.
    - `steering`, `calls to turn`, `checklists` and `pull request` are data, not components.
    - No box has its kind in angle brackets.
    - `guard` (:43, :53) is turn's, laid by lane; rn has no hooks (CHANGELOG :26), and the physical view
      has no place for it.
43. Physical view `:194-195`.
    Kind: inconsistency (architecture.md B-4). It does not show the links (records.py, template.py,
    call.py, forms.py). "rn's own, one per kind" also holds checklist.md, fix.md and usability.md, which
    are no kinds.
44. `:130-131` "a plan's CCS holds, in place of what it serves, the calls of each done task, what it served, decided and made"; `:15-16` rn's Principle 2 "replans from the steering alone".
    Kind: inconsistency, the user's decision. A plan's CCS should hold, per done task, only what
    replanning needs. Principle 2 itself contradicts any done-task input: say "from the steering and what
    each done task served, decided and made".
45. `:167-170` "made from the steering and the calls to turn alone. So it says nothing turn's first user did not read."
    Kind: inconsistency (architecture.md B-6). The proposal shows the decisions from the CCS constraints,
    but turn shows its first user only the work, `has` and the checklists (turn/scripts/call.py:88
    `run["shown"] = run["work"] + run["has"] + run["checklist"]`), not the CCS.
46. `:74-79` lists the steering's contents (plan.md F-1); `:124-132` lists the CCS contents (run_ccs); `:171-178` says what the learnings' maker reads (ty step 3, run_records); `:217-219` gives the call numbering; `:225-226` describes the texts in the git folder.
    Kind: noise (architecture.md B-7, behaviour and lists written again). Keep each decision and link the
    rest.
47. `:103-104` "in the plan stage only the research or trials a gap calls for" (tasks) vs `:107` "its actions are ... research into current practice ..., a small trial, or the making"; ux.md:49 "A task is ... such as research".
    Kind: inconsistency (usability.md B-14). Research is both a task and an action. Decide which.
48. `:5-7` "decides every move from the steering, the plan and where the session stands".
    Kind: inconsistency (architecture.md B-8 "one thing under three names"). By :74-78 the steering holds
    the plan and where the session stands.

## dev/rn/ux.md

49. `:196` "stays, in the README and the design in the user's repository".
    Kind: inconsistency (ux.md B-6). Documents are only those the purpose needs (:20-21). Say "in the
    documents rn writes".
50. `:184` "What the user gains with rn, each with why it holds; these are why the user chooses rn."
    Kind: noise (ux.md B-5). It tells what the section is.

## dev/rn/cosmic-ray.toml

51. `:8-9` `"rn/scripts/call.py", "rn/scripts/forms.py"`.
    Kind: noise, unused (goes with #22).
52. The file has no `# pragma: no mutate` reason and no cr-filter-pragma step.
    Kind: inconsistency, the user's decision (#15). The reason for the idiom now sits at rn.py:1891-1893
    (and lane's template.py:175-176). Write it once here.

dev/rn/README.md: no finding.

## Structure

| Part | Takes on | Split / reshape |
|---|---|---|
| `rn.py` (1,895 lines) | the stop and input checks; git/gh/files; the steering's form, parse and edits; the session's record and calls; building the CCS; the proposals; Claude Code records; the learnings' stretch | modules `stop` (Stop, named, given, joined), `repo` (ran, git, gh, at_top, base, changed, at, push, pushed, read/write), `steering` (forms, sections, items_of, Task, *_out, parsed, render, tick, pruned, put_plan), `session` (paths, current, kept_steering, keep, Call, calls, latest, part_of, moved, learnings I/O), `ccs` (served, done_made, the CCS builder; or turn's `call.py`), `proposal` (SIGNOFFS..ready), `conversations` (project_folders, conversations, since, told, typed, on `records.entries`), `stretch` (stretch, history, session_files, turns_learnings), `rn` (parser, main, thin `run_*`) |
| `run_state` :1093 | put back a part (plan or learnings), tick, prune, move the stage, Next/Open, keep, remove the records folder | `put_part()` and `move_stage()` return new values; `run_state` composes them and keeps |
| `run_ccs` :1257 | check the args; cut a part; collect the done tasks' outputs; find the finished work; build the CCS; keep | `cut_part()`, `ccs_for(work, ...)` (pure), then keep; do every check before any write (#6) |
| `run_start` :855 | start a new session; or reopen the PR of one already started | `start_branch()` and `open_pr()`; the second path is just `open_pr()` |
| `ticked` :928 | tick the actions and prune the done tasks | the caller calls `tick` then `pruned` |
| `run_proposal` :1529 | check stage and sign-off; diff against the last proposal; render; set waiting | `proposal_text(then, now)` (pure) apart from the keep |
| up SKILL.md (301 lines) | reference conventions (Role :21-79), 11 steps, fixed strings, forms for the user's messages | shared conventions once for up/ty/gm; fixed strings and Next to rn.py (#25); message forms to a form file or script (#28) |
| ty/gm Role | copies of up's Role | point to the one place (#32) |
| architecture.md "Logical view" lines :56-184 | decisions mixed with behaviour lists | keep the decisions and why; link plan.md F-1, rn.py and the skills (#46) |

## Cross-slice

- turn/scripts/call.py:88 (the first user is not shown the CCS) contradicts architecture :167-170 (#45).
- turn/agents/generator.md never names `fix`, yet rn.py:1302-1309 and architecture :93-94 rely on it
  (#14).
- rn/checklists/session/learnings.md F-1 has no heading, while rn cuts `## Learnings` (#17).
- rn/checklists/session/plan.md:72-73 has two action forms, and rn.py:623-624 a third (#12). plan.md F-1
  has `pr: <the pull request's URL>`, while rn writes `pr: none` before `start` opens it (rn.py:891).
  plan.md F-1's Next form differs from rn.py:1569 (#7).
- turn/agents/up.md step 5 and the "goods" move in turn/scripts sit beside rn up step 4's own Good check
  (#23). rn would then judge Good twice in a row, against the decision.
- dev/rn/tests/test_rn.py:1000-1011 has no case for a learnings call in the design stage (#1).
- dev/architecture.md:262-265 says `dev/check.sh` fails on lines copied between any two files, but
  check.sh:23-25 runs pylint duplicate-code on Python only. The copies between ty and gm (#32) pass.
- lane/hooks/lane/template.py:175-177 uses the same membership idiom with its own reason (#52).
- dev/rn/trials/moves/stand.py:31 and flow/write.py:19 import turn's `call` (#22).

## Prior audit (.rn/20261013-writ-rebuild/audits/rn.md), point by point in this slice

- §1 split, `run_*` size, far callees, mid-file constants: kept (Structure, #21).
- §1 up fixed strings, Next texts, decision grep, session layout: kept (#25, #26, #30). ty/gm copies:
  kept (#32).
- §1 plan.md opening: dropped here, not in this slice (checklists).
- §2.1 call.py/forms.py: kept (#22, #51). §2.2 jq: kept (#35). §2.3 moves.py model: not in this slice.
  §2.4 "rn's own learner": kept (#37). §2.5 docstring: kept (#13). §2.6 :1302-1309: kept and widened
  (#14). §2.7 idiom: kept, now 35 places listed (#15). §2.8 done_made docstring and §2.9 `served`: kept
  (#3, #18).
- §3.1 to §3.3: kept (#4, #5, #9). §3.4 tests: not in this slice. §3.5 to §3.8: kept (#10, #11, #8,
  #30).
- §4.1 work naming: kept (#2, #24). §4.2 session_files: kept (#16). §4.3 the heading: kept (#17). §4.4
  `served`: kept (#18). §4.5: kept (#3, #44). §4.6: kept (#47; the plan.md half is not in this slice).
  §4.7: kept (#41, #42, #43). §4.8: kept (#38). §4.9 `moved` counting research: kept and found worse,
  since it is reached on every run where no document is needed (#1). §4.10: kept (#12). §4.11: kept
  (#19).
- §5: not in this slice.
- New here: #1 (verified), #6, #7, #14 (the architecture half), #20, #23, #27 to #29, #31, #33, #34, #36,
  #39, #40, #42 (the scripts and records missing), #45, #48 to #50, #52.

## Read

rn/README.md 274; rn/CHANGELOG.md 139; rn/.claude-plugin/plugin.json 11; rn/skills/up/SKILL.md 301;
rn/skills/ty/SKILL.md 75; rn/skills/gm/SKILL.md 65; rn/scripts/rn.py 1895; rn/scripts/call.py 165;
rn/scripts/forms.py 395; rn/scripts/records.py 118; rn/scripts/template.py 185; dev/rn/architecture.md
237; dev/rn/ux.md 200; dev/rn/README.md 13; dev/rn/cosmic-ray.toml 18.

Checklists and the base, read whole: rn/checklists/product/code.md 202, prompt.md 150, readme.md 219,
ux.md 190, architecture.md 218; rn/checklists/usability.md 208; dev/architecture.md 411;
.claude/rules/dev.md 115; .rn/20261013-writ-rebuild/audits/rn.md 125.

Read in part, to check claims: rn/checklists/session/plan.md :40-100; session/learnings.md :1-60;
fix.md :1-30; turn/README.md :15-40 and grep; turn/agents/generator.md (grep); dev/rn/tests/test_rn.py
:1-40, :990-1030; dev/rn/trials/moves/stand.py :20-40; flow/write.py :10-25; moves/cases.py :15-30;
dev/check.sh (grep).

## Not read

rn/scripts/__pycache__/*.pyc: compiled files, ignored by git (.gitignore:3), not part of the product.
