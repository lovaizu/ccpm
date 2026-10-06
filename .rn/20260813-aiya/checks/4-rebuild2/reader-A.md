# Reader trial — doc-A (current `aiya/docs/design.md`, 6,487 words), report 1 of 2

Verbatim report from a fresh-context subagent given only `doc-A.md` under a neutral filename and the
prompt in `trials.md` §The prompt. It could not read any other file and did not know a second
document existed.

> **Note on two reports.** The doc-A trial returned two complete reports (see `trials.md` §Anomaly).
> Both are recorded. This is report 1.

---

## 1. The decision

**QUALIFIED — the mechanisms are sound in shape, and the document does not establish that they discharge the properties.**

The two properties (§1): the director's context must stay bounded as work grows; divergence must be caught while it is happening. The two mechanisms: the CCS (a written compression that carries state between waves) and the two-layer traceability chain (fixed yardsticks above, a Plan re-derived from them below).

**Where the argument holds.** Bounded context has a real structural spine. Every Turn starts from an empty context and returns a bounded artifact (§5.1) — so nothing accumulates inside the workers. The Conductor's per-wave input is one CCS plus the Plan, and the CCS is a fresh file each wave that carries paths rather than contents (§4.2). That is a genuine constant-shape input, and §4.6's claim that it does not grow with the number of Steps in flight follows from it. The chain's shape is likewise coherent: yardsticks are versioned and frozen, the Plan is disposable and rebuilt from zero each wave (§4.3), verification is done by a party that did not do the work and is aimed only at the frozen yardstick (§5.3), so an unbacked claim in a Report cannot silently pass.

**Where it does not.** Four load-bearing gaps, in descending order of weight:

1. **The Conductor's context is not the same object as "the Conductor's input per wave."** §4.5 concedes the transcript "still grows linearly with the number of Turns dispatched," and hands the remedy to a human typing `dn` → `/clear` → `up`. §1 asked for context that stays bounded *as the work grows*; §4.6 discharges a narrower claim (per-wave input shape) and does not reconcile the two. The document never says how many waves a run survives before the human must intervene, so the property is unbounded in the dimension that matters.
2. **Drift detection is stated as a *derivation* property but no mechanism performs the derivation check.** §3.1: "a Step that cannot be derived from the Plan, or a Plan that cannot be derived from the documents above it, is drift, and it is visible on the page." Visible to whom? The Conductor may not read products (§2, §5.7); the verifier is aimed at one Step against a yardstick (§5.3); Turn(brief) summarizes. No role compares the Plan against the yardsticks and reports non-derivability. §4.6 admits it: "no mechanism enforces re-planning." The re-plan-from-zero rule (§4.3) is a *default*, and the document says so.
3. **The verifier's aim is chosen by the party whose drift it is meant to catch.** The Conductor writes the work order that fixes which yardstick criteria a verifier is pointed at (§4.1, §5.3). If the Conductor's Plan has drifted, it will aim verification at the drifted criteria and every Verdict will come back green. §5.4 hardens verify against persuasion by the maker; nothing hardens it against omission by the director.
4. **The CCS's bound is asserted, not shown.** §4.2 gives a 2,000-byte "soft cap" that "signals when breached" — a signal, not a cap. The nine components are cited to an external paper (Bousetouane 2026), and the schema itself is not in the document. §4.6 says "sub-linear"; the document offers no argument for sub-linearity beyond "paths not contents," which bounds each entry, not their number.

**What would change the verdict to YES:** a named role that performs the derivation check and reports it (gap 2), and a reconciliation of the transcript growth with §1's property (gap 1). Gaps 3 and 4 are weaknesses; 1 and 2 are the ones that decide it.

## 2. Headings-only pass

**Reconstructed argument from headings alone:** big work turns into babysitting → two roles, two walls, one bet → one chain of yardsticks with defined ownership → one loop from Step to run, with gates and suspend/resume → per-part rules → observability → trade-offs. From "4.6 Bounded context and drift detection, discharged" I could see the document intends to close a debt, and from §5.1's "five rules, one invariant" that there is a hard core somewhere.

**Where the thread broke — three places:**

- **The two properties are never named in a heading before §4.6 claims to discharge them.** §1's heading ("Big work turns into babysitting") names the symptom, not the two properties. So the argument's spine — *two properties are owed, here is what pays them* — is invisible until the payment is announced.
- **§2 "Two roles, two walls, one bet"** does not say what the bet is or what it buys. It reads as inventory. I could not tell from the heading whether §2 was foundational or contextual; it turned out to be the load-bearing chapter.
- **§3 and §4 headings describe machinery, not claims.** "One chain of yardsticks, and who owns what" and "One loop, from a Step to the whole run" tell me what is described, not what is asserted. Between §1 (problem) and §4.6 (discharged), no heading advances the argument.

## 3. Stumbles, in reading order

1. **§1, "Delegating it makes two things worse instead."** Two things: context bloat, drift. But the first sentence of §1 sets up "the amount of work outgrows one person" — a *capacity* problem — and the two failures are *delegation* problems. I expected the two properties to be derived from the capacity problem; they are derived from delegation. Minor, but I re-read the paragraph to check I had the right frame.
2. **§1, "the director's context has to stay bounded as the work grows."** "Context" is undefined at this point and stays ambiguous the whole way. It means at least three things later: the transcript (§4.5), the per-wave input (§4.2, §4.6), the working state. This ambiguity is the reason gap 1 exists.
3. **§2, "Everything else is prose."** I expected this to be a statement about implementation; it turned out to be the central architectural fact and the source of every "default, not enforced" caveat later. Its placement — third paragraph of §2, in a list of what ships — buries it.
4. **§2, "The bet."** The heading of the chapter says "one bet," so I stopped to find it. The paragraph says "declarative prose is a viable substrate for orchestration." That is a claim about *feasibility*, not the bet I expected (which would be a claim about *value*). I held the question open: what is the wager's downside? It is answered only in §7.
5. **§2, "the Conductor never reads the work."** Stopped hard. If the Conductor plans, re-plans from zero each wave, and decides when the goal is met, and it never reads any product, then everything it knows comes from Reports and Verdicts. I wrote a note: *this is the crux; the whole design's honesty depends on Reports being trustworthy.* The document does not flag this here — it is presented as a hygiene rule.
6. **§2, "no Turn may spawn another."** The word "structural" appears later (§5.1) for this. Here it is one of two "walls" and I could not tell which of the two walls is enforced and which is convention. Had to hold both open until §5.1.
7. **§3.1, "Yardsticks are versioned; the Plan is disposable."** Clean. But then §3.1's last paragraph: "a Step that cannot be derived from the Plan … is drift, and it is visible on the page." **"Visible on the page" is doing enormous work.** Visible to a reader — but the design has no reader. This is the moment I stopped believing drift detection was mechanized, and nothing after recovered it.
8. **§3.2, the ownership table.** Read it three times. It is the densest useful thing in the document, but "Verified by" for the Plan says "the Conductor's own re-derivation," which is the same party that wrote it. Circular. Had to go looking for an external check; there is none.
9. **§3.3, "One directory per run."** Skimmed the tree, then had to come back twice — once to find where Verdicts live (to check whether anything reads them across Steps), once for `state.yaml`. The tree is the only place several load-bearing files are named.
10. **§3.3, `state.yaml` marked "(proposed)".** I could not tell whether the run-state file exists in the design I am evaluating. It is used as fact in §4.4 and §4.5 ("the run-state file records the gate's standing") with no "proposed" qualifier. **I do not know whether resume works as described or is a proposal.** This directly affects §4.5, which I would otherwise credit.
11. **§4.1, "three attempts."** Expected a rationale for three. None given here; §7 says "a number chosen, not derived." Fine, but I stopped to look for it.
12. **§4.2, "one CCS per wave."** The core of the bounded-context claim. The paragraph explains what the CCS holds but the *bound* is a "soft cap of 2,000 bytes" that "signals when breached." I re-read twice: nothing enforces the cap, and a signal presupposes a reader. Same shape as stumble 7.
13. **§4.2, "sub-linear."** Sub-linear in *what*? The number of Steps? Waves? Total work? The document uses the word twice and never states the variable. This is the single most important quantitative claim in the document and it is unquantified.
14. **§4.3, "re-plan from zero."** Strong idea. But: from zero using *what*? The CCS and the yardsticks. So the CCS is now load-bearing for drift detection too, not just bounded context — if the CCS omits a discovery, re-planning from zero reproduces the old plan and the omission is invisible. The document does not address omission anywhere; §5.4 addresses over-claiming. I re-read §5.4 to be sure.
15. **§4.4, six gates.** Counted them against §2's claim of six. §2 says "six stops"; §4.4's table lists Planning and Delivery gates per phase across three phases = 6. Consistent, but §4.4's prose says "three Planning Gates and three Delivery Gates" only after describing them individually, so I counted by hand first.
16. **§4.5, "the transcript still grows linearly."** This is the concession that undoes §1's property, and it is one clause inside a paragraph about suspend/resume — a *housekeeping* section. Expected it in §4.6 where the property is discharged. Jumped forward to §4.6 to see whether it was addressed there. It is not.
17. **§4.6, "discharged."** The section discharges a *narrower* claim than §1 stated (per-wave input shape, not context over the run) and does not say it is narrower. Two backward passes here: to §1 to re-read the property, to §4.5 to re-read the concession.
18. **§4.6, "Each mechanism carries two supports alongside it."** So the two mechanisms are actually six things. This changed the count I had been carrying since §2 ("two roles, two walls, one bet" → two mechanisms → now six legs). Every count in this document is different from the last one, and I lost confidence in the arithmetic.
19. **§4.6, "structural."** §4.6 names fresh contexts and the omitted spawn tool as structural. §5.2 then says Turn(generate) carries Bash. If a Turn has a shell, "no spawn tool" is not structural — it is the absence of a convenience. Contradiction, and it weakens the one part of the design I had credited as genuinely enforced.
20. **§5.1, "five rules, one invariant."** Read this because §2's walls were unresolved. The invariant is that a Turn returns "an artifact of bounded size." Good. But rule 2 ("a Turn does not read the work of another Turn") is then admitted to be enforced only by the work order's contents, and Bash is available. So the wall is a default.
21. **§5.4, the CCS's nine components.** Cited to Bousetouane (2026) with a URL. Not in the document. Since the CCS is the mechanism for property 1, **I cannot evaluate the mechanism without leaving the document.** This is the biggest single blocker to a YES.
22. **§5.7, "The Conductor: does, and never does."** The "never" list includes "read a product." Confirms stumble 5. Also confirms that the derivation check (gap 2) has no home: the Conductor is the only party with the Plan and the yardsticks in view, and it is forbidden from reading what was produced.
23. **§6, the three ratios.** All three measure *cost* (keep rate, escalation rate, verification overhead). None measures whether drift was caught. For a design whose second property is "catch divergence while it happens," there is no observability of the catching. I checked twice for a fourth ratio.

## 4. Content I did not need

- **§3.3's directory tree and backend detection** (`github` / `gitlab` / `local`, `gh` vs `glab`, the `history/` archive). Serves an implementer or an operator, not someone judging whether the mechanisms hold. I needed exactly two facts from it (where Verdicts live, where the CCS lives) and got two pages.
- **§3.4 "What ships"** — the inventory of six skills, six Turn definitions, seven formats. Serves an implementer or a packager.
- **§5.5 Turn(record)** — commit granularity, the three backends' adapters, the five dispatch points. Serves an implementer. Nothing in it bears on either property.
- **§5.6's three-line Plan item format and §5.2's version-line mechanics.** Serve an implementer.
- **§4.4's gate ergonomics** — console output shape, `gm` with and without a line, comment fetching, "aiya never merges." Serves a user of the tool, not an evaluator of it.
- **§7's rejected shapes** — genuinely interesting, and it did answer stumble 4, but it serves a reviewer relitigating the design, not a first-time evaluator.
- **§4.5's suspend/resume mechanics** beyond the one clause about transcript growth. Serves an operator.

Roughly: chapters 3.3–3.4, 5.5–5.6, and most of §7 are reference material for people building or running this, not for the reader the document says it addresses in chapters 1–4.

## 5. Effort score

**4 out of 5.**

Two things drove it. First, **the arithmetic keeps changing** — two roles, two walls, one bet; two properties, two mechanisms; each mechanism with two supports; six legs; five rules, one invariant; three attempts; six gates. Nearly every section opens with a count, and the counts do not compose. I spent real effort maintaining a map that the document reshuffled at each section.

Second, **the load-bearing claims are deferred out of the document** — the CCS schema to a cited paper, the enforcement question to §5.1, the wager's cost to §7, the transcript concession to §4.5. Chapters 1–4 are supposed to let me decide, and three of the four facts that decided it live outside them.

**The one change that would most reduce effort:** state the two properties as named, numbered claims in §1, and give §4.6 a two-column ledger — property, what pays it, what does *not* (transcript growth, no derivation check, unenforced re-planning) — so the discharge is auditable in one place instead of assembled from four sections and a concession buried in a housekeeping paragraph.

## 6. The path I took

1. Headings only, §1 → §7 (as instructed), wrote down the reconstructed argument.
2. §1 straight through.
3. §2 straight through; stopped twice (stumbles 5, 6), noted "walls: which are enforced?" as an open question.
4. §3.1 → §3.2 → §3.3 → §3.4 in order. Re-read §3.2's table three times. Skimmed §3.3's tree, flagged it as reference.
5. §4.1 → §4.2 → §4.3 → §4.4 → §4.5 in order. At §4.5's "transcript still grows linearly," **jumped forward to §4.6** to check whether it was reconciled; it was not; returned to finish §4.5.
6. §4.6 in full. **Jumped back to §1** to re-read the property statement, then **back to §4.5** to re-read the concession. Two backward passes.
7. **Left chapters 1–4** at this point, having reached QUALIFIED but with two blockers I could not resolve from the read-through: the enforcement question and the CCS schema. Went to **§5.1** (walls, invariant), then **§5.2** (Bash — which contradicted §4.6's "structural"), then **§5.4** (CCS schema — not present), then **§5.7** (the Conductor's never-list).
8. **§6** for observability of drift detection; found none.
9. **§7** only to answer stumble 4 (the bet's cost). Did not read it fully.
10. Did not read §5.3, §5.5, §5.6 in full — skimmed to confirm they were implementer material.
