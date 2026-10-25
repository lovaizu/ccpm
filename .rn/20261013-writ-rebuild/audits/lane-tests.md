# lane's tests and trials audit (read-only, at c537dc3)

Scope: every git-tracked file under `dev/lane/tests/` and `dev/lane/trials/`; code under test read
where a test needed it. `python3 -m unittest discover -s dev/lane/tests`: 504 tests, 0.4 s, OK;
coverage (`.venv`, branch) 100 % of `lane/hooks/lane` and `lane/scripts`. `ruff --select E501`
(line-length 100 from `ruff.toml`): 22 lines over in the slice. No trial result or record JSON is
tracked under `dev/lane/trials/` (the trial writes `<run>.jsonl` into a folder outside the repo), so
there were none to judge.

41 findings. Line numbers are each file's own.

## Defects

1. `dev/lane/trials/trial.py:89` `DRIFT = ("/notes:changelog Add an entry…"` is rebound at `:163`
   `DRIFT = ("This run tries memo's hooks…`; `:434` `changelog(new, "drift", DRIFT)` and `:436`
   `changelog(new, "python", DRIFT, …)` send memo's text, which never calls `/notes:changelog`, so
   the `drift` and `python` trials try nothing. Kind: defect (code.md B-5, one name for two things).
   Should be: `NOTES_DRIFT` and `MEMO_DRIFT`. (Prior audit: kept.)
2. `dev/lane/trials/trial.py:423-436` `else: … changelog(new, "python", DRIFT, no_python(new))`: any
   action not named (a typo such as `drfit`) runs the `python` trial, a paid Claude Code run; and
   `:411` `action, *folders = sys.argv[1:]` dies with a bare ValueError on no arguments. Kind: defect
   (code.md B-2). Should be: an `elif action == "python"` and a usage stop naming the actions, as
   `lay.py` does with `USAGE`.

## dev/lane/tests/helpers.py

3. `:190-197` `recorded`'s docstring, "…each with the request as sent after it, here given text
   apart from them; for each text among the calls, the subagent's reply…" (line 195, 125 chars):
   garbled, and one sentence for four kinds of item. Kind: noise/complexity (code.md B-3, F-1).
   Should be: one line per kind of item (tuple = call, `Failed` = error, `str` = told, `dict` = entry
   as is), wrapped at 100.
4. `:1-3` "its subagent `changelog-writer` with the steps of lane's README" and `:52-69` `STEPS`: the
   README shows only step 3 (`lane/README.md:22`), and the trial's own `notes`
   (`dev/lane/trials/notes/agents/changelog-writer.md:13-16`) has other steps 1, 2 and 4. Two
   `notes` fixtures that differ, neither one the README's. Kind: duplication/inconsistency (code.md
   B-5). Should be: say the steps are the tests' own (the frontmatter tools line and Out line are
   what the tests need), or have one `notes` plugin both use.
5. `:32-44` re-exports every lane but `write_only`, so `test_write_only.py:10` and
   `properties_write_only.py:16` take `from lanes import write_only` while every other test takes
   `from helpers import <lane>`. Kind: inconsistency (code.md B-3, last item). Should be: add
   `write_only` to the list, the two imports through helpers.

## Duplicated helpers across the test files

6. The pattern "a call read from `{"cwd": …, "tool_name": …, "tool_input": …}`" is written again in
   `test_call.py:15-17` (`runs`), `test_hands_off.py:11-13`, `test_start_with.py:17-19`,
   `test_read_only.py:21-24`, `test_in_form.py:32-35`, `test_write_only.py:16-19`,
   `test_call.py:340-341`, `properties_shell.py:114, :126, :142, :156`,
   `properties_write_only.py:27-35`, and `"/r"` as the folder in four files (`test_call.py:12`,
   `test_shell.py:10`, `test_shell_reads.py:10`, `test_hands_off.py:12`). `PluginTest.called`
   (`helpers.py:94`) already builds the event. Kind: duplication (code.md B-5). Should be: one
   `helpers.read(tool, given, cwd=HERE)` and one `HERE`.
7. "about to end having made the calls" is built three times the same way:
   `test_end_when.py:14-18`, `test_every_item.py:28-32`, `test_test_after.py:17-21`
   (`call.End(helpers.made(self.base, list(calls)), reply, False)`). Kind: duplication (B-5).
   Should be: `helpers.ended(base, calls, reply="")`.
8. Each lane's guard class lays its sentence by hand-replacing `STEPS`/`LAID` and then calls
   `self.guard(json.dumps(event), (helpers.AGENT, "<n>:<lane>:<takes>"))`: `test_as_printed.py:257-266`,
   `test_follow_next.py:137-146`, `test_read_whole.py:166-177`, `test_wait_for.py:110-118`,
   `test_in_form.py:178-187`, `test_read_only.py:95-126`, `test_write_only.py:129-138`,
   `test_guard.py:80-87, :118-131, :236-244, :297-309, :317-327`. The sentence and the word are typed
   apart, so they can disagree. Kind: duplication (B-5). Should be: one `GuardTest.lay(step, lane,
   takes)` that writes `lanes.sentence(...)` into the step and keeps the word, as `lay.py` would.
9. Same classes, two names: `TestGuard` (`test_as_printed.py:254`, `test_follow_next.py:132`,
   `test_read_whole.py:163`, `test_wait_for.py:107`) and `TestLaid` (`test_in_form.py:175`,
   `test_read_only.py:92`, `test_write_only.py:126`). Kind: inconsistency (B-5, two names for one).
   Should be: one name.
10. `GuardTest.setUp` (`test_guard.py:30-33`) writes `helpers.LAID`, which every subclass but
    `TestStop` and `TestOtherAgents`/`TestCommandLine` overwrites at once. Kind: noise (B-4). Should
    be: the write in the classes that use it, or the `lay` helper of 8.
11. The hook command's format `exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" <agent>
    <step:lane:takes>` is typed by hand in `test_guard.py:282-286`, `test_lanes.py:196-199,
    :236-239`, `test_read_only.py:107-112`, `test_lay.py:20-27` (expected value, fine), `:781-784`,
    `:893`, `:917-918`, `:929`, and split again in `trial.py:363` (`split("exec ", 1)[1]`), beside
    `lay.py` writing it and `dev/lane/testing.py:136-149` parsing it. Kind: duplication (B-5). Should
    be: tests that need a current-form command take `lay.command(...)`; only `test_lay.py`'s expected
    value and the older forms of `TestUp` written out. (Prior audit 3.1: kept, widened.)
12. The Hypothesis guard `try: from hypothesis import … except ImportError: raise
    unittest.SkipTest(...)` plus `testing.load_hypothesis_profile()` is repeated in
    `properties_forms.py:10-17`, `properties_hand_on.py:10-17`, `properties_shell.py:11-20`,
    `properties_write_only.py:10-19` (and turn's and rn's `properties.py`). Kind: duplication (B-5).
    Should be: kept once in `dev/lane/testing.py`.
13. `test_python_check.py:68-85` runs `subprocess.run(["/bin/sh", "-c", self.command], …)` again
    instead of `run_hook` (`:33-46`), and leaves out `env.pop("PYTHONPATH", None)` that `run_hook`
    does. Kind: duplication/inconsistency (B-5). Should be: `run_hook` takes `agent_type`.

## dev/lane/tests/test_lay.py

14. 986 lines, 12 classes for print, step rewriting, hooks.json, code placing, validation, proposal
    checks, run values, in_form, `up`, main: mirrors `lane/scripts/lay.py` doing six things. Kind:
    complexity (B-5). Should be: split with lay.py (see Structure). (Prior audit 1.1: kept.)
15. `:958-975` `test_lanes_own_code_is_taken_before_modules_of_the_same_name` and `:977-986`
    `test_the_script_exits_with_what_main_gives` both `runpy.run_path(lay.py, "print")` and assert
    `(0, PRINTED)`; the second adds nothing the first does not fail on. Kind: duplication (B-7).
    Should be: drop the second, its "coverage counts it" reason moved to the first.
16. `:863-885` `test_code_not_an_older_copy_is_left_as_it_is`: five cases set up by `if
    os.path.islink…; shutil.rmtree…; if what == "a link" … elif …`, one with `lay.CODE` patched;
    `:606-673` `TestProposal` branches `None`/`str`/dict in the body. Kind: complexity (B-7). Should
    be: a setup per case in the table (a callable or the files to write), no branching in the body.
17. `:17` "The proposal of lane's README: hands_off on step 3" and `test_guard.py:16` "The lane the
    README lays on step 3": the README proposes write_only and hands_off (`lane/README.md:39-43`).
    Kind: inconsistency (B-3, says something else). Should be: "hands_off of the README's proposal".
18. `:70-87`, `:458`, `:808` helper methods (`proposal`, `propose`, `hooks`, `code`, `up`) with no
    docstring or types, while `helpers.py` gives both. Applies to most test files' helpers
    (`test_call.py:340`, `test_guard.py:86`, `test_hook.py:45, :51`, `test_hands_off.py:11`,
    `test_read_whole.py:28`, `test_lanes.py:207`, `test_step.py:55`, `test_shell.py:13`,
    `properties_shell.py:30`). Kind: inconsistency (code.md F-1). Should be: one line and types each,
    as helpers.py does.

## dev/lane/tests/test_guard.py

19. `:367-386` `TestRun` holds hook.run's agent filter, while `test_hook.py:34-121` has its own
    `TestRun` of hook.run; and `test_hook.py:48` calls `hook.run("p", checks, …, err)` without
    `agent`, the only caller using the default `agent: str | None = None` (`hook.py:41`; the one
    product caller, `lanes/__init__.py:263`, always passes it). The tests reveal the default is
    test-only. Kind: duplication (B-5) + noise in the product (B-4). Should be: hook.run's tests in
    test_hook.py alone, `agent` required. (Prior audit 2.2: kept.)
20. `:209-224` `test_lanes_given_to_the_entry_of_another_event_let_it_through_saying_so` sits in
    `TestEnd` but tests the command line's form, as `TestCommandLine` (`:343`) does. Kind: complexity
    (B-3). Should be: in `TestCommandLine`.
21. `:116` `TestEnd.LAID` shadows `helpers.LAID` (the laid agent file) for a tuple of hook words;
    `test_follow_next.py:135` `TestGuard.SENTENCE` shadows `helpers.SENTENCE`. Kind: inconsistency
    (B-5, one name for two things). Should be: `WORDS`, `FOLLOW`.
22. `:184-192` `test_a_step_no_longer_saying_the_sentence_is_told_once` holds two behaviors (told,
    then let end after answering); same in `test_read_whole.py:144-153` (input gone, input empty),
    `test_every_item.py:94-116` (`# And:`), `test_schema.py:179-197`. Kind: B-7. Should be: one test
    each.
23. No `if __name__ == "__main__": unittest.main()` in `test_guard.py`, `test_lay.py`,
    `test_python_check.py`, `test_step.py`, `properties_shell.py`; every other file has it. Kind:
    inconsistency (B-3). Should be: the same in every file.

## dev/lane/tests/test_lanes.py

24. `:117`, `:146`, `:187` patch `lanes.LANES` with stand-ins of three places (`"Put `<a>` into `<b>`
    by `<c>`."`) and `SHOWN=2`, which no lane has (the most is two places, `in_form`/`test_after`;
    `SHOWN` only `wait_for = 1`, `lanes/wait_for.py:20`). The tests hold generality of
    `slots`/`alone`/`fits` (`lanes/__init__.py:76-115`) no requirement asks. Kind: noise, in tests
    and product (B-4, "code more general than its callers use"). Should be: the code for the lanes
    there are, these three tests gone.
25. `:18` `readme_rows` and `:26` `test_each_lane_has_the_action_and_wording_of_its_row_in_the_readme`
    read `lane/docs/lanes.md`, not the README. Kind: inconsistency (B-3). Should be: `lanes_rows`,
    "…of its row in docs/lanes.md".

## dev/lane/tests/test_in_form.py, test_write_only.py

26. `test_in_form.py:214-222` and `test_write_only.py:153-164` (`TestHook`) test `lay.entry`'s
    matcher, `lay.py`'s job, which `test_lay.py:294-308, :416-432` test for other lanes. Kind:
    duplication/complexity (B-5). Should be: in test_lay.py, one table of lanes → matcher.
27. `test_in_form.py:131` `for named in ("${CLAUDE_PLUGIN_ROOT}/../form.json",): with
    self.subTest(...)`: a loop and a subTest over one value. Kind: noise (B-4). Should be: the value
    inline.
28. `test_write_only.py:134-138` `event = self.event("", tool="Write"); event["tool_input"] = …`
    where every other guard class uses `self.called("Write", {...})`. Kind: complexity (B-3). Should
    be: `self.called`.
29. `assert x is not None, "…"` in `test_in_form.py:220`, `test_write_only.py:163`,
    `test_call.py:416`, `test_record.py:20`, beside `self.assert…` everywhere else. Kind:
    inconsistency (B-3). Should be: `self.assertIsNotNone` (or a typed helper).

## dev/lane/tests/test_shell.py, test_shell_reads.py

30. `test_shell.py` mixes reading words and statements, reads, writes, heredocs and git, with
    `TestRead` (`:22`, mostly `shell.reads`) beside `TestReading` (`:249`, statements), a module
    function `read` defined mid-file (`:240`), and one-test classes `TestWrittenByReadWrite` (`:374`)
    and `TestSedInPlace` (`:382`) apart from `TestWritten` (`:139`); `shell.reads` is tested in both
    files. Kind: complexity/inconsistency (B-3, B-5). Should be: split by what shell gives (see
    Structure).
31. Heredoc ends tested twice: `test_shell.py:186-194`
    `test_a_heredoc_s_end_word_ends_it_only_at_a_line_s_start` and `:279-283`
    `test_a_heredoc_ends_only_at_its_end_word_alone_on_a_line`; the line after a heredoc in `:206`,
    `:213` and `:272`. Kind: duplication (B-7). Should be: one class, one test per behavior.
32. `test_shell.py:410` 108 chars and `:414` "# Each folder as a cd or -C makes it, a path of its own."
    after the Then, about nothing below it. Kind: noise (B-3). Should be: wrapped; the stray comment
    gone.
33. `test_shell_reads.py:12` `WHOLE = (1, None)` restates `shell.WHOLE`, which
    `properties_shell.py:80` imports. Kind: inconsistency (B-5). Should be: one way; an expected value
    written out is allowed, so keep it but use it in both.
34. `test_shell.py:353-354` `commands = (...)` then `commands + ("git push a2>x",)`: one case added
    apart for no reason. Kind: noise. Should be: one tuple.

## Other test files

35. Given/When comments that name the mutation, not the behavior: "its name sorting before Bash or
    after" `test_call.py:138`, `:173`; `test_follow_next.py:37-38`; `test_lanes.py:212`;
    `test_lay.py:531`; `test_start_with.py:57`; `test_test_after.py:52`; `test_shell_reads.py:153`;
    `test_step.py:35`; `test_shell.py:410`. The inputs are what kill `==`→`<=`/`>=` mutants and stay
    needed once the `x in ("a",)` idiom becomes `==` (maintainer's decision); the reason is told ten
    times in the reader's way. Kind: noise (B-3). Should be: the Given says the behavior ("a tool of
    another name"); the reason once, beside the pragma reason in `dev/lane/cosmic-ray.toml`.
36. `test_every_item.py:86-90` `test_a_written_file_not_there_answers_nothing`: the reply leaves B-2
    out and `answers.md` never existed, so the result is the same as `:42`
    `test_a_reply_leaving_a_key_out_drifts` whatever the code does with written files; only a crash
    would fail it. Kind: test that tests nothing named (B-6). Should be: named for what it holds ("a
    written file gone is read without stopping"), or a file written then removed while its key would
    otherwise answer.
37. `test_as_printed.py:37` `field = call.HANDS.get(tool, "command")`: the test builds its input
    from the table under test. Kind: B-6 (value taken from the code). Should be: the field per tool
    written out (`prompt` for Agent).
38. `test_test_after.py:16` base class named `TestAfter`, read as a test class of "after"; `test_step.py:54`
    `TestSpan` and `:109` on `PluginTest`, which makes a plugin folder they never read. Kind: B-3 /
    B-8. Should be: `TestAfterTest`, as the other files name their bases (`EndWhenTest`), and
    `unittest.TestCase` where no folder is read.
39. `test_shell.py:119-124` `test_a_bare_cd_goes_home` reads the machine's `~`. Kind: B-7 (reads the
    machine). Should be: `HOME` patched to a folder of the test.

## dev/lane/trials/trial.py

40. One 436-line script holding seven trials of two plugins: notes' `lay/drift/python/up/changed`,
    turn's `turn`, memo's six cases; constants named per plugin only in part (`ANSWERS` and
    `ANSWERS_MEMO`, `MEMO_LANES` beside `FORMS`, `SCRIPTS`, `SUMMARY`, `ALONE`, `DRIFT`); module-level
    dispatch with no `main()`; `project` (`:275-277`) a one-line wrapper of `made`; the reviewer's
    prompt JSON (`:214-215`) restates `MEMO_PROJECT["memo.json"]` (`:129-137`); files printed by
    `subprocess.run(["cat", …])` (`:271-272`); quoted annotations (`:297`, `:373`, `:388`) where the
    tests use `from __future__ import annotations`; lines 61, 67, 85, 95, 156 over 100. Kind:
    complexity/duplication (B-3, B-4, B-5). Should be: split (see Structure); the reviewer prompt
    from `MEMO_PROJECT`; `project` gone. (Prior audit 1.6: kept.)
41. `dev/lane/trials/memo/scripts/publish.py:1` "prints its title" but `:7` prints
    `Published {run['work']}.`, the memo's path. Kind: inconsistency (B-3). Should be: "prints the
    memo's path".

## Structure

| Part | Takes on | Split / reshape |
|---|---|---|
| `test_lay.py` | print, step text, hooks.json, code placing, validation, proposal checks, run values, in_form, up, main | `test_lay_proposal.py` (proposal and in_form checks), `test_lay_steps.py` (print, write step, lay again), `test_lay_hooks.py` (hooks.json, both events, matchers incl. the two `TestHook`s), `test_lay_code.py` (copy/link, up), main in the first; as lay.py splits |
| `test_shell.py` + `test_shell_reads.py` | words, statements, heredocs, reads, writes, cd, git | `test_shell_words.py` (words, statements, heredocs, redirects), `test_shell_reads.py` (all of `reads`), `test_shell_written.py` (all of `written`), `test_shell_folders.py` (cd, git, inside) |
| `test_guard.py` | the entry's stop and let-through, command-line form, run values for four lanes, the agent filter of hook.run | guard behaviour and command-line form here; run values to `test_started.py`'s neighbour as `test_run_values.py`; `TestRun` to `test_hook.py` |
| each lane's guard class | sentence laid by hand + guard run | one `GuardTest.lay(step, lane, takes)` in test_guard.py |
| `helpers.py` | path setup, re-exports, PluginTest, record builders | as is, plus `read`, `ended`, `HERE`, `write_only` re-export; `recorded`'s docstring one line per item kind |
| 4 `properties_*.py` | the same guard and profile | guard and profile in `dev/lane/testing.py` |
| `trials/trial.py` | 7 trials of notes, turn, memo, their fixtures and the dispatch | `trials/notes.py` (lay, drift, python, up, changed, turn), `trials/memo.py` (MEMO_* and cases), each with a `main()` and a usage stop; shared `copied`, `made`, `run` in `dev/lane/trying.py` |

## Cross-slice

- `lane/hooks/lane/hook.py:41` `agent: str | None = None`: default used only by
  `dev/lane/tests/test_hook.py:48` (finding 19).
- `lane/hooks/lane/lanes/__init__.py:76-115` (`slots`, `alone`, `fits`, `SHOWN`): generality held only
  by stand-in lanes in tests (finding 24).
- Hook command format in `lane/scripts/lay.py`, `lane/hooks/lane/lanes/__init__.py`,
  `dev/lane/testing.py:136-149`, `dev/lane/trials/trial.py:363` and the hand-written test commands
  (finding 11).
- Hypothesis guard repeated in `dev/turn/tests/properties.py` and `dev/rn/tests/properties.py`
  (finding 12); lane has four `properties_*.py`, turn and rn one `properties.py` each.
- `dev/lane/README.md:6` names only the tests, not `dev/lane/trials/trial.py`;
  `dev/architecture.md:226-227` says it covers trials. `dev/lane/trying.py`, which `trial.py:42`
  imports, sits outside `trials/` though `dev/architecture.md:339-340` puts trial code there.
- `dev/lane/testing.py:24-25` `KEPT`/`atexit` and `GitTest.copied` are not used by lane's tests (no
  `GitTest` in `dev/lane/tests/`); they serve turn and rn, so "kept beside that code's tests" in
  `dev/architecture.md:255-256` holds only by location.
- `test_shell.py:245-246` `KEEP` copies the command of rn's `/rn:up` as a fixture; it drifts if rn's
  changes.
- Maintainer decisions: the membership idiom change touches finding 35 (those inputs are what kill
  `==` mutants); none of the turn or rn decisions touches this slice.

## Prior audit (`.rn/20261013-writ-rebuild/audits/lane.md`) in this slice

- Defect 2 (DRIFT): kept as finding 1.
- 1.1 (test_lay mirrors lay.py): kept, finding 14.
- 1.6 (trial.py seven trials): kept, finding 40.
- 2.2 (`hook.run` agent default): kept, finding 19, shown from the tests.
- 2.4 (E501, `helpers.py:195`): kept; 22 lines in this slice (findings 3, 32, 40).
- 3.1 (hook command format in three places): kept and widened, finding 11.
- 3.7 (`"Stop hook feedback"` beside `record.TOLD`): dropped for this slice; `helpers.py:257` and
  `test_record.py:336` write it as an expected value, which `dev/architecture.md:264-265` allows.
- 4.2 (trying.py outside trials/, dev/lane/README): kept under Cross-slice.

## Read

- `dev/lane/tests/`: helpers.py 268, properties_forms.py 110, properties_hand_on.py 70,
  properties_shell.py 161, properties_write_only.py 54, test_as_printed.py 316, test_call.py 483,
  test_end_when.py 75, test_every_item.py 137, test_follow_next.py 162, test_forms.py 125,
  test_guard.py 386, test_hands_off.py 68, test_hook.py 125, test_in_form.py 226, test_lanes.py 277,
  test_lay.py 986, test_python_check.py 104, test_read_only.py 145, test_read_whole.py 194,
  test_record.py 355, test_schema.py 365, test_shell.py 424, test_shell_reads.py 163,
  test_start_with.py 165, test_started.py 159, test_step.py 148, test_template.py 369,
  test_test_after.py 137, test_wait_for.py 134, test_write_only.py 168.
- `dev/lane/trials/`: trial.py 436; memo/.claude-plugin/plugin.json 6, memo/agents/reviewer.md 17,
  memo/agents/runner.md 19, memo/agents/writer.md 23, memo/forms/entry.json 9, memo/forms/summary.md 7,
  memo/scripts/given.py 8, memo/scripts/next.py 9, memo/scripts/publish.py 7,
  memo/scripts/status.py 12, memo/skills/make/SKILL.md 20; notes/.claude-plugin/plugin.json 6,
  notes/agents/changelog-writer.md 16, notes/skills/changelog/SKILL.md 18.
- Beside the slice, whole: rn/checklists/product/code.md 202, dev/architecture.md 411,
  .claude/rules/dev.md 115, .rn/20261013-writ-rebuild/audits/lane.md 118, dev/lane/testing.py 149,
  dev/lane/trying.py 79, dev/lane/README.md 6, dev/lane/cosmic-ray.toml 13.
- Beside the slice, in part: lane/hooks/lane/hook.py:35-66, lane/scripts/lay.py (grep of `CODE`,
  `USAGE`, `command`, `entry`, `lane_version`), lane/hooks/lane/lanes/*.py (`WORDING`, `SHOWN`),
  lane/README.md (grep), ruff.toml (head).

## Not read

- None in the slice. The product code under test was read only where a test pointed to it; findings
  on it are left to its auditor but those above that the tests show.
