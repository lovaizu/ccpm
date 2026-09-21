# Reader trial — round 3, Part I (the mandated comparable prompt, whole document)

Fresh subagent, given only `doc-W.md` (a neutral-named copy of the whole document after the round-2
fixes) and the run brief's verbatim reader prompt. Verbatim and unedited. This is the third and final
round under writ's cap; the document was not edited after it.

---

# Report: reading `doc-W.md` cold

---

## 1. The decision

**QUALIFIED — and the document's own qualification, while unusually honest, is incomplete in three specific places.**

### What discharges

**Mechanism 2 (the two-layer yardstick chain) discharges most of property 2.** The traceability half is real: Step -> Plan -> gate-approved yardstick -> purpose is a chain where a Step justified by nothing is a *broken link*, not a mood, and §5.6's four fixed viewpoints check exactly that. The "output nobody asked for" half is genuinely well-built: §5.3's verifier is independent by construction — the Report is withheld, the expected answer is withheld, and the ruling hits disk *before* the return, so a ruling that would suit the Conductor cannot be arranged after the fact. That is the strongest design in the document, and it is the part I would defend to someone else.

**Mechanism 1 (the CCS) discharges property 1 exactly as property 1 is worded.** One wave of any width converges on one file; the next wave reads one file. Flat in the width. That is architecturally true and the shape is right.

### What qualifies it

**(a) Property 1 was narrowed until it no longer answers the failure that motivated it.** §1.2 diagnoses context bloat as "Whichever agent is directing piles up state **in proportion to the size of the job**." §1.3 then defines bounded context as being about the wave-to-wave carry-forward only, and §1.4/§4.5 exclude the two things that actually grow with the size of the job: the wave's Verdicts (Steps x viewpoints) and the transcript ("bounded by nothing"). The transcript is *precisely* "state piling up in proportion to the size of the job." The mechanism discharges the narrowed property; the narrowed property does not discharge the stated failure. The document states every one of these facts and never puts them next to each other. The manual remedy — `dn` -> `/clear` -> `up` — is a person doing housekeeping, which is the watching §1's title says the design removes.

**(b) One of drift's two shapes has no detection at all — and §4.3 does not admit what §1.4 admits.** §1.2 says drift "arrives in two shapes," the second being "the original plan finished to the letter while everything learned on the way is ignored." The leg that catches it is re-derive-the-Plan-from-zero, and §1.4's third column says **"Nothing."** — no trace, "an instruction rather than a property." Then §4.3, the section that owns that leg, presents it in bold as if it were a rule in force and never mentions that nothing can distinguish a from-zero derivation from an edit. Half of the failure this mechanism exists to catch is undetectable, by the document's own accounting.

**(c) Two admissions that compound are never joined.** §3.2: the CCS is measured by **"Nobody"**, and a false line "does reach the Conductor's steering (§4.3) unchallenged." §1.4: steering (re-planning) is the leg with **no trace whatsoever**. So the one unmeasured artifact feeds the one untraced leg. Both facts are stated; their product is not. An unmeasured CCS producing a corrupted re-plan leaves nothing behind anywhere.

**(d) "Traced" has no named reader — and five of six legs rest on it.** The word does a colossal amount of work and the document never once says who inspects a trace, when, or on whose budget. Worse, where it *does* get concrete, the reader turns out not to exist: §5.1's breach trace for the firmer wall is "the nested session's transcript, which no bounded return reports — **so nobody inside the loop ever sees it**." A trace nobody reads is operationally identical to "nothing." I cannot tell, from this document, whether the five "traced" legs are one category or two, and that distinction is the whole difference between a design that self-corrects and one that merely leaves forensic residue for a post-mortem that may never happen.

**(e) A smaller hole the document never names.** Elicit items "bypass this pipeline entirely" (§4.1) and elicit answers are "exempt" from measurement (§3.2). Human-sourced content enters the run unmeasured, and the Conductor is its transcriber. Property 2 says "**any** piece of work can be traced back to the purpose." Elicit answers are a declared exception to that "any" and the document never reconciles the two. (The Purpose drafted *from* them is measured for sourcing, so this is partial — but a mis-transcribed answer is undetectable, and the transcriber is the party the design otherwise keeps away from artifacts.)

### The honest bottom line

At the level of *design shape*: mechanism 1 works for the narrowed claim, mechanism 2 works for one of two drift shapes and fails the other. At the level of *runtime guarantee*: nothing is discharged. Exactly two things are enforced (fresh context, absent delegation tool), and the second is softened for four of six definitions by Bash. Everything else is prose a model is asked to follow, untested — "a wager, and it is untested" (§1.4), with chapter 7 in unbroken future tense. I did not find a single measurement in this document. So the decision is QUALIFIED on the design and **unproven** on the enforcement, and the document says so about itself, which is to its credit and does not change my answer.

---

## 2. Headings-only pass

**Yes, largely — better than most documents.** Reading only the headings, I wrote down before opening the body:

> A single person directs many agents at one goal without supervising them. Delegating naively fails two ways, which yields two required properties. Two mechanisms answer them — a compressed state object and a chain of approved yardsticks — and **neither is enforced**. Then: roles and the walls between them; the chain, ledger and layout; how the loop runs, wave by wave, with human gates; then reference material — per-part promises, cost measures, and rejected alternatives.

That is the document's actual argument. §1.4's heading — "the CCS bounds context, the chain catches drift, **and nothing enforces either**" — is the best sentence in the file: it delivers thesis and self-undermining qualification in one line, before any body text. Most design docs bury that.

**Where the thread broke:**

1. **Chapter 2's sub-headings are unnumbered** while 1, 3, 4 are numbered. On the headings pass I could not tell whether "Two roles, and no third" was a peer of "1.1" or something lesser. Small, but it wobbles the skeleton.
2. **"The bet"** is the only heading in Part I that is a noun instead of a claim. Every other heading tells me what it concludes; this one tells me a topic. And the body turns out to contain a *different* bet from the wager §1.4 named — the headings gave me no warning of two bets.
3. **"3.4 What ships"** — same problem. After the headings pass I had no idea what ships, and this section is where I would learn how much of the design is real.
4. **"3. Structure — One chain, one ledger, one layout"** enumerates parts without asserting anything. Contrast §1.4, which asserts. I could not predict what §3 would argue.
5. **The headings gave me no signal that §4.3 would silently contradict §1.4's tone** about the un-traced leg. That is the single most decision-relevant tension in the document and it is invisible from the outline.

---

## 3. Every stumble, in reading order

**Headings pass**

1. **L1–8, "This file holds two documents, and it says which is which."** Expected: two files, or two clearly separable halves. Got: one title, one continuous chapter numbering 1–7. I re-read to establish that "documents" meant "chapter ranges." The framing overpromises a separation the file does not physically have.

**Chapter 1**

2. **L18–21, "The target is a tenfold jump... Proving the tenfold figure is out of scope."** Expected: a motivation I could use. Got: a headline number introduced and disclaimed within three lines. As an evaluator I now hold a figure I have been told to ignore. Why raise it?
3. **L26, "the cheapness that made running many streams attractive is precisely what evaporates."** Cheapness of *what* — tokens, time, human attention? Guessed tokens. Not settled until chapter 6, which I would not have read.
4. **L34, the bounded-context bullet.** "Two things are outside this claim and stay outside it... **§1.4 gives the shape of all three.**" Expected: the exclusions, here, where the property is defined. Got: a pointer forward one section. I held "what are the three?" open across a section boundary for the most decision-critical caveat in the document. Why is the exclusion not simply written where the claim is?
5. **L34, "A batch is a wave — the Steps whose inputs are all ready, dispatched together (§4.2)."** A load-bearing term is defined parenthetically, mid-bullet, inside a sentence about something else, three chapters before the section that owns it. Re-read the bullet twice.
6. **L39, "nine fixed components."** A number with no contents and no reason to be nine. Held open until §5.4's table, which I eventually consulted. At this point the number told me nothing.
7. **L39, "Two layers, because one of them must not move and the other must."** "Two-layer yardstick chain" is named here for the first time. I jumped forward to §3.1's diagram to check whether the two layers were the solid/dotted split. They are. One clause would have saved the jump.
8. **L48, "Traced only indirectly."** §2 fixes exactly three ways a rule can hold — structural, traced, nothing. This table cell invents a fourth, and L58 invents a fifth ("Partly structural"). I stopped to work out whether "traced only indirectly" counts as traced. Unresolved. The vocabulary is presented as closed and is not.
9. **L47, "**Traced.** The tell is the Conductor citing content no return delivered."** Expected: who notices the tell, and when. Got: nothing, here or anywhere. This question stayed open through my entire read and is never answered. It is the largest hole in the argument (see decision, point d).
10. **L51, "One more thing belongs beside the claim rather than in chapter 3: the CCS is the one product nothing measures."** The sentence spends its first half explaining its own editorial placement. I re-read to extract the fact from the meta-commentary. The document narrates its own structure at L5–8, L32, L51, L61, L67, L304, L308 — each one costs a beat.
11. **L61, "Read the third column before the first two."** I had already read the table left-to-right. Now I re-read it. If the third column is the point, make it the first column.
12. **L63, "even that wall softens where a definition carries a shell — four of the six do."** "Carries a shell" is undefined. Jumped to §5.1 and found the plain word: **Bash**, with "an indirect escape through the platform's own CLI." The euphemism sits in the argument chapter, the plain word in the reference. That is backwards.
13. **L65, "That prose alone holds all six is a wager, and it is untested."** Held open: is there *any* result in this document? I jumped ahead to chapter 7 to check. There is none — chapter 7 is entirely future tense ("Falsified in dogfooding, the first hardening to try is..."). This forced my decision to be about design shape only, and I want that on the record.

**Chapter 2**

14. **L73, "Two roles inside the loop, because the design needs exactly one that holds the purpose and never touches the work..."** Expected: a reason. Got: a restatement of the split as its own justification. Circular as written.
15. **L86, the diagram's `C -. "never reads" .-> A` edge.** The diagram precedes the paragraph that names the wall. On first pass the dotted edge was unexplained; I read on, then came back.
16. **L92, "outside the three-attempt ceiling (§4.1)."** First mention of a three-attempt ceiling, forward-referenced, in a subordinate clause of a sentence about something else. Held open until §4.1.
17. **L101 vs L192 vs L318 vs L57–59 — four different sixes.** Six halts, six skills, six Turn definitions, six legs. I miscounted once and had to go back and separate them. Nothing warns the reader that "six" is a coincidence four times over.
18. **L104, the vocabulary entry for structural / traced / nothing.** Fixed here — *one section after* §1.4 used all three as the backbone of its two tables, and after §1.4 had already violated the three-way closure twice. I jumped back to §1.4 to re-read the tables with the definitions in hand.
19. **L108–112, "The bet."** §1.4 called the wager *"that prose alone holds all six."* §2's bet is a different one: code freezes, models improve. Two bets, both called the bet/the wager, never distinguished at the point of introduction. §7's first bullet finally welds them together ("the compliance bet... (§1.4)" argued against with §2's reason), which is where I finally understood they were meant as one argument. I held both separately for five chapters.

**Chapter 3**

20. **L139, the CCS row of the ledger table: "but it does reach the Conductor's steering (§4.3) unchallenged."** I stopped dead. This is the admission that flipped my decision from YES toward QUALIFIED, and it is buried in a table cell in the middle of a nine-row table. It deserves a paragraph.
21. **L143, "*(proposed)*."** First use of a marker whose convention is explained at L304 — in Part II's preamble, which this reader is told not to need. I guessed the meaning, then confirmed at L174/L186.
22. **L166, "unless a Planning Gate redirects them for a project laid out differently (§4.4)."** I jumped to §4.4 and searched for redirection. It is not there — §4.4 only says missing documents get Steps to write them. I read §4.4 twice looking for the referent. **Dangling cross-reference.**
23. **L170–186, the whole backend / `state.yaml` block.** Irrelevant to my decision, and long. I skimmed it, then had to return when §4.4 and §5.5 leaned on the local degradation.
24. **L186, "`skills/conductor/SKILL.md:26`."** A design document citing implementation line numbers, immediately after a YAML sample for a thing that does not exist. I re-read to work out that the citation describes what ships *instead of* the proposal.
25. **L186, "waits on the owner's ruling."** Who is the owner? First and only use of the term. The human at the gates? Someone else? Guessed.
26. **L198, "That is §2's bet at its most concrete, and it is the reason §1.4's qualifier reads the way it does."** Two back-references in one sentence. I jumped to §1.4 to determine *which* qualifier. Presumably "and nothing enforces either." Guessed.

**Chapter 4**

27. **L204, "An elicit item sends none and bypasses this pipeline entirely."** Held open: so human-sourced content is never measured? §3.2 confirmed ("elicit answers exempt"). Property 2 claims **any** piece of work traces to the purpose. The exception is never reconciled with the claim. Open at the end of my read; I closed it myself (see decision, point e).
28. **L219, "so a well-argued claim has no route in."** The verifier still reads the product, which the maker wrote and can make persuasive. Small overclaim; noted, moved on.
29. **L223, "Two side paths exist."** Lost returns and late-spotted viewpoints. Did not serve my decision; I read it wondering why it was in the argument half.
30. **L245, the committing paragraph.** Git-index collisions. Operator content sitting in the middle of the behavioral argument.
31. **L251, "derived from zero out of the present position, never by editing the standing Plan."** I stopped. §1.4 L59 already told me **nothing** distinguishes the two. §4.3 restates the instruction in bold and adds no mechanism, in a voice that reads like a rule in force. I jumped back to L59 to confirm the contradiction in tone. Confirmed. **The most consequential stumble in the document.**
32. **L179–184 vs L267, the gate log.** The sample logs `G1: gm` then `G1: ty` — the same gate ruling twice. I had to derive for myself that the log appends send-backs and approvals alike. L286 eventually says so ("approvals and send-backs alike"), two sections later.
33. **L276, "Four things must already exist..."** UX and Design go from a parenthetical at L166 ("outside that tree") to hard prerequisites for all Approach and Delivery work. I re-read L166.
34. **L284, "the voided ones are found by search and their Steps measured again."** By whom, with what? The Conductor may not read artifacts. Held open until §5.7's intake list showed Verdicts are permitted intake. Required a jump.
35. **L296, "Bounded means the working state, and nothing else."** The third statement of the same exclusion (§1.3, §1.4, §4.5), each worded differently. I stopped to check whether §4.5 was conceding something new. It was not. Repetition without addition — and, given point (a) of my decision, repetition in place of the reconciliation that is actually owed.

**Sections I entered out of order to reach the decision**

36. **L318 (§5.1), "the nested session's transcript, which no bounded return reports — so nobody inside the loop ever sees it."** I came here from L63 and L92. This sentence lowered my confidence in the word "traced" across the entire document.
37. **L359 (§5.4), "what grows sub-linearly is the total the Conductor has read across the run."** Sub-linear **in what**? A constant-size file per wave, summed over waves, is linear in waves. I could not resolve the variable, and this is a claim about the exact property I was asked to decide. Guessed: sub-linear in total work volume. Unverifiable from the text.
38. **L344 (§5.4), the Bousetouane citation.** The only external authority in the document, load-bearing for the CCS schema, and uncheckable from here. Noted; does not move the decision.
39. **L413 (§5.7), "Nothing inside the loop can take reading away from the Conductor: its whole state is files, and the tool that reads them is the tool it works with."** This explains *why* wall #1 is unenforceable — strictly stronger than §1.4's "Nothing blocks the read," and it belongs in the argument, not the reference.

---

## 4. Content I did not need

Roughly 45% of what I read did not serve the decision. Where I can identify the audience:

- **§1.1's tenfold framing (L18–21)** — serves a sponsor or a pitch, not an evaluator. It is disclaimed on arrival.
- **§3.3's three backends, the `state.yaml` YAML sample, and the `SKILL.md:26` citation (L170–186)** — serves a builder/operator. The `local` degradation is later load-bearing for two other sections, so a single sentence of it was needed; the page was not.
- **§3.4 entirely** — serves a builder. Its last sentence (L198) is argument, and is stranded there.
- **§4.1's "two side paths" (L223)** — operator.
- **§4.2's committing paragraph (L245)** — operator. Git-index serialization has nothing to do with either property.
- **§4.4's gate mechanics — `ty`/`gm`, the review surface, the bare-`gm` comment fetch, "aiya does not merge" (L282–286)** — operator. The version-invalidation rule inside it *is* relevant to drift detection and is the one thing I would rescue from this block.
- **§4.5's suspend/resume mechanics (L290–294)** — operator. Its final paragraph is load-bearing for property 1 and is stranded behind them.
- **All of chapter 5** except the four fragments cross-references forced me into (5.1's Bash admission, 5.3's independence argument, 5.4's ceiling honesty, 5.7's intake list) — serves a builder. Notably, those four fragments are the ones that most changed my decision, which means the argument half is under-carrying its own case.
- **Chapter 6 entirely** — serves an operator justifying cost. The document says so itself: "These ratios answer a separate question."
- **Chapter 7's "Shapes discarded"** — serves a future reviewer of the decision record. **Chapter 7's "Costs paid" did serve me**, as confirmation that nothing has been measured; it is the only place several concessions are gathered where the argument can see them.

---

## 5. Effort score

**4 out of 5.**

Not because the prose is bad — it is dense, controlled, and nearly every sentence carries load. That is the problem. There is no slack to coast on, the forward-reference count in chapter 1 alone is nine, and the vocabulary that governs the two decision tables is fixed one section *after* those tables use it — while the tables themselves use five terms from a three-term set. I read chapter 1 three times.

**The one change that would most reduce it: name the reader of every trace.** Five of the six legs — the whole substance of both mechanisms once "structural" is stripped down to two platform facts — rest on the single word *traced*. The document defines traced as "cheap to spot afterwards" and then never says who is spotting, when, or as part of what step. Where it does get specific (§5.1), the answer turns out to be "nobody inside the loop." Until that is answered, an evaluator cannot distinguish "traced" from "nothing," and the document's central table becomes unreadable in the one column it tells me to read first.

Runner-up, if that one is refused: write §1.4's third-column verdicts into the prose of §4.3 and §4.5, so the argument chapters stop sounding more confident than the tables that qualify them.

---

## 6. The path I actually took

**A disclosure first:** the file is one file, and my reading tool returned it whole in a single call. Chapters 5–7 were therefore physically in front of me from the start; I could not partition the read the way the brief asked. I did the headings pass first from that output, then read the body of 1–4 in order, and I consulted later chapters only where I record doing so below. Every consultation is listed.

1. **Headings only**, L1 -> L468, top to bottom. Wrote down the predicted argument (§2 above).
2. **§1.1 -> §1.2 -> §1.3.** Stopped at L34; held the "three exclusions" question open; re-read the bullet for the definition of *wave*.
3. **§1.4.** Read the first table left to right, hit L61's instruction, **re-read both tables third-column-first.**
4. **Jump forward to §3.1's diagram** from L39, to resolve "two layers." Returned.
5. **Jump forward to chapter 7**, skimmed, from L65, to check whether any dogfooding result exists. None. Returned.
6. **§2 straight through.** At L63 **jumped to §5.1**, read it in full (this is where "shell" = Bash and the unobservable breach trace appeared). Returned.
7. **Re-read §1.4's tables a third time**, from L104's vocabulary entry, to check the three-way classification against the five phrasings actually used. It does not hold.
8. **§3.1 -> §3.2.** Stopped hard at L139's CCS row. Re-read it. **Jumped back to §1.4 L59** to confirm that the leg the CCS feeds is the untraced one. Confirmed — this is where my decision moved off YES.
9. **§3.3**, skimmed the backends and the YAML.
10. **§3.4.** At L198 **jumped back to §1.4** to identify "§1.4's qualifier." Returned.
11. **§4.1 -> §4.2.** At L204 **jumped back to §3.2** to check the elicit exemption. Confirmed. Returned.
12. **§4.3.** Stopped at L251. **Jumped back to §1.4 L59** a second time to confirm the contradiction in tone between the table's "Nothing" and this section's bold instruction. Confirmed.
13. **§4.4.** **Searched it for the docs-redirection referent from L166.** Not present. Re-read the section a second time to be sure. Dangling.
14. **§4.5.**
15. **Jumped into §5.3** to test the independence claim behind property 2. Read in full. **Then §5.4** for the CCS operating rules and the ceiling — hit L359's "sub-linearly" and could not resolve it. **Then §5.7** for the intake list, which retroactively answered stumble 34 and produced stumble 41.
16. **Skimmed §5.5 and §5.6**; read §5.6's four fixed viewpoints properly, since the traceability leg depends on them.
17. **Skimmed chapter 6**; read chapter 7's **"Costs paid"** in full.
18. **Final pass over §1.3 and §1.4** to write the decision.
