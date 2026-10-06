# Check: rn/docs/design.md

Target: rn/docs/design.md
Receiver and purpose: A builder or maintainer of the rn plugin; they build rn from it, and weigh any change by what it would cost the user.
Aim: The builder learns which features give each of rn's acceptance criteria (A1-A4 and M1-M7 as the document states them) and why each is built as it is, so they can build rn and tell what a change would cost the user. They know who does what: the conductor alone decides and uses git; a generator makes a task's result; a first user, knowing nothing of how a thing was made, uses it and reports without judging; writ writes the README, design and verification documents. They know when a first user is used, how a report is settled into Good and More, what a proposal at a sign-off holds and why, how the record lets any conversation go on, what the hooks check and why, and how rn is installed. Each decision comes with its reason, so the builder does not reopen it. This check is of the document as it is today, to find what serves the builder and must be kept when it is rewritten.

The first user read rn/docs/design.md once from the top, with rn/README.md, rn/docs/verification.md and parts of rn/hooks/. The change it picked: "Let the conductor start the first user in the background, so the user can keep talking while a check runs." The benefit it tried to check: A4.

## doc.md: Once you finished reading, what did you take it you should decide and do?

Report: What I took from it:
- Build rn as seven features (table, design.md:38-46), each tied to a criterion ID: A1–A4 and M1–M7 (design.md:15-34).
- Keep seven policies (design.md:65-107), with the first one above the others: "Attractive quality is the goal" (design.md:67).
- Build 14 hook checks with defined run times (design.md:536-576), in Python 3.9 with the standard library only (design.md:578).
- Lay the parts out as listed in design.md:593-597.

I took it that I weigh a change by naming the criterion ID it touches and asking whether the user loses that benefit. The opening says this: "so a builder knows what a change would cost the user" (design.md:3-4).

- Good: `rn/docs/design.md:3-4` The builder takes the document's job exactly as the aim sets it: weigh a change by the criterion it touches and what the user would lose.
  - Evidence (work): "must always hold, so a builder knows what a change would cost the user."
- Good: `rn/docs/design.md:36-46` The criterion IDs and the feature table give the builder the whole shape of rn (features, the criteria each gives, where it works in the README) before any detail.
  - Evidence (report): "Build rn as seven features (table, design.md:38-46), each tied to a criterion ID"

## doc.md: Which parts did you use to decide or act, which did you skip without using, and where did you find yourself reading again what you had already read?

Report: **What I used:** the feature table (design.md:38-46); the policies (design.md:65-107); "the conductor waits for it, so its turn ends only when it stops for the user or asks them a question" (design.md:293-294); check 12 (design.md:565-567); the hook timing paragraph (design.md:536-542); the pause/resume parts (design.md:458-462, 494-502); the front matter of steering.md (design.md:525-530).

**What I skipped:** the Kano citation (design.md:8-10); the grilling provenance line (design.md:119-120) and the wayfinder line (design.md:211-212); the upstream-maintenance line (design.md:222-223); the Nygard/MADR references (design.md:520-522); the Anthropic harness citation (design.md:284-285).

**Where I read the same point again:** the rule that must-be gaps are fixed only on the golden path and let go elsewhere comes up at design.md:70-74, 183-187, 329-332, 370-372, 390-392 and 425-427. I skimmed it from the third occurrence on. The rule that a fix to an attractive More goes to "a fresh first user for that viewpoint alone" comes up at design.md:376-377 and 399-401, and again in the flowchart (design.md:349). I read it more than once to see whether the two places differ: 376 is about an unanswered viewpoint, 399 is about a fix.

- Good: `rn/docs/design.md:290-294` The parts the builder used to weigh the change (why the conductor waits, the policies, the pause and resume parts) carried the decision.
  - Evidence (work): "first user for each use, so each one's attention holds only its own work. Each returns to the"
- More: `rn/docs/design.md:70-74` The rule that must-be gaps are fixed only on the golden path is said six times; the builder skims it from the third time on, so any new point placed among the repeats is skimmed too.
  - Evidence (report): "I skimmed it from the third occurrence on."
- More: `rn/docs/design.md:376-377` Two sentences about a fresh first user "for that viewpoint alone" sit apart and read alike; the builder rereads them to find they cover different cases (an unanswered viewpoint, and a fix).
  - Evidence (report): "I read it more than once to see whether the two places differ"
- More: `rn/docs/design.md:119-120` Source and maintenance lines (Kano citation, grilling and wayfinder origins, the upstream-maintenance line, Nygard/MADR, the Anthropic citation) were read past without use in building or weighing a change.
  - Evidence (report): "the grilling provenance line (design.md:119-120) and the wayfinder line (design.md:211-212); the upstream-maintenance line (design.md:222-223)"

## doc.md: In trying to decide or act, what was not in the document, so that you could only guess or ask someone?

Report: - **README benefit 4 has no counterpart.** The README says: "The other Claude Code sessions you run in the same repository keep working beside it: `rn`'s checks act only in the conversation that runs it and on the agents it starts" (rn/README.md:10-12). I found no criterion for this among A1–A4/M1–M7, no feature row, and no section. Grepping design.md for "other session" / "another session" found nothing. The implementation distinguishes callers by `agent_type`, `session_id`, and "The session directory on this branch" (rn/hooks/record.py:43; rn/hooks/pretooluse.py:20,32; rn/hooks/checks/typed_command.py:12-13). I could only guess that this is how the benefit is delivered.
- **Which branch a session uses.** The README says: "When you start on a branch of your own that has no commits yet and is level with the latest default branch, `rn` works on that branch; otherwise it makes its own" (rn/README.md:36-37). The design says only: "A session works on its own branch with a draft pull request ... It starts from the latest default branch" (design.md:466-468). I could not tell from the design whether reusing the user's branch is a design decision.
- **Approving in plain words.** The README says: "`/rn:ty` approves, and so does saying it in your own words, such as "approved"; both are recorded the same" (rn/README.md:118). Check 7 says: "A sign-off is passed ... only after the user typed `/rn:ty`" (design.md:555). I could not tell which of the two to build.
- **Why a background agent with a later notification was not chosen.** The only reason I found is "an agent left running reports to a turn that has ended" (design.md:566-567).
- **"Golden path" is never defined.** It is first used at design.md:72.

- More: `rn/README.md:10-12` The README's fourth benefit (other sessions in the same repository keep working) has no criterion, feature or section in the design; the builder can only guess from the hooks how it is given, and cannot tell what a change would cost it.
  - Evidence (report): "I found no criterion for this among A1–A4/M1–M7, no feature row, and no section."
- More: `rn/docs/design.md:466-468` The design says a session works on its own branch, while the README says rn may work on the user's fresh branch; the builder cannot tell whether reusing the user's branch is a decision.
  - Evidence (report): "I could not tell from the design whether reusing the user's branch is a design decision."
- More: `rn/docs/design.md:555` Check 7 lets a sign-off pass only after `/rn:ty`, while the README says plain words such as "approved" approve too; the builder cannot tell which to build.
  - Evidence (report): "I could not tell which of the two to build."
- More: `rn/docs/design.md:72` "Golden path", on which several decisions rest, is never defined; the builder has to guess its reach.
  - Evidence (report): "is never defined.** It is first used at design.md:72."

## doc.md: Reading through, where did you stop, go back or look ahead, and what did you not understand there?

Report: - **design.md:28.** `steering.md` and `open/` are used here in M4. I looked ahead and found them explained at design.md:482-485 and 525-530.
- **design.md:72.** "on the golden path": I did not find a definition anywhere.
- **design.md:148.** "`Assumption`", in code font, reads like a field name. Where it lives became clear only at design.md:525 ("checked facts kept apart from assumptions").
- **design.md:258.** `/rn:up` is first used here. I had it from the README, not from this document.
- **design.md:534.** "checks 12 to 14 also give A2, and checks 6 and 14 A3": I read this before the checks were listed, then went back to it after design.md:544-576.
- **design.md:538.** "The checks run right after a file is written, before the first user is called, and when the conductor ends its turn." Only checks 4–14 are then assigned run times. I worked out by elimination that 1–3 are the file-written ones.
- **design.md:555 vs rn/README.md:118.** I stopped here over the /rn:ty-only versus plain-words difference described above.

- More: `rn/docs/design.md:28` `steering.md` and `open/` are used in M4 long before they are explained, so the builder looks ahead to line 482 and 525.
  - Evidence (report): "I looked ahead and found them explained at design.md:482-485 and 525-530."
- More: `rn/docs/design.md:148` "`Assumption`" in code font reads like a field name, and where it lives shows only at line 525.
  - Evidence (report): "in code font, reads like a field name."
- More: `rn/docs/design.md:534` Which checks give A2 and A3 is said before the checks are listed, so the builder comes back to it.
  - Evidence (report): "I read this before the checks were listed, then went back to it after design.md:544-576."
- More: `rn/docs/design.md:538-542` When checks 1 to 3 run is not said; the builder works it out by elimination.
  - Evidence (report): "I worked out by elimination that 1–3 are the file-written ones."

## doc.md: When you looked for a part to read again by its heading, under which heading did you find it, and under which did you not?

Report: - **The background-agent rule:** found under "Hooks check rn's rules as it goes" (design.md:532, check 12). The reason the conductor waits was not under "Who does what, and what holds throughout" (design.md:48). I found it under "The first user uses the work before the user does" (design.md:290-294).
- **Resume behaviour:** found under "Everything decided is pushed, so any conversation goes on" (design.md:437) and "Where rn stops" (design.md:492).
- **Isolation from other Claude Code sessions:** no heading led to it. "Keeping the first user apart" (design.md:296) looked like it might, but it is about isolating the first user from the maker.
- **The form of steering.md fields:** "A session has one directory under .rn/" (design.md:504) gave the list. The form itself is pointed to rn/references/ (design.md:594).

- Good: `rn/docs/design.md:437` Headings named after what the user gets ("so any conversation goes on", "Where rn stops") led the builder straight to resume behaviour.
  - Evidence (work): "## Everything decided is pushed, so any conversation goes on"
- More: `rn/docs/design.md:48` The conductor's waiting for every agent, a rule that holds throughout, is not under "Who does what, and what holds throughout", where the builder looked for it.
  - Evidence (report): "The reason the conductor waits was not under"
- More: `rn/docs/design.md:296` No heading leads to how rn leaves other sessions alone; "Keeping the first user apart" looks like it might and is about something else.
  - Evidence (report): "**Isolation from other Claude Code sessions:** no heading led to it."

## doc.md: Where, while reading, did you have to piece together in your head who does what, what passes, and in what order?

Report: - **Hook run times (design.md:536-542).** I built a table in my head of when each of checks 1–14 runs.
- **The More-decision loop.** The flowchart at design.md:342-365 gave the order. I combined it with the prose to place "A viewpoint the report leaves unanswered goes to a fresh first user" (design.md:376-377), which is not in the chart, and "The final check looks again at every Good a fix touched" (design.md:402), which is also not in the chart.
- **The flow of a feedback round.** I joined three passages to get it: design.md:227-237 (feedback goes into open/ and back to the plan or design), design.md:257-258 (stop) and design.md:494-499 (stop commit).

- Good: `rn/docs/design.md:342-365` The flowchart gives the builder the order of making, using, deciding and fixing at a glance.
  - Evidence (report): "The flowchart at design.md:342-365 gave the order."
- More: `rn/docs/design.md:536-542` The builder builds in their head a table of when each of the 14 checks runs.
  - Evidence (report): "I built a table in my head of when each of checks 1–14 runs."
- More: `rn/docs/design.md:376-377` Two steps of the More loop (an unanswered viewpoint, and the final look at touched Goods) are in prose only, and the builder fits them into the chart.
  - Evidence (report): "which is also not in the chart."
- More: `rn/docs/design.md:227-237` The flow of a feedback round is spread over three sections, and the builder joins them.
  - Evidence (report): "I joined three passages to get it"

## doc.md: How certain did you take each statement you relied on to decide or act?

Report: - **Facts stated flatly, with no sign of having been checked:** "Python 3.9 with the standard library only, which comes with git on a Mac" (design.md:578); "A hook sees a shell command's text, not every file it touches" (design.md:309-310); "an agent left running reports to a turn that has ended" (design.md:566-567). I took all three as facts.
- **Stated as a cited finding:** "an agent asked to evaluate its own work tends to praise it" (design.md:286). I took it as a finding from the cited source.
- **Stated as accepted decisions:** "this is accepted" (design.md:311) and "Two languages in one script ... are not told apart" (design.md:575-576). I took both as known limits.
- **Elsewhere:** I took the policies and the "must always hold" items as decisions. The document marks nothing as an assumption or proposal, so I read everything as current decisions.

- Good: `rn/docs/design.md:309-312` Known limits are stated as accepted, with the reason, so the builder takes them as decided and does not reopen them.
  - Evidence (work): "touches, so a read or write through the shell is not stopped; this is accepted, since the first user"
- More: `rn/docs/design.md:566-567` Facts about Claude Code that decisions rest on, such as what happens to an agent left running, are stated flatly with no sign of whether or how far they were checked; the builder acts on them as fact.
  - Evidence (report): "I took all three as facts."

## design.md: Having picked one likely change, how did you decide, from what the user would lose, whether it fits the design?

Report: I looked for every place that touches it: check 12 (design.md:565-567); design.md:293-294 "the conductor waits for it, so its turn ends only when it stops for the user or asks them a question"; feature row "It calls the user only for decisions that are theirs | A2" (design.md:41); policy "Every agent ... returns only a short result and where the file is" (design.md:97-101).

The loss I named was A2: the user would be left waiting on work no one carries on. My decision: the change does not fit. I could not find in the design whether the loss would remain if Claude Code notified the conductor when the agent finished, so the decision rests only on the reason given in check 12.

- Good: `rn/docs/design.md:565-567` The check names the criterion it gives and the user's loss, so the builder weighs the change by what the user loses (A2) and reaches a decision.
  - Evidence (work): "the background, since an agent left running reports to a turn that has ended, and the user is"
- More: `rn/docs/design.md:565-567` The loss is tied to one mechanism (a report arriving after the turn ended); the builder cannot tell whether it remains if Claude Code tells the conductor when the agent ends, so the decision rests on an unexamined premise.
  - Evidence (report): "I could not find in the design whether the loss would remain if Claude Code notified the conductor when the agent finished"

## design.md: When you were unsure whether a change fits the design, which principle did you recall and use?

Report: - **"Only the conductor decides what happens next" (design.md:76).** I used it to reason that a background first user's report would arrive with no conductor turn to decide on it.
- **Check 12's own reason (design.md:566-567).** It settled the question, but it is a hook check, not one of the seven policies.
- **"Every agent the conductor calls leaves its whole result in a file" (design.md:97).** I recalled it and asked whether results in files would make background running safe. The design does not answer this.

- Good: `rn/docs/design.md:76` A short policy came to mind and gave the builder a way to reason about a change no rule names.
  - Evidence (work): "- Only the conductor decides what happens next."
- More: `rn/docs/design.md:97` The policy that results go in a file raises whether background running would then be safe, and the design does not answer it, so the builder holds two principles they cannot weigh against each other.
  - Evidence (report): "I recalled it and asked whether results in files would make background running safe. The design does not answer this."

## design.md: For each principle you used, what did you take it would break if it were not kept?

Report: - **"Only the conductor decides what happens next."** Its reason: "a fix keeps what already serves the goal. Fixes decided by the first user's words would rebuild what works" (design.md:78-79). I took the breakage to be work that already serves the goal getting rebuilt. No criterion ID is named; I connected it to A1 myself.
- **Check 12.** Its breakage is named: A2, the user left waiting (design.md:567).
- **"Results in a file."** Its reason: "crowds the conductor's context and is lost when the conversation is summarized" (design.md:100-101). I took this as tied to A4 (going on without explaining again), but no ID is given.

None of the seven policies (design.md:67-107) names a criterion ID.

- Good: `rn/docs/design.md:78-79` Each policy carries what it protects, so the builder knows what breaks if it is not kept.
  - Evidence (work): "already serves the goal. Fixes decided by the first user's words would rebuild what works."
- More: `rn/docs/design.md:65-107` No policy names the criterion it protects; the builder ties each to A1 or A4 by their own reading, so two builders may weigh the same policy differently.
  - Evidence (report): "None of the seven policies (design.md:67-107) names a criterion ID."

## design.md: For each of the README's benefits, through which feature did you take it the user gets it?

Report: README benefits (rn/README.md:6-12):
1. **"You get what you really want, without writing a careful prompt first"** comes through A1, via "It works out the goal and the design with the user" (design.md:40, 109-237) and "The first user uses the work before the user does" (design.md:42).
2. **"Your time goes only to the decisions that are yours ... you don't babysit ... you don't re-read all of it to approve it"** comes through A2 and A3. The features are "It calls the user only for decisions that are theirs" (design.md:41, 239-263) and "A sign-off comes with a proposal and its grounds" (design.md:43, 410-435).
3. **"Work that takes days goes on the next day"** comes through A4, via "Everything decided is pushed, so any conversation goes on" (design.md:44, 437-530).
4. **"The other Claude Code sessions you run in the same repository keep working beside it"** has no feature, criterion or section in the design that I found.

The feature row "Hooks check rn's rules as it goes" (design.md:45) is named after a mechanism. I worked out what it gives only from the ID list at design.md:534.

The "Works at README step" column numbers (1–6, Install) matched the README's headings "### 1." through "### 6." and "## Install".

- Good: `rn/docs/design.md:38-46` The table maps three of the README's four benefits to features and to the README steps where they work, and the step numbers match the README.
  - Evidence (report): "column numbers (1–6, Install) matched the README's headings"
- More: `rn/README.md:10-12` The fourth benefit reaches the user through no feature in the design.
  - Evidence (report): "has no feature, criterion or section in the design that I found."
- More: `rn/docs/design.md:45` "Hooks check rn's rules as it goes" is named after its mechanism; what it gives shows only from the ID list at line 534.
  - Evidence (report): "is named after a mechanism. I worked out what it gives only from the ID list at design.md:534."

## design.md: After the change you picked, what did you take it must always hold?

Report: The conductor's turn ends only at a stop for the user, or with a question waiting: "its turn ends only when it stops for the user or asks them a question" (design.md:293-294), and check 13 says "ends its turn only at a stop or with a question waiting in `open/`" (design.md:568). Also, every agent the conductor calls returns to the conductor, never to the user (design.md:292-293). I read both as conditions that hold at every turn end, not as steps.

- Good: `rn/docs/design.md:292-294` What holds after every turn is written as a condition, so the builder knows what must keep holding whatever is changed.
  - Evidence (report): "I read both as conditions that hold at every turn end, not as steps."

## design.md: In trying to check one benefit, what did you take it must happen for the check to pass?

Report: For A4 the design gives only the general form of a scene: "starts from the state just before ... and ends at the first result that shows whether they got it" (design.md:180-182). The pass bar is in the verification document, not the design.

The bar I used: "Passes when it goes on with that task, handing the written test to its generator rather than writing it again or asking whose it is, and speaks Japanese" (rn/docs/verification.md:98-99). The second scene: "Passes when it goes on from that session's goal and what was done, with `steering.md` in the current form and what the old design approved in a `notes` item, and asks nothing the old record holds" (rn/docs/verification.md:104-106).

I did not run the trials; dev/rn/trials/ is named in verification.md:18.

- Good: `rn/docs/design.md:189-198` The design says the verification document holds each criterion's scenes with "Passes when", and the builder found a pass bar for A4 written as what happens to the user.
  - Evidence (report): "Passes when it goes on with that task, handing the written test to its generator rather than writing it again or asking whose it is, and speaks Japanese"

## design.md: In what situation did you take it that check is run?

Report: - **First scene:** "The coupon session paused in its first build task, its generator's test written and the code not yet changed (fixture `coupon-paused`): `/rn:up`" (rn/docs/verification.md:95-96). This is a pause in the middle of a task, followed by a fresh conversation.
- **Second scene:** a session paused under rn 0.8.0 (rn/docs/verification.md:101-102).

The design's own statement of the situation is "A pause leaves what is unsettled as it is, with a note on where the task stands and its generator's edits, even those it had not returned" (design.md:497-498).

- Good: `rn/docs/design.md:497-498` The situation is a pause in the middle of a task with a fresh conversation, where the user would plainly struggle without A4, so a pass is real proof.
  - Evidence (work): "A pause leaves what is unsettled as it is, with a note on where the task stands and its generator's"

## design.md: Where did you take it the checking effort goes?

Report: To attractive criteria first, through scenes on the golden path. The design says "Its checks are the fewest that confirm it" (design.md:67-68) and "Each attractive criterion gets the fewest scenes, and each scene the fewest inputs" (design.md:177-178). Must-be quality goes to machine checks and hooks: "What a machine can judge is checked by machine every time" (design.md:186-187), and "Edge cases and other flows are not covered in advance" (design.md:183-184).

- Good: `rn/docs/design.md:176-187` The builder knows the effort goes to attractive criteria on the golden path, and must-be quality to the machine.
  - Evidence (work): "comparing what happened with what was aimed for. Each attractive criterion gets the fewest scenes,"

## design.md: Where you were tempted to replace the current way with another option, why did you take it the current way was chosen?

Report: - **Background agents.** The reason given is only "an agent left running reports to a turn that has ended, and the user is left waiting" (design.md:566-567). No alternative, such as being notified on completion, is named as considered.
- **Re-checking the whole after fixes.** I was tempted to use the whole work again after fixes. The reason it is not: "each fresh use raises new points that are not essential" (design.md:402-403).
- **Holding the rules in agent definitions instead of hooks.** "since a definition holds however an agent is called" (design.md:299-300), and hooks cover "What a definition cannot hold, since the first user and the generator need the shell" (design.md:307).
- **Shell commands that hooks cannot see.** That reads and writes through the shell are not stopped is "accepted, since the first user is given no path to the maker's account" (design.md:309-312).

- Good: `rn/docs/design.md:402-403` Decisions a builder would reach to undo carry the reason (not using the whole again, definitions before hooks, accepting what hooks cannot see), so they are not reopened.
  - Evidence (work): "again, since each fresh use raises new points that are not essential."
- More: `rn/docs/design.md:565-567` The option a builder reaches for first, running an agent in the background and being told when it ends, is not named, so its cost against the current way is unknown.
  - Evidence (report): "No alternative, such as being notified on completion, is named as considered."

## design.md: Supposing the change you picked were made, which sentences would have to be rewritten though the intent stays the same?

Report: - Check 12 (design.md:565-567).
- design.md:293-294 ("the conductor waits for it").
- The machine-checks row "Hook checks 12–14: the conductor starts no agent in the background" (rn/docs/verification.md:117).
- Any renumbering of the hook checks would also force rewrites of design.md:534, 538-542 and 3, and of the verification rows at rn/docs/verification.md:112-117, since they refer to checks by number.

Other sentences that name settings, files or layout:
- "Python 3.9" (design.md:578).
- `rn/agents/` (design.md:299).
- `rn/references/essentials/` (design.md:317).
- `dev/rn/tests/` (design.md:597).
- The whole "The parts" section (design.md:591-597).
- The open/ name pattern `{NN}-{kind}-{about}.md` (design.md:545).

- More: `rn/docs/design.md:534-542` The hooks are referred to by number, so splitting or merging one check forces rewrites of the run times, the criteria they give, and the verification rows, though the intent stays the same.
  - Evidence (report): "Any renumbering of the hook checks would also force rewrites"
- More: `rn/docs/design.md:591-597` Directory paths and the parts list go stale with a rebuild of how the code is split.
  - Evidence (report): "section (design.md:591-597)."

## design.md: In trying to change the form of something left in the user's environment for later versions or people to read, which fields did you take it could be changed without breaking those who read it?

Report: I looked at what stays in the user's repository: the `.rn/{yyyymmdd}-{slug}/` layout ("`/rn:up` finds the session by this layout", design.md:522-523); the open/ file names `{NN}-{kind}-{about}.md` with kinds `report`, `feedback`, `notes` (design.md:545); the decision line `● … ── … → …` (design.md:549); steering.md front matter: "the version of `rn`, the pull request, whether the session is finished, the two languages, and where the three documents are" (design.md:528-530).

The design lists these fields but not their keys or formats, and not which reader needs each one. The form is pointed elsewhere: "`rn/references/`: ... the form of `steering.md`" (design.md:594). I could not tell from the design alone which fields can change without breaking a reader.

The one rule I found for later versions: "A session started under an older `rn` has its goal worked out again from the old record and stops at a new Plan sign-off" (design.md:459-462). From that I took it that a form change does not break old sessions, but it costs the user a new Plan sign-off. The `rn` version field is what tells an older record apart; that is my inference from design.md:528.

- Good: `rn/docs/design.md:459-462` What an older record costs the user is decided (a new Plan sign-off), so the builder knows the price of a form change.
  - Evidence (work): "last decision line, in the conversation language `steering.md` records. A session started under an"
- More: `rn/docs/design.md:525-530` The record left in the user's repository (steering.md front matter, open/ names, the decision line) is listed without its form or which reader needs each field, and the form lives in the implementation; the builder cannot tell which field can change without breaking a reader.
  - Evidence (report): "I could not tell from the design alone which fields can change without breaking a reader."
