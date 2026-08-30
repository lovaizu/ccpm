# Reader trial — doc-A (current `aiya/docs/design.md`, 6,487 words), report 2 of 2

Verbatim report from a fresh-context subagent given only `doc-A.md` under a neutral filename and the
prompt in `trials.md` §The prompt. It could not read any other file and did not know a second
document existed.

> **Note on two reports.** The doc-A trial returned two complete reports (see `trials.md` §Anomaly).
> Both are recorded. This is report 2.

Read: chapters 1–4 straight through, then a look-up jump into §5.4 and (in the same window) §5.5–§5.7. Did not read §5.1–§5.3, §6, §7.

---

## 1. The decision

**QUALIFIED — and the question as posed cannot be answered YES, because the document itself withdraws it.**

§2 promises: "The two properties map to two mechanisms: bounded context → the **CCS** (§5.4); drift detection → the **two-layer traceability chain** (§3.1)." Then, same paragraph: "Each mechanism carries two supports alongside it." By §4.6 the CCS is one of *three* things carrying bounded context, and the chain one of *three* carrying drift detection. So neither mechanism discharges its property alone, by the document's own accounting. Judged on the full six, here is where each lands.

**Bounded context — qualified, and the qualification is load-bearing.**

What genuinely works: replacement semantics (a fresh CCS per wave, never appended) kills accumulation across waves, and one brief per wave kills the width term for the CCS specifically. Those two are real and the argument for them is clean.

What does not close:

- **The Verdict intake is linear in wave width and the document contradicts itself about it.** §4.2: "the Conductor's intake stays at one bounded state per wave, so parallel width and bounded context stop being in tension." §5.7's closed intake list: "the latest CCS, **bounded Verdicts**, approved phase documents, the current Plan, the run-state file…" Verdicts are one per Step per viewpoint (§4.1, §5.3), and the Conductor must read them because aggregation is its own act ("the AND over Verdicts," §4.3). Each Verdict is bounded in size; their *number* is not bounded, it is width × viewpoints. "Doubling a wave's width does not double what the Conductor reads" is false on the document's own terms. Nothing anywhere folds Verdicts into the CCS before the Conductor sees them.
- **The document concedes the property fails in the literal sense and hides the concession.** §4.5: "the Conductor's history still grows with the number of Turns; the design minimizes the coefficient … and the residue is cycled by `dn` → `/clear` → `up`." So the real working context is linear in Turns, and the remedy is a human typing three commands. That admission belongs in §4.6 where the discharge is claimed; instead it sits in the suspend/resume section where a reader checking the discharge will not find it.
- **The property survives only by redefinition.** §1 says "working state"; §3.2 and §5.4 quietly define working state *as* the CCS. Under that definition the property is nearly true by construction, and everything else — transcript, Verdicts — is out of frame.
- **The bound is soft and unmachined.** §3.2's table says the CCS is verified by "Mechanical compression rules (§5.4)." §5.4 delivers "a soft size cap's breach is a health signal, not a license to grow." That is not mechanical and nothing enforces it; §2 already told me no controller program exists. The table oversells its own chapter.

**Drift detection — one form discharged, one form asserted.**

Form 1 (work the purpose never asked for): discharged, and this is the strongest part of the design. Every Step carries a done-when and viewpoints, an independent Turn(verify) measures the product against version-pinned gate-approved yardsticks, and a fail is caught before the wave settles. The version-invalidation rule ("A new version invalidates what was measured against the old one") is the right mechanic. I took §5.3's "each Verdict pins the edition it measured" on faith without reading it.

Form 2 (completing the stale plan while ignoring discoveries): **not discharged — asserted.** The whole answer is "planned from zero out of the current position, never by amending the current Plan," and §4.6's claim that "a plan rebuilt from the current position cannot silently inherit the old one." That is exactly what it cannot guarantee. The same agent holds both plans; a lazily reproduced plan and a genuinely rebuilt one are the same artifact on disk. §2 promises every non-structural rule "leav[es] a trace when broken," and §5.6 lists traces for format breaks, consumes lies, unrecorded changes, and unapproved editions — **no trace for amend-vs-rebuild**. The document breaks its own enforcement principle at the one place form 2 is answered.

**What qualifies the YES, in one line each:** bounded context holds for the CCS but not for the Verdict stream or the transcript, and only under a narrowed definition of "working state"; drift detection holds for unasked-for work but rests on an unobservable rule for the stale plan.

## 2. Headings-only pass

**The headings carried the shape and lost the thesis.**

From headings alone I wrote down: *delegating large work to AI agents costs human babysitting; the fix is two roles held apart by two walls; a chain of yardsticks gives traceability; the machine runs as a loop of Steps→waves→gates with suspend/resume; then per-part rules, observability, trade-offs.* That much is right, and 3.1–3.3 and 4.1–4.5 read in a genuinely sensible order.

Two breaks:

- **The two properties are invisible in the headings.** "1. Problem — Big work turns into babysitting" does not name bounded context or drift, and no chapter-1 subheading exists. The properties first surface in the headings at "4.6 Bounded context and drift detection, discharged" — after the four chapters that are supposed to be establishing them.
- **The headings point at the wrong mechanisms.** "2. Core — Two roles, two walls, one bet" made me predict the two mechanisms were the two walls. They are not; they are the CCS and the chain, named in the last line of §2's body. A heading-level reader would leave with the wrong answer to the exact question I was asked.

## 3. Every stumble, in reading order

1. **"2. Core — Two roles, two walls, one bet"** (heading pass). Expected: the two walls are the two mechanisms. Got: the walls are a supporting structure; the mechanisms are named nowhere in any heading.
2. **"the working state of the directing agent (aiya's Conductor, §2) stays sub-linear in the number of parallel work streams — the waves of §4.2."** Expected a definition of "working state." Got two forward references in one sentence and no definition; it is pinned only in §3.2/§5.4. Held open for three chapters.
3. Same line: **"sub-linear in the number of parallel work streams — the waves"**. A wave is a *set* of streams. Is the variable the width of one wave, or the number of waves over a run? Held open. §4.6 answers "width"; §4.5 admits the count-of-Turns term separately. Two different claims wearing one word.
4. **"The two properties map to two mechanisms: bounded context → the CCS (§5.4); drift detection → the two-layer traceability chain (§3.1)."** The thesis is the last line of §2, after a twelve-term glossary. I jumped back to §1 to re-read the properties.
5. **"Each mechanism carries two supports alongside it; §4.6 states the full discharge."** Expected the supports named. Got a deferral 120 lines forward. This sentence silently changes the answer to the question I was sent to answer.
6. **The "Vocabulary, fixed here" block** — twelve bolded terms in a row mid-argument. I retained about half and came back for "elicit item" and "viewpoint" at §4.1.
7. **"`/aiya:ty` approve, `/aiya:gm` send back … mnemonics in the README."** Command syntax I have no use for, plus a pointer to a file I was told not to open.
8. **"beyond the attempt cap (three attempts per Step, §4.1)"** — the number three lands in a parenthesis a hundred lines before the section that defines it, with no reason given. "Why three?" never answered in 1–4; possibly §7.
9. **§3.2 table, CCS row: "Verified by (machine): Mechanical compression rules (§5.4)."** Expected a mechanism. §5.4 gives "a soft size cap's breach is a health signal." The table's word "mechanical" is not supported by the section it cites.
10. **"The run-state file, `state.yaml` (proposed)."** "(proposed)" appears exactly once in the document. Is the filename tentative, the schema, or the whole file? Guessed "the schema" and moved on.
11. **§3.3's backend paragraph** — "exactly two things degrade under local, both named, never hidden" plus a three-backend rundown, dropped into the middle of the structural argument. Read it fully before realizing it bore on nothing I was deciding.
12. **§4.1: "an elicit item (§2) dispatches none and skips this pipeline — verification, the attempt cap, and §6's counts apply only to items whose work a Turn performs."** Held open: an unverified Plan item is a hole in drift detection. Partly answered a chapter later at §4.4 ("elicit answers exempt"; "Until the human approves at G1, it is not the purpose"). Two passes to resolve.
13. **§4.1's closing prose block** — aggregation AND, re-aim gap union, investigation semantics, escalation, missing return, missing viewpoint, all in one paragraph. Re-read twice. The missing-viewpoint rule is load-bearing for drift detection and is filed as a "side path."
14. **"Turn(record) runs after brief so it can read the fresh CCS — commit messages are content-aware, not mechanical."** Expected the point about the serial write point (which the sentence before makes well). Got a sentence about commit-message quality.
15. **§4.2 "one bounded state per wave" vs §5.7 "the latest CCS, bounded Verdicts, …"** — flat contradiction, and I only found it by jumping out of chapters 1–4. This is what moved my decision from YES to QUALIFIED.
16. **"planned from zero out of the current position, never by amending the current Plan."** Expected the next line to say how an observer tells the two apart. Got "steering degenerates into ritual" — motivation, not a trace. Went looking in §5.6; it is not there either.
17. **§4.4: "Generation needs prerequisites — the run's own Purpose and Plan, plus the product's UX and Design documents."** UX and Design arrive as hard prerequisites having been mentioned once in §3.3 as an aside. Are they yardsticks? Verified against anything? Never said — and §3.2, whose table promises "Everything, listed once," omits both.
18. **§4.4's "Drafting the Purpose is divided" paragraph** — "the Conductor does not draft … transcribing the human's answers verbatim is not drafting." Read three times. The distinction is real but the paragraph argues for it instead of stating it.
19. **"each Verdict pins the edition it measured (§5.3), so the invalidated ones are found mechanically"** — took on faith; §5.3 unread. Flagging it as an unverified dependency of my drift verdict.
20. **§4.5: "the Conductor's history still grows with the number of Turns … the residue is cycled by `dn` → `/clear` → `up`."** Expected suspend/resume mechanics. Got the document's biggest concession about property 1, in the section where nobody auditing the discharge will look.
21. **§4.6: "Bounded context is carried by three things"** — after §2's "two supports." Consistent once I did the arithmetic; I had to stop and do it.
22. **§5.4: "The CCS is bounded and sub-linear, not byte-constant."** Sub-linear in *what*? §1 said parallel streams; this reads as sub-linear in work done. The variable is never named at the one place it matters most.
23. **§5.4: "The nine-component YAML schema is adopted from Bousetouane … (2026)."** The nine components are listed nowhere. To judge whether the CCS is bounded I need to know what it holds; I was pointed at an arXiv paper and "the Turn definition," neither readable. The mechanism's own contents are absent from the design document.
24. **§5.7: "This wall cannot be made physical: the Conductor's working state is files, so it cannot lose the ability to read."** Expected the no-reading wall — one of three legs of bounded context — to be structural, as §2's framing implies ("This wall caps what *kind* of thing can enter its context"). Got observable-only, admitted here and not in §2.

## 4. Content I did not need

- **§3.3 backends and degradation matrix, §5.5's three record adapters** — operator and implementer material. Nothing here bears on either property.
- **§3.3's directory tree** — serves someone debugging a live run.
- **§3.4 (six skills, five entry skills, packaging)** — serves a plugin implementer.
- **§2's command words and mnemonics** — serves an end user reading a README.
- **§4.2's commit-message aside, §4.4's console-summary / progress-board / dispatch-round mechanics, `gm` vs bare `gm`** — serves a user operating a run.
- **§5.6's three-lines-per-item format** — serves whoever writes a Plan.
- **The `state.yaml` YAML sample** — serves an implementer.

Roughly a third of what I read served an implementer or operator, not an evaluator. The two chapters I actually needed to *judge* the design were §1 and §4.6, and §4.6's supporting facts are scattered into §5.

## 5. Effort score

**4 of 5.** Not because the writing is bad — sentence for sentence it is dense and well made — but because the discharge argument is dismembered across the document and one of its two halves contradicts itself between §4.2 and §5.7. I could not reach a verdict without leaving the assigned chapters, and the fact that changed my verdict was in §5.7.

**The one change:** put the whole discharge in one place at the front — the two properties, all six carriers, *and the residual linear terms* (Verdict count, transcript growth, the unobservability of re-plan-from-zero) — and make §4.2's "intake stays at one bounded state per wave" agree with §5.7's actual intake list. Right now the honest accounting exists in the document but is distributed so that no single reading position sees it whole; §4.5 confesses what §4.2 and §4.6 claim is solved.

## 6. The path I actually took

1. Headings only, top to bottom; wrote the predicted argument (wrong on the mechanisms).
2. §1 → §2 → §3.1 → §3.2 → §3.3 → §3.4, straight.
3. Back to §1 from §2's mechanism-mapping line, to re-read the two properties.
4. §4.1 (final paragraph twice) → §4.2 → §4.3 → §4.4 (Purpose-drafting paragraph three times) → §4.5 → §4.6.
5. Back to §1 after §4.5, to check "working state" against the transcript-growth concession.
6. Back to §2's mechanism line after §4.6, to confirm the two-vs-three mismatch.
7. **Jumped out of chapters 1–4** to §5.4, because §4.6 defers the CCS's actual bound there and chapters 1–4 never state it. Read §5.5, §5.6, §5.7 in the same pass; §5.7's intake list is what decided the bounded-context half.
8. Back to §4.2 to set its "one bounded state per wave" against §5.7's list.
9. Stopped. §5.1–§5.3, §6, §7 unread — so my drift verdict rests on §5.3's edition-pinning being what §4.4 says it is, and §7 may price some of the gaps above as accepted costs.
