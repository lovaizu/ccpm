# Evaluation — rn as a whole, per viewpoints.md — 1eaf227

Scope: read in full `rn/skills/{on,dn,up,ty,gm}/SKILL.md`, `rn/references/{conductor,implement,evaluate,steering}.md`, and `rn/docs/design.md` (as the author's claim only). `rn/` is unchanged between 1eaf227 and HEAD. Nothing was run. `evaluations/01-try-issue-18.md` was deliberately not read (an earlier verdict).

## Purpose, stated from the files

A goal that outlives one conversation keeps going: `rn` draws the real aim out of the user, keeps the plan and where the session stands in git (`steering.md`), gets each task built by one agent and judged against its purpose by another, and brings the user in only for decisions that are theirs (the plan, an approach, the finished work). A fresh conversation picks the session up from git alone (`skills/on/SKILL.md:9-10`, `skills/up/SKILL.md:9-10`, `references/conductor.md:3-9`, `references/steering.md:3-4`).

## Verdict

**The prompt reaches its purpose in its structure, with two faults that would make it go wrong in ordinary use, and it has not yet been shown end to end on a real case.** The generator/evaluator split, the purpose-first briefs, the "decide the next move by the Goal" role, and the git-only hand-off are all in place and consistent across the nine files. The Mores that decide it:

1. **A second-pass evaluator is handed the earlier verdict through the commit range.** The conductor names "the commits since the last check-off" (`references/conductor.md:19-20`). After a failed first pass, that range contains `docs: evaluation {NN} — Result — task #N` (`references/conductor.md:43`), whose diff *is* the earlier verdict. The evaluator is told to read "the commits named to you" (`references/evaluate.md:30`) and at the same time not to judge from `evaluations/` (`references/evaluate.md:53-55`). Case: task #3 fails once, the implementer fixes it, the new evaluator runs `git show` over the named range and reads verdict 04 before judging. This breaks exactly the property `conductor.md:40-41` exists to keep. The fix belongs in `conductor.md:19-20`: name the implementer's commits (the build and its fixes), not the whole range.
2. **At a sign-off, the Plan evaluator is not told which tasks it is judging.** `evaluate.md:12-13` and `:19-22` judge "the tasks up to the next sign-off". When the Plan kind is run, the first incomplete task *is* a sign-off: #1 at the Plan sign-off, or the Design sign-off whose follow-on tasks the conductor has just written after it (`conductor.md:22-25`). Read literally, the "next sign-off" is that same task, so the new tasks after a Design sign-off fall outside what is judged. The conductor's hand-off also names no target for the Plan kind (`conductor.md:37-38` covers only a task's commits or a migrated plan). Case: at a Design sign-off, the evaluator checks tasks #2–#4 (already built and checked off), passes, and the tasks #6–#9 the user is about to approve never get an independent look. The fix belongs in `conductor.md:24` / `:37-38`: name the pending sign-off and the tasks written for it.

The remaining Mores below are smaller. Each would make the text more robust but does not decide the verdict alone.

**The real case that settles it:** one fresh `/rn:on` on a small real request in a scratch clone, run through to the Evaluation sign-off. It should include a Design sign-off, one Result that fails and is re-evaluated, a `/rn:dn` → `/clear` → `/rn:up`, and a plain `/rn:gm` from a PR review. Faults 1 and 2 would show up in the second-pass and Design-sign-off evaluators' transcripts. Whether `${CLAUDE_PLUGIN_ROOT}` expands in skill bodies, so the conductor can hand agents absolute brief paths (`conductor.md:16-17`, `:36-37`), is also settled only by running.

## Structure

### Are generation and evaluation split?

**Good**
- Every result has a separate evaluator. The implementer is `Agent`, `model: sonnet` (`conductor.md:16`). The evaluator is `Agent`, `model: opus`, "a fresh one each time" (`conductor.md:36`). Plans, which the conductor writes, are also evaluated by that separate agent (`conductor.md:24`, `:28`; `steering.md:150-151` for a migrated plan).
- The generator's own check is never final. `implement.md:14-15` has the implementer check itself, and the session still "moves on only when it holds" under someone else's judgment (`implement.md:3-5`).

**More**
- None.

### Is the evaluator kept clear of the generator's pull?

**Good**
- The hand-off is explicit: "not the implementer's account and not an earlier verdict" (`conductor.md:40-41`). The evaluator reads its brief itself, so no summary is passed on (`conductor.md:7-9`), and it is told not to judge from `evaluations/` or the PR (`evaluate.md:53-55`).
- A disputed verdict goes to a *fresh* evaluator, and on the conductor's own plan the dispute goes straight to the user (`conductor.md:58-61`).

**More**
- Fault 1 above: the commit range handed on a second pass carries the earlier verdict (`conductor.md:19-20` vs `:40-43`, `evaluate.md:30`, `:53-55`).
- "A fresh evaluator, told which of its questions to answer again" (`conductor.md:58-59`) hands on the conductor's disagreement. That is pull of a milder kind. Naming only the question, not the reason, keeps it small. The text does not say which; adding "name the question only" at `conductor.md:59` would close it.

### Does a role between them decide the next move by the purpose?

**Good**
- `conductor.md:47-65` decides by what the Goal needs, not by a count. It covers every move: accept, send back to whoever can fix it, re-evaluate on a verdict that misjudges, and stop for the user when the fix would change the Goal, a criterion or an approved approach, when a fault recurs, or when it is a matter of taste, scope or cost. "Change the viewpoints" is covered through the criteria: the user's answer goes into `steering.md` before work goes on (`conductor.md:64-65`), and the evaluator judges against that.
- A sign-off that the verdict finds short gets a new task before it (`conductor.md:55-57`), so there is always something to send the work back to.

**More**
- The reuse rule (`conductor.md:31-32`) sits beside the numbered flow, not in it. Case: on `/rn:up` at a Design sign-off, the conductor follows step 3 ("have the plan evaluated") and runs a new evaluator, although a verdict on the unchanged plan is already committed. It belongs as the first step of "Having a result evaluated" (`conductor.md:34-36`).

## Generation

### Is it handed the essential purpose?

**Good**
- Each brief opens on what its result is for: `conductor.md:3-7`, `implement.md:3-5`, `evaluate.md:3-8`, and each skill's opening line (e.g. `skills/gm/SKILL.md:9-10`: "so the revision starts from the feedback and not from a summary of it").
- The implementer gets the Goal ("why the work exists") and the Purpose, and treats Steps as the planned way it may leave (`implement.md:7-10`). Feedback and verdicts are passed word for word, not summarised (`conductor.md:17-18`, `skills/gm/SKILL.md:16-20`).
- `/rn:on` reaches past the request to "the aim they had not put into words" (`skills/on/SKILL.md:19-20`, `steering.md:22`).

**More**
- None in these files.

### Does it check its own result against that purpose?

**Good**
- The implementer checks against the Purpose "on the thing itself — run it on a real case where it runs", and loops back to building when it falls short (`implement.md:14-15`).
- The plan writer checks that tasks trace to criteria and criteria to the Goal as agreed (`skills/on/SKILL.md:23-25`).

**More**
- The hand-off has no check that what it wrote is enough. The purpose is that `/clear` then `/rn:up` resume "with nothing more said" (`conductor.md:111-112`), but steps 1–4 (`conductor.md:114-126`) write `State` without checking it against that. Case: a question the user answered in words mid-task (`conductor.md:64-65`) gets recorded only in the conversation, and the next session asks it again. One line in step 1, "read `steering.md` as a fresh conversation would, and add what it would still need", closes it.

## Evaluation

### Is it handed the essential viewpoints?

**Good**
- Each kind has three to five questions drawn from the purpose, not a checklist of steps or formats (`evaluate.md:15-26`, `:32-37`, `:43-49`). "Do the criteria survive a change of means?" (`evaluate.md:17-18`) targets the commonest plan fault directly.
- The migration-only question "Is nothing lost?" (`evaluate.md:25-26`) is scoped to the case where it matters.

**More**
- Fault 2 above: at a Plan sign-off or Design sign-off, "the tasks up to the next sign-off" does not tell the evaluator which tasks to judge (`evaluate.md:12-13`, `:19-22`; `conductor.md:24`, `:37-38`).

### Does it evaluate whether the purpose is achieved?

**Good**
- The evaluator states the purpose from `steering.md` itself (`evaluate.md:56-57`). It checks "on the thing itself — run it on a real case" (`evaluate.md:32-33`, `:43-44`), in a remote-less clone when running would commit, push or post (`evaluate.md:58-60`). It opens its verdict on "whether the result reaches its purpose and the Mores that decide it" (`evaluate.md:65-66`), which keeps a detail from failing the work.
- The Session kind re-reads the Goal for what the criteria missed (`evaluate.md:45-46`), so passing every criterion is not enough on its own.

**More**
- `evaluate.md:60` says "Leave the repository … as you found them", while step 5 writes the verdict into the session directory inside the repository (`evaluate.md:64-67`). An evaluator that takes step 3 literally may write the verdict outside the repo or refuse. Adding "apart from the verdict file" at `:60` removes the conflict.
- For a migrated plan, the Plan questions judge a plan the old `rn` wrote to its own shape. For example, "the tasks reach the sign-off that ends them" (`evaluate.md:19-22`) may not hold for a 0.8.0 plan written to the end. `conductor.md:60-61` also sends plan disputes to the user "at once" on the ground that the conductor wrote the plan, which it did not. Whether this produces spurious fails is settled by running `/rn:up` on a real 0.8.0 session (the issue-18 session).

## Work steps

### Are only context-dependent work rules written as steps?

**Good**
- What is written as steps is what an agent could not guess: commit messages and the `complete task #` marker a later command keys on (`conductor.md:52-53`, `implement.md:16-17`, `skills/ty/SKILL.md:19-20`); the `<!-- rn -->` marker and the GraphQL query that tells rn's replies from the user's (`skills/gm/SKILL.md:17-21`); the session map's shape (`conductor.md:89-102`); the frontmatter and headings commands read (`steering.md:8-9`, `:79-83`); where verdicts land (`conductor.md:39`); and the dialogue style this user wants (`skills/on/SKILL.md:15-20`).
- Judgment is left to the purpose: "Build it." (`implement.md:13`), and "act on what the Goal needs" (`conductor.md:49`).

**More**
- `/rn:on` writes `steering.md` (step 3) before it checks the tree and creates the branch (step 4). The check "uncommitted changes in the tree are the user's" (`skills/on/SKILL.md:27-28`) then meets the untracked plan rn itself just wrote. Case: the agent asks the user whether to set aside its own `steering.md`, or it stashes the user's changes together with it. Checking the tree and creating the branch before writing the plan removes the conflict.

### Are they steps, not rules or prohibitions?

**Good**
- Prohibitions sit inside the step they govern and carry their reason. Examples: "without `complete task #` — that marker belongs to the check-off" (`implement.md:16-17`); "Hand it nothing else … so it judges the result and not the story" (`conductor.md:40-41`); "Ask in plain words, not a list of options" (`skills/on/SKILL.md:18`).
- "Fold what the work taught" (`conductor.md:67-69`) is called from the flow ("(below)", `conductor.md:51`), not left beside it.

**More**
- The reuse rule at `conductor.md:31-32` is the one rule standing beside the flow (see Structure above).
- A minor mismatch: `steering.md:80-81` defines `status: running` as "while a conversation holds the session", but closing at the Evaluation sign-off (`skills/ty/SKILL.md:23-26`) leaves `running` on a session nothing holds. Commands read finished from the sign-off (`steering.md:82-83`, `:126`), so nothing breaks, but the field then says something false. Setting it in `ty` step 4, or dropping the "while held" definition, aligns them.
