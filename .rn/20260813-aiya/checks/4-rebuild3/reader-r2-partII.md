# Reader trial — round 2, Part II (reference part, chapters 5–7 only)

Fresh subagent, given only `doc-T.md` (a neutral-named copy of Part II after the round-1 fixes) and
the Part II reader definition. Verbatim and unedited.

---

# Report — reading Part II cold, as a lookup user

## 1. The decision

**QUALIFIED — leaning NO for three of the five lookups.**

Three of my five lookups (a, b, e) landed on a single entry that answered them cleanly. Two (c, d) forced me to assemble the answer from two or three separate places, and one of those (c) I had to answer partly by *inference* rather than by reading a statement.

The bigger problem for a reference is different: **the document is written as prose argument, not as lookup entries.** Section 5 headings are titled with editorial hooks ("makes the thing, then says what happened", "the two lists", "three lines an item, and how it may change") rather than with the part name plus the fact it holds. There is no index, no defined-term list, no cross-reference from a concept to the entry that owns it. I found things by scanning, not by looking them up. For a reader who arrives by search, lands, and leaves, that's the whole job half-done.

The "what a breach leaves behind" promise is the document's strongest feature — it is stated per entry, consistently, and it admits its own gaps (5.2 "none", 5.5 "unavailable under local"). That is genuinely good and it is why this is QUALIFIED and not NO.

The killer for *self-containedness* is stated up front and never mitigated: line 5, "Chapter 2 fixes the vocabulary and this part does not repeat it, so an entry may use a term it does not define." That is an announcement that entries are **not** complete on their own. It is honest, and it is also the single thing that most breaks lookup use. See §5 below for the list of terms it cost me.

---

## 2. Per lookup

### (a) What exactly may a Turn hand back to its caller?

**Found — mostly.** §5.1 rule 4 (line 16): "Paths and a line, a ruling, a CCS path, a few lines naming what got committed — no raw output, no transcript."

What I had to reconstruct: that list is four items for a role family of *three* (generate / verify / brief / record — actually four names appear). I had to map each clause onto a role myself by reading §5.2–5.5:
- "Paths and a line" -> generate (§5.2: "hands back the two paths" — note the prose says *two paths*, the rule says "paths and a line". Those are not the same thing and nothing reconciles them).
- "a ruling" -> verify (§5.3 confirms: writes to disk, then "hands back that same text").
- "a CCS path" -> brief (never actually stated in §5.4 — I inferred it. §5.4 describes what brief *writes*, never what it *returns*).
- "a few lines naming what got committed" -> record (§5.5 says adapters share "a small return" but never says what is in it).

So the general answer is in one place; the per-role answer is only complete for verify. For generate it conflicts, for brief and record it is absent from the owning entry.

### (b) What stops the CCS file from growing without bound, and what is the number?

**Found, cleanly, in one place.** §5.4 line 68: three mechanisms — work travels by path and is never pasted; **a ceiling of 2,000 bytes**; the Conductor keeps no rolling summary.

Nothing to reconstruct on the number. One thing worth flagging as an answer-quality issue rather than a findability one: the same sentence retracts the guarantee — "The ceiling is advisory, not enforced — so the honest claim is that the file stays small and grows sub-linearly." So the honest answer to "what stops it" is "nothing stops it; 2,000 bytes is a target." A lookup reader who copies "2,000 bytes" out of the table-of-facts and moves on will be wrong about what it means. The retraction being in the same sentence is what saves this.

### (c) When does the physical-record worker actually run, and what happens if it runs twice?

**Found the "when" — had to reconstruct the "twice" for one of five cases.**

"When": §5.5 lists five dispatch points explicitly (lines 75–81): `on`, every wave settle (after brief), every pre-Planning-Gate Plan push, a gate ruling, `dn`. Clean, enumerated, easy to find. Plus the exception on line 82 — a Planning Gate approval sends *no* record dispatch, and that is marked *(proposed)*.

"Twice": line 84 — "a path already committed stages nothing, and a push with nothing new behind it moves nothing." And for local, line 86 — "A copy already sitting under that name is confirmed rather than rewritten."

What I had to guess: the git-side argument covers commit and push. It does **not** cover the `on` dispatch, which "creates the run branch, opens the pull or merge request." Running *that* twice is not a commit and not a push — creating a branch that exists, or opening a second PR, is exactly the operation the stated argument does not reach. I had to decide for myself whether the doc means "these too are idempotent, obviously" or simply overlooked them. It also doesn't cover the bare-`gm` fetch of review comments. Line 84 says "at this granularity the operations do nothing twice," which asserts the conclusion for all five points while only demonstrating it for two operations.

Also: I had to work out that "the physical-record worker" = Turn(record) from your phrasing, not the document's. The document never uses a word like "physical". Minor, but it's the kind of vocabulary gap that defeats search.

### (d) What are the criteria a Plan is checked against, and who owns them?

**Found — both halves in one paragraph.** §5.6 line 94: four viewpoints, enumerated (all three required lines present; `consumes` reflects real consumption including same-file writes; `done when` can be run; items add up to the phase product exactly, nothing over or missing). Ownership stated in the same sentence: "**aiya** fixes rather than the Conductor — a Conductor authoring the criteria for its own Plan would be approving itself."

What I had to reconstruct: **when** they are checked. Line 96 says they re-run "on every revision," §5.5 mentions "Plan and its check rulings" at Plan push, and §5.6 calls them "the fixed-viewpoint check." Whether the initial draft is also checked I inferred from "re-running... on every revision" implying an original run. Also: "aiya" owns them — aiya is the system's name, which I got only from context (line 29, "No other party writes a version anywhere in aiya"). The document never introduces itself.

### (e) Why was a controller program rejected, and what would reverse that decision?

**Found, cleanly, first bullet of §7** (line 132). Reason against: "code fixes the ceiling wherever understanding happened to stand on the day somebody wrote it." Reason for, acknowledged: it would retire the compliance bet. Reversal condition, explicitly stated: "Whether prose alone can carry the cycle, the attempt ceiling, and the gates gets settled in dogfooding. If it cannot, the loop moves into code and nothing else does."

The best entry in the document. Argument, counter-argument, falsification condition, and blast radius, in four sentences. Nothing guessed.

---

## 3. Every stumble, numbered

**1. Line 5 — the document tells me its entries are incomplete.**
> "Chapter 2 fixes the vocabulary and this part does not repeat it, so an entry may use a term it does not define."

Expected: a reference that stands alone, or at least a pointer per undefined term. Got: a blanket disclaimer and no pointers. I cannot look up "wave", "Step", "gate", "re-aim", "yardstick", "elicit", "discretion line", "G1/G3", "attempt ceiling", "bare-`gm`", "the round" — all used as load-bearing terms here. A single glossary link, or `(ch.2)` after first use, would cost nothing.

**2. Line 9 vs. §5 contents — the count doesn't come out.**
> "Two of the seven leave none and say so."

Expected: seven entries in §5, two of which say "breach trace: none." Got: §5.1–5.7 is seven entries, fine. But 5.2 says "none", and 5.5 says the trace is "unavailable" *under local only* (it exists under git). 5.1's trace exists but "nobody inside the loop ever sees it" — which is arguably also none. So which two? I counted three candidates and gave up. A figure that disagrees with the prose.

**3. Line 19 — "six definitions" arrives with no antecedent.**
> "Four of the six definitions carry Bash: generate, verify, and the two remote record adapters."

Expected: six named things I can count. Got: four of them named. §5 describes generate, verify, brief, and record-as-three-adapters — that's 3 + 3 = 6 if you count adapters separately, and the sentence's own list (generate, verify, github, gitlab) = 4 confirms it. But I had to derive the denominator. Compounding it, §7 line 134 says "Roles stop at the three families" — three families, six definitions, four with Bash, seven entries in §5. Four different counts of what is arguably the same thing, none of them tabulated.

**4. Line 19 — rule 2's status flips inside one paragraph.**
> "Rules 1 and 2 are structural" ... "for those four rule 2 is a norm and not a block."

Expected: a rule is structural or it isn't. Got: structural for two of six definitions, a norm for four. So the headline "five rules that never vary" is false for rule 2 in the majority case. I had to re-read this three times to be sure I wasn't misreading. The heading and the body contradict each other.

**5. Line 16 vs. line 26 — generate's return is described two ways.**
> Rule 4: "Paths and a line"
> §5.2: "hands back the two paths"

Expected: the same fact twice. Got: "paths and a line" vs "the two paths." Is there a line or isn't there? Held open, unresolved.

**6. §5.4 never says what brief returns.**
Rule 4 says someone hands back "a CCS path." §5.4 is the brief entry and describes only what brief *writes*. I had to assign that clause to brief by elimination. The entry that owns the role does not state the role's return.

**7. §5.5 says "a small return" and never says what's in it.**
> "sharing a role, a small return, and five dispatch points"

Expected: what the return is. Got: an adjective. Rule 4's "a few lines naming what got committed" is presumably it — but under the local adapter, which "writes nothing at all," what does it name? Guessed.

**8. Line 39 — "the hook §4.4's invalidation reaches for" is unreadable on first pass.**
> "the ruling names the edition it judged (`purpose.md@G1-v2`) — the hook §4.4's invalidation reaches for."

Expected: a sentence. Got: a noun phrase with a dropped relative pronoun, referring to a mechanism in a section I am not reading. I know a version-stamped ruling can be invalidated when the document changes. I do not know how, and this entry does not tell me.

**9. §5.3's breach trace is a category error.**
> "**Breach trace:** offered a moving state, the verifier refuses by filing a fail whose evidence names the breach"

Expected: what evidence a *breach of this rule* leaves. Got: the description of correct behavior. If the verifier refuses correctly, the rule was not breached — it was enforced. What the entry never says is what it looks like when a verifier is handed a moving yardstick and *doesn't* refuse. That is the actual breach and its trace is missing.

**10. Line 45 — a citation I cannot evaluate.**
> Bousetouane, "AI Agents Need Memory Control Over More Context" (arxiv 2601.11653), 2026.

Expected: a source. Got: a source, cited twice (again at line 138). I have no way to check it from here and the nine-component schema is attributed entirely to it. Flagging as a thing I had to take on trust, not as an error.

**11. The nine-component table is the largest block in §5 and served none of my lookups.**
Nine rows x three columns to say "brief reads from Reports, Verdicts, artifacts, phase docs, the Plan, and paths." It's a schema dump, and it sits between the CCS definition and the thing I actually needed (the size ceiling), which is *below* it.

**12. Line 68 packs three distinct mechanisms into one sentence.**
> "Three things keep it small: real work travels by path and is never pasted in; a ceiling of 2,000 bytes, where the component that pushed past it is itself the diagnosis of the Step's scope; and the Conductor keeps no rolling summary of its own..."

Expected: three bullets, since the doc bullets freely elsewhere (line 60–66 is a six-bullet list of *softer* material). Got: a 70-word semicolon chain. The one number in the whole section is buried mid-clause. This is the single hardest-to-scan sentence carrying the single most-looked-up fact.

**13. Line 82 — the *(proposed)* marker's scope is ambiguous.**
> "its run-state line becomes durable at whichever dispatch point comes next *(proposed, along with the run-state file)*."

Expected: to know whether the Planning-Gate-sends-no-dispatch behavior is what ships, or is the proposal. Got: a marker whose scope could be the sentence, the paragraph, or just the run-state file. Line 5 says *(proposed)* means "design that is not built — §3.3 says what ships in its place," so I now have to leave the document to learn what actually happens at a Planning Gate approval. §5.7 line 102 has the same marker on the run-state file again.

**14. §5.7's "Does" list is a run-on of eleven verbs.**
> "Holds the purpose. Elicits, its one human touchpoint. Drafts the Plan and derives it again each wave. Writes and dispatches work orders. Combines the wave's rulings with a plain AND..."

Expected: a list, given the heading is "the two lists." Got: two paragraphs of clipped fragments. "Combines the wave's rulings with a plain AND" — AND of what, producing what? Not answerable from here.

**15. Line 108 — a 90-word sentence I read three times.**
> "So the wall holds as a traceable default, because what may enter is short and closed — the newest CCS, small rulings, the approved phase documents, the standing Plan, the run-state file, gate feedback as an arrival and a path, the elicit exchange it writes under `research/`, and paths."

This is a *whitelist* — the most lookup-shaped content in §5.7 — delivered as a subordinate clause with eight comma-separated items, one of which is "paths" while another is already "a path." Should be a list.

**16. Line 108 forward-references §7 for something §7 doesn't have.**
> "A block would have to come from outside the loop, and §7 names the one to reach for first"

I went to §7. The nearest match is line 142, "the first hardening to try is a hook refusing the Conductor's reads by path" — which is under **Costs paid**, not under "Shapes discarded", and is not phrased as "the block to reach for." I had to match it by content. Two sections describing the same hook in different words.

**17. §6's three ratios are defined but not addressed to anyone.**
The table (lines 114–118) is clean. But "Keep rate = Steps ÷ Turn(generate)s. Work that passes first time scores 100%" — if every Step needs exactly one generate to pass, the ratio is 1. Fine. But then "below a 50% keep rate the loop spends more than it saves" means two generates per Step. I had to do that arithmetic to understand the threshold, and the doc could just have said "two attempts per Step on average."

**18. Line 122 — "Nothing is instrumented" undercuts the section it's inside.**
Section 6 is titled "What the loop costs to run" and gives three measures; then says nothing measures them and you count by hand off disk afterward. Not wrong, but the heading promises observability and the body delivers post-hoc forensics. I expected a tool and got a method.

**19. Line 137 — "Git as a requirement" rejected, but git is required in §5.5.**
§5.5 line 74 says record "ships as three per-backend adapters — github, gitlab, local." §7 says git-as-requirement was discarded. These agree, but I stumbled because §5.5's *default* prose is entirely git-shaped ("Create the run branch, push, open the pull request") with local described afterward as an exception (line 86) and again as a degradation (line 148). Three separate places describe local mode. None of them is "the local entry."

**20. Machine-written tells — sentences I had already read.**
Several near-repetitions across sections, each restating a prior point in fresh words rather than cross-referencing:
- "the artifact wins" appears at line 31 (§5.2 containment), line 64 (§5.4 bullet), and line 70 (§5.4 breach trace) — three phrasings of one rule.
- "re-sending is safe" appears at line 17 (rule 5), line 84 (git adapter), line 86 (local adapter).
- The compliance bet / rules-are-defaults point appears at line 132 and line 142.
- Local mode's degradation appears at line 86, line 88, and line 148.

**21. The rhetorical-aphorism register, everywhere.**
> "a ruler that may have shifted measures nothing" (39)
> "a state pieced together from partial views has lost the very thing that made it a state" (65)
> "a named degradation beats a pretended uniformity" (148)
> "An author reads" (104, 136 — twice)
> "code fixes the ceiling wherever understanding happened to stand on the day somebody wrote it" (132)

Individually these are good lines. At this density they slow lookup: I keep having to decode an epigram to extract a rule. "An author reads" appears twice as a standalone justification and I still had to work out it means *an author would have to read the real work, which the Conductor may not do.*

**22. §5.1 heading says "five rules that never vary" but rule 3 is one word of content.**
> "**Touches the real work freely.** Nothing else does."

"Nothing else does" contradicts §5.5, where record commits products, and §5.4, where brief reads artifacts. Presumably "the real work" is narrower than "files", but the entry doesn't say what it excludes. Held open.

---

## 4. Content I did not need

- **The nine-component CCS table (lines 47–57).** Largest single block, served nothing. Serves: whoever *implements* Turn(brief), or a reviewer checking the schema against Bousetouane. Not a lookup reader.
- **§5.4's six operating bullets (60–66).** Rationale for design choices ("Third person", "After the ruling", "Replaced, not appended"). Serves: someone deciding whether to adopt or change the design. Note the doc itself calls these "the four operating rules" at line 138 while printing six bullets — another count mismatch.
- **§5.1's closing invariant paragraph (line 21).** Argues extensibility. Serves: someone proposing a new role or backend.
- **§6 entirely, apart from confirming record counts as overhead.** Serves: whoever has to justify the loop's cost to a skeptic, after a run.
- **§7's "Costs paid" list (140–149).** Eight admissions. Serves: a reviewer or adopter deciding whether the trade is acceptable — genuinely valuable to them, irrelevant to me looking up a promise.
- **§7's other six discarded shapes.** I needed one (controller program). The other six serve someone re-litigating the architecture.

The pattern: roughly half of Part II is addressed to an **evaluator** (should we build it this way?) and half to an **operator** (what does this part promise?). They're interleaved. A reference should separate them, or at least mark which is which.

---

## 5. Things I needed that are not here

**Terms used as load-bearing and never defined in this part** (line 5 pre-announces this, which does not fix it):

- **wave** — used ~15 times, structurally central, never defined. Related to Steps and `consumes`, but the relation is only inferable.
- **Step** — capitalized, so it's a defined term. Not defined here.
- **gate**, **Planning Gate**, **G1**, **G3**, **bare-`gm`**, **`on`**, **`dn`**, **`up`**, **`/clear`** — nine operational terms treated as known. `gm` appears three times and is never expanded.
- **yardstick** — the pivot of §5.3 and used in §5.6 and §5.4. "Phase yardstick", "fixed yardstick", "yardstick chain", "phase's approved, frozen document" — I *think* they're all one thing but I'm inferring.
- **re-aim** — used in §5.4, §6, §7. Costs "the round twice." Never defined.
- **attempt ceiling** — the escalation-rate numerator. No number given anywhere in this part.
- **the discretion line (§4.3)** — one of "three things that make a revision safe" and it's a pure pointer out.
- **phase**, **Research**, **Purpose**, **elicit** — capitalized, undefined.
- **work order** — the only thing that gets into a Turn (rule 1) and the thing the Conductor writes; never specified.
- **aiya** — the system's own name, never introduced.

**Promises referenced but not stated here:**

- **§1.4's "two properties"** — referenced at line 126 and the compliance bet at 132/142 leans on §1.4. Central to the controller-program decision and absent.
- **§3.3, "what ships in place of *(proposed)*"** — I hit two *(proposed)* markers (82, 102) and both dead-end outside Part II. The run-state file is in the Conductor's Does list and in record's commit list, and it's proposed. I cannot tell what ships today.
- **§4.4's invalidation mechanism** — referenced three times (29, 37, 78). The version stamp exists to feed it. What it does is elsewhere.
- **§4.1's re-send safety** and **§4.5's bounded working state** — both cited as the justification for claims made here.
- **§2** — cited as the whole argument against the controller program.

**Missing numbers a lookup reader would want:** the attempt ceiling value (§6 counts against it, §5.6 mentions restarting counts, no number), the number of Steps per wave, the gate count (§7 line 149 says "six points" — the only place a gate count appears, in the costs list, not in a gate entry).

---

## 6. Effort score

**4 out of 5.**

Not a 5, because every one of my five lookups was eventually answerable and two (b, e) were genuinely easy. Not lower, because I re-read on every lookup, held nine undefined terms open throughout, reconciled four conflicting counts, and had to reconstruct answers for (a) and (c) rather than read them.

**The one change that would most reduce it:**

**Give each §5 entry a fixed, identical opening block — a fact card — before the prose.** Same fields, same order, every entry:

```
Turn(record) — the only writer to storage
Promise:   every platform operation happens here, nowhere else
Returns:   a few lines naming what got committed
Runs at:   on | wave settle (after brief) | pre-gate Plan push | gate ruling | dn
Numbers:   3 adapters (github, gitlab, local); 5 dispatch points
Breach:    a commit no dispatch produced stands out in history
           — unavailable under local (no history)
Terms:     wave, gate, on, dn -> ch.2
```

That alone fixes lookups (a) and (c) outright, surfaces the 2,000 for (b) and the four viewpoints for (d) without reading a paragraph, makes the count mismatches (stumbles 2, 3, 20) impossible to hide because the numbers would sit side by side, and gives the undefined vocabulary a per-entry pointer instead of one blanket disclaimer. The existing prose can stay underneath, unchanged, for the evaluator who wants the argument.

Second-best, if only one line changes: **break line 68 into three bullets** so the 2,000-byte ceiling is not buried mid-clause in a 70-word sentence.
