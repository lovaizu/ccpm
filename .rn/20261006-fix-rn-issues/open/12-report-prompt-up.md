# Check: rn/skills/up/SKILL.md

Target: rn/skills/up/SKILL.md
Receiver and purpose: Claude running /rn:up in a fresh conversation on a branch with an rn session. Run as its receiver would with `claude -p --plugin-dir rn` from the repository root.
Essentials: pith/references/essentials/prompt.md
Aim: The session goes on from its record without the user explaining anything again: a stop at a sign-off gives the proposal again, anything else takes up the next move.

## prompt.md: When you gave it a situation the writer foresaw, what did the AI do?

Report: About 45 runs over 12 session states in throwaway repositories with a local bare origin; `claude -p --plugin-dir rn` alone did not load rn (its dependencies writ and pith were not installed), so every run added `--plugin-dir` for pith and writ. Waiting at #1 Plan sign-off, level with origin/main, English (Opus, 3 runs): each printed `● resuming export-csv at #1: Plan sign-off` and repeated the commit body exactly, ending with `● plan ── worked out → waiting for #1 Plan sign-off`, and made no commits. Japanese conversation-language: translated the body, kept `●`, `──`, `/rn:ty`, `/rn:gm`, and to find `plugin.json`, it ran `find / -path '*copy2/rn/.claude-plugin/plugin.json'`. No session: "There's no rn session on this branch (`main`), so I stopped without resuming." Finished session: "The session `export-csv` on this branch is already finished … To start new work, run `/rn:on`." Older rn session: both runs read on/SKILL.md, conduct.md and essentials/plan.md, made no commits, and asked one language question first. Feedback item: merged, printed `● resuming export-csv at the next move of the last decision line: working out the plan again from your feedback`, and asked one question. python3 missing: stopped with install instructions.

- Good: `rn/skills/up/SKILL.md:25-28` At a sign-off with the branch level, the user gets the proposal back word for word and nothing is done in their name, so they can approve or give feedback without explaining anything.
  - Evidence (work): "give the proposal again as that commit's message body prints it, the decision line included"
  - Evidence (report): "repeated the commit body exactly, ending with `● plan ── worked out → waiting for #1 Plan sign-off`"
- Good: `rn/skills/up/SKILL.md:28-29` When the session stopped anywhere but a sign-off, the receiver takes up the next move from the record, so feedback left before the conversation was cleared is acted on without being given again.
  - Evidence (work): "Otherwise take up the session"
  - Evidence (report): "working out the plan again from your feedback"
- Good: `rn/references/steering.md:136-137` With no session or a finished one, the user is told so and where to go next, and nothing is touched.
  - Evidence (work): "None → say there is no session on this branch: check out the session's branch, or run `/rn:on`."
  - Evidence (report): "There's no rn session on this branch (`main`), so I stopped without resuming."
- Good: `rn/skills/up/SKILL.md:16` Without a working python3 the user is told how to install it before anything is written.
  - Evidence (work): "Check that `python3` runs; when it does not, say so and how to install it, and stop."
  - Evidence (report): "stopped with install instructions"
- More: `rn/references/steering.md:139-140` To tell whether the session is older, the receiver must find rn's own `plugin.json`, and the path it is handed does not resolve in a file read from the skill, so it searches the whole disk; the wait grows, and a search can land on another copy of rn.
  - Evidence (report): "it ran `find / -path '*copy2/rn/.claude-plugin/plugin.json'`"

## prompt.md: When you gave it a situation that no step reaches, what did the AI do?

Report: Waiting at sign-off, but origin/main one commit ahead (Opus, 3 runs): all ran `git merge --no-edit origin/main`, added a Fact such as "- Fact, src/todo.py:5 (merged from main): a todo is done when its `done` key is true…", made a new commit with the proposal as body and a decision line such as `● plan ── main's done state taken in → waiting for #1 Plan sign-off`, pushed, and showed the new proposal with a short explanation first. Runs 1 and 3 added under "For you to decide" the change to M1; run 1 wrapped the proposal in a code fence; run 2 left out the `● resuming` line. Uncommitted edits in the working tree (2 runs): both repeated the proposal, then noted "the working tree has two changes that were never committed… I haven't touched them." Neither committed or discarded anything.

- Good: `rn/skills/up/SKILL.md:25-29` When the default branch moved on while the user was away, the receiver takes it in and brings back a proposal that matches it, rather than one the user would approve on stale ground.
  - Evidence (work): "and the branch is level with the latest default branch"
  - Evidence (report): "made a new commit with the proposal as body and a decision line such as `● plan ── main's done state taken in → waiting for #1 Plan sign-off`"
- Good: `rn/skills/up/SKILL.md:9-12` Edits the user left uncommitted are neither swept into the session nor thrown away, and the user is told they are there.
  - Evidence (work): "The user can clear the conversation at any stop and come back without explaining anything again"
  - Evidence (report): "the working tree has two changes that were never committed… I haven't touched them."

## prompt.md: When you gave it a situation where following the steps leads away from the purpose, what did the AI do?

Report: After the proposal, the user changed the Goal in steering.md and committed it themselves (`tweak goal: share with team`, no decision line); the last decision line still says `waiting for #1 Plan sign-off` and the branch is level. Run 1 repeated the old proposal word for word, then added "**This proposal is out of date.** … your commit `bf0e410` … added 'Also share it with their team.'" and offered `/rn:gm …` (recommended) or `/rn:ty`. Runs 2 and 3 did not repeat the proposal: "I'm not showing the plan proposal again because it's out of date." Each asked one question. No run committed anything.

- More: `rn/skills/up/SKILL.md:25-28` When the record changed after the proposal was made, the step to repeat it "adding nothing" collides with going on from the record, and nothing tells the receiver which wins; one run in three repeated a proposal it called out of date, two withheld the proposal, so the user cannot tell what they would be approving with `/rn:ty`.
  - Evidence (work): "adding nothing and leaving nothing out, and stop"
  - Evidence (report): "I'm not showing the plan proposal again because it's out of date."

## prompt.md: When it met something the user or the people around them decide, what did the AI do?

Report: Old session: every Opus and Sonnet run asked the user to confirm the languages before anything else, and wrote nothing. Feedback and user-commit runs 2 and 3: each asked one question about what they want, offering no ways to choose from. Behind: the AI decided to merge main and rewrite the plan's Facts and M1 without asking, then put the M1 change before the user under "For you to decide" (runs 1 and 3). Dirty tree: it left the uncommitted edits alone and named them for the user. Without the prompt: the runs left the merge to the user and asked "merge or rebase?", plus which conversation language to use.

- Good: `rn/references/steering.md:150` Migrating an older session, the receiver asks the user only what the old record cannot settle, the languages, and writes nothing before it is answered.
  - Evidence (work): "ask only what it leaves unclear"
  - Evidence (report): "every Opus and Sonnet run asked the user to confirm the languages before anything else, and wrote nothing"
- Good: `rn/references/conduct.md:60-62` The merge of the default branch, which is not the user's to decide, is done without asking, and what it changes in the plan is put before the user.
  - Evidence (work): "First merge the latest default branch from the remote into the branch, keeping both sides' intent"
  - Evidence (report): "then put the M1 change before the user under "For you to decide" (runs 1 and 3)"

## prompt.md: When you gave it the same situation several times, where did the AI's actions differ from run to run?

Report: Level (3 runs): identical text; only how they found the session differed (the `git diff` command once, `ls` twice). Behind (3 runs): the same actions; they differed in whether the `●` resuming line was printed (missing in run 2), the code fence (run 1 only), whether the M1 note was added (runs 1 and 3), and the wording of the decision line. User commit (3 runs): run 1 repeated the old proposal with a warning and options; runs 2 and 3 held it back and asked a question. Dirty (2 runs): run 2 wrapped the proposal in a code fence and added `/rn:gm` guidance. Old (2 runs): only run 2 printed a `●` resuming line, `● export-csv を #2「Add export subcommand writing CSV」から再開します`, before saying it would migrate the session first.

- Good: `rn/skills/up/SKILL.md:25-28` In the plain sign-off case the user gets the same text every time.
  - Evidence (work): "give the proposal again as that commit's message body prints it"
  - Evidence (report): "Level (3 runs): identical text"
- More: `rn/skills/up/SKILL.md:17-23` Whether the user is told where the session resumes varies by run, and for an older session one run announced a resume at a task it then did not take up, since it migrated to a new Plan sign-off instead; the user is told a place the session is not going to.
  - Evidence (report): "only run 2 printed a `●` resuming line, `● export-csv を #2「Add export subcommand writing CSV」から再開します`, before saying it would migrate the session first"

## prompt.md: When you took out one instruction and ran it again on the same situation, what changed in what the AI did?

Report: Step 1 removed, level state: it no longer ran `python3 --version`; the rest was identical; the no-python case without step 1 was not run. "adding nothing and leaving nothing out" removed: in the dirty state, the same proposal plus the same kind of note; in the user-commit state, the proposal in a code fence, then "**This proposal no longer matches the record.**" and two numbered options; both look like the full prompt's run 1 in those states. "and the branch is level with the latest default branch" removed, behind state: it did not fetch or merge, repeated the old proposal unchanged and stopped; with the condition in place, all 3 runs merged and re-proposed.

- Good: `rn/skills/up/SKILL.md:25-26` The level condition is what keeps the user from being handed a stale proposal; without it the receiver repeats the old one and stops.
  - Evidence (work): "and the branch is level with the latest default branch"
  - Evidence (report): "it did not fetch or merge, repeated the old proposal unchanged and stopped"
- More: `rn/skills/up/SKILL.md:27-28` In the states tried, taking out "adding nothing and leaving nothing out" changed nothing the receiver did, while in the state where it bites hardest, the user's own commit, it is the words two runs out of three set aside; it costs attention without its effect being shown (the plain sign-off state was not tried without it).
  - Evidence (report): "both look like the full prompt's run 1 in those states"

## prompt.md: When you gave the same situation to the AI without the prompt, or with the version in use now, what did it do differently?

Report: Without the prompt (body reduced to its title), level state: it replied in Japanese, summarised the plan in its own words instead of repeating the proposal, and recommended `/rn:ty`. Behind state: it did not merge, asked the user to choose merge or rebase, `/rn:ty` or `/rn:gm`, and the conversation language; no commits. With the version in use now (`~/.claude/plugins/cache/ccpm/rn/0.9.0`, whose `up/SKILL.md` matches the work, with different references and hooks): level, the same proposal in a code fence; behind, 22 turns at $1.45, against 8–9 turns at about $0.36 for the work, ending with a question and no sign-off proposal; user commit, 27 turns at $1.14 and 5 commits, ending with a question.

- Good: `rn/skills/up/SKILL.md:25-29` Over Claude without it, the user gets the proposal itself rather than a summary, in their language, and is not asked to decide the merge.
  - Evidence (work): "translated into the conversation language when the two differ"
  - Evidence (report): "summarised the plan in its own words instead of repeating the proposal"
- Good: `rn/skills/up/SKILL.md:28-29` Over the version in use, the behind case reaches a sign-off proposal at about a quarter of the cost; the SKILL.md is the same in both, so the gain comes from the references it hands to.
  - Evidence (work): "Otherwise take up the session as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`."
  - Evidence (report): "22 turns at $1.45, against 8–9 turns at about $0.36 for the work"

## prompt.md: When you ran it on each model it will be run on, where did what the AI did differ?

Report: Opus (default), Sonnet (`claude-sonnet-5-5`) and Haiku (`claude-haiku-4-5-20251001`). Sonnet: level, the same as Opus; Japanese, it printed the resuming line in Japanese but left the proposal untranslated, in a code fence, with the note "(コミットメッセージ本文の提案は英語で、会話言語も日本語なので、上の本文は原文のままです。)"; behind, like Opus; user commit, repeated the proposal and noted the user's commit; old, asked the language question. Haiku: level, it ran `git merge main` (local branch) and reformatted the proposal, adding bold labels and an "**Acceptance criteria:**" header that is not in the commit body; behind, it compared only against local `main` and never fetched, repeated the old proposal including the commit subject line, and did not merge; user commit, repeated the proposal including the subject line and did not mention the user's commit; old, it searched for `plugin.json` and found `~/.claude/plugins/data/rn-inline/plugin.json`, printed `● resuming export-csv at #2: Add export subcommand writing CSV` and "I'll check the data structure and start implementing the export subcommand.", and ended asking what fields the todo items have (23 turns, no commits).

- Good: `rn/skills/up/SKILL.md:25-28` On Sonnet the plain, behind and old cases go as on Opus.
  - Evidence (work): "give the proposal again as that commit's message body prints it, the decision line included"
  - Evidence (report): "level, the same as Opus"
- More: `rn/skills/up/SKILL.md:26-27` On Sonnet with a Japanese conversation, the user got the proposal in English with a note that reads the rule backwards, so they read a proposal in a language they did not choose.
  - Evidence (report): "left the proposal untranslated, in a code fence"
- More: `rn/skills/up/SKILL.md:25-28` On Haiku the proposal is reshaped and the default branch is taken from the local copy, so the user gets a proposal that is not the one recorded, and in the behind case a stale one.
  - Evidence (report): "it compared only against local `main` and never fetched"
- More: `rn/references/steering.md:139-140` On Haiku an older session was not recognised as older: it found another rn's `plugin.json`, announced a resume at #2 and set out to implement, so the migration the user needs never starts.
  - Evidence (report): "found `~/.claude/plugins/data/rn-inline/plugin.json`"
