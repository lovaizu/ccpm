# Check: rn/skills/on/SKILL.md

Target: rn/skills/on/SKILL.md
Receiver and purpose: Claude running the /rn:on command in a git repository with a GitHub remote. To run it as its receiver would, load the plugin with `claude -p --plugin-dir rn` from this repository's root.
Essentials: pith/references/essentials/prompt.md
Aim: A session starts on the user's branch when it is a fresh worktree's or else a new one, with steering.md and a draft pull request, and the conductor goes on to hear the plan without asking anything the repository settles.

## prompt.md: When you gave it a situation the writer foresaw, what did the AI do?

Report: With `--plugin-dir rn` alone the plugin did not load ("`rn/.claude-plugin/plugin.json` declares `"dependencies": ["writ", "pith"]`"); with `--plugin-dir rn --plugin-dir pith --plugin-dir writ` it loaded. Every run first ran `python3 --version` and `git status`. With a modified README.md (a4) the AI stopped after two tool calls and touched nothing. On `main`, every run fetched and created a new branch from `origin/main`. In a fresh worktree on `tags-wt` (w1, w2) both used it as is: "ブランチ `tags-wt` は main の最新と同じ位置なので、このまま使います". With local `main` behind (a8) it branched from `origin/main`. Every Opus run asked one question with one proposal: English for the repository, Japanese for the talk. Each steering.md had `rn: 0.9.0`, the two languages, the default paths, and Tasks #1 and #2 only. Every Opus run made two commits with the decision lines `● plan ── started → working out the plan` and `● plan ── pull request opened → working out the plan`. Every Opus run that got to step 5 read `references/essentials/plan.md` and `conductor.md`, stated its reading of the request and asked one question about why, with no proposed answer.

- Good: `rn/skills/on/SKILL.md:18-19` The user's uncommitted work is never swept into the session; the run stops and says so.
  - Evidence (work): "When the working tree has uncommitted changes, say so"
- Good: `rn/skills/on/SKILL.md:20-23` A fresh worktree's branch becomes the session branch, and from `main` (even a stale local one) the session gets a new branch from the latest default branch.
  - Evidence (report): "ブランチ `tags-wt` は main の最新と同じ位置なので、このまま使います"
- Good: `rn/skills/on/SKILL.md:29-35` The session ends turn two with steering.md, two commits carrying the decision lines, and a draft pull request whose URL is recorded.
  - Evidence (report): "Every Opus run made two commits with the decision lines"
- Good: `rn/skills/on/SKILL.md:36-37` The conductor goes straight on into hearing the plan with one open question about why, asking nothing the repository settles.
  - Evidence (report): "stated its reading of the request and asked one question about why, with no proposed answer"

## prompt.md: When you gave it a situation that no step reaches, what did the AI do?

Report: `/rn:on` with no arguments (a6): the AI checked python3 and git, made no branch and wrote nothing. It asked for the goal and the languages in one message: "`/rn:on` に「何をしたいか」が書かれていなかったので、ここで止めています。目標が決まらないと、作業フォルダ名(`.rn/20261007-{名前}/`)もブランチも決められないためです。次の2点を教えてください。1. **何をしたいか** … 2. **言語** …". Untracked `.DS_Store` only (a7): the AI checked `git check-ignore` and `core.excludesfile`, then went on, staged only steering.md by path, and told the user it had left the file alone. Local `main` one unpushed commit ahead (b1): it branched from `origin/main`, without the commit, and said: "ローカルの `main` には push していないコミット `8329921 add delete stub` が 1 つありますが、触らずにそのまま残しています（このブランチには入っていません）。" It did not ask whether the commit belonged in the work.

- Good: `rn/skills/on/SKILL.md:9-13` Without a goal the AI neither guesses one nor makes a branch; it stops and asks, from the purpose that the goal must be what the user wants.
  - Evidence (report): "made no branch and wrote nothing"
- More: `rn/skills/on/SKILL.md:25-28` With no arguments, the user is asked two points in one message, the goal and the languages, so the goal, the point the whole session rests on, shares the user's attention with a yes/no on languages.
  - Evidence (report): "次の2点を教えてください。1. **何をしたいか** … 2. **言語** …"

## prompt.md: When you gave it a situation where following the steps leads away from the purpose, what did the AI do?

Report: `.DS_Store` (a7): read literally, SKILL.md:18-19 would stop the session for a stray Finder file. The AI did not stop. It went on and reported the file to the user. Unpushed commit (b1): following step 2 left the user's unpushed commit out of the session branch; the AI followed the step and said it had done so. Feature branch (a5): with "A second name for the same work leaves the user's worktree and its branch apart" (SKILL.md:23-24), the AI put the new branch in a separate worktree, `../a5-note-tags`. It did not switch the user's checkout away from `feature/export`. Every later command did `cd` into that worktree. The conversation's own cwd stayed in `a5` on `feature/export`. In the other runs where a new branch was needed (a1-a3, a8, b1), the AI ran `git switch -c` in place.

- Good: `rn/skills/on/SKILL.md:18-19` The stop for uncommitted changes is read by its reason, so an untracked Finder file does not block the session.
  - Evidence (report): "The AI did not stop. It went on and reported the file to the user."
- More: `rn/skills/on/SKILL.md:23-24` On a feature branch with its own commits, the AI read this sentence as a call for a separate worktree: the session lives in `../a5-note-tags` while the conversation stays on `feature/export`, where rn's hooks, which look for `.rn/` under the conversation's working directory (`rn/hooks/record.py`), find no session, and a cleared conversation started where the user is finds none either.
  - Evidence (report): "The conversation's own cwd stayed in `a5` on `feature/export`."

## prompt.md: When it met something the user or the people around them decide, what did the AI do?

Report: Languages: handed back to the user every time, as one question with a proposal. The goal's reason: handed back in every Opus run that reached step 5, as one open question with no proposed answer. Decided by the AI and reported, not asked: branch name, placing the work in a new worktree (a5), leaving the unpushed commit out (b1), treating `.DS_Store` as not the user's work (a7).

- Good: `rn/skills/on/SKILL.md:25-28` The languages, the user's to choose, come as one question already proposed from the repository and the user's settings, so a single yes settles them.
  - Evidence (work): "so a single yes settles both"
- Good: `rn/skills/on/SKILL.md:20-24` What the repository settles (branch, base, untracked files, an unpushed commit) is decided and reported rather than asked, so the user can still overrule it.
  - Evidence (report): "Decided by the AI and reported, not asked"

## prompt.md: When you gave it the same situation several times, where did the AI's actions differ from run to run?

Report: Same situation (clean `main`), a1, a2, a3 on Opus: branch name `note-tags` / `20261007-note-tags` / `20261007-note-tags`; push in turn 1 yes / no / yes; language question re-asked after "はい" yes / no / yes. Turn-2 surprise (a1, a3): after "はい", both said they had not sent the question yet and asked it again. a1: "前回は言語についての質問をお送りできていませんでした。改めて確認させてください。" Turn 1 of both runs had ended with that question as visible output. A second "はい" made both go on. Across all Opus runs, the PR body link to steering.md varied: Absolute `https://github.com/acme/notes-cli/blob/<branch>/…`: a7, and a2 after a `gh pr edit 3`. Relative `.rn/20261007-note-tags/steering.md`: a5, a6, a8, b1, w3. `../blob/<branch>/…`: w2. Same in every run: step order, the two decision lines, the single language question, and the single "why" question.

- Good: `rn/skills/on/SKILL.md:15-37` The parts the session's later commands rely on come out the same every time: step order, the decision lines, one language question, one why question.
  - Evidence (report): "Same in every run: step order, the two decision lines, the single language question"
- More: `rn/skills/on/SKILL.md:33-34` In most runs the pull request body links steering.md by a relative path, which on GitHub resolves against the pull request's own URL, so the reader of the draft pull request clicks a link that does not reach the record.
  - Evidence (report): "Relative `.rn/20261007-note-tags/steering.md`: a5, a6, a8, b1, w3."
- More: `rn/skills/on/SKILL.md:25-28` In two of three runs the user's "はい" to the language question was not taken; the AI said it had not sent the question and asked it again, so the user answers the same point twice.
  - Evidence (report): "前回は言語についての質問をお送りできていませんでした。改めて確認させてください。"

## prompt.md: When you took out one instruction and ran it again on the same situation, what changed in what the AI did?

Report: Removed sentence: "A second name for the same work leaves the user's worktree and its branch apart." (SKILL.md:23-24). Situation: a fresh worktree on `tags-wt` at `origin/main`. Runs: two with the sentence removed (w3, w4) and two with the work as is (w1, w2). Result: all four used `tags-wt` as the session branch and did not create another branch. I saw no difference between the two versions in this situation. I did not repeat the feature-branch situation (a5, where the AI made a separate worktree) with the sentence removed.

- More: `rn/skills/on/SKILL.md:23-24` The sentence changed nothing in the fresh-worktree case, and the only run where it may have acted (a5) is the one that split the session from the conversation; the AI reads an instruction whose effect on the purpose shows in no run.
  - Evidence (report): "I saw no difference between the two versions in this situation."

## prompt.md: When you gave the same situation to the AI without the prompt, or with the version in use now, what did it do differently?

Report: Without the prompt (the plugin not loaded): the AI implemented tagging in `src/notes.py`, did not commit, made no branch, no PR and no record, and asked the user nothing about languages or the reason. With the version in use now (installed 0.9.0, whose only difference is step 2: "Work on a new branch from the latest default branch…"), in the fresh-worktree situation (w5): The AI ran `git switch -c note-tags origin/main` inside the worktree. The session went on `note-tags`, and the user's `tags-wt` branch was left at `initial` with nothing on it. With the current work (w1, w2), the session used `tags-wt` itself.

- Good: `rn/skills/on/SKILL.md:20-23` Against 0.9.0, a fresh worktree's branch now carries the session instead of being left empty beside a second branch.
  - Evidence (report): "With the current work (w1, w2), the session used `tags-wt` itself."
- Good: `rn/skills/on/SKILL.md:9-13` Against no prompt, the user's first words are not built at once; the session starts with a record, a pull request and a question about why.
  - Evidence (report): "made no branch, no PR and no record, and asked the user nothing about languages or the reason"

## prompt.md: When you ran it on each model it will be run on, where did what the AI did differ?

Report: I do not know which models it will be run on. I ran the clean-`main` situation on Sonnet (m1) and Haiku (m2) as well as Opus. Sonnet: created branch `rn/20261007-add-note-tags`, asked the language question in one message, wrote steering.md, made the two commits with the decision lines, opened the PR with a relative link to steering.md, and asked one "why" question. Haiku: Created `.rn/20261007-add-tags-filter` while still on `main`, with no branch yet. Did not read conduct.md. Answered in English despite the user's Japanese setting. In turn 2 it wrote invented criteria and a task #3 into steering.md: "A1: Users can add and remove tags from notes / A2: Users can filter notes by one or more tags / A3: The tag system works smoothly with the existing note interface" and "Assumption: The project has an existing note list and storage system". Then asked five questions in one message. Some of them the repository answers: "1. **現在のノートシステム** — ノートはどのように保存・表示されていますか？… 5. **フィルタリング** — 複数タグでフィルタする場合、AND/ORはどちらが優先ですか？"

- Good: `rn/skills/on/SKILL.md:15-37` On Sonnet the session starts the same way as on Opus: one language question, steering.md, two decision lines, a draft pull request, one why question.
  - Evidence (report): "made the two commits with the decision lines, opened the PR with a relative link to steering.md"
- More: `rn/skills/on/SKILL.md:36-37` On Haiku the conductor never reads conduct.md, writes criteria the user never said into the record, and asks five questions at once, some of which the repository answers. Which models rn is run on is written nowhere in the repository, so whether this counts is open.
  - Evidence (report): "Did not read conduct.md."
