# lane and dev tooling audit (2026-10-25, read-only, at 4b69a1d)

504 tests pass, ruff and pylint copied-code clean; two modules do several jobs, some knowledge in two
or three places, three real defects.

## Defects

1. Pre-push misses plugins that use lane's code: `dev/changed.sh:18` counts only
   `lane/hooks/lane/(hook|shell)\.py|dev/lane/testing\.py` as shared, but turn links all of
   `hooks/lane` (`turn/hooks/lane -> ../../lane/hooks/lane`), `dev/turn/tests/test_lanes.py` imports
   lane's `lanes` and `step`, rn links `template.py`. A change to a lane's wording or `template.py`
   runs only lane's checks before push; turn's/rn's property tests and mutation never run for it.
   `dev/README.md:9`, `:17` repeat the stale list. Should be: changed.sh finds the plugins from the
   links pointing into a changed file; the README says it once.
2. `dev/lane/trials/trial.py:89` `DRIFT = ("/notes:changelog Add an entry…` and `:163` redefines
   `DRIFT = ("This run tries memo's hooks…`; calls at `:434`, `:436` send memo's. Two names
   (`NOTES_DRIFT`, `MEMO_DRIFT`).
3. `lane/CHANGELOG.md:22` says lane:up "says so in its first reply"; `lane/agents/up.md:24-26` puts
   `Brought lane's code` in the step 9 reply (after the OK), likely as as_printed allows one line
   before the print (`as_printed.py:51-60`). One true statement: `lay.py print` includes the
   bring-up note, or the CHANGELOG says "before writing".

## 1. Size and structure

1. `lane/scripts/lay.py` (536) does six jobs: reading/checking the proposal (:95-189), rewriting
   step text (:192-228), printing (:231-265), building hook commands (:52-63, :268-296), editing
   hooks.json (:299-345, :395-423), placing lane's code with link/copy and VERSION (:348-392,
   :463-482) plus the `up` migration (:485-529). `test_lay.py` (986, 12 classes) mirrors it. Should
   be: lay.py the command line over `proposal`, `steps`, `hooks_file`, `code`; tests split to match.
2. `lane/hooks/lane/lanes/__init__.py` does five: registry, sentence building
   (`slots/shown/sentence/alone/fits`), hook-command format (`word/read/hook_words/laid`), reading
   hooks.json (`taken/texts`), runner (`Laid`, `main`). Split into wording, command-format (taking
   the writer half now in lay.py, §3.1) and runner.
3. Lane-specific rules outside their lane's module: `lanes/__init__.py:159` `if self.lane in
   ("read_only",): … self.forms()` (`:174-179`); `lay.py:182` `if known in ("in_form",):
   in_form.form(...)`; `Laid.run_values` (:167-172) on start_with's rules. Should be optional hooks
   in each lane's module (`extra_takes`, `checked`) called for any lane.
4. `start_with.runs` used as a library by `as_printed`, `follow_next`, `wait_for`, `__init__`:
   "does a call run the command the step names" belongs in `call.py`.
5. `call.Call` 12 fields (`call.py:40-63`) for two kinds: `before`, `text`, `heard` the call being
   made; `result`, `failed`, `ends` one made before. Two types.
6. `dev/lane/trials/trial.py` (436) holds seven trials and fixtures; rn keeps a folder per trial.
   Split notes and memo trials.

## 2. Noise

1. USER'S DECISION: membership idiom `x in ("a",)` for `==` 38 times (plain `==` 7), explained in
   9 near-identical comments ("Told by membership rather than `==` … a mutant making it one would
   pass every test": `lay.py:363`, `:532-534`, `shell.py:104-107`, `lanes/__init__.py:116-118`,
   `read_whole.py:31`, `write_only.py:23`, `hands_off.py:17`, `test_after.py:36`, `template.py:175`;
   rn.py too, 35 times). It works around the mutation tool. Should be plain `==`, the equivalent
   mutants excluded once in each `cosmic-ray.toml` by Cosmic Ray's operators filter
   (`cr-filter-operators` installed), the reason written there (code.md B-6).
2. `hook.run(..., agent: str | None = None)` (`hook.py:41`) and its `None` branch (:59): the only
   caller (`lanes/__init__.py:263`) always passes it; the docstring implies other hooks. Defaults
   `event="PreToolUse"` on `lay.command`, `lay.entry` (:273, :280) unused. Make `agent` required,
   drop the defaults.
3. Docstrings repeating: `call.py:1-12` repeats `Call` (:41-50) and each function's; `lay.py:12-24`
   repeats `written`, `brought_up`. Module openings: what and why in two or three lines.
4. `ruff.toml` says 100 is "The width this repository's documents wrap at" but E501 is not
   selected: 37 lines pass (20 outside tests), e.g. `lanes/in_form.py:59` (116), `schema.py:3`,
   `lay.py:49`, `lay.py:261`, `wait_for.py:2`, `helpers.py:195`. Select E501.
5. `rn/scripts/call.py`, `rn/scripts/forms.py` unused links (see rn audit).

## 3. Duplication

1. Hook-command format in three places: lay writes it (`lay.py:52-58`, :268-277), lanes reads it
   (`lanes/__init__.py:63-67`, :212-247), `dev/lane/testing.py:136-149` parses it again
   (`rpartition("; exec ")`, `split(":", 2)`). One module both ways, testing imports it.
2. hooks.json read twice: `lanes.taken` (:182-200), `lay.hooks_read`/`laid_before` (:299, :485).
3. `up.md:28-34` teaches `<step>:<lane>:<takes joined by commas>` to read lanes laid, which
   `lay.laid_before` parses; `up.md:41-42` finds stale sentences, which `step.holds` does. `lay.py
   up` prints lanes laid before and the stale ones; the prompt drops the format.
4. "A command the step names" matched two ways: `hands_off.py:16`, `test_after.py:29` use
   `str.split()` prefixes; `start_with.runs` uses `shell.words` with interpreter stripping and
   path-suffix matching (used by wait_for, as_printed, follow_next). One function in `call.py`.
5. A take to a path two ways: `write_only.py:21`, `in_form.py:46` `os.path.realpath(t)`;
   read_only, read_whole, test_after `shell.path(os.getcwd(), t)`; end_when, every_item
   `shell.paths`. They differ on `$`. One helper.
6. Front matter two ways: `step.py:12-14` own `FRONT`, `NAME` regexes; `template.keys`/`text_of`.
   `step.agent_file` uses `template`.
7. Claude Code's record format in several places: `lane/hooks/lane/record.py`; turn's
   `scripts/records.py:15-20` (which rn links); `dev/lane/trying.py:57` (path glob), :73 (`"Stop
   hook feedback"` = `record.TOLD`). One reader in lane's record.py.
8. File text read with `errors="replace"` three times (`call.py:122`, `read_whole.py:40`,
   `every_item.py:52`); JSON found in script output two ways (`started.objects`/`loaded` :50-66,
   `follow_next.printed`).
9. Dev tooling: "every plugin is a `dev/*/tests` folder" coded four times (`check.sh:9-14`,
   `properties.sh:9-15` identical, `changed.sh:9-13`, `tests.yml:45`): one script. The check scheme
   described in full in `dev/architecture.md:297-311`, `dev/README.md:11-17`, and headers of
   `tests.yml:11-17`, `check.sh:2-5`, `properties.sh:2-6`, `mutate.sh:2-15`, `pre-push:2-6`,
   `changed.sh:2-7`; "3.9 for users, newer only to test" five times. The why in the architecture,
   the commands in dev/README.md, usage alone in each header. `dev/architecture.md:264` says
   check.sh "fails on lines copied between any two files" but only `*.py` is checked.

## 4. Inconsistency

1. `dev/lane/architecture.md:129` "lane runs on Claude Code, python3 3.9 or later, git and jq":
   lane runs neither git nor jq; README Requirements lists Claude Code and Python only.
2. `dev/lane/README.md` lists only tests; `dev/architecture.md:226-227` says it covers trials, as
   turn's and rn's do. `dev/lane/trying.py`, shared by every plugin's trials, sits outside
   `trials/` and is named nowhere (`dev/architecture.md:339` puts trial code in
   `dev/<plugin>/trials/`).
3. `README.md:35` "under the action it keeps"; `docs/lanes.md:3`, `ux.md:73` "it watches".
4. One name, different things: `texts` (`lanes/__init__.py:203`, `started.py:28`), `runs`,
   `shown`, `alone`, `held`, `told`, `made`; lane's `call.py`/`forms.py` share names with turn's
   unrelated modules (`testing.lane_code` and the per-plugin pyrefly loop in `check.sh:28-33` exist
   to work around it).
5. Architecture repeats the UX or holds behaviour detail (architecture.md B-7): :53-56 repeats the
   UX "Laying lanes" scene; :154-157 (record path), :161 (in_form's forms) belong to the code or
   `docs/lanes.md`; :138 "as tried on Claude Code 2.1.306" is how it was reached.

## 5. Other

1. `up.md:77` "Run `lay.py write <proposal>`. Do not go on until `OK`.": a laid lane's sentence is
   appended at the step's end, so a wait comes after the action it guards (prompt.md B-5). Place
   wait_for's sentence before the commands it holds back, or lay it on step 8.
2. `Laid.check` (`lanes/__init__.py:135-165`) five rules in one method: split with §1.2.
