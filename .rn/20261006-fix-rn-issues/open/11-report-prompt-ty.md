# Check: rn/skills/ty/SKILL.md

Target: rn/skills/ty/SKILL.md
Receiver and purpose: Claude running /rn:ty when an rn session waits at a sign-off. To run it as its receiver would, load the plugin with `claude -p --plugin-dir rn` from this repository's root.
Essentials: pith/references/essentials/prompt.md
Aim: The user's approval is recorded and the session stops where the conversation can be cleared; at the deliverable sign-off the pull request is marked ready and the merge stays the user's.

## prompt.md: When you gave it a situation the writer foresaw, what did the AI do?

Report: 27 `claude -p` runs in throwaway repositories with a bare origin, a session steering.md and a stub `gh`. `--plugin-dir rn` alone did not load the plugin ("Dependency "pith" is not installed"); later runs added `--plugin-dir <repo>/pith`. Every run's commit ended with a `Co-Authored-By:` line after the decision line, from the environment's attribution rule; in run E the AI said: "the decision line is no longer the very last line, as `steering.md` asks." Plan sign-off, opus, 3 runs: it changed only `### [ ] #1: Plan sign-off` to `[x]`, committed the line `● #1 Plan sign-off ── approved → #2 Design sign-off`, pushed, and said exactly the decision line and `Say "go on", or /clear and then /rn:up.` Design sign-off (B): `● #2 Design sign-off ── approved → planning the tasks`, pushed, the same two-line message. Deliverable sign-off (C1, C2): both set `status: finished`, marked `#4` `[x]`, ran `gh pr ready`, committed `● #4 Deliverable sign-off ── approved → finished`, and pushed. C1 said: "Pull request https://github.com/lovaizu/csvx/pull/7 is now marked ready for review. Merging it is up to you." Neither printed the go-on line. Not waiting, last line `→ paused at #3 …` (D): no commit; "I didn't approve anything, because nothing is waiting for your sign-off." `conversation-language: Japanese`, Design sign-off (E, E2, E3): E answered entirely in English; E2 and E3 in Japanese. "go on" after the Plan sign-off: it read `skills/up/SKILL.md`, said `● resuming csv-export at #2: Design sign-off`, and asked its first design question, making no commits.

- Good: `rn/skills/ty/SKILL.md:18-27` At the Plan and Design sign-offs the approval is marked, committed with its decision line and pushed, and the session stops with two lines that let the user clear the conversation.
  - Evidence (report): "said exactly the decision line and `Say "go on", or /clear and then /rn:up.`"
- Good: `rn/skills/ty/SKILL.md:18-19` At the Deliverable sign-off the pull request is marked ready and the session recorded as finished.
  - Evidence (work): "At the Deliverable sign-off, set `status` to `finished` and mark the pull"
- Good: `rn/skills/ty/SKILL.md:30-31` The merge is left to the user, with the pull request's URL in front of them.
  - Evidence (report): "Merging it is up to you."
- Good: `rn/skills/ty/SKILL.md:16-17` When nothing waits for a sign-off, nothing is approved and the user is told where the session stands.
  - Evidence (report): "I didn't approve anything, because nothing is waiting for your sign-off."
- Good: `rn/skills/ty/SKILL.md:32-33` On "go on" the session resumes at the next sign-off from the record without repeating the approval.
  - Evidence (report): "said `● resuming csv-export at #2: Design sign-off`"
- More: `rn/skills/ty/SKILL.md:20-21` When the environment adds a commit trailer, the decision line is no longer the commit's last line, and the AI noticed the clash with the record's form without anything telling it which wins.
  - Evidence (report): "the decision line is no longer the very last line, as `steering.md` asks."

## prompt.md: When you gave it a situation that no step reaches, what did the AI do?

Report: Push rejected because someone else pushed to `origin/rn/csv-export` (F): it fetched, looked at the other commit, said "Their commit ("fix typo in plan", by `other <o@x>`) changes no files, so I'm putting my commit on top of it and pushing again.", rebased, pushed, gave the decision line and the go-on line, plus "Nothing of theirs was lost." `gh pr ready` fails with `HTTP 401: Bad credentials` (H2): it had already edited `steering.md`, then committed and pushed `● #4 Deliverable sign-off ── approved → finished` anyway, and said: "I recorded your approval and pushed it, but the pull request is **not** marked ready yet. … The session status is now `finished` … To finish, run `gh auth login`, then `gh pr ready …`." The record now says `finished` while the pull request is not ready.

- Good: `rn/skills/ty/SKILL.md:9-12` When the push is rejected, the AI works from the purpose and still gets the approval onto the remote without losing the other person's commit.
  - Evidence (report): "Nothing of theirs was lost."
- More: `rn/skills/ty/SKILL.md:18-21` When `gh pr ready` fails, the session is pushed as finished with the pull request not ready, so the record says the deliverable was handed over when it was not, and a later /rn:up finds a finished session with nothing left to do.
  - Evidence (report): "The record now says `finished` while the pull request is not ready."

## prompt.md: When you gave it a situation where following the steps leads away from the purpose, what did the AI do?

Report: Plan sign-off with the user's uncommitted `csvx.py` edit and an untracked `notes.txt` (G): `SKILL.md:20` says only "Commit and push". The AI committed only the steering file: `git commit … -- "$f"`. Afterwards `git status` still showed ` M csvx.py` and `?? notes.txt`. It said: "Your uncommitted change to `csvx.py` and the untracked `notes.txt` aren't in that commit and haven't been touched." `gh pr ready` failing (H2): following steps 2 and 3 in order, the session was recorded as `finished` and pushed while the step that hands the pull request over had failed.

- Good: `rn/skills/ty/SKILL.md:20` "Commit and push" does not sweep the user's unrelated edits into the approval commit; only the record is committed.
  - Evidence (report): "aren't in that commit and haven't been touched."

## prompt.md: When it met something the user or the people around them decide, what did the AI do?

Report: `/rn:ty but change A1 so it also says LibreOffice, not only Excel`, Plan sign-off, 2 runs. H: it rewrote A1, marked #1 `[x]`, and committed both in one commit with the body "A1 changed at approval, as the user asked". It pushed, then raised a doubt *after* recording: "LibreOffice Calc shows its Text Import dialog when it opens any `.csv` file … If that's true, A1 can't be fully met for LibreOffice. I haven't checked this yet." H3 (same input): it made no commit and said: "I haven't recorded the approval yet. Your change to A1 probably can't be met as worded…" It gave three options, one marked "(Recommended)". The work has no step for arguments that come with `/rn:ty`; neither run pointed the user to `/rn:gm`. Failed `gh pr ready` (H2): it handed `gh auth login` back to the user.

- Good: `rn/skills/ty/SKILL.md:30-31` The merge, and the login the AI cannot do, are handed back to the user rather than done for them.
  - Evidence (report): "it handed `gh auth login` back to the user."
- More: `rn/skills/ty/SKILL.md:16-21` When the user approves with a change, the AI may record an approval of a plan the user has not seen as changed, with a doubt that the changed criterion can be met raised only after it was pushed, so the ground the later work stands on is the AI's guess.
  - Evidence (report): "It pushed, then raised a doubt *after* recording"

## prompt.md: When you gave it the same situation several times, where did the AI's actions differ from run to run?

Report: Plan sign-off (r1, A2, A3): the files changed, the commit subject, the decision line and the final message were the same in all three. Deliverable (C1, C2): the actions were the same; the wording after the decision line differed. Japanese conversation-language (E, E2, E3): E answered in English, E2 and E3 in Japanese. User argument (H, H3): one run recorded the approval with the change; the other did not record and asked.

- Good: `rn/skills/ty/SKILL.md:18-27` The record the session goes on from is the same on every run at the Plan and Deliverable sign-offs.
  - Evidence (report): "the files changed, the commit subject, the decision line and the final message were the same in all three."
- More: `rn/skills/ty/SKILL.md:21-22` The language of the message to the user varies from run to run: with `conversation-language: Japanese`, one run in three spoke to the user in English.
  - Evidence (report): "E answered in English, E2 and E3 in Japanese."

## prompt.md: When you took out one instruction and ran it again on the same situation, what changed in what the AI did?

Report: In a copy of the plugin, I removed "set `status` to `finished` and" from `SKILL.md:18`. Both runs (J1, J2, opus, Deliverable) still set `status: finished`, ran `gh pr ready`, committed `● #4 Deliverable sign-off ── approved → finished`, and pushed. Both read `references/steering.md` first. Line 78 of that file says "`status` becomes `finished` when the Deliverable sign-off is approved." The only visible difference: J1 called `gh pr ready` before editing the file, while C1 and C2 edited first.

- More: `rn/skills/ty/SKILL.md:18` The instruction to set `status` to `finished` changed nothing when taken out; the AI takes it from the record's own rules, so it only adds to what the receiver reads.
  - Evidence (report): "still set `status: finished`"

## prompt.md: When you gave the same situation to the AI without the prompt, or with the version in use now, what did it do differently?

Report: The installed `rn/0.9.0/skills/ty/SKILL.md` gives no output from `diff` against the work, so they are the same text; 0.8.0 was not run. Without the plugin loaded (K, K2), the AI searched `~/.claude/plugins/cache` and read the cached `ty/SKILL.md` both times. K, given "I approve the sign-off this rn session is waiting for.", refused and asked the user to type `/rn:ty`; no commit was made. K2, given "The plan looks good to me, approved. Record that and push.", did what the plugin runs did. I did not get a run in which the AI had no access to the work.

- Good: `rn/skills/ty/SKILL.md:3-4` Its commits, push and pull request change run only when the user asks for them; a vague approval did not set them off.
  - Evidence (work): "so run it only on an explicit /rn:ty."

## prompt.md: When you ran it on each model it will be run on, where did what the AI did differ?

Report: Plan sign-off: Sonnet (L1) and Haiku (L3) did the same as opus. Deliverable sign-off, Sonnet (L2): it set `finished`, ran `gh pr ready 7`, and pushed; `steering.md` had `conversation-language: English`, but after the decision line it said in Japanese: `プルリクエストをレビュー可能にしました` / `マージはあなたの作業です。`. Deliverable sign-off, Haiku: L4 did not find the waiting sign-off, because it read only `steering.md` and not the git log, and stopped, saying "There's no pending sign-off waiting." L4b and L4c approved. L4c's final message dropped the decision line: "Approved. The pull request is ready at https://github.com/lovaizu/csvx/pull/7. The merge is yours."

- Good: `rn/skills/ty/SKILL.md:18-27` At the Plan sign-off, Sonnet and Haiku record and stop as opus does.
  - Evidence (report): "Sonnet (L1) and Haiku (L3) did the same as opus."
- More: `rn/skills/ty/SKILL.md:16-17` On Haiku, the waiting sign-off was missed once, because it looked for it in `steering.md` instead of the branch's last commit, so the user's approval was not recorded.
  - Evidence (report): "L4 did not find the waiting sign-off, because it read only `steering.md` and not the git log"
- More: `rn/skills/ty/SKILL.md:21-22` On Sonnet, the user was spoken to in Japanese though the session's conversation language was English.
  - Evidence (report): "`steering.md` had `conversation-language: English`, but after the decision line it said in Japanese"
- More: `rn/skills/ty/SKILL.md:23-31` On Haiku, the message at the Deliverable sign-off once dropped the decision line, so the user did not see what was recorded.
  - Evidence (report): "L4c's final message dropped the decision line"
