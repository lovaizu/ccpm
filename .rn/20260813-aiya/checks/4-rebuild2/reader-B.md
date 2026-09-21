# Reader trial — doc-B-2 (the writ round-2 blank-page rebuild, 9,276 words)

Verbatim report from a fresh-context subagent given only `doc-B.md` under a neutral filename and the
prompt in `trials.md` §The prompt. It could not read any other file and did not know a second
document existed.

Read: prompt → headings of doc-B.md → chapters 1–4 → §5.4 and §5.6 (out of order, deliberately; explained in item 6).

---

# 1. The decision

**QUALIFIED — leaning NO on the question as asked.**

The document asks me to judge whether **CCS** discharges **bounded context** and the **two-layer chain** discharges **drift detection**. By the document's own accounting, they do not:

- §2 retracts the claim in its own heading one sentence after making it: "Neither carries its property alone — two further legs stand under each."
- §4.6 states the finding outright: "**none of the six legs is enforced**." Five of six depend on one party (the Conductor) following prose that nothing checks; the sixth (no nesting) is structural for 2 of 6 shipped definitions and a default for the other 4.

What actually survives scrutiny is narrower than "discharge":

**What I credit.** The *shape* argument for bounded context is real and is the best engineering in the document. Three couplings are cut at the structural level: width→input (N Steps collapse into one brief), length→input (fresh file per wave, never appended, only the newest read), and size→input (paths, never inlined content). Underneath sits one genuinely structural fact — a subagent starts on an empty context and only its return travels back — so what a Turn read cannot leak upward. That is a design that *can* be bounded. Likewise the chain's contribution is real: it converts "drift" from a thing someone must sense into a named object — "a Step the Plan cannot derive from the document above it" — with a fixed viewpoint that tests it and a Verdict on disk. Both properties become **checkable**. The document says exactly this and I agree with it.

**What qualifies it — four specifics.**

1. **The size claim contradicts itself.** §4.2 says a 2,000-byte ceiling "governs the file however wide the wave was — it fails nothing," and then says the CCS "does not shrink to a constant… What it does is grow far slower than the width." A fixed ceiling that holds is a constant bound; a ceiling that "fails nothing" is not a bound at all. The document cannot have both, and the property in §1 ("grows slower than their number") is never given a threshold. So there is no stated, testable size claim to judge — only a diagnostic hint. Bounded context is not discharged; it is *instrumented*.
2. **The property is discharged partly by redefining its scope.** §1 carves the transcript out ("Its conversation transcript is a separate thing"), and §4.5 confirms the transcript "still lengthens with every Turn dispatched," reset only by a person typing `dn` → `/clear` → `up`. The thing that actually grows linearly with the number of streams is handed to the human and relabelled "housekeeping."
3. **The compliance actor is the constrained party.** Both walls, the CCS rules, and replanning-from-nothing are obligations on the Conductor, checked by nobody. §4.6 admits the worst case plainly: "a Conductor that lightly edits the standing plan while calling it a rebuild leaves no trace that says so." Drift's third leg — the one covering the second failure §1 named (the stale plan) — has **no detector whatsoever**. Of §1's two named drift forms, one is caught mechanically and one is not caught at all.
4. **One CCS rule that carries truthfulness has no trail.** §5.4: "nothing distinguishes brief paraphrasing the Report from brief reading the product." "The artifact outranks the account" is the rule that stops the state from drifting off the artifacts, and it is unevidenced.

**Verdict in one line:** the two mechanisms give both properties an object you can measure and an object you can inspect, plus a genuinely structural floor (empty context, return-only channel, absent spawn tool). They do not discharge the properties — the document says so, and it is right to.

---

# 2. Headings-only pass

**Partly. The headings carry the architecture and lose the conclusion.**

From headings alone I reconstructed: two failures → two required properties; a director/worker split with prohibitions; a chain of frozen yardsticks over a mobile plan; a step→wave→gate loop; the CCS and the chain named as the carriers. That is roughly the argument, and headings like "3.1 The chain — frozen yardsticks over a plan that keeps moving" and "4.2 One wave — many Steps, one CCS" do real work — the second one telegraphs the entire bounded-context mechanism.

**Three breaks:**

- **The finding is absent from every heading.** The document's actual conclusion is "none of the six legs is enforced; both properties are checkable, not kept." No heading says this. §4.6's "six legs, and what each is worth" is a promise to price something, not a price. Reading headings only, I predicted a document arguing the mechanisms *work*. The body argues they are *not enforced*. That is an inversion, not a nuance.
- **"Nothing enforces this — two classes of rule instead"** was the only heading pointing at the truth, and I read it as a subordinate implementation note (2 levels deep, inside chapter 2), not as the governing fact about the whole design.
- **Two headings actively mislead.** "The words this design fixes, and **two rules it never breaks**" — the body of that section contains no such rules, and the design does not have two unbreakable rules; the very next section says so. And "**The CCS and the chain carry the two properties**" is contradicted by its own second sentence.

---

# 3. Every stumble, in reading order

1. **"This file holds two documents… neither borrows the other's reader."** (intro) — I expected the read-through part to be self-contained. It is not: Part 1 defers to §5.4, §5.6, §5.7, §5.1, §5.3, §5.5 continuously. The head note's promise is false, and I had to decide on every deferral whether the argument was still complete without it.
2. **"grows slower than their number"** (§1) — expected a stated bound (linear? log? constant?). Got a comparative with no threshold. Held the question open for the whole document; §4.2 refers back to "the sub-linear claim §1 made," but §1 never says "sub-linear." Never resolved into anything measurable.
3. **"brief, which writes the CCS (the Compressed Cognitive State, what one wave hands to the next — §4.2)"** (§2 glossary) — the lead mechanism for property #1 is introduced inside a parenthesis, in a sub-clause of a bullet about role *families*. Re-read to confirm I had found the actual definition and not a passing mention.
4. **"`/aiya:ty` for yes, `/aiya:gm` to send it back… `on` starts one, `dn` sets it down"** (§2) — two commands get the slash-namespace form, three get bare words in the same bullet. Guessed the bare ones are `/aiya:on` etc. Never confirmed.
5. **"two rules it never breaks"** (§2 heading) — read the whole section looking for them; they are not in it. Jumped forward, found "Two walls" two sections later, then found that section says one wall is a **default** and the other is structural for only 2 of 6 definitions. So the heading's "never breaks" is wrong on its own terms. Jumped back to re-read the heading twice.
6. **"the two that also ship without a shell — brief and the local record adapter"** (§2) — a count of six agent definitions is used before §3.4 establishes that there are six. Had to hold "six of what?" open for a chapter.
7. **"None of the frame is new… aiya's own contribution is what keeps the work honest"** (§2) — expected argument, got positioning. Stopped to decide whether it bore on my decision. It does not.
8. **"Neither carries its property alone — two further legs stand under each… §4.6 walks through all six"** (§2) — the section heading had just told me these two mechanisms carry the properties. The answer to the exact question I was sent to decide is deferred two chapters. This is the largest structural stumble in the document.
9. **`PP["Plan"] -.->|"translated into Steps"| P`** (§3.1 diagram) — the arrow runs Plan→Purpose, labelled "translated into Steps," while the other two run Purpose→Plan→Approach and the prose says the Plan is "the hinge converting a signed document into Steps." So one arrow points the opposite way from the prose and its label names the wrong endpoint. Re-read the diagram three times against the paragraph below it.
10. **CCS row, "Machine check" column: "The compression rules of §5.4"** (§3.2 table) — expected a check. Compression rules are prose brief is asked to follow; §5.4 later confirms one of them has no trail at all. The column header asserts checking that does not exist.
11. **Run-state, "*(proposed)*"** (§3.2, again §3.3, again §4.4, again §4.5) — a thing that does not ship, raised four times, once at full paragraph length ("The proposal deliberately runs ahead of the code and is waiting on the owner's decision"). Each time I had to re-establish that it was not part of what I was judging.
12. **"Physical layout appears here and in no other chapter"** (§3.3) — the section announces that it is reference material, then stays in the read-through part. Skimmed and moved on, then re-read `ccs/tNNN.yaml` later when §4.2 made the per-wave file matter.
13. **"Reaching the ceiling raises an exception"** (§4.1) — code vocabulary in a system whose §3.4 says "No compiled or scripted part sits beside it." Guessed it means "notifies the person out of band."
14. **"A soft ceiling of 2,000 bytes governs the file however wide the wave was — it fails nothing"** (§4.2) — expected the mechanism that bounds the state. Got a number that is explicitly toothless. Held open until §4.6, which confirmed it is a default.
15. **"the CCS does not shrink to a constant as a wave widens… What it does is grow far slower than the width, under a ceiling that stays put"** (§4.2) — re-read four times. If the ceiling stays put, growth *is* bounded by a constant. If growth is merely sub-linear, the ceiling does not hold. The sentence asserts both. This is the sharpest confusion in the document and it sits directly on top of the property I was asked to judge.
16. **"Whatever the project lacks becomes Steps on the Plan."** followed 30 words later by **"whatever a project lacks becomes Steps on the Plan, written in aiya's formats."** (§4.4) — near-verbatim duplication inside one paragraph. I re-read the paragraph assuming I had lost my place.
17. **"Publishing a new version voids every measurement taken against the previous one"** (§4.4) — expected the cascade case: a new Purpose voids Approach verdicts, which are what the Deliverable was measured against. Got only the single-hop case. Question left open.
18. **"A Planning Gate still waiting and one just approved look identical on disk"** (§4.5) — expected resume to be settled by then; got a disclosed hole plus the fourth appearance of the run-state proposal.
19. **"A default — nothing stops a Conductor dispatching two briefs"** (§4.6, leg 3) — expected the stated failure mode to threaten the property. Two small CCS files instead of one is still bounded. The named risk does not match the leg it sits under; I could not tell what the real failure mode of this leg is.
20. **"Counted honestly: none of the six legs is enforced."** (§4.6) — the document's real finding, arriving at the end of chapter 4 after ~250 lines written in the register of guarantees ("never reaches," "cannot start," "belongs to record alone," "Nothing in this design crosses the line"). It retroactively re-reads chapters 2–4. I went back over §2's "Two walls" and §3.2's Machine-check column after reading it.
21. **"a schema taken from Bousetouane, "AI Agents Need Memory Control Over More Context" (2026)"** and **"Schema, the nine component names… : the definition."** (§5.4, jumped to) — I went here specifically to check whether the CCS's contents bound its size. The nine components are named nowhere in the document; the authority is an external citation I cannot check and the content is in a file that is not in front of me. Dead end on the one thing I needed to size the CCS independently.
22. **"One rule has no trail — nothing distinguishes brief paraphrasing the Report from brief reading the product."** (§5.4) — the rule that keeps the state anchored to artifacts is the one with no evidence. Directly weakens property #1.

---

# 4. Content I did not need

For deciding whether two mechanisms discharge two properties, none of this contributed:

- **§3.3 disk layout and the three backends** (github / gitlab / local, `gh`/`glab`, `docs/ux.md` placement, `history/` archiving). Serves an implementer and an auditor locating files. The section says as much itself.
- **The run-state proposal, all four appearances** (§3.2 row, §3.3 paragraph, §4.4 conditional, §4.5). Serves the owner who has to rule on it. It is a decision memo interleaved into an argument, and it made me re-check three times whether I was judging shipped behavior.
- **§3.4 "What ships"** — file inventory. Serves an implementer.
- **§2 "One wager," second paragraph** ("None of the frame is new… whatever it establishes transfers to anything built with it"). Positioning for a sponsor or a reader choosing between tools.
- **§4.4 gate ergonomics** — console summaries, `gm <one line>` vs bare `gm`, comment downloading, "merging is not something aiya does." Serves an operator.
- **§4.1's off-counter cases** (lost returns, missing viewpoints) and **§4.5's backend durability**. Serves an implementer.
- **Most of §3.2's table.** Only the CCS and Plan rows bore on my decision; the Author / Human-owner columns are ownership reference.
- **The glossary in §2** was half necessary (Phase, Plan, Turn, wave, viewpoint) and half not (Elicit item, Yardstick, the six command words, "Investigation is first-class work").

Roughly a third of Part 1 is reference material sitting inside the part whose stated reader is not looking things up.

---

# 5. Effort score

**4 out of 5.**

Not because the writing is bad — it is unusually disciplined prose and unusually honest at the end. It is a 4 because the document withholds its own conclusion until after I had built a model on the opposite assumption, and because the one quantitative claim I was sent to evaluate contradicts itself in a single paragraph.

**The one change that would most reduce it:** put the §4.6 verdict at the front — in §1 or in the §2 heading that currently reads "The CCS and the chain carry the two properties." Say there: *none of the six legs is enforced; what the design delivers is that both properties become checkable objects, over a structural floor of exactly three facts (empty subagent context, return-only channel, no spawn tool).* Every mechanism after that would then read as evidence for a claim I already hold, instead of as promises I have to retroactively downgrade.

Second, and nearly as valuable: pick one size claim in §4.2 — fixed ceiling **or** sub-linear growth — and delete the other.

---

# 6. The path I actually took

1. Read `prompt-B.txt`.
2. **Headings-only pass** over doc-B.md — all 27 headings, top to bottom, wrote down the predicted argument (§2 above) before opening the body.
3. Read the title block and the Part 1 reader note.
4. **§1** straight through.
5. **§2** — read to the end of "The words this design fixes," **jumped forward** hunting the "two rules it never breaks," landed in "Two walls," **jumped back** to re-read the heading, then resumed in order.
6. Re-read the "Two walls" nesting paragraph after tripping on the count of six definitions.
7. **§3.1** — read prose, read the mermaid, **re-read the diagram three times** against the prose over the `PP -.-> P` arrow.
8. **§3.2** table — read the CCS and Plan rows closely, skimmed the rest.
9. **§3.3, §3.4** — skimmed; flagged both as reference.
10. **§4.1, §4.2** — read in order; **re-read §4.2's size paragraph four times** over the ceiling/sub-linear contradiction; **jumped back** to §1's "grows slower than their number" to check which claim was original. It was neither.
11. **§4.3, §4.4** — read in order; re-read the §4.4 prerequisites paragraph after hitting the duplicated sentence.
12. **§4.5, §4.6** — read in order. At "none of the six legs is enforced," **jumped back** to §2's "Two walls" and §3.2's Machine-check column to re-read them under the corrected assumption.
13. **Jumped out of Part 1** into **§5.4** and **§5.6** — deliberately, and this is the disclosure the prompt asked for. §4.2 explicitly defers the CCS's rules and its "nine components" to §5.4, and my decision on bounded context could not be made without seeing whether anything actually constrains the file's contents. §5.6 for the same reason on the other side: §3.1 rests drift detection on "the fourth of the Plan's fixed viewpoints," and I needed to see what that viewpoint says. Both changed my decision at the margin — §5.4 supplied stumbles 21 and 22, and §5.6's fourth viewpoint is what made me credit the chain more than the CCS.
14. Did **not** read §5.1, §5.2, §5.3, §5.5, §5.7, chapter 6, or chapter 7.
