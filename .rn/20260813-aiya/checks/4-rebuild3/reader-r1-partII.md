# Reader trial — round 1, Part II (reference part, chapters 5–7 only)

Fresh subagent, given only `doc-Q.md` (a neutral-named copy of Part II) and the Part II reader
definition. Verbatim and unedited.

---

# Report — reading doc-Q.md cold, as an operator running five lookups

---

## 1. The decision

**QUALIFIED — leaning NO for three of the five lookups.**

Three of the five lookups (a, b, e) resolve in one entry, more or less. Two (c, d) forced me to read across three or four sections and still left me guessing. The bigger problem is one the document announces in its own first line and then does not solve: "Vocabulary is chapter 2's and is not repeated." I do not have chapter 2. I do not have §1.4, §2, §3.3, §4.1, §4.3, §4.4, §4.5. Every one of those is cited as load-bearing, and several carry exactly the thing a lookup needs — the discretion line, the invalidation rule, the two properties the whole design answers for. As a reference this file is a set of entries that are *unique* (I never found the same promise stated twice in two places) but repeatedly *not complete on their own*. An entry that ends in "(§4.3)" for the actual rule is not a lookup answer; it is a pointer.

Second structural problem: the doc promises "Every entry states a promise and the trace a breach leaves behind" (line 7). It does not deliver that. §5.5, §5.6, §5.7 have explicit "Breach trace:" statements. §5.1, §5.2, §5.3, §5.4 do not. §5.2 has no breach trace at all. So the one guarantee the reference makes about its own uniformity is false, and I discovered that only by checking all seven entries — which is exactly what a lookup reader should never have to do.

Third: the doc is unstable about what is decided. Two places are marked *(proposed)* mid-sentence — line 61 and line 77. If I am operating this system, "the Conductor keeps the run-state file current at every boundary event *(proposed)*" tells me a promise I cannot rely on, and there is no marker convention explained anywhere.

---

## 2. Per lookup

### (a) What exactly may a Turn hand back to its caller? — **FOUND, complete**

Line 14, §5.1 rule 4: "Paths and a line, a ruling, a CCS path, a few lines naming what got committed — no raw output, no transcript." Enforcement named on line 17: "Rule 4 the Conductor checks on each return."

This is the one clean lookup in the document. It even cross-checks: the four items map onto the four Turn families in §5.2–5.5 in order (generate → two paths; verify → the ruling text; brief → a CCS path; record → a few lines). Nothing to guess.

Minor gap: "Hands back something small" has no number attached, unlike the CCS which gets 2,000 bytes. "Small" is enforced by the Conductor's check against a four-item list, not a size. Fine, but I had to infer that.

### (b) What stops the CCS file from growing without bound, and what is the number? — **FOUND, with a contradiction I had to resolve myself**

Line 49, §5.4: "Three things keep it small: real work travels by path and is never pasted in; a soft ceiling of **2,000 bytes**, where the component that pushed past it is itself the diagnosis of the Step's scope; and the Conductor keeps no rolling summary of its own."

Number: 2,000 bytes, soft. Also relevant, line 45: "Replaced, not appended. Each wave gets a whole new file" — which is arguably the actual mechanism that stops unbounded growth, and it is listed *outside* the "three things keep it small" list. So the answer to my question is split across two bullets that are not presented as related.

What I had to reconcile: line 49 ends "Small and sub-linear, not fixed in size" — while the preceding clause gave me a fixed number. A soft ceiling that is not a size limit, stated one clause after a byte figure, is a sentence I read twice. And §7 line 122 then says "History still grows linearly. Only the working state is bounded (§4.5)" — pointing me to a section I do not have for what "bounded" means.

Also: "nine YAML components" (line 41) is stated, but the components are never listed, and the ceiling is described as being blamed on "the component that pushed past it." I cannot use that diagnosis without the list. It "travels with the Turn definition," which I do not have.

### (c) When does the physical-record worker actually run, and what happens if it runs twice? — **FOUND for the when; the twice-answer required reconstruction across three sections**

**When** — §5.5, lines 53–60, five dispatch points: at `on`; at every wave settle (after brief); at every pre-Planning-Gate Plan push; at a gate ruling; at `dn`. Clear, enumerated, each with a reason. This is the best-structured entry in the document.

But line 61 immediately undercuts the enumeration: "A Planning Gate's approval sends out no record dispatch at all" — so one of my five points has a carve-out attached as an afterthought paragraph, plus a *(proposed)* marker. I had to re-read to work out that "a gate ruling" (point 4) and "a Planning Gate's approval" are different things. The doc never says so directly; I inferred it from the fact that point 4 talks about "the approved document" and gates G3/`gm`, while line 61 talks about a run-state line only.

**If it runs twice** — line 63: "Re-sending stays safe because at this granularity the operations do nothing twice: a path already committed stages nothing, and a push with nothing new behind it moves nothing." That is git-idempotence, and it is a real answer.

What I had to reconstruct: this is only asserted for the **git** adapters. The **local** adapter "runs no git whatsoever" and its "single write files the approved edition into `history/` under a name carrying its version." Whether a double-run of the local adapter overwrites, duplicates, or errors is **not stated**. The version in the filename suggests it would be a same-name overwrite, i.e. safe — but I am guessing. For an operator running local mode, that is the exact question I came for and I left without it.

Also: §5.1 rule 5 (line 15) says "Being stateless is exactly what makes a re-send harmless (§4.1)." That is a *different* justification for the same safety claim, in a different section, pointing at a section I do not have. Two answers to "what if it runs twice," neither cross-referencing the other.

### (d) What are the criteria a Plan is checked against, and who owns them? — **FOUND, but scattered, and the ownership answer is by inference**

Line 69, §5.6: "**The Plan is measured too**, against four viewpoints aiya fixes rather than the Conductor — a Conductor authoring the criteria for its own Plan would be approving itself. The four: every item carries its three lines; `consumes` reflects real consumption, same-file writes included; `done when` can be run; and the items, held up against the phase yardstick, add up to that phase's product exactly, with nothing over and nothing missing."

**Owner: "aiya."** That is the entire answer to "who owns them," and "aiya" is a proper noun this document never defines — it appears first on line 41 ("What aiya adds"), then line 27, and is clearly the name of the system, but as an *owner of criteria* it is an abstraction, not a party. If I want to change a criterion, I do not know who or what I go to. The doc tells me who *doesn't* own them (the Conductor) far more clearly than who does.

What I had to assemble myself: the four viewpoints only make sense if I already know the item format from line 67 ("three lines, optionally four... product / consumes / done when / viewpoints"). Criterion 1 says "every item carries its three lines" — so the optional fourth is not checked. Fine, but I had to hold line 67 open while reading line 69. Then criterion 4 depends on "the phase yardstick," a term used on lines 27, 31, 33, 69, 73, 79 and never defined here (chapter 2, presumably). Then line 71 adds a *fifth* obligation — "re-running the four fixed viewpoints on every revision" — which is a rule about the criteria, not a criterion, and sits under a different bold heading. Then line 73 tells me the breach traces.

So the full answer to (d) is spread over lines 67, 69, 71, 73 — four separate paragraphs under three bold leads. That is a read-through, not a lookup.

### (e) Why was a controller program rejected, and what would reverse that decision? — **FOUND, and it is the clearest reversal condition in the doc**

Line 107, §7: "**A controller program.** It retires the compliance bet, and it fixes the ceiling wherever understanding happened to stand on the day somebody wrote it (§2). Whether prose alone can carry the cycle, the attempt ceiling, and the gates gets settled in dogfooding. If it cannot, the loop moves into code and nothing else does — formats, chain, and measures cross over unchanged."

Two reasons, one reversal condition (dogfooding falsifies "prose alone can carry it"), and a stated blast radius for the reversal. Good entry.

What I had to guess: "**the compliance bet**" is used as a defined term and is not defined here. §7 line 117 gives me the nearest thing — "the bet is that a model following prose is enough (§1.4)" — so I reconstructed it, but from a different section, 10 lines later, under "Costs paid" rather than in the entry that uses the term. Also "it *retires* the compliance bet" reads as a *benefit* of a controller program, listed under "reason for rejection." I read that sentence three times. I think it means: yes, it would retire the bet, but the price is the frozen ceiling. The word "and" between the two clauses hides that concession/objection structure completely.

---

## 3. Every stumble

**1.** Line 3: "Vocabulary is chapter 2's and is not repeated."
Expected: a reference I can enter at any point. Got: an explicit declaration that entries are not self-contained. Every subsequent §-reference is a consequence of this one sentence. For a document whose stated job is "Find the entry you need," this is the wrong policy.

**2.** Line 7: "Every entry states a promise and the trace a breach leaves behind."
Expected: a breach trace in each of §5.1–5.7. Got: explicit breach traces in only §5.5 ("a commit no record dispatch produced stands out in the history"), §5.6 ("Breach traces: ..."), and §5.7 ("the tell is the Conductor citing content that no return delivered"). §5.2 has none. §5.3 has an implicit one at best. §5.4 has "A CCS that overclaims will not last" which I *think* is the trace but is not labeled. The document's own promise about its shape is broken.

**3.** Line 17: "Where a definition carries Bash an indirect escape remains, so rule 2 is a traceable default there instead of a block."
Expected: rule 2 ("Is the Conductor's direct child. It dispatches nothing itself.") to be structural, as the same sentence's opening said — "Rules 1 and 2 are structural." Got: rule 2 is structural *except* where it isn't, in the same sentence. Which definitions carry Bash? Not stated. So I cannot tell for any given Turn whether rule 2 is a guarantee or a hope.

**4.** Line 17: "the evidence would be the nested session's own transcript, which no small return will ever mention."
Expected: a breach trace I could look for. Got: a breach trace that is explicitly unobservable through the normal channel. This is honest, and it is also a hole — it means rule 2's violation is undetectable in practice, and the doc does not say so plainly.

**5.** Line 19: "**The invariant is this contract, not how many definitions exist.**"
Expected, after "five rules that never vary": that the five rules are the invariant. Got: a paragraph re-framing the invariant that mostly restates rules 1–5 in other words ("dispatching is the Conductor's alone" = rule 2; "an author reads what it writes" = a §5.7 rule appearing here first). Reworded repetition.

**6.** Line 19: "The single change on the Conductor's side is one more entry in the backend roster it checks at `on`."
Expected: a continuation of the "new role" discussion. Got: a jump to *backends*, which is §5.5's subject, not §5.1's. "backend roster" is used once, here, and never explained.

**7.** Line 25: "with Turn(brief) as its only reader, so nothing first-person ever crosses the wall."
Expected: "the wall" defined before use. Got: first use of "the wall," defined 58 lines later at line 83 ("This wall admits no physical form"), and even there only by description. Held open the whole read.

**8.** Line 27: "`v1` for a first draft, read-then-increment on a rework. No other party writes a version anywhere in aiya."
Then line 58: "whose version stamp came from generate and never from record."
Expected: one statement of the rule. Got: the same rule twice, 31 lines apart, in different words. Not harmful — but it is the doc restating rather than cross-referencing, which is what it forbids elsewhere by implication.

**9.** Line 33: "which is what makes a ruling convenient to the Conductor impossible to invent after the fact."
Expected: parseable English. Got: a sentence I re-read three times. "a ruling convenient to the Conductor" is a noun phrase with a postposed modifier and no comma, so it first parses as "makes a ruling convenient." This is the single worst sentence in the document.

**10.** Line 33: "the dispatch identifiers."
Expected: definition. Got: none. It is one of exactly four things a verifier dispatch may name, so it is load-bearing, and I do not know what it is.

**11.** Line 35: "At the chain's head, `evidential-soundness` stands in for a document."
Expected: what that is. Got: a bare identifier, in code font, never defined. Also "the chain's head" — which chain? The CCS chain (line 97) or the yardstick chain? Guessed the latter.

**12.** Line 37: "Whatever can be run gets run first, with the model as a thin layer over the top."
Expected: after two paragraphs of hard rules, a mechanism. Got: a principle with no way to check it. Who decides what "can be run"? Not stated.

**13.** Line 41 vs line 49: "nine YAML components" ... "the component that pushed past it is itself the diagnosis."
Expected: the nine components, in a reference. Got: a count and no list, plus an operating rule that requires the list to use. Deferred to "the Turn definition," which is not here.

**14.** Line 41: an arXiv citation with a URL and a 2026 date, inline in a reference entry.
Expected: an operating fact. Got: attribution. Repeated again at line 113 ("The schema is Bousetouane's (§5.4)"). Twice-cited provenance is not lookup content.

**15.** Line 47: "Brief judges facts alone, and never direction."
Expected: this bullet to be about "One per wave, never split," which is what its own bold lead says. Got: a second, unrelated rule bolted onto the end of the bullet. Misfiled.

**16.** Line 49: "a **soft ceiling** of 2,000 bytes" ... "Small and sub-linear, **not fixed in size**."
Expected: one clear statement of the bound. Got: a number and then a denial that there is a fixed number, in the same paragraph. Resolvable (soft = advisory), but it cost me a re-read on the single most quotable figure in the document.

**17.** Line 53: "five dispatch points, each of which is serial by construction."
Expected: what "serial by construction" buys me. Got: a claim used nowhere afterward. Line 63's idempotence argument does not depend on it; §7 line 124's "Gates are serial" is about humans, not this.

**18.** Line 58: "A bare-`gm` send-back has it fetch the review comments to a file and hand back the path."
Expected: `gm` explained. Got: a bare command token, appearing here and again at line 123, never defined. Same for `on`, `dn`, `up`, `/clear`, `G1`, `G3`. Six-plus command/gate identifiers used as if known.

**19.** Line 61: "*(proposed, along with the run-state file)*" and line 77: "*(proposed)*."
Expected: a reference states what is. Got: two inline hedges with no convention explained. I do not know whether to build against these lines or not.

**20.** Line 63: "The **local adapter** runs no git whatsoever."
Expected, given lines 53–60 were written entirely in git verbs ("Create the run branch, push," "Commits... then pushes," "pushes last"): the five points restated in local terms. Got: "keeping the same five points and the same return," and nothing about what four of the five points *do* under local. Only the fifth (the gate ruling → `history/`) is described. This is the gap that broke lookup (c).

**21.** Line 67: "An item is three lines, optionally four."
Expected: consistency. Got: line 69 criterion 1, "every item carries its three lines," and line 65's heading "three lines an item, and how it may change." Three phrasings of the count in five lines, one of which contradicts the other two unless you notice "optionally."

**22.** Line 69: "four viewpoints aiya fixes rather than the Conductor."
Expected: a named owner I could act on. Got: the system name as an owner. See (d).

**23.** Line 71: "each of them restarts its attempt count."
Expected: "attempt count" / "attempt ceiling" defined somewhere. Got: used here, at line 92 ("Steps that hit the attempt ceiling"), at line 97 ("Attempt numbers ride on the rulings"), at line 99 ("smaller Steps rather than more attempts"), and at line 107. Five uses, no number, no definition. For an operator this is a tuning knob I cannot find the value of.

**24.** Line 77: "ANDs the rulings together and computes waves."
Expected: plain description. Got: "ANDs" as a verb, and "computes waves" with no statement of the input. Wave computation is presumably from `consumes` (line 67, line 120) but that is my inference.

**25.** Line 79 "Never." list vs line 83.
"Never: ... Opening the real work, Report contents included."
Then line 83: what may enter includes "the elicit exchange it writes under `research/`."
Expected: consistency. Got: the Conductor never opens real work, but does write a research file. I assume elicit output is not "real work." Guessed.

**26.** Line 81: "**A doubt becomes a Step** (§4.3). The rule exists for the moment when checking directly looks faster than delegating."
Expected: the rule. Got: the rule's *motivation* and a pointer. The rule itself is not on this page.

**27.** Line 83: "This wall admits no physical form: the Conductor's whole state is files, so nothing can remove its ability to read."
Expected: after §5.1 line 17 established that rules 1–2 *are* physically enforced, an explanation of why this one cannot be. Got: an assertion, then line 117 in §7 proposing exactly a physical form ("a hook refusing the Conductor's reads by path"). Line 83 says no physical form is possible; line 117 names one. Direct contradiction unless "admits no physical form" means "none is currently used" — which is not what it says.

**28.** Line 87: "Each Step buys N verifiers."
Expected: N defined. Got: N introduced here and reused at line 118, never bound. From §5.3 line 31, N = number of viewpoints. Reconstructed.

**29.** Line 91, the table: "**Keep rate** | Steps ÷ Turn(generate)s. Work that passes first time scores 100%."
Expected: a rate. Got: a ratio that is only a "keep rate" if you read it backwards — Steps over generates means *fewer generates is better*, so this is a pass-first-time rate. The name says "keep," the formula says "reciprocal of attempts." The gloss sentence is doing all the work. This is the figure-disagrees-with-prose case.

**30.** Line 93: "**Verification overhead** | (Turn(verify)s + Turn(brief)s + Turn(record)s) ÷ Turn(generate)s."
Then line 95: "Record is inside the overhead on purpose."
Expected: the table to be self-explaining. Got: a defense of the formula in prose immediately after, which tells me the formula is contentious and the table alone will be misread.

**31.** Line 99: "below a 50% keep rate the loop spends more than it saves."
Expected: given line 91's definition, a check that 50% is achievable. Steps ÷ generates = 50% means two generates per Step. Fine — but "an opening heuristic, meant for tuning by use rather than treatment as a measured rule" is a 20-word hedge on a one-number threshold. The hedge is longer than the fact.

**32.** Line 101: "§1.4 answers for the two properties."
Expected: the two properties named. Got: "the two properties," definite article, never named in this file. §1.4 is cited four times (lines 7, 101, 117, and by implication) and I never learn what it says.

**33.** Line 107: "It retires the compliance bet, and it fixes the ceiling."
Expected: two reasons for rejection. Got: one benefit and one cost joined by "and," presented as a list of reasons against. See (e). Also "the compliance bet" undefined until line 117.

**34.** Line 109: "Roles stop at the three families."
Expected: three. Got: §5.2–5.5 define **four** Turn types — generate, verify, brief, record. Either record is not a "family," or this is wrong. Line 109 then immediately says "a new backend adds one record adapter," treating record as the exception — so I *think* the three families are generate/verify/brief and record is something else. But §5.1 line 14 lists four return shapes as one contract, and §5.5's heading is "Turn(record)." **This is a figure that disagrees with the prose, and I could not resolve it.**

**35.** Line 111: "Products drafted by the Conductor. An author reads, and the no-reading wall convinces only while the Conductor has no reason to read."
Expected: something not already said. Got: the third statement of "an author reads" (line 19, line 79, here). Reworded repetition across three sections.

**36.** Line 112: "Two roles are the real requirement: somewhere durable to keep things, and somewhere the human reads them."
Expected: this in §5.5, where the adapters are defined. Got: it in §7, under rejections. The clearest statement of *why there are three adapters* is filed under "what was rejected."

**37.** Line 123: "approved editions survive in `history/`, machine loss and intermediate drafts do not."
Expected: consistency with line 63. Line 63 says the local adapter's "**single write**" files the approved edition into `history/`." Line 56 says wave settle "Commits the wave's products, rulings, Reports, the new CCS, the standing Plan, and the run-state file." So under local, do wave settles write anything? Line 63 says one write; line 53 says the local adapter keeps "the same five points." Five points, one write. I cannot reconcile these and it is the same hole as stumble 20.

**38.** Line 124: "Six points still need one human, one at a time."
Expected: the six gates named, or a pointer. Got: a count. The doc names G1 (line 33) and G3 (line 58) and "Planning Gate" (lines 57, 61) and never enumerates. Third undefined-count case after "nine components" and "three families."

---

## 4. Content I did not need

**§5.1's second paragraph, lines 17 and 19** (~180 words on structural-vs-traceable enforcement and "the invariant is the contract"). Serves a designer defending the architecture, or a reviewer asking "is this actually enforced." An operator looking up rule 4 stops reading at line 15.

**§5.4's citation apparatus, line 41** — author, title, arXiv link, year — plus its restatement at line 113. Serves a reader auditing originality. Nothing in my five lookups touches it, and it sits *between* the CCS definition and the operating rules, so I read past it to get to the rules.

**§5.4's justifications inside each bullet** — "which is why brief writes it and generate does not," "so the carried state includes the judgment," "because the next measurement reads the artifacts and never the CCS," "but a state pieced together from partial views has lost the very thing that made it a state." Every one of the five operating rules carries its own defense inline. Serves a design reviewer. For lookup (b) it roughly doubled the reading to reach the number on line 49.

**§6 entirely, lines 85–101.** No lookup needed it. Serves someone deciding whether to *adopt* the system, or reporting on a completed run — not someone operating it. And within §6, line 101 ("These three measure the loop's efficiency, not a human's productivity") is a disclaimer aimed at an organizational objection, not at any reader of the table.

**§7's "Costs paid," lines 115–124.** Ten bullets. Serves a decision-maker or a critic ("read as chosen rather than missed" says so outright). Two of them contain operating facts filed in the wrong place — line 117's definition of the compliance bet, and line 123's local-mode durability limits, which belong in §5.5.

**§5.3's last paragraph, line 37.** Advice on Step sizing. Serves a Plan author, not a verifier operator.

**§5.7's "A doubt becomes a Step," line 81.** Two sentences that give motivation and defer the rule. Serves nobody as written — the person who needs the rule has to leave.

---

## 5. What I needed and is not here

Terms used as if defined, that this file never defines:

- **"the phase yardstick" / "yardstick document"** — six uses (27, 31, 33, 69, 73, 79). It is the thing verifiers measure against and the thing Plan criterion 4 checks. Nothing here says what it is.
- **"Step," "wave," "round," "phase"** — the four scheduling units, all load-bearing, all assumed.
- **"the two properties" (line 101)** and **§1.4's "qualifier" (line 7)** — cited three times as the thing the whole design answers for.
- **"the discretion line" (§4.3, line 71)** — one of exactly three things that make a Plan revision safe, and it is a pointer.
- **§4.4's invalidation rule** — cited at lines 27, 33, 57 as "the hook" that editions reach for. Never stated.
- **"the compliance bet"** — used at line 107, glossed only at line 117.
- **"the attempt ceiling" / attempt count** — five uses, no number.
- **The nine CCS components** — counted, never listed, but required to use the ceiling diagnostic.
- **The six gates** — counted at line 124, two named in passing (G1, G3), never enumerated.
- **`evidential-soundness`** (line 35) — a named default, undefined.
- **"the dispatch identifiers"** (line 33) — one of four permitted dispatch contents, undefined.
- **`on`, `dn`, `up`, `gm`, `/clear`** — five commands used as anchors for dispatch timing, none defined.
- **"backend roster"** (line 19), **"work order"** (lines 11, 77, 110) — the work order is what a Turn receives and the only thing that gets in; its contents are never stated.
- **"three families"** (line 109) vs four Turn sections — unresolved.
- **Local adapter behavior at four of its five dispatch points** — the direct cause of my failure on lookup (c).
- **Turn(generate)'s breach trace** — promised by line 7, absent.

---

## 6. Effort score

**4 out of 5.**

Not 5, because §5.1 and §5.5 are genuinely well-built entries and two lookups landed fast. Not 3, because two of five lookups failed to complete and I ended up reading roughly the whole document to answer questions that should each have been one entry — which is the definition of a reference that does not work as a reference.

**The one change that would most reduce it: make every entry answer without leaving the page. Concretely — inline the terms rather than deferring them.** Every `(§x.y)` in this file marks a place where a lookup dies. There are twelve of them, and at least five sit on the critical path of a question an operator will actually ask: the discretion line (§4.3), the invalidation hook (§4.4), the two properties (§1.4), the ceiling rationale (§2), the re-send safety argument (§4.1). Either state the one sentence the entry needs, or accept that this document is chapter 5–7 of a book and not a reference at all.

If I could have a second change: **give §5.5 a local-adapter column.** The five dispatch points are written entirely in git verbs, then one sentence says local uses "the same five points" and describes only one of them. That single omission is the whole reason lookup (c) came back incomplete.
