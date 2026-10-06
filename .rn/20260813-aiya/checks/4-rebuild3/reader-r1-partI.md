# Reader trial — round 1, Part I (the mandated comparable prompt, whole document)

Fresh subagent, given only `doc-K.md` (a neutral-named copy of the whole document) and the run
brief's verbatim reader prompt. Verbatim and unedited.

---

# Report — doc-K.md, read cold

## 1. The decision

**QUALIFIED.** The yardstick chain largely discharges drift detection. The CCS discharges a *narrower* property than the one chapter 1 states, and chapter 1's own proof table asserts something two later sections contradict.

**What holds.**

- Drift leg 1 (the chain) is real: freezing yardsticks at gates and deriving Plans as the only mutable joint does turn "a Step nothing justifies" into a checkable object rather than a mood.
- Drift leg 2 (independent verification) has actual structural support, not just prose: the Report is withheld from the verifier, the expected answer is withheld, the ruling is written to disk *before* it returns, and the ruling names the edition it judged so a new version voids prior measurements by search (§4.4, §5.3). That is the strongest engineering in the document.
- The CCS genuinely bounds what carries *across* waves and across sessions. Replaced-not-appended, third-person, written after the ruling, artifact-wins — those four rules are well-chosen and §7 explains convincingly why replay and retrieval were rejected.

**What does not hold, and qualifies the YES.**

1. **§1.4's third bounded-context leg is false as written, and it is the leg the section says makes the property sub-linear.** The table asserts "ten Steps in flight cost the Conductor the same read as one." But §4.1 has the Conductor aggregating one Verdict per viewpoint per Step, §5.7 admits "small rulings" onto the entry list, and §5.4 states outright "Small and sub-linear, not fixed in size." Within a wave, the Conductor's intake is N Steps x V viewpoints of rulings — linear in wave width. Only the carry-forward is O(1). The document never says which of the two the property is about, and its headline proof picks the one that is not true.

2. **The property is narrowed 250 lines after it is stated.** §1.2 names the failure as "whichever agent is directing piles up state in proportion to the size of the job... each extra stream adds to what that agent has to hold, old failures resurface inside it." §4.5 concedes "The Conductor's transcript still lengthens with every Turn dispatched" and defends itself with "§1.4's property was never stated about it." True of §1.3's *wording*; false against §1.2's *failure*, which is the thing the mechanism was introduced to fix. The actual remedy is `dn` -> `/clear` -> `up` — a human typing three commands, in a design whose whole premise is a person who does not sit and watch. That is an operator procedure, not a mechanism.

3. **Nothing measures the CCS, and the document's answer to that is a non-sequitur.** §3.2's ledger names a *rule* where every other row names a party, then says "An unsupported line is caught at the next measurement, which reads artifacts and not the CCS." A measurement that does not read the CCS cannot catch anything in the CCS. What it establishes is that a bad CCS line does not corrupt a *verdict* — fine — but §4.3 has the Conductor steering entirely off the CCS. So a distortion introduced by Turn(brief) reaches steering undetected, and steering is where drift's second shape ("the plan finished while everything learned is ignored") is supposed to be caught. The single unverified party sits directly on the drift-detection path.

4. **Drift leg 3 has no trace, contrary to §1.4's blanket claim.** "Every one of the six is a default that leaves a trace." I went looking in §5.6 for the trace that distinguishes a Plan *re-derived from zero* from a Plan *edited*. There is none — the traces listed catch bad format, lying `consumes`, unlogged revisions, and unapproved editions, and both behaviors produce an identical diff plus an identical change-record entry. Leg 3 is unfalsifiable in practice.

5. **The mechanism answering property 1 is not specified in this document.** The CCS is "nine YAML components" from a cited 2026 paper, and the components "travel with the Turn definition." I am asked to judge whether the CCS discharges bounded context and I am never shown what is in it. The 2,000-byte figure is explicitly a *soft* ceiling whose overrun is "a symptom to report rather than a budget to raise" — a norm, not a bound.

6. **Everything above rests on an admitted, untested wager** (§1.4 "Nothing stops a breach"; §7 "the bet is that a model following prose is enough"). The document is honest about this and §7 even names the fallback (a path-refusing hook). But "discharge" cannot be answered YES on a bet the document says is unsettled.

I read Part II — §5.1, §5.3, §5.4, §5.6, §5.7, §6, §7 — to reach this. I would not have gotten there from Part I alone, because points 1, 3 and 4 all resolve only against chapter 5.

## 2. Headings-only pass

**What I predicted from headings alone:** delegation to agents fails in two ways -> therefore two properties are required -> two mechanisms with six supporting legs answer them -> here are the roles, the structure, and the loop -> then a reference section. That much came through, and the Part I/Part II split with its stated audiences was the clearest structural signal in the document.

**Where the thread broke:**

- **The headings never name the two mechanisms.** §1.4 reads "The answer — two mechanisms, six legs." I could not learn from the headings what the mechanisms *are*. The two nouns the entire document exists to justify — CCS and the yardstick chain — appear in no heading in Part I.
- **Chapters 2–4's headings describe the system, not the argument.** "Two roles, and no third", "The chain", "The ledger", "A Step", "A wave" — none of them says which property it is discharging. From headings alone, Part I looks like it turns from an argument into a system description at chapter 2 and never comes back. The argument thread stops dead at §1.4.
- **"Behavior — The loop, at three scales" is followed by five subsections.** I spent a moment deciding which three were the scales (Step, wave, and... steering? gates?). The count in the heading does not match the headings under it.
- **One heading did real work:** "4.5 Suspend and resume, **and what stays unbounded**." That clause is the only heading in the document that flags a concession, and it turned out to be the most decision-relevant heading in Part I. More of the argument should be visible at that level.

## 3. Every stumble, in reading order

1. **§1.1** — "The target is a tenfold jump in what a single expert delivers... Proving the tenfold figure is out of scope." Expected the goal section to set up the two properties. Got a headline number that is disowned in the next sentence. Held open the whole read: why is it in the document at all, if nothing later uses it?
2. **§1.3** — "Those streams are waves (§4.2)." The central property is stated in terms of a noun defined three chapters later. I held "wave" as an unknown through all of §1.4 and §2.
3. **§1.4, leg-2 cell** — "puts a soft ceiling of 2,000 bytes on the file and treats an overrun as a symptom to report rather than a budget to raise." Re-read twice. Expected a bound on "the amount"; got a norm that explicitly permits overrun. A table cell is also the wrong place for a full policy clause.
4. **§1.4, leg-3 cell** — "ten Steps in flight cost the Conductor the same read as one." Expected this to be the proof. It is contradicted by §4.1 and flatly by §5.4. This one stumble caused every jump I made into Part II.
5. **§1.4** — "**What qualifies all six legs.** Nothing supervises them... Nothing stops a breach." Re-read the whole section to work out whether this voids the two tables I had just been given. Expected an answer section to answer; got the answer and a retraction of its force in the same section, with the retraction in bold.
6. **§1.4** — "checked in `agents/turn-generate.md`, `agents/turn-verify.md`, `agents/turn-brief.md`." I am the first-time reader this chapter names as its audience; I have no repository. Unverifiable, had to take on faith.
7. **§2, "Vocabulary, fixed here"** — arrives *after* §1.4 has already used Conductor, Turn, CCS, wave, Step, Plan, gate, yardstick and viewpoint in load-bearing sentences. Right chapter, wrong order relative to first use.
8. **§2 onward, the counting** — six legs, six halts, six skills, five command words, five Turn rules, five dispatch points, three phases, three backends, three families, three ratios, three questions, four viewpoints, four preconditions, four resume items, nine YAML components. By chapter 4 the numbers stopped orienting me and started colliding; three different "six"s land within two chapters. Guessing at which six was which cost me time on every back-reference.
9. **§2, "The bet"** — "Judgment, steering, and **the last layer** of measurement all sit with the model." What are the earlier layers? Held open until §5.3 ("Whatever can be run gets run first, with the model as a thin layer over the top"). Three chapters to resolve a phrase that needed four words in place.
10. **§3.2, CCS row** — "Measured by (machine): The compression rules of §5.4." Every other row names a party; this one names a document section. Re-read the row twice to confirm that the answer is "nobody."
11. **§3.2, CCS row** — "An unsupported line is caught at the next measurement, which reads artifacts and not the CCS." Read three times, and again when §5.4 repeats it verbatim in spirit. As written, the sentence explains why the CCS is *not* checked while sounding like a guarantee that it is. This is the most misleading sentence in the document.
12. **§3.3 and after** — "**Run-state** *(proposed)*". A component that does not exist is threaded through §3.2, §3.3, §4.4, §4.5, §5.5 and §5.7, re-flagged each time. Six separate places where I had to suspend belief and remember which half of the sentence was real.
13. **§3.3** — "What ships today instead is a one-line `backend` file (`skills/conductor/SKILL.md:26`)". Second unverifiable repo citation, this time to a line number.
14. **§3.4** — "**Six skills.** Five are typed entry points for the command words." Jumped back to §2 to count the command words (`ty`, `gm`, `on`, `dn`, `up` — five) and confirm the arithmetic the document leaves implicit.
15. **§4.1 / §3.2 / §5.2** — establishing who reads a Report took three sections. §2 says the Conductor may not see it, §3.2 says brief holds it against the artifact, §5.2 says brief is its "only reader." Consistent, but assembled by me rather than stated once.
16. **§4.2** — "No file describes a wave: it is computed from the Plan's `consumes` lines every time." Jumped back to §1.3 to check whether a property stated about "work streams... those streams are waves" still parses when a wave is not a persistent object. It does, barely.
17. **§4.3** — "derived from zero out of the present position, never by editing the standing Plan." §1.4 promised every leg leaves a trace, so I jumped to §5.6 to find this one's. Found four traces, none of which distinguishes re-derivation from editing. Concluded by guessing that no trace exists.
18. **§4.4 vs §3.3** — "Numbers are given to the outputs alone," i.e. the three Planning Gates are unnamed. But §3.3's `state.yaml` sample contains `{gate: purpose-planning, verdict: ty}`. They are named. Direct contradiction between an example and a rule.
19. **§4.4** — "**Four things must already exist before anything can be generated**: the run's Purpose and its Plan, and the product's UX and Design documents." Read four times. The Purpose is generated by a Turn (§3.2, §4.4's own table). So the Purpose must exist before generation, and is produced by generation. I assume "anything" silently means "anything in Approach or Delivery," but the sentence sits in a section covering all three phases and never says so.
20. **§4.5** — "**Bounded means the working state, and nothing else.** The Conductor's transcript still lengthens with every Turn dispatched... §1.4's property was never stated about it." Went back and re-read §1.2 and §1.3 in full to judge whether this is disclosure or redefinition. Verdict: honest against §1.3's letter, not against §1.2's stated failure. This is the single most important paragraph for my decision and it is 250 lines from the claim it qualifies.
21. **§5.1, rule 2** — "Where a definition carries Bash an indirect escape remains... the evidence would be the nested session's own transcript, which no small return will ever mention." So the trace is unreachable by anyone in the loop. A trace nobody can read is not a trace; the sentence concedes this and then hides the concession in its own trailing clause.
22. **§5.4** — "Small and sub-linear, **not fixed in size**." Straight contradiction of §1.4's "the same read as one." Two sentences that cannot both be true, 300 lines apart, with the false one doing the argumentative work.
23. **§5.4** — "Its schema — nine YAML components — comes from Bousetouane... Schema, component roles, ceiling, and worked example travel with the Turn definition." The mechanism I am asked to evaluate is never specified here. I cannot check nine components I am not shown, from a paper I cannot open.
24. **§6** — "below a 50% keep rate the loop spends more than it saves." Same shape as stumble 1: a specific number, immediately hedged as "an opening heuristic, meant for tuning by use." Two unfounded figures bookend the document.
25. **§7** — "Falsified in dogfooding, the first hardening to try is a hook refusing the Conductor's reads by path — after the measurement, not ahead of it." Not confusing, but this is the answer to the objection §1.4 raises about itself, and it lands 350 lines later. I had held that question open since chapter 1.

## 4. Content I did not need

- **§1.1's tenfold claim.** Serves a sponsor or a pitch reader. It funds nothing in the argument.
- **§3.3's directory tree and the `state.yaml` block.** Serves an implementer. The *fact* that persistence has two jobs and three backends mattered; the file layout did not.
- **§3.4 "What ships."** Packaging detail for an implementer.
- **§4.4's console mechanics** — `gm <one line>` versus bare `gm`, review-comment fetching. Serves the human operator at a gate.
- **§4.5's resume mechanics** beyond the final concession paragraph. Operator.
- **§5.5 in full.** Five dispatch points, adapters, idempotence — operator and implementer. Nothing here touches either property.
- **§5.6's item format** (`product` / `consumes` / `done when` / `viewpoints` semantics). Plan author. The *four fixed viewpoints* mattered; the line format did not.
- **§6 entirely.** It says so itself: "These ratios answer a separate question." Serves whoever is tuning the loop's cost.
- **Roughly half of §2's vocabulary list** — `Phase`, `Work order`, `Elicit item`, the command words. Needed to read Part II, not to judge Part I.
- **Two of the four mermaid diagrams.** The §2 role diagram restates the paragraph directly above it with no addition. The §4.4 phase diagram restates the table directly above it with no addition. The §4.1 and §4.2 diagrams did earn their space — the attempt-ceiling branch and the many-to-one convergence are genuinely clearer drawn.

## 5. Effort score

**4 out of 5.** Not because the prose is bad — it is dense and largely well-made — but because the load-bearing claim in §1.4 is contradicted twice in later chapters, so I could not trust chapter 1 and had to verify each leg against Part II. That is exactly the reading stance chapter 1 says it does not require.

**The one change:** rewrite §1.4's third bounded-context leg to state the real shape of the Conductor's intake — one CCS carried across waves regardless of width, plus rulings that scale with Steps x viewpoints *within* a wave, plus a transcript that grows per Turn and is cleared by hand at `dn` -> `/clear` -> `up`. Say it once, there, in the table that claims to be the proof. That kills stumbles 4, 20 and 22, removes the need to read §4.5 and §5.4 defensively, and lets a first-time reader decide from Part I as intended. The document already knows all three facts; it just does not say them where the claim is made.

## 6. The path I actually took

1. Headings-only pass over the whole file (grep of `#` lines), wrote down the predicted argument.
2. §1 through §2 and into §3.1, straight through.
3. Re-read §1.4's two tables after the "**What qualifies all six legs**" paragraph, to decide whether the tables still stood.
4. §3.1 through §4.5, straight through.
5. Back to §1.3 from §4.2, to check the "waves" definition against the property.
6. Back to §1.2 and §1.3 from §4.5, to judge the "bounded means the working state" concession. Re-read both in full.
7. Jumped out of Part I into Part II — §5.1, §5.3, §5.4, §5.6, §5.7 — driven by stumbles 4, 17 and 11: I needed to know what the Conductor is actually allowed to take in, and whether leg 3 has a trace.
8. Read §6 and §7 to see whether the enforcement gap and the cost model were priced. §7 answered the question I had held open since §1.4.
9. Back to §3.3's `state.yaml` sample from §4.4, to check the gate-naming contradiction (stumble 18).
10. Re-read §3.2's CCS row a third time after §5.4, to confirm that nothing measures the CCS.
