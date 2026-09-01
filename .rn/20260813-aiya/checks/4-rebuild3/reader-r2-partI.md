# Reader trial — round 2, Part I (the mandated comparable prompt, whole document)

Fresh subagent, given only `doc-M.md` (a neutral-named copy of the whole document after the round-1
fixes) and the run brief's verbatim reader prompt. Verbatim and unedited.

---

# Report — reading `doc-M.md` cold

---

## 1. The decision

**QUALIFIED.** The two mechanisms discharge the two properties *as the document defines those properties* — but the document defines them, in part, to fit what the mechanisms do, and one of the six legs holding them up has, by the document's own admission, nothing behind it.

**Bounded context — discharged, but the property shrank.** §1.2 names the failure as an agent that "piles up state in proportion to the size of the job." §1.3 then states the property as working state growing "more slowly than the number of work streams running at once" — i.e. sub-linear in *wave width*, not in *job size*. Those are different claims, and the second is the one the CCS actually answers. §1.4 then concedes outright that of the three things entering the Conductor, only one is flat in width; Verdicts scale with Steps x viewpoints, and the transcript is "bounded by nothing," cleared by hand. So the mechanism wins the test it was given, and the test was rewritten to be the one it wins. §4.5 and §7 both restate the concession honestly, which I credit — but the honesty is downstream of a redefinition, not a substitute for it. The original failure in §1.2 is *not* discharged: state still grows with the job, and a human typing `dn` -> `/clear` -> `up` is the only thing that reclaims it.

Two further weaknesses inside the leg that does hold. The 2,000-byte ceiling is "advisory, not enforced" (§5.4) and nothing measures it. And §3.2 lists the CCS as the one product whose "Measured by (machine)" column reads **"Nobody."** So the artifact carrying the entire bounded-context claim is the one artifact with no check on it.

**Drift detection — discharged for one of the two failure shapes, not the other.** §1.2 names two shapes: output nobody asked for, and a plan finished to the letter while learnings are ignored. Shape one is genuinely covered — §5.3's verifier is the strongest thing in the document: it never sees the maker's Report or the expected answer, it writes its ruling to disk *before* returning so the record predates the Conductor seeing it, it measures against a frozen edition, and it names that edition so version bumps invalidate by search. That is real independence with a real trace in `verdicts/`.

Shape two is not covered. It rests on leg three — "the Plan is derived again from zero" — and §1.4 says plainly: *"none of them tells a Plan re-derived from zero apart from a Plan edited. That leg is a norm with no check behind it."* §5.6's four breach traces confirm it: broken format, lying `consumes`, unlogged revision, unapproved edition — none detects a Conductor that quietly edited yesterday's plan. So one of the two named drift failures is answered by an unfalsifiable instruction.

**The cross-cutting qualifier.** Nothing enforces any of this. Two platform facts (empty subagent context, delegation tool absent) hold the role wall and explicitly "do not hold the six legs." Even that wall is weaker than chapter 2 presents it: §5.1 reveals four of six Turn definitions carry Bash, so "Turns are leaves" is a norm for those four, and its breach trace is a nested transcript "nobody inside the loop ever sees." The document's own summary is *"That prose alone holds all six is a wager, and it is untested."*

**The gap the document never joins up.** §3.2 says a false CCS line "does reach the Conductor's steering (§4.3) unchallenged." The CCS is the bounded-context mechanism; steering is where drift shape two is supposed to be caught; the CCS is measured by nobody. So mechanism one can inject exactly the failure mechanism two is uncovered for. That closes a loop the document leaves open — it states each half in a different chapter and never puts them side by side. This is my single largest reservation and it is not in the document's own list of costs.

---

## 2. Headings-only pass

**What I reconstructed from headings alone:** delegation breaks in two ways -> two required properties -> one mechanism each, CCS for context and a yardstick chain for drift. Then roles (two, plus walls, plus a bet), then structure (chain / ledger / layout), then the runtime loop (Step -> wave -> steering -> gates -> suspend). Part II is lookup material.

**The headings carry the skeleton well.** §1.4's heading is a full sentence stating the answer — that is the right move, and it let me predict the shape of the whole argument before reading a word of body.

**Where the thread broke — three places:**

- **§1.3 "The two properties" names neither property.** The one heading I most needed to carry content carries none. I had to guess, and my guess ("context stays small; work stays on target") was right in spirit and wrong in scope — I did not predict that the context property would be restricted to wave width.
- **The heading pass gave no hint that any of this is unenforced or untested.** §1.4's heading asserts flatly: *"the CCS bounds context, the yardstick chain catches drift."* The body says it is a wager. Nothing in any heading — through chapter 7's "what is being paid" — warns a skimmer that the load-bearing qualifier exists. A reader who skims headings and reads §1.4's tables walks away with a stronger claim than the document actually makes.
- **§2's "The bet" and "Two walls hold the roles apart" name a thing without saying which thing.** Compare §1.4's heading, which does the work. Chapter 2's headings are labels; chapter 1's are claims. §4.4 "Gates — where the human rules" and §4.5 likewise tell me the topic but not the finding, so from §4.3 onward the headings stop advancing the argument and start indexing.

---

## 3. Every stumble, in reading order

**1. §1.1 — "The target is a tenfold jump in what a single expert delivers" / "Proving the tenfold figure is out of scope."**
Expected the goal to feed into the properties. Got a number stated and disowned in consecutive paragraphs. It plays no role anywhere else in the document. Held open the whole read wondering if it would return. It does not.

**2. §1.3 — "grows more slowly than the number of work streams running at once — how many run at once being the width of a **wave**, the set of Steps whose inputs are all ready (§4.2)."**
Re-read twice. This is *the* sentence stating *the* property I was asked to judge, and it carries a mid-sentence definition of a new term plus a forward reference. Also "grows more slowly than" is a loose bound — is it sub-linear, logarithmic, what? The mechanism actually delivers *flat* (one CCS however wide), which is stronger than what is claimed. The claim is weaker and vaguer than the thing it describes.

**3. §1.4 — "One mechanism per property."**
Then three parties, then two tables of three legs each. Expected two mechanisms explained. Got six legs, and neither mechanism is actually *described* in chapter 1 — I learn "CCS" expands to Compressed Cognitive State and nothing else. I had to reach §5.4, in Part II, to learn what a CCS contains. That is a chapter-1 hole for a chapter-1 reader.

**4. §1.4 — "The **two-layer yardstick chain** answers drift detection."**
"Two-layer" appears exactly once in the document and is never explained. I guessed it means §3.1's solid (frozen) plus dotted (Plan) edges. Never confirmed. Guessing about the name of one of the two mechanisms I am judging.

**5. §1.4 table — "puts a soft ceiling of 2,000 bytes on the file and treats an overrun as a symptom to report rather than a budget to raise."**
A column headed "What it bounds" containing the word "soft." Expected a bound; got a suggestion. Had to reach §5.4 to get the straight answer ("advisory, not enforced"). Chapter 1 should not be softer about its own qualifier than chapter 5 is.

**6. §1.4 — "§1.3's property is a claim about the first of the three. The second and third are stated where they arise and are not covered by it."**
Re-read twice. This is the property being narrowed *after* being stated, in service of the mechanism. Expected a property functioning as a test the design must pass; got a property retrofitted to what the design delivers. The paragraph is honest and it is also the moment the argument's spine bends.

**7. §1.4 — "Five of the six leave a trace... The sixth does not."**
Had to count. There are two tables of three rows, neither numbered, and "the sixth" means row three of table two. I resolved it only by elimination via §5.6's trace list. The single most consequential admission in the document is delivered through unnumbered cross-table row arithmetic.

**8. §1.4 — "the `tools:` line of all six files under `agents/` carries none."**
`agents/` appears here with no introduction. §3.3's layout tree shows `.aiya/<slug>/` and does not contain `agents/`. I looked back at §3.3 to find it; it is not there. No repository layout is ever given, so this and the later `skills/conductor/SKILL.md:26` are references to a filesystem I cannot see.

**9. §2 — "Two roles, and no third... The human is neither."**
Collides with §1.4's "Three parties do the work," and with the mermaid directly below, which draws three boxes including the human. Re-read to work out that "party" != "role." The document never says that.

**10. §2 vocabulary — "Three more command words — `on`, `dn`, `up` — drive the session."**
Command words arrive before I know a session lifecycle exists. `dn` is never expanded; I inferred "down" from its pairing with `on`/`up` and its use in `dn` -> `/clear` -> `up`. A guess.

**11. §2 vocabulary — "**Structural** and **default and observable** — the two ways a rule can hold, from §1.4."**
Jumped back to §1.4. Neither phrase appears there. §1.4 says "defaults"; "structural" first appears in §5.1. A back-reference to text that does not exist, in the entry defining the document's central distinction.

**12. §2 — "the final layer of measurement — the one that runs after every mechanical check has run (§5.3)."**
Forward reference carrying the weight of "the bet." Held open until §5.3 ("reads only for what no check could have decided"). Chapter 2 asserts the claim it needs and defers the support to Part II, which the intro told me Part I readers would not need.

**13. §3.2, CCS row — "**Nobody.** ...it does reach the Conductor's steering (§4.3) unchallenged."**
Stopped and re-read. This is a top-three finding for my decision and it is inside a cell of a nine-row table in the middle of chapter 3. Expected it in §1.4, alongside the claim it undercuts. Nothing in §1.4's bounded-context table mentions that the CCS is unmeasured.

**14. §3.3 / §4.4 / §4.5 / §5.5 / §5.7 — "*(proposed)*", five times.**
Every occurrence forced a re-evaluation of whether the surrounding paragraph describes something real. Worst case is §4.5: "Four items make up the whole resume point... and the run-state file *(proposed)*." So the whole resume point is three items. The word "whole" is wrong as written.

**15. §3.3 — "What ships today instead is a one-line `backend` file (`skills/conductor/SKILL.md:26`)."**
Source line citations in a design argument. Cold, I cannot check them and they do not advance the case. Second appearance of an unintroduced directory (`skills/`).

**16. §3.4 — "Six skills. Five are typed entry points for the command words... The sixth is a Claude-only conductor skill."**
Counted back to §2: ty, gm, on, dn, up = five. Fine, but the count is left to me. "Claude-only" is undefined jargon.

**17. §4.1 — "Turn(generate) writes product + Report" vs §2 "Even a Turn's own account of what it just did — the Report (§5.2) — is out of bounds."**
Re-read to establish that the Report goes to `reports/` and is read only by brief, never travelling to the Conductor at all. Resolvable, but the diagram shows a Report being produced inside a pipeline whose output goes to a party forbidden to read it.

**18. §4.1 — "putting at most three gaps in front of the human."**
Why three? Presumably one per attempt against a ceiling of three. Inferred; never stated.

**19. §4.3 — "derived from zero out of the present position, never by editing the standing Plan."**
The most emphatic prose in the chapter, on the one leg with no check. Nothing in §4.3 flags that. The claim is in §4.3, the admission in §1.4, the trace-list that omits it in §5.6. Three chapters, and the reader assembles the finding.

**20. §4.4 — "Four things must already exist... the run's approved Purpose and its Plan, and the product's UX and Design documents."**
UX and Design appeared once, in §3.3, as documents that "outlive any single run." Their being a hard precondition for all Approach and Delivery work is new here, and neither appears in §3.1's chain diagram. So the yardstick chain has two inputs the chain diagram does not draw. Held open; never resolved.

**21. §4.4 — "the voided ones are found by search and their Steps measured again."**
Searched by whom? The Conductor may not read artifacts. Verdicts are on §5.7's allowed list, so it is probably legal — but I had to reason it out rather than being told.

**22. §4.5 — "the resume then offers the pending gate a second time — the cheap direction to fail in, costing one repeated `ty`."**
Asserted, not argued. Re-approving a gate whose approval may already have launched downstream work is not self-evidently cheap.

**23. §5.1 — "Four of the six definitions carry Bash... for those four rule 2 is a norm and not a block. **Breach trace:** the nested session's transcript, which no bounded return reports — so nobody inside the loop ever sees it."**
This directly softens §2's "Two walls hold the roles apart" and §1.4's "What the platform does enforce." Chapter 2 presents "Turns are leaves" as structural; chapter 5 says it is structural for two of six and a norm with an invisible breach for the other four. A Part I reader who follows the document's own advice and stops at chapter 4 leaves with the wrong picture. I count this as an inconsistency, not just a stumble.

**24. §5.4 — nine YAML components, ceiling 2,000 bytes.**
Nine components of substantive content in under 2KB is tight, and the document never checks the arithmetic or shows an example at size. Held open as a doubt about whether the ceiling is reachable, let alone enforceable.

**25. §5.4 — "the file stays small and grows sub-linearly with the run."**
Contradicts the bullet three lines above: "Replaced, not appended. Each wave gets a whole new file." If it is replaced wholesale, why does it grow with the *run* at all? Unexplained.

**26. §6 — "**Nothing is instrumented.**"**
Immediately after three ratios are defined as the way cost stays visible. Expected measurement; got three quantities that could in principle be reconstructed by hand from disk afterwards.

**27. §7 — "the first hardening to try is a hook refusing the Conductor's reads by path."**
First indication anywhere that real enforcement is available on this platform. That weakens §2's framing of prose-vs-code as a principled allocation: the enforcement option exists, is named, and is deferred. That is a schedule decision presented as a design philosophy.

---

## 4. Content I did not need

- **§5.5 (Turn(record)), entire.** Backends, five dispatch points, local adapter idempotency. Serves an implementer or operator. Nothing in it bears on either property.
- **§6 (Observability), entire.** The chapter says so itself: "§1.4 answers for the two properties. These ratios answer a separate question." Serves an operator tuning cost.
- **§3.3's layout tree and the three-backend discussion.** Serves an implementer and an evaluating adopter deciding whether their setup fits. The `state.yaml` sample YAML in particular is pure reference material sitting in Part I.
- **§3.4 "What ships."** Serves someone deciding whether to install it.
- **§2's vocabulary list.** Twelve entries; I used four (wave, gate, viewpoint, elicit item). It is a glossary, not argument, and it sits in the middle of the argument chapter. Whoever reads Part II by search is who it serves — and Part II's own preamble says it borrows this vocabulary, which is an argument for moving the list to the front of Part II.
- **§4.4's gate mechanics** — `ty`/`gm`, bare-`gm` comment fetching, console summaries, review surfaces. Serves the human operator. The part I *did* need from §4.4 is the fixed-yardstick paragraph and the versioning/invalidation paragraph.
- **§5.2's version stamping rules.** Serves an implementer.
- **§1.1's tenfold figure.** Serves nobody in this document, by its own admission.

**Chapters beyond 1–4 that I did read, and why.** I read all of Part II. I needed §5.4 (is the CCS ceiling real? — no, advisory), §5.6 (do the breach traces cover the re-derive leg? — no), §5.3 (is the verifier actually independent? — yes, and this is the strongest section), §5.1 (is the Turn wall structural? — only for two of six), and §7 (what the author concedes). Chapter 1 alone was not sufficient to reach the decision: it asserts the mechanisms without describing them and defers every qualifier's evidence to Part II.

---

## 5. Effort score

**4 out of 5.**

The prose is dense but well made — the writing is not the problem. The effort comes from the argument being *distributed*: to judge either mechanism I had to assemble a claim in chapter 1, its qualifier in a paragraph after an unnumbered table, a contradicting detail in a chapter 3 table cell, the operational reality in chapter 4, the enforcement truth in chapter 5, and the concession in chapter 7. The document knows all of its own weaknesses and never puts any one of them next to the claim it weakens.

**The one change that would most reduce it:** give §1.4's two tables a third column — *How it holds: structural / traced / nothing* — with the trace named inline. That single column absorbs the "What qualifies all six legs" paragraph (killing the row-counting), pulls §5.x's breach traces to where they are needed, exposes at a glance that leg six holds by nothing and that leg four (the CCS) is unmeasured, and lets a Part I reader reach a correct verdict without entering Part II. Second choice: state the two properties in §1.3 with their exclusions attached, so the narrowing happens before the mechanism is named rather than after.

---

## 6. The path I actually took

1. **Headings-only pass** — extracted all 33 headings, read top to bottom, wrote down the reconstructed argument (section 2 above). No body text seen.
2. **Lines 1–120** — front matter, §1.1 -> §3.1's first diagram, straight through.
3. **Re-read §1.3's property sentence** immediately, for the mid-sentence wave definition.
4. **Re-read §1.4's "What this bounds, and what it does not"** paragraph twice.
5. **Re-read §1.4's "What qualifies all six legs,"** counting rows across both tables to identify "the sixth."
6. **Jumped back from §1.4 to §3.3's layout tree** looking for `agents/`. Not there. Returned.
7. **Re-read §2's opening** against §1.4's "three parties" to reconcile roles vs parties.
8. **Jumped back from §2's vocabulary to §1.4** looking for "structural" and "default and observable." Neither present. Returned.
9. **Lines 120–300** — §3.1 -> end of §4.5, straight through.
10. **Jumped back from §4.3 to §3.2's CCS row** on realising the unmeasured CCS feeds steering. This is where my main reservation formed.
11. **Lines 300–448** — all of Part II, read in order rather than by search, because chapters 1–4 had left four questions open (CCS contents, ceiling enforcement, coverage of the re-derive leg, verifier independence).
12. **Re-read §5.1's rule 2** against §2's "Two walls" on hitting the Bash concession.
13. **Re-read §5.4's "replaced, not appended" bullet** against the same section's "grows sub-linearly with the run."
14. **Re-read §5.6's breach-trace list** to confirm nothing covers a re-derived-vs-edited Plan. It does not.
15. Composed the decision.

Note on mechanics: I read the file in three large reads, so my "jumps" were re-readings within text already in front of me rather than scrolling. A reader on a screen would pay more for the same jumps than I did, which means my effort score of 4 is, if anything, generous.
