# Audit: shared parts

Findings are numbered across the report (S1...). Kinds: noise / duplication / inconsistency /
complexity / defect. "ck" = rn/checklists/checklist.md, "us" = rn/checklists/usability.md.

## Development tooling (dev/*.sh, githooks, CI, configs)

### dev/changed.sh
- S1 `dev/changed.sh:131` "`^(lane/hooks/lane/(hook|shell)\.py|dev/lane/testing\.py)$`" — defect, code.md B-6/B-5. The shared-file list is hand-kept and wrong: `turn/hooks/lane -> ../../lane/hooks/lane` links the whole folder, `rn/scripts/template.py -> lane/hooks/lane/template.py`, `rn/scripts/{call,forms,records}.py -> turn/scripts/*`. A change to `lane/hooks/lane/template.py`, any `lanes/*.py`, or `turn/scripts/records.py` runs only the owner's tests; rn's and turn's tests that run that code are skipped by pre-push and CI. Should be: find the plugins from the symlinks (`git ls-files -s` mode 120000 / `find -type l`) pointing into a changed path. (Prior audit lane 1: kept.)
- S2 `dev/changed.sh:6-7` "the session records, the decisions, the rules for the assistant" — noise/inconsistency, code.md B-3. "the decisions" is `.rn/<session>/decisions/`, already under `.rn/`; a second name for part of the session records. Same words at `dev/architecture.md:305`, `tests.yml:16`. Drop "the decisions".
- S3 `dev/changed.sh:128-132` with `dev/architecture.md:304-305` "skips the checks on a push that changes only what no check reads" — inconsistency. A push changing only `dev/architecture.md`, `dev/README.md` or `.claude/rules`-adjacent docs outside the regex (any `dev/*.md`, `.github` aside) falls in "a file of no plugin" and runs every plugin's checks. Either list docs no check reads in the regex, or say the skip is only for `.rn/`, `.claude/rules/`, root README and LICENSE.

### dev/check.sh
- S4 `dev/check.sh:63` "`if command -v pylint >/dev/null 2>&1; then`" — defect, code.md B-2/B-7. The copied-code check is skipped silently where pylint is absent, which is every local run set up as `dev/README.md:11` says (`uv sync --locked` installs the `dev` group only; pylint is in `test-quality`). `dev/README.md:11` lists "the check for code copied between files" among what that run does; `dev/README.md:15` says only the test-quality group runs it; `dev/architecture.md:264` says check.sh "fails on lines copied". Should be: one explicit switch (run pylint where the Python allows, say "skipped: needs Python 3.11" otherwise), and one description.
- S5 `dev/architecture.md:264-265` "fails on lines copied between any two files, but a test's expected value written out again" — inconsistency. check.sh checks `*.py` only (`check.sh:64`), and nothing exempts a test's expected value (no pylint config; duplicate-code has no test exception). Say what is checked, or add the exemption. (Prior audit lane 3.9 last point: kept.)
- S6 `dev/check.sh:48-54`, `dev/properties.sh:9-15`, `dev/changed.sh:123-127`, `.github/workflows/tests.yml:45` "`for tests in dev/*/tests`" / "`ls -d dev/*/tests`"; and `dev/mutate.sh:63` "`dev/*/cosmic-ray.toml`" — duplication, code.md B-5. "Which plugins exist" is coded five times, two ways. One `dev/plugins.sh` (or changed.sh with no args) printing the list. (Prior audit lane 3.9: kept, plus mutate.sh.)
- S7 `dev/check.sh:74-78` (computed pyrefly search paths) vs `dev/{lane,rn,turn}/cosmic-ray.toml` `test-command` (hand-listed `--search-path ...`, turn's naming each trials subfolder) — duplication, code.md B-5. How a plugin is type-checked is in four places that already differ (the toml lists omit folders check.sh finds). One script `dev/typecheck.sh <plugin>` called by both.

### dev/mutate.sh
- S8 `dev/mutate.sh:63-90` — defect against the maintainer's decision (pragma). The decision gives each untestable mutant a `# pragma: no mutate` filtered by `cr-filter-pragma`; mutate.sh runs only `cr-filter-git` and only with `--since`. Add `cr-filter-pragma "$copy/config.toml" "$db"` after `cosmic-ray init`, on every run.
- S9 `dev/mutate.sh:66-79` "The config's distributor, its last table, is replaced" with `.split("[cosmic-ray.distributor]")[0]` — complexity/duplication. The rule "distributor is the last table" lives in mutate.sh and silently in each toml's layout; each toml's `[cosmic-ray.distributor] name = "local"` (rn:17-18, lane:30-31, turn:45-46) exists only to be cut. Write the run's config from the toml's `[cosmic-ray]` table alone (or keep the tomls without a distributor).
- S10 `dev/mutate.sh:78` writes `[cosmic-ray.filters.git-filter] branch = ""` on every run, used only when `--since` is given (`:84-90`) — noise, code.md B-4. Write it only with `--since`.
- S11 `dev/mutate.sh:26-58, 66-79, 93-96` — complexity, code.md B-5. Three heredoc Python programs and one `python3 -c` inside a shell script (ports, waiting, config rewrite, asyncio work-around). One `dev/mutate.py` reads plainly and is checked by ruff/pyrefly; today none of this Python is linted or type-checked.
- S12 `dev/mutate.sh:26,46,66,93` `python3` vs `dev/properties.sh:19` `python` and the tomls' `python -m unittest` — inconsistency, code.md B-3 (idiom unlike the code around). Pick one.

### dev/properties.sh
- S13 `dev/properties.sh:2-6` "many inputs each in CI and few elsewhere" — code.md B-3. The switch is `dev/lane/testing.py:112-114` (`CI` env, 1000 vs 10 examples); no header names it, so a reader of properties.sh, dev/README.md:15 or dev/architecture.md:298-303 cannot find it. Name it once.

### dev/githooks/pre-push
- S14 `dev/githooks/pre-push:116` "`git merge-base "$local" origin/main`" and `tests.yml:37-38` "`git merge-base HEAD origin/main`" — duplication: the base a change is measured from is decided twice, in two forms (pre-push has no "commit before passed" case). Acceptable if said why; otherwise one helper.
- S15 `dev/githooks/pre-push:109` "install it as dev/README.md says" — code.md B-2. dev/README.md only links uv's site; it says no install step. Name the action (`https://docs.astral.sh/uv/getting-started/installation/`) or have dev/README say it.

### .github/workflows/tests.yml
- S16 `tests.yml:11-17` (job comment), `dev/architecture.md:297-311`, `dev/README.md:11-17`, headers of `check.sh:2-5`, `properties.sh:2-6`, `mutate.sh:2-15`, `pre-push:2-6`, `changed.sh:2-7` — duplication, code.md B-5 / us B-7. The whole check scheme is told seven times; they already drift (S3, S4). The why in dev/architecture.md, the commands in dev/README.md, each header its usage alone. (Prior audit lane 3.9: kept.)
- S17 "Users run 3.9" at `tests.yml:62`, `pyproject.toml:6` "Users run Python 3.9.", `pyproject.toml:10-11`, `pyproject.toml:16-17` "need a newer Python only to check, not to run", `check.sh:61-62` same words, `dev/architecture.md:245-248, 300, 307`; the value 3.9 also in `ruff.toml:1`, `pyrefly.toml:1`, `tests.yml:68`, `lane/scripts/lay.py:53,56` — duplication. Keep the reason once (dev/architecture.md); the value from `requires-python` where the tool reads it (ruff falls back to `requires-python` when `target-version` is unset — verify on 0.17.2 before relying on it).

### ruff.toml, pyrefly.toml, pyproject.toml
- S18 `ruff.toml:2` "The width this repository's documents wrap at." `line-length = 100` — inconsistency. E501 is not selected, so 78 code lines exceed 100 (`ruff check --select E501` on this tree, e.g. `lane/scripts/lay.py:49`); documents are not checked by ruff at all, and `dev/README.md` (9 lines) and root `README.md` are not wrapped. Either select E501 and say it is the code width, or drop the claim. (Prior audit lane 2.4: kept, count now 78.)
- S19 `ruff.toml`, `pyrefly.toml` (1 line) — complexity/noise. Two config files of one and three lines beside `pyproject.toml`; both tools read `[tool.ruff]` / `[tool.pyrefly]` there. Fold them in (keep `.coveragerc`: coverage on 3.9 needs `tomli` to read pyproject).

## dev/README.md
- S20 `dev/README.md:11-17` — noise/duplication, us B-4/B-7. `dev/architecture.md:226-229` gives this README the job "lists each plugin's folder and links the order the work goes in"; it also tells the check scheme in full (see S16). Keep: how to set up and run the checks, one line each.
- S21 `dev/README.md:17` "or every plugin where it changes what they all stand on, such as lane's `hook.py` and `shell.py`" — inconsistency: repeats changed.sh's wrong list (S1).
- S22 `dev/README.md:3` "Installing a plugin copies only its own folder, so nothing here reaches its users' machines." — duplication of `dev/architecture.md:219-222` and root `README.md:21`. Link.
- S23 `dev/README.md:9` lane's bullet "also the tests of `hook.py` and `shell.py`, the hook code the plugins share" — inconsistency: turn shares all of `lane/hooks/lane/` and rn shares `template.py` (see links in S1); `dev/lane/trying.py`, which every plugin's trials import, is not named.
- S24 `dev/README.md:11` "A `coverage` installed outside a virtual environment does not count the scripts the tests start as separate processes." — noise, us B-4: a pitfall for a way of running the README does not offer. Drop, or say it as the reason to use `uv run`.
- S25 `dev/README.md` lines unwrapped (1-19) while `ruff.toml:2` says documents wrap at 100 — inconsistency (S18).

## Root README.md
- S26 `README.md:7-8` plugin lines vs `.claude-plugin/marketplace.json` descriptions — inconsistency/duplication. turn's is the same text twice; rn's differs (README: "...you decide what you really want, how it is built and whether the result is it, and nothing else"; marketplace: "...rn hears what you really want one point at a time, turn makes every piece ..."). `dev/architecture.md:407` asks for "a one-line description" in both, changed together. One description, copied by a check or kept in one place.
- S27 `README.md:7-8` "**[rn](...)**" — us F-1 "No item is set in bold".
- S28 `README.md:3` "Claude Code plugin marketplace for lovaizu projects." — us B-12/B-9: "lovaizu projects" is unexplained, and the opening does not say what the reader can do with the marketplace. Say what the plugins are for, in one line.
- S29 `README.md` has no License section though `LICENSE` exists — readme.md B-5 (license named), as far as readme.md applies to a marketplace README.
- S30 `README.md:21` "outside the folder that is installed" — duplication of `dev/architecture.md:219-222` (S22).

## dev/architecture.md

Judged against rn/checklists/product/architecture.md and usability.md.

- S31 `dev/architecture.md` as a whole vs architecture.md F-1 — inconsistency. No `## User stories`, `## Architecture` (Logical/Physical view) or `## Test` link; it has `Code`, `Test` with counts and CI behaviour, and `Release` with steps. architecture.md B-5 says the test rule is "the project's rule, not the architecture's: the architecture links it", and the project's rule lives here. Either a base architecture is its own kind with its own checklist, or split (see Structure).
- S32 `dev/architecture.md:3-5` "This is the architecture every ccpm plugin is built on: how its roles work..., where its files are placed, how its code is written, and how it is tested and released." — architecture.md B-1: an opening that says what the document holds rather than how a plugin is put together.
- S33 `dev/architecture.md:22-23` "each is said with its reason under Why it is so, and a plugin's design adds only what that plugin gives on top of them" — us B-4: tells what the document does.
- S34 `dev/architecture.md:42-213` "Why it is so" — complexity, architecture.md B-7/us B-20. 8 principles, 17 subsections, no 1:1 map (P2 has two, P1 three: "holds the whole", "Where the orchestrator runs", "Messages"); five subsections are decisions of no principle (Languages, Where the orchestrator runs, JSON between agents, Messages, A plugin that uses another). The reader cannot tell which why backs which principle. One subsection per principle, named as the principle; decisions under the parts they shape.
- S35 `dev/architecture.md:25, 28, 44-54` — touches decision 1 (turn's orchestrator judges for running the flow). P1 "decides each move" and P3 "Each job has a role of its own, given only what the job needs" leave open whether the CCS check and the wording questions are a job that needs a role. The base is where "judging what the run needs is the orchestrator's own job, not a role's" belongs once, so turn's architecture links it instead of arguing it.
- S36 `dev/architecture.md:29-30, 112-117` "Each work is first used by AIs that did not make it ... each reading it on its own" / "two readings add a check only when each is made on its own" — touches decision 1. With the orchestrator's Good check gone, turn has one Good reader; the plural and "two readings" read as if two independent readings are required. Say "one or more".
- S37 `dev/architecture.md:115` "The maker finds the Good it meant" — architecture.md B-8: "Good" (capitalised, a turn term) is used with no line saying what it is.
- S38 `dev/architecture.md:288-291` "Mutation testing with Cosmic Ray, in which the unit tests must catch every mutant" — touches decision 4; us B-7 "with every case where it does not hold beside it". The pragma exemption (cr-filter-pragma, reason in cosmic-ray.toml) must be beside this rule.
- S39 `dev/architecture.md:287-313` "C0 and C1 coverage, 100%", the CI paragraph `:297-305`, "A plugin's whole test run takes seconds" `:313` — architecture.md B-7 (counts, step-by-step behaviour) and duplication of tests.yml / pre-push / dev/README (S16) and of code.md B-8 ("in seconds ... in minutes"). Keep the rule and why; the CI mechanics in the workflow.
- S40 `dev/architecture.md:126` "The spec-driven tools read on 2026-10-21 (Spec Kit, BMAD-METHOD, OpenSpec, superpowers, cc-sdd)" — architecture.md B-7 "how a decision was reached"; the date is status. Keep the finding, drop the reading date, or link the research.
- S41 `dev/architecture.md:99-100` "cc-sdd's agent sets its own approval flag, which then stops nothing" — architecture.md B-8: another product named before it is introduced (`:126`), and a comparison for an idea already said. Drop or move after `:126`.
- S42 `dev/architecture.md:274` "as the official `hookify` plugin does" — architecture.md B-8: product named with no link or line.
- S43 `dev/architecture.md:186-190` "Roles do not message one another. / What passes between roles goes through the orchestrator." — duplication within (two sentences, and the figures at `:9-18`, `:171-184`), architecture.md B-7.
- S44 `dev/architecture.md:320` "on Opus, the model the maintainer uses" before `:331` defines "the maintainer" — architecture.md B-8 (reason/term after its use).
- S45 Names: "caller" (P2, `:15`, `:81-100`), "user" (P8 `:38`, `:148-160`), "person" (`:58-77`), "maintainer" (`:320-354`), "builders" (`:220`), "plugin's makers" (`:39`, `:152`), "assistant" (`:386`) — architecture.md B-8 "one thing under two names". Which of these are the same is left to guess (is "user" the caller when a person? are makers the maintainer and assistant?). Define each once, use one name each.
- S46 `dev/architecture.md:252-256` "Code more than one plugin needs ... kept once ... each other plugin takes it through a relative symbolic link" — inconsistency with the tooling: changed.sh does not follow those links (S1), and `rn/scripts/forms.py`, `rn/scripts/call.py` are links nothing shipped in rn imports (cross-slice, prior audits turn 3.8 / rn 2.1: kept; `call` imported only by `dev/rn/trials/moves/stand.py:31`, `dev/rn/trials/flow/write.py:19`; `forms` by nothing).
- S47 `dev/architecture.md:339-340` "The code that runs a trial ... is kept in `dev/<plugin>/trials/`" — inconsistency: `dev/lane/trying.py`, imported by `dev/rn/trials/moves/moves.py:36`, `dev/rn/trials/flow/flow.py:58`, `dev/turn/trials/shared.py:22`, sits outside any `trials/`. (Prior audit lane 4.2: kept.)
- S48 `dev/architecture.md:228` "`dev/README.md` lists each plugin's folder and links the order the work goes in" — inconsistency with what dev/README.md holds (S20).
- S49 `dev/architecture.md:4` lists, `:9-18` figure — fine; `:375-376` "grouped under `Added`, `Changed`, `Fixed` and `Removed`" vs `rn/CHANGELOG.md:4-6` which states its own versioning rule ("the middle number for anything you would notice") — duplication with `:365-368` (cross-slice).

## .claude/rules/dev.md
- S50 `.claude/rules/dev.md:25-28` step 1 "Write `<plugin>/README.md` ... before anything else is made" vs `rn/checklists/product/ux.md:229-230` "A UX is read by the user who agrees it, before anything else of the product is made", `readme.md:16-20` (README built "from the UX's users, goals and benefits"), `architecture.md:23` (parts "drawn from the UX") and dev.md's own `:51` "key results in the UX" — inconsistency, us B-21. No step writes the UX (`dev/<plugin>/ux.md`) or names `ux.md`. Add "Write the UX with `ux.md` open" as step 1.
- S51 `.claude/rules/dev.md:49-53` "A unit is the smallest slice through which the user meets one or more of the key results" vs `dev/architecture.md:285` "Unit tests: code" / `:317` "Unit tests: prompts" (tests of one part alone) — us B-14 one name for two things; dev.md step 5e tries "the unit as its user" by "Acceptance tests". Rename the slice (e.g. "slice") or the tests.
- S52 `.claude/rules/dev.md:42-46` step 3 "Have a first user who does not know the discussion read" — us B-12: "first user" is turn's term, unexplained here.
- S53 `.claude/rules/dev.md:79-84` "Change a prompt or a document after a trial only for a cause confirmed in the records" — duplication of `rn/checklists/fix.md` B-1 (cause, not one run's slip); fix.md is named by no step though steps 3, 5 and 6 are fixes. Name fix.md where a finding is settled.
- S54 `.claude/rules/dev.md:17-18` "Source: facts confirmed in the official docs (plugins reference / plugin marketplaces, prompting best practices / skill authoring best practices) and the official plugins." — noise, us B-4: no link, no claim it backs.
- S55 `.claude/rules/dev.md:99-101` step 7 "Pass the checks of The manifests checked" — noise: `dev/check.sh:90-95` runs them on every push and CI requires them; a step for what every push already enforces.
- S56 All four rules files: `- **<rule>**` with `- Rationale:` sub-bullets (`dev.md`, `output.md`, `issue.md`, `final-check.md`) vs us F-1 "No item is set in bold ... explanation, after a blank line, indented" and `dev.md` itself mixing bold lines with `Rationale:` paragraphs (`:9-12`) — inconsistency of form; and Rationale present on some items only (dev.md steps 2, 5b, 5d, 5e, 7, 8 none). One form for the rules.

## .claude/rules/final-check.md
- S57 `final-check.md:6-8` "whether anything in it is not needed for its purpose, and whether any of its work does nothing toward that purpose" — duplication within one item (two wordings of one point); us B-7.

## .claude/rules/output.md
- S58 `output.md:6-8` "Be concise **and** specific — never trade one for the other." repeats `:16-20` ("Match length to payload ... trade specificity for brevity") — duplication.
- S59 `output.md:37-38` "not a planning document like `steering.md` — that follows its own template and is out of scope here" — noise: names an rn file to say the rule does not apply to it.

## .claude/rules/issue.md
- S60 `issue.md:1-30` headings `## 1. One place...`, `## 2. Form` numbered; the other rules files are not — inconsistency of form (minor).

## Checklists (rn/checklists/**), each against checklist.md

### rn/checklists/usability.md
- S61 `usability.md:52-207` IDs B-9, B-16, B-12, B-13, B-14, B-11, B-20, B-4, B-19, B-3, B-6, B-7, B-21 — ck F-4 "a number counted up within the section". No checklist was ever released (no tag holds `rn/checklists/`), so no released ID binds; renumber B-1..B-13 in order. Nothing outside `.rn/` cites a usability ID.
- S62 `usability.md:1-4` no `made_from` — ck F-1 template requires it; ck F-3 exempts only checklist.md ("This file names `usability.md` alone"). Say in ck that usability.md, the base, has none.
- S63 `usability.md:58` "Look for: the main point right under the title." — ck F-1 ("Look for: <the signs a deliverable falls short of it>"): a sign of meeting, and a repeat of F-1's shape (`:33`). Drop it (ck B-3 "one way of meeting another item").
- S64 `usability.md:63-80` B-16 asks three things (who-does-what at a glance; figure for a person, steps for an AI; box naming with kind in angle brackets) — ck B-5 "an item that checks two things"; extra paragraphs between question and Why outside ck F-1's shape (also B-12 `:89`, B-6 `:178`). Box naming is a sign; the figure/steps rule overlaps B-20 `:131-133` "a figure for who acts on whom" — duplication within.
- S65 `usability.md:114-125` B-11 "each word ... it rests on comes before it" vs B-12 `:82-96` "the place where it is first used ... shows what it means" — ck B-3 "a point asked in two items" (a term after its use fails both).
- S66 `usability.md:138-160` B-4 "Every part used" and B-19 "As short as the subject allows" — overlap (part vs word of the same question); B-4's sign "the history of how a decision was reached" is B-6's point (`:171-181`). ck B-3.
- S67 `usability.md:19-20` "Each kind's checklist is made from this file, as `checklist.md` says ... a deliverable is judged by its kind's checklist alone" — duplication of `checklist.md:18-21`; the "judged by its own checklist alone" clause is also at `fix.md:222`. Say it in checklist.md alone.

### rn/checklists/checklist.md
- S68 `checklist.md:136` "steps of the work, which are the plan's tasks" — us B-12: "the plan" is rn's term (steering.md); a checklist maker outside rn does not know it.
- S69 `checklist.md:62` template "Look for: <the signs a deliverable falls short of it ...>" vs the form used: `learnings.md:107` "Look for a place no learning takes up:", `usability.md:58` (S63) — inconsistency; either the template allows a lead-in or the two are rewritten.

### rn/checklists/fix.md
- S70 `fix.md:221-223` "a deliverable is judged by its own kind's checklist, and this one is held while it is changed" — prompt.md B-5/us B-12: meaning (fix.md applies beside the kind's checklist during a change) is left to guess; and the first clause repeats S67.
- S71 `fix.md:237-240` B-1 signs "a cause taken from a summary of the fault rather than the work and the record it is in" and "a change after which the next case of the same kind shows" — ck B-4: asks how the work was done, and what a later run shows, neither answerable from the changed work.
- S72 `fix.md:252-254` B-2 "guarding against a fault more completely than its likelihood and harm call for" — ck B-5: a bar that depends on who answers, with no sign saying what is looked at.
- S73 `fix.md:251-252` B-2 "a rule or part added where the work's purpose gives no need for it" and `:266-268` B-3 "a line added beside the one that should change ... a part kept that the change made needless" — ck B-3: overlapping points across B-2 and B-3; B-3 `:271` "a thing said in two places comes to say two things" is us B-7 again.

### rn/checklists/product/code.md
- S74 `code.md:50-65` B-1 asks two things (only what the development rules name; no place shared with a concurrent run) — ck B-5 "an item that checks two things". Split.
- S75 `code.md:163-165` B-6 last sign "with nothing beside it saying that the user decided it and why" — touches decision 4: the reason for each `# pragma: no mutate` is to be written once in cosmic-ray.toml, not beside each line. As written, every pragma fails B-6. Say "beside it, or in the file it names".
- S76 `code.md:100-101` B-3 "an idiom ... unlike the code around it" — touches decision 4 (`x in ("a",)` → `==`): 38 `in ("...",)` sites in lane/turn/rn/dev (`grep -c`), e.g. `rn/scripts/rn.py:621`; no finding in this slice, listed so the sweep covers all.

### rn/checklists/product/prompt.md
- S77 `prompt.md:221-223` "a step a hook holds is told again by that hook" — us B-12/prompt.md B-5: "told again" (the hook repeats the step to the AI on a drift) reads as "the prompt repeats it", the opposite of B-4's sign `:310-311`. Say "a hook tells the AI that step again when it drifts".
- S78 `prompt.md:338-352` B-6 asks two things (what only the user decides; what the user must see while the AI works) — ck B-5.

### rn/checklists/product/architecture.md
- S79 `architecture.md:27-30` "where the project has none for a kind, the rule is made first" and B-5 `:156-157` "which is a rule to be made first rather than a check written here" — ck B-3 "steps of the work": what to do next is not what the architecture's reader gets. Keep the sign "a kind no rule checks".

### rn/checklists/product/ux.md
- S80 `ux.md:266` template "KR1.1: <What is measured for G1, which way is better, and its value once G1 is reached>" vs `ux.md:240-242` "with no target value" and B-2 sign `:333` "a target value" — inconsistency: "its value once G1 is reached" reads as a target. Say what distinguishes them, or drop one.
- S81 `ux.md:239-242` "is not met or missed but come close to ... a value the user's need does not rest under draws the work toward the number" — us B-11/ck B-5: the wording is not plain ("rest under"); the idea is lost.

### rn/checklists/product/readme.md
- No finding beyond its use in S27-S29.

### rn/checklists/session/plan.md
- S82 `plan.md:175` "### B-8" between B-4 and B-5 — ck F-4; renumber (unreleased). (Prior audit rn §5: kept.)
- S83 `plan.md:11` "A plan, the part of `steering.md` from its title to its tasks" and `:36-37` "turn makes the plan ... in a file of its own" vs F-1 `:45` "Does the steering the plan is put back into follow this template" with front matter, Next and Open "written by rn's scripts" (`:89-90`) — inconsistency/ck B-4: the plan's maker is judged on lines it does not write. F-1 should hold the plan's part (title to tasks) only.
- S84 `plan.md:11` "in the session's record, the folder where rn keeps one piece of work" vs `:33`, `:86` "the session's folder" — us B-13 two names for one thing, in one checklist; across the session checklists also "its record of the work" (`deliverable.md:230-231`), "the session's folder `.rn/<yyyymmdd>-<slug>/`" (`research.md:11`, `trial.md:102`), "the session's record" (`learnings.md:11`). One name.
- S85 `plan.md:19-37` the opening paragraph holds the purpose's idea, the stage rule, the task/action rule, research/trial, and what the plan keeps — ck B-1/us B-19: one paragraph of 19 lines; the stage rule is said again in B-5 `:198-201`, the action forms in F-1 `:84-88`, "only what is left" in B-6 `:232`. Keep the idea; let the items carry the rest.
- S86 `plan.md:72-73` two action forms vs `rn/scripts/rn.py:623-624` stop text "`  - [ ] {number}. <what is done>. <who does it>`" — inconsistency (cross-slice; prior audit rn 4.10: kept).
- S87 `plan.md:87-88` "A task line has no tick, as a task is in the steering only while an action of it is not ticked" and B-6 `:232` "a task whose actions are all done" — duplication within.
- S88 `plan.md:29-31, 73, 161` "one call to turn for each work" / "two actions of turn's on the same work" — matches decision 2; the code naming every call of a task `t<n>` (cross-slice, rn.py) breaks it. Listed as a touch point.

### rn/checklists/session/deliverable.md
- S89 `deliverable.md:230-234` one sentence of five clauses with three appositions ("every file ... outside `.rn/`, the folder where ...", "at the deliverable sign-off, where ...", "the plan, `steering.md` in that record, each one ...") — us B-11/B-19.
- S90 `deliverable.md:259` "the user approves the finished work from the proposal" — us B-12: "proposal" is not explained in this checklist.

### rn/checklists/session/research.md, trial.md
- S91 `research.md:87` and `trial.md:173` "a term ... that the reader may not know, with no line showing its meaning" under B-4 "Each line used by its readers" — ck B-5/B-3: understanding is a second thing under a usage item.
- S92 `trial.md:107-108` "the check that says whether it works, set before the run" — ck B-2: the opening's "set before the run" is asked by no item (B-1 asks only that a check exists).

### rn/checklists/session/learnings.md
- S93 `learnings.md:52-61, 111` "at which move", "a move that does not rest on the facts of the move before it" — us B-12: "move" is not explained here.
- S94 `learnings.md:60` B-1 sign "a term of rn's insides ... that no line shows the meaning of" — ck B-5: understanding under "What happened, in the records' own words".
- S95 `learnings.md:107` "Look for a place no learning takes up:" — ck F-1 form (S69).

## Cross-plugin: one piece of knowledge in several of lane, turn, rn

| # | Knowledge | Every place | Should be |
|---|---|---|---|
| S96 | Claude Code's record files: where they are (`~/.claude/projects/<folder>/<session>.jsonl`, `subagents/agent-<id>.jsonl`, `.meta.json`) and what an entry holds (`tool_use`, `tool_result`, `timestamp`) | `lane/hooks/lane/record.py:51-57, 60-95, 117, 163-166`; `turn/scripts/records.py:15-20, 42-51, 74-94`; `rn/scripts/rn.py:1643-1680` (`project_folders`, `lines_of`, `begun`, `conversations`), `:1737`; `dev/lane/trying.py:57, 66-78`; `dev/turn/trials/trial.py:54, 69-73`; `dev/turn/trials/roles/kept.py:88`; `dev/turn/trials/flow/flow.py:109-113`; `dev/rn/trials/moves/place.py:215-219`; `dev/rn/trials/moves/moves.py:100`; `dev/rn/trials/flow/flow.py:316` | one reader in lane's `record.py`, linked; trials import it |
| S97 | The project folder's name from a path | `rn/scripts/rn.py:1643-1655` (UTF-16 aware, 200-char cut and hash); `dev/turn/trials/trial.py:54` `re.sub('[^A-Za-z0-9]', '-', place)` — they disagree on non-ASCII and long paths | one function |
| S98 | Where Claude Code keeps records (`CLAUDE_CONFIG_DIR`) | honoured in `turn/scripts/records.py:74-78`; hard-coded `~/.claude` in `dev/lane/trying.py:57`, `dev/turn/trials/trial.py:54`, `dev/turn/trials/roles/kept.py:88`, `dev/rn/trials/flow/flow.py:316`, `dev/rn/trials/moves/moves.py:100` | `records.kept()` everywhere |
| S99 | Claude Code version the record format is taken from | "2.1.306" in `lane/hooks/lane/record.py:6,19,21,28,128`, `dev/lane/architecture.md:138,157`, `dev/lane/tests/helpers.py:180,191,255`, `dev/lane/tests/test_record.py:2`; CI pins `dev/package.json:4` "2.1.310"; `dev/rn/trials/moves/gh.py:25` "2.1.0" | one version, stated once |
| S100 | Hook command format (`<python check> || {...}; exec python3 ".../hooks/lane/<event>.py" <plugin>:<agent> '<step>:<lane>:<takes>'`) | written `lane/scripts/lay.py:48-58, 268-277`; read `lane/hooks/lane/lanes/__init__.py:224-247` (`laid`, `read`, `LANE`); parsed again `dev/lane/testing.py:136-149` (`rpartition("; exec ")`, `split(":", 2)`) | one module both ways, testing imports it (prior audit lane 3.1: kept) |
| S101 | Markdown code fences | `lane/hooks/lane/template.py:31` (``` and ~~~, indented); `turn/scripts/call.py:133`, `turn/scripts/forms.py:347` (``` only); `lane/hooks/lane/lanes/as_printed.py:21` `FENCE = "```"` | lane's `template` linked into turn (prior audit turn 3.2: kept, plus as_printed) |
| S102 | Markdown headings and list items | `lane/hooks/lane/template.py:116` `headings`; `lane/hooks/lane/step.py:40-42` (`"## Steps"`, `startswith("#")`); `turn/scripts/forms.py:17` `TOP = "## "`; `turn/scripts/call.py:19` `ITEM`; `rn/scripts/rn.py:138` `TITLE`, `:436`, `:1337` (`startswith("- ")`) | headings from `template.headings` |
| S103 | Front matter | `lane/hooks/lane/step.py:12` own `FRONT` regex; `lane/hooks/lane/template.py:15, 74-96` (`keys`, `text_of`), used by `rn/scripts/rn.py:310-318` | `step` uses `template` (prior audit lane 3.6: kept) |
| S104 | CCS reading | `turn/scripts/call.py:92-122` (`read_ccs`, `entries`); `rn/scripts/rn.py:765-800` (`entry`, own `json.loads` and shape check in `calls`), `:808` `decisions_of` | rn takes turn's `call` (already linked at `rn/scripts/call.py`, unused) (prior audit rn 3.1: kept) |
| S105 | The Python-version guard and its message "install Python 3.9 or later, run as python3" | generated by `lane/scripts/lay.py:52-58` into `lane/hooks/hooks.json:10,22`, `turn/hooks/hooks.json:10-82` (generated: fine); the requirement also in `lane/README.md:88`, `turn/README.md:108`, `rn/README.md:240` and S17's places | the READMEs are each plugin's own (fine); see S17 |
| S106 | The plugins' shared-code map (which files are shared) | the symlinks themselves; `dev/changed.sh:131`; `dev/README.md:9, 17`; `dev/check.sh:70-73`; `dev/rn/cosmic-ray.toml:6-12` (`excluded-modules` list of linked files); `dev/turn/cosmic-ray.toml:32-33` | derive from the links (S1) |

## Structure

| Part | Takes on | Split / reshape |
|---|---|---|
| `dev/architecture.md` | the base architecture (who does what, principles), repository layout, code rules, test rules with CI mechanics, release procedure | `dev/architecture.md`: figure, principles each with its why, repository structure. `dev/rules/` (or sections linked as "the project's rules"): code, test, release — the rules architecture.md B-5 says an architecture links. CI mechanics only in `tests.yml` comments |
| `dev/architecture.md` "Why it is so" | reasons for 8 principles mixed with 5 decisions of none | one subsection per principle; decisions (Languages, JSON, Messages, ...) under the part they shape |
| `dev/mutate.sh` | port finding, worker copies, config rewrite, git filter with an index copy, asyncio work-around, report check | `dev/mutate.py` (Python, linted and type-checked); config written from the toml's `[cosmic-ray]` table; add `cr-filter-pragma` |
| plugin discovery and type-check paths | `check.sh`, `properties.sh`, `changed.sh`, `tests.yml`, `mutate.sh`, three `cosmic-ray.toml` | one `dev/plugins.sh` (list; shared-code dependents from links); one `dev/typecheck.sh <plugin>` used by check.sh and each toml's test-command |
| check-scheme description | 7 places (S16) | why in architecture, commands in dev/README.md, usage in each script header |
| `.claude/rules/dev.md` | the order of work, but missing the UX step and naming fix.md nowhere | step 1 UX with `ux.md`; README after; name `fix.md` where findings are settled |
| `rn/checklists/session/plan.md` opening | purpose, idea, stage rule, task/action rule, research rule, what is kept | opening: user, purpose, the idea of links; the rest left to F-1 and the items that already ask it |
| tool configs | `pyproject.toml`, `ruff.toml`, `pyrefly.toml`, `.coveragerc` | ruff and pyrefly into `pyproject.toml`; `.coveragerc` stays (coverage on 3.9) |

## Cross-slice
- `rn/scripts/forms.py`, `rn/scripts/call.py` (links unused by shipped rn) — S46.
- `dev/lane/trying.py` outside `trials/` — S47.
- `rn/scripts/rn.py:623-624` third action form — S86.
- `rn/scripts/rn.py` naming every call of a task `t<n>` breaks plan.md's one call per work — S88 (decision 2).
- `dev/lane/testing.py:112-114` Hypothesis profiles, named in no doc — S13.
- `rn/CHANGELOG.md:4-6` restates the versioning rule of `dev/architecture.md:365-368` — S49.
- 38 `in ("...",)` sites to change under decision 4 — S76.
- The cross-plugin table S96-S106 lists places in lane, turn and rn.

## Prior audit points in this slice
- lane 1 (changed.sh shared list): kept, S1. lane 2.4 (E501): kept, S18 (now 78). lane 3.1: kept, S100. lane 3.6: kept, S103. lane 3.7: kept, extended, S96. lane 3.9: kept, S6/S16/S17/S5. lane 4.2: kept, S47.
- turn 3.2: kept, S101. turn 3.3: kept, S96. turn 3.8: kept, S46.
- rn 3.1: kept, S104. rn 4.10: kept, S86. rn §5 plan.md B-8: kept, S82.
- None dropped.

## Read
rn/checklists/checklist.md 168; rn/checklists/usability.md 208; rn/checklists/fix.md 77;
rn/checklists/product/code.md 202; prompt.md 150; architecture.md 218; ux.md 190; readme.md 219;
rn/checklists/session/plan.md 261; research.md 91; trial.md 85; learnings.md 117; deliverable.md 43;
.claude/rules/dev.md 115; output.md 70; issue.md 30; final-check.md 22;
dev/architecture.md 411; dev/README.md 19; dev/check.sh 55; dev/properties.sh 18; dev/mutate.sh 99;
dev/changed.sh 28; dev/githooks/pre-push 38; dev/package.json 6; .github/workflows/tests.yml 130;
README.md 21; pyproject.toml 30; ruff.toml 3; pyrefly.toml 1;
also whole: dev/{lane,rn,turn}/cosmic-ray.toml (15, 13, 15), .coveragerc 8, .gitignore 4,
.claude-plugin/marketplace.json 22, the brief common.md 51; the three prior audits read where they touch this slice.
Read in part for the cross-plugin table: lane/scripts/lay.py:48-60, lane/hooks/lane/lanes/__init__.py:224-250,
lane/hooks/lane/step.py:36-50, turn/scripts/call.py:88-145, turn/scripts/forms.py:340-355,
turn/scripts/records.py:70-82, rn/scripts/rn.py:305-318, 615-630, 760-800, 1630-1680, plus grep hits listed.

## Not read
None of the slice. Outside it, the files in the cross-plugin table were read at the lines cited only.
