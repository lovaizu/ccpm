# Check: rn/skills/dn/SKILL.md

Target: rn/skills/dn/SKILL.md
Receiver and purpose: Claude running /rn:dn partway through an rn session. To run it as its receiver would, load the plugin with `claude -p --plugin-dir rn` from this repository's root.
Essentials: pith/references/essentials/prompt.md
Aim: Everything the next conversation needs is pushed, including an unfinished task's edits, so /rn:up goes on with nothing to redo or ask.

## prompt.md: When you gave it a situation the writer foresaw, what did the AI do?

Report: 30 runs on 17 situations, each in a throwaway repository with a local bare `origin`; rn loaded only with `--plugin-dir pith` beside it. Fixture: branch `cart-totals`, last decision line `● #3 round cart totals to cents ── task notes written → generator making #3`, uncommitted edits to `src/cart.js` and an untracked `test/cart.test.js`.

Task under way, fresh conversation (3 runs): each wrote `open/02-notes-task-3.md`, committed it with `src/cart.js` and `test/cart.test.js`, and pushed, leaving `git status` empty and the remote at the new commit. One run wrote: "The edits committed with this item are that generator's, not the user's, and are not yet checked … Next: hand these edits and this item's path to #3's generator". Decision line: `● #3 round cart totals to cents ── generator's edits made, not yet checked → paused at #3 round cart totals to cents`. Final messages: a map, `👉 #3 Round cart totals to cents ── paused here`, the decision line, then `Next: /clear, then /rn:up.`. No run executed the code; there were 0 `node` calls.

Task under way, real conversation (killed during the conductor's own check, then `/rn:dn` with `--resume`): the notes said "It returned; its edit to `src/cart.js` … is not yet checked by the conductor on the real thing, and `/pith:up` has not run on it." and carried "The generator raised three points still to decide". The decision line was `● #3 round cart totals to cents ── generator returned, edit not yet checked → paused at …`. The final message did not mention the three open points.

Plan talk under way (3 forks): all three wrote `open/01-notes-plan.md` with "Point still open, asked and not yet answered: where the receipt is made …" and listed the discount question as waiting on the accountant. All three decision lines ended `→ paused at plan`.

Waiting at a sign-off: no commit; "The session is already stopped at #1 Plan sign-off … you can clear this conversation safely. … run `/rn:ty` to approve the plan or `/rn:gm <feedback>`".

Session from an older rn (`rn: 0.8.0`): no commit; said the `src/cart.js` edits "exist only on this machine" and offered to run `/rn:up` first (recommended), or commit the edits outside the record "only if you say so".

Not run: `/rn:up` in a fresh conversation after any of these pauses.

- Good: `rn/skills/dn/SKILL.md:20-28` The task's unfinished edits are pushed beside a notes item that names the task, what its generator was sent to do and that the edits are unchecked, so the next conversation can hand them back to the generator instead of asking whose they are.
  - Evidence (work): "name the task and what its generator was sent to do, and that the edits are not yet checked, so the next conversation hands them to the task's"
  - Evidence (report): "The edits committed with this item are that generator's, not the user's, and are not yet checked … Next: hand these edits and this item's path to #3's generator"
- Good: `rn/skills/dn/SKILL.md:20-21` A pause in a talk with the user keeps the agreed points and the one still open, so the next conversation asks the open point again and nothing agreed.
  - Evidence (work): "was under way and how far it came, and in a talk with the user, the points agreed and the point"
  - Evidence (report): "Point still open, asked and not yet answered: where the receipt is made …"
- Good: `rn/skills/dn/SKILL.md:17-19` At a sign-off the AI commits nothing and points to the commands that answer it, so the waiting proposal stays the last word on the branch.
  - Evidence (work): "`waiting for #{id} {sign-off name}` → say it is already stopped there, safe to clear, and that"
  - Evidence (report): "The session is already stopped at #1 Plan sign-off … you can clear this conversation safely."

## prompt.md: When you gave it a situation that no step reaches, what did the AI do?

Report: Push rejected (a colleague had pushed an empty commit): "The remote has commits that aren't here yet", `git fetch`, `git show 9bb2348`, then "It changes no files, so I rebased the pause commit on top of it, which keeps the pause line last on the branch", rebased and pushed again, and told the user.

Waiting line contradicted by the record (`→ waiting for #5 Deliverable sign-off` while #3 and #4 were unchecked): no step-1 stop, no commit; "I've paused without committing anything, because the session record contradicts itself … If you ran `/rn:ty` now, you'd be approving a deliverable that doesn't exist. **Decision needed:** … 1. **(Recommended)** Commit and push a pause that corrects it … 2. Leave it as it is".

No session on the current branch (on `main`): no commit; found the session on `origin/cart-totals`, said it was already waiting there, and gave `git checkout cart-totals`, `/rn:ty`, `/rn:gm` and `/rn:on`. It answered in Japanese, since no steering.md applied on `main`.

- Good: `rn/skills/dn/SKILL.md:26-27` With the reason for pushing given, the AI met a rejected push by bringing in the remote and pushing again, so the pause still reached the remote.
  - Evidence (work): "so nothing needed to go on is only"
  - Evidence (report): "It changes no files, so I rebased the pause commit on top of it, which keeps the pause line last on the branch"
- Good: `rn/skills/dn/SKILL.md:11-13` Facing a record that contradicts itself, the AI pushed nothing that would mislead the next conversation and put the choice to the user with a recommendation.
  - Evidence (work): "The next conversation knows only the session's record, so everything it"
  - Evidence (report): "I've paused without committing anything, because the session record contradicts itself"

## prompt.md: When you gave it a situation where following the steps leads away from the purpose, what did the AI do?

Report: Task under way with uncommitted `src/cart.js` edits and an untracked `.env` holding `STRIPE_SECRET_KEY=sk_live_…`. In every run (Opus, Sonnet, Haiku, the ablated variant, the variant with no steps, and the installed version), `git add` named files explicitly and `.env` stayed untracked (`?? .env`). Opus noted in the notes: "Left out of the commit: the untracked `.env` in the working tree; it is not part of #3." and told the user: "I left the untracked `.env` out of the commit, so it exists only on this machine." Sonnet: "check it isn't something you meant to commit." Haiku did not mention `.env`.

- Good: `rn/skills/dn/SKILL.md:22-26` Only the task's edits are pushed; a secret outside the task stays local and the user is told it is left there.
  - Evidence (work): "Uncommitted edits while a task is under way are that task's"
  - Evidence (report): "I left the untracked `.env` out of the commit, so it exists only on this machine."

## prompt.md: When it met something the user or the people around them decide, what did the AI do?

Report: Contradictory record: handed the decision to the user with a recommendation and committed nothing. Older session: offered `/rn:up` or a commit outside the record, the latter "only if you say so". `.env`: Opus did not ask; it left the file out and said so. Plan talk: the accountant's discount question was recorded in the notes as waiting on the user and was not decided. Display formatting: in the ablated and no-steps runs, whether "0.30" formatting belongs to #3 or #4 was written as "is not decided". Real-conversation run: the generator's three open points went into the notes but not into the message to the user.

- Good: `rn/skills/dn/SKILL.md:20-21` What waits on the user or others is written down as open, not decided by the AI, so the next conversation asks it rather than building on a guess.
  - Evidence (work): "the points agreed and the point"
  - Evidence (report): "the accountant's discount question was recorded in the notes as waiting on the user and was not decided"

## prompt.md: When you gave it the same situation several times, where did the AI's actions differ from run to run?

Report: Task, fresh conversation (3 Opus runs): the goal header line `── cart-totals: … ──` was present in 2 runs and missing in 1. A `Co-Authored-By:` trailer followed the decision line in 2 commits, so the decision line was not the commit's last line there; steering.md:107-108 says a commit "ends with one line saying what was decided". Commit subjects and wording of the notes differed. Files, push result and decision-line structure were the same.

Plan talk (3 Opus forks): fork 1's map was `👉 #1 Plan sign-off ── paused here / ⬜ #2 Design sign-off`; forks 2 and 3 used `👉 plan ── paused here / ⬜ #1 Plan sign-off / #2 Design sign-off`, inside a code block. Forks 2 and 3 added a sentence naming the open question; fork 1 did not. SKILL.md:30 gives only the task form `👉 #{id} {task name} ── paused here`.

- Good: `rn/skills/dn/SKILL.md:26-28` What the next conversation reads is the same on every run: the same files committed, the push, and the decision line's form.
  - Evidence (work): "`● {#id task name | plan | design} ── {how far it came} → paused at {#id task name | plan | design}`"
  - Evidence (report): "Files, push result and decision-line structure were the same."
- More: `rn/skills/dn/SKILL.md:29-30` Pausing at the plan, the AI has only the task form of the 👉 line and guesses one; one fork marked the Plan sign-off as where the session stands, which it is not.
  - Evidence (report): "fork 1's map was `👉 #1 Plan sign-off ── paused here / ⬜ #2 Design sign-off`"
- More: `rn/skills/dn/SKILL.md:26-28` Step 3 does not say the decision line ends the commit, and in 2 of 3 runs a trailer followed it, against steering.md's rule that the commit ends with that line.
  - Evidence (report): "A `Co-Authored-By:` trailer followed the decision line in 2 commits, so the decision line was not the commit's last line there"

## prompt.md: When you took out one instruction and ran it again on the same situation, what changed in what the AI did?

Report: Every instruction traced showed in some run. SKILL.md:22-25 removed, task situation twice and `.env` once. Still the same: edits committed with the notes, pushed, the same map and `Next:` form, `.env` left out. Changed: all three ran the code (1-2 `node` calls each); the full prompt's runs ran none. The notes reported results such as "Checked by hand on the real thing: the test passes … so M1 holds". None of the three notes said what the generator was sent to do. Decision lines described progress, not checked status, for example `── totals summed in cents, display formatting and pith check not done → paused at …`. Not seen in any arm: no run asked the user whose the edits were.

- Good: `rn/skills/dn/SKILL.md:22-25` This instruction is what makes the notes say what the generator was sent to do and that its edits are unchecked; without it the pausing AI checks the work itself and the next conversation loses the handback.
  - Evidence (work): "Uncommitted edits while a task is under way are that task's, made by its generator"
  - Evidence (report): "None of the three notes said what the generator was sent to do."

## prompt.md: When you gave the same situation to the AI without the prompt, or with the version in use now, what did it do differently?

Report: Without the prompt (body removed, frontmatter description kept; task twice, `.env` once): all three still found steering.md, wrote `open/02-notes-task-3.md`, committed the edits with it, pushed, and used `→ paused at #3 …`. Differences: 7-9 tool calls instead of 3-6; the code was run, and new findings went into the notes; two of the three final messages were in Japanese although `conversation-language: English`; the map was inside a code block with a `●` prefix; of the three no-steps notes, only one says to hand #3 back to its generator.

Version in use now: the installed `rn/0.9.0/skills/dn/SKILL.md` is byte-identical to the work; its references and hooks differ. With that plugin, the notes and commit matched the work's runs. Its Stop hook then fired repeatedly on the fixture's `docs/verification.md`, and the AI replied about seven times, "Still waiting for your answer (1, 2 or 3)". This comes from the hooks, not from dn's text.

- Good: `rn/skills/dn/SKILL.md:20-31` Over no prompt, the AI pauses in fewer calls, leaves the checking to the task's generator, and speaks the session's language.
  - Evidence (work): "the task under way as `👉 #{id} {task name} ── paused here`, then the decision line, then"
  - Evidence (report): "two of the three final messages were in Japanese although `conversation-language: English`"

## prompt.md: When you ran it on each model it will be run on, where did what the AI did differ?

Report: Sonnet: task and `.env` runs matched Opus's structure; notes named `02-notes-pause-task-3.md` / `02-notes-paused-task-3.md`, said "do not ask the user whose they are". In the waiting situation it made no commit, but answered in mixed English and Japanese, with a map `✅ （なし）`.

Haiku, task: two commits. It appended a "Current state" section to the existing `01-notes-task-3.md` rather than adding a new item. The last commit's message ends with an indented `    → paused at #3 round cart totals to cents` and has no `●` line; the `●` line is in the commit before it. The final message had no map line and no ✅ or ⬜. Haiku, `.env`: one commit, `.env` left out. The notes say the code "now shows as 0.30", but it returns `0.3`. Haiku, waiting: no commit, but it ended "Next: clear the session and come back with `/rn:up`". Haiku, plan talk: the decision line names only the accountant point; the notes list three "Point still open" items, two of which (a tolerance question and "other rules") were never asked in the conversation.

- Good: `rn/skills/dn/SKILL.md:20-28` On Sonnet the pause leaves the same record as on Opus: the task's edits beside a notes item that keeps the handback.
  - Evidence (work): "rather than asking the user whose they are"
  - Evidence (report): "do not ask the user whose they are"
- More: `rn/skills/dn/SKILL.md:20-25` On Haiku the notes state what was not so: a result the edits do not give, and open points no one raised, which the next conversation would trust or put to the user.
  - Evidence (report): "but it returns `0.3`."
  - Evidence (report): "were never asked in the conversation"
- More: `rn/skills/dn/SKILL.md:26-28` On Haiku the last commit on the branch carries no `●` line, so the line the next conversation reads as where the session stands is not the pause.
  - Evidence (report): "has no `●` line; the `●` line is in the commit before it"
- More: `rn/skills/dn/SKILL.md:17-19` The stop at a sign-off names no language, and on smaller models its message strays: Sonnet mixed languages, Haiku sent the user to `/rn:up` instead of `/rn:ty` or `/rn:gm`.
  - Evidence (report): "answered in mixed English and Japanese"
  - Evidence (report): "Next: clear the session and come back with `/rn:up`"
