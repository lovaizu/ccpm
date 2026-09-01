# Reader trial — round 3, Part II (reference part, chapters 5–7 only)

Fresh subagent, given only `doc-Z.md` (a neutral-named copy of Part II after the round-2 fixes) and
the Part II reader definition. Verbatim and unedited. This is the third and final round under
writ's cap; nothing was edited after it.

---

# Report — doc-Z.md read as a lookup user

## 1. The decision

**QUALIFIED.**

Four of five lookups landed in one place and answered cleanly. But this document is not a reference — it is an essay wearing a reference's headings. The section titles announce lookup ("Find the entry you need"), and then every entry is written as continuous argumentative prose where the answer is buried mid-paragraph, in a subordinate clause, after the rationale. I found what I needed by reading whole sections, not by scanning to a fact. That is the opposite of what a reference does.

Two specific failures push it below YES:

- **Lookup (b) — the headline number is contradicted three lines later.** "A ceiling of 2,000 bytes" is stated as one of "three things keep it small," and then paragraph 60 says the ceiling "is advisory, not enforced" and that "the honest claim is not that the file has a fixed size." So the answer to "what stops it growing" is: *nothing does*. That is a legitimate answer, but it is filed under a heading that promises the opposite, and a scanner who stops at the bullet leaves with the wrong fact.
- **Lookup (c) — "what happens if it runs twice" is answered twice, in two places, with two different scopes**, and neither says which one governs.

Against that: the "Breach trace" convention is genuinely good and is the single most reference-like thing here. Every rule entry ends with what a breach leaves behind, and where it leaves nothing, it says so in bold. That is exactly what I came to check, and it is consistently placed.

---

## 2. Per lookup

### (a) What exactly may a Turn hand back to its caller?

**Found. §5.1 rule 4, line 16.** Complete on first read.

> "**Hands back something small.** Paths and a line, a ruling, a CCS path, a few lines naming what got committed — no raw output, no transcript."

Four permitted shapes, enumerated, plus two explicit exclusions. I did not have to guess. Each shape is then confirmed at its own entry — generate at §5.2 ("returns those paths with one line of completion — rule 4's 'paths and a line'"), verify at §5.3, brief at §5.4 ("Brief returns the CCS path and nothing else"), record at §5.5 ("one return: a few lines naming the paths"). That cross-confirmation is the best-built thing in the document.

**Reconstructed:** rule 4 is enforced ("Rule 4 the Conductor checks on each return"), but *how* it is checked — by shape, by size, by eyeball — is not stated. If I am implementing the Conductor, I do not know what the check is.

### (b) What stops the CCS file from growing without bound, and what is the number?

**Found, then unfound. §5.4, lines 54–60.** This is the worst entry in the document for a lookup reader.

The number: **2,000 bytes.** Stated in a bullet under the bold lead-in "Three things keep it small."

Then line 60: "The ceiling is advisory, not enforced." So the honest answer to my lookup is: **nothing stops it.** What is actually true is a different claim — "each wave's file is written whole and stays small, and what grows sub-linearly is the total the Conductor has read across the run."

I had to hold the question open across two paragraphs and then revise the answer I had already taken. The real mechanism that bounds growth is not the number at all — it is **"Replaced, not appended. Each wave gets a whole new file."** That is the actual answer, and it is filed three bullets above, under a different heading ("the way it is operated"), not under the heading that promises to answer my question.

**Reconstructed:** what happens when the 2,000 bytes is exceeded. The document says "Whichever component pushed past it is the diagnosis of the Step's scope" — so the overflow is *diagnostic*, not a failure. But nobody is said to look at it. §5.4's own breach trace says "Nothing inspects the CCS directly." So a 2,000-byte ceiling that nothing enforces, on a file nothing inspects, is not a mechanism. I had to work that out myself; the document never says it.

### (c) When does the physical-record worker actually run, and what happens if it runs twice?

**Found, in pieces. §5.5, lines 80–92.**

*When:* five dispatch points, listed as bullets. Clean and scannable — the best-formatted block in the document. `on`, every wave settle, every pre-Planning-Gate Plan push, a gate ruling, `dn`. Plus one exception in its own paragraph (line 88): a Planning Gate approval sends no dispatch at all.

*If it runs twice:* answered **twice, differently.**

- Line 90 (git backends): "a path already committed stages nothing, and a push with nothing new behind it moves nothing."
- Line 92 (local adapter): "A copy already sitting under that name is confirmed rather than rewritten, which is what makes a re-send safe here too."

Both say "safe." Neither is stated as the general rule with the other as its instance. I had to assemble "idempotent under both backends, for different reasons" myself. A reference entry should say that once, up front, then qualify.

**Reconstructed / guessed:**
- The gate-ruling bullet (line 85) carries three unrelated behaviors crammed into one bullet: the normal move-to-durable, the special G3 closing settle, and the bare-`gm` comment fetch. I read that bullet three times. Whether G3 is idempotent — a "closing settle" that sets `status: closed` and sweeps "whatever is unrecorded" — is not addressed by line 90's reasoning about paths and pushes. I do not know if re-sending a G3 close is safe.
- "the request stays open" — I guessed this means the PR is deliberately *not* closed by G3. Not stated why.

### (d) What are the criteria a Plan is checked against, and who owns them?

**Found. §5.6, line 100.** The cleanest lookup in the document after (a).

Owner, stated with its reason: "against four viewpoints **aiya fixes rather than the Conductor** — a Conductor authoring the criteria for its own Plan would be approving itself."

The four, enumerated inline: (1) every item carries all three required lines; (2) `consumes` reflects real consumption, same-file writes included; (3) `done when` can be run; (4) the items, held against the phase yardstick, add up to that phase's product exactly.

**Stumble:** they are run together in one prose sentence separated by semicolons, not listed. Four criteria that a reader will check off one at a time are formatted as a paragraph. I counted them on my fingers to confirm there were four.

**Reconstructed:** "aiya" as the owner. The document never says what aiya is — it is used as a proper noun throughout (§5.2 "No other party writes a version anywhere in aiya") with no definition here. I inferred: the system/plugin itself, i.e. the criteria are hard-coded rather than authored per run. Line 5 warns me chapter 2 holds the vocabulary, so this is disclosed — but for a cold lookup it means the *owner* half of my question is answered by a word I cannot resolve.

### (e) Why was a controller program rejected, and what would reverse that decision?

**Found. §7, line 151.** Both halves present, and this is the only entry that answers a "what would reverse this" question directly.

*Why rejected:* "code fixes the ceiling wherever understanding happened to stand on the day somebody wrote it."

*What reverses it:* "Whether prose alone can carry the cycle, the attempt ceiling, and the gates gets settled in dogfooding. If it cannot, the loop moves into code and nothing else does."

That last clause is the useful part — the reversal is scoped. Formats, chain, and measures cross over unchanged.

**Reconstructed:** what "settled in dogfooding" means operationally. No threshold, no measure, no owner of the call. §6 gives me three ratios and one heuristic (50% keep rate), but none of them is tied to this decision. So the reversal condition is "somebody decides it didn't work." I cannot act on that.

Also unresolved: "the compliance bet" is named as something the controller "would retire," pointing at §1.4. §1.4 is not in this document.

---

## 3. Every stumble

**1. Line 5 — the document tells me up front it will not be self-contained.**

> "Chapter 2 fixes the vocabulary and this part does not repeat it, so an entry may use a term it does not define."

Expected: a reference where each entry stands alone. Got: an explicit declaration that it does not. Honest, and it saved me hunting — but it means the answer to "is each entry complete on its own" is *no, by design*.

**2. Line 9 — a teaser I then had to verify by hand.**

> "Two of the seven leave none and say so."

Seven what? There are seven §5.x subsections, so: seven entries. I then counted breach traces to find the two: §5.2 (generate) says "**Breach trace: none.**" That is one. The second I had to hunt for — §5.1's rule 2 is described as "a norm and not a block" for four definitions, and §5.5's trace is conditionally absent ("Under local there is no history to stand out in, and this trace is unavailable"). Neither is a clean "none." **§5.7 (the Conductor) has no breach-trace line at all.** So my candidates for the second are: §5.7 by silent omission, or §5.5 by conditional absence. The count does not resolve. I guessed §5.7. A reference should not make me audit its own claim.

**3. Line 19 — the most load-bearing caveat in §5.1 is the last clause of a dense paragraph.**

> "There an indirect escape through the platform's own CLI remains, so for those four rule 2 is a norm and not a block."

Expected, from the heading "five rules, two of them enforced": two enforced, three not. Got: rule 2 is enforced for two of six definitions and unenforced for four. The heading is wrong, or at best true only of two definitions. I re-read the paragraph to work out which four (generate, verify, two remote adapters) and which two (brief, local adapter — arrived at by subtraction, never stated).

**4. Line 19 — six definitions named as "generate, verify, brief, and one record adapter per backend."**

Three backends (§5.5), so 3+3=6. Correct, but the arithmetic is mine. And it collides with §7's "Roles stop at the three families" — three families, six definitions, four carrying Bash. Three different counts of the same thing across three sections, none reconciled in one place.

**5. Line 19 — a breach trace that admits it is not observable.**

> "the nested session's transcript, which no bounded return reports — so nobody inside the loop ever sees it."

I had to hold open whether this counts as a trace. It is evidence that exists but that no party in the system can reach. For my decision — "unambiguous about what a breach leaves behind" — this is the honest answer, but it means the count in stumble 1 should arguably be three, not two.

**6. Line 31 — containment described as if it were a check, then corrected in the same sentence.**

> "What limits the damage is that Turn(brief) takes the artifact over the Report wherever the two disagree (§5.4) — a containment, not a check."

Good self-correction. But I had already started reading it as a check before the dash arrived.

**7. Line 37 — one sentence carrying four separate mechanisms.**

> "It writes its ruling to disk before it returns and then hands back that same text, so the record exists before the Conductor has seen a word of it and a ruling that would suit the Conductor cannot be arranged afterwards."

Write-before-return, return-the-same-text, ordering guarantee, tamper resistance — one sentence, no punctuation break at the "and." I re-read it twice to separate the mechanism from its justification.

**8. Line 39 — a special case that changes the entry's core promise, introduced mid-paragraph.**

> "At the head of the yardstick chain — the Purpose, and every Research product — nothing is approved yet, so the dispatch names `evidential-soundness` where a document would go"

§5.3's bold promise is "**What it measures against never moves**: always the phase's approved, frozen document." Then, four lines later, sometimes there is no document at all and a named string goes in the slot instead. The exception is bigger than a parenthetical and is not flagged as one.

**9. Lines 54–60 — the 2,000-byte contradiction.** Detailed in (b). "Three things keep it small" -> the second of the three does not keep it small. This is the single worst thing in the document.

**10. Line 60 — a sentence that admits the section's framing was wrong.**

> "So the honest claim is not that the file has a fixed size"

Expected: the honest claim stated first. Got: the overclaim, then the retraction. For a scanner, the retraction is what gets skipped.

**11. Lines 62–74 — the nine-component table is the only clean lookup surface in §5.4, and it does not carry the size story.**

The table answers "what is in a CCS and where does each part come from." Useful, well-formed. But my lookup was about size, and the table is silent on it — no per-component budget, nothing tying the nine components to the 2,000 bytes. Line 57 says "Whichever component pushed past it is the diagnosis," implying components are individually measurable, but the table gives me no measure.

**12. Line 76 — the breach trace for §5.4 undercuts the entry's own enforcement story.**

> "Nothing inspects the CCS directly."

Combined with "The ceiling is advisory, not enforced," the CCS is the one part with a number, and the number is checked by nobody. I held this open for the whole of (b).

**13. Line 85 — three behaviors in one bullet.** Detailed in (c). Normal gate move, G3 closing settle, bare-`gm` fetch. Read three times.

**14. Line 85 and line 92 — `gm` appears with no definition, in two contradictory-sounding statements.**

> "A bare-`gm` send-back has it fetch the review comments to a file"
> "A bare `gm` never reaches this adapter"

Also written two ways ("bare-`gm`" hyphenated, "bare `gm`" not). I never learned what `gm` is. Same for `on` and `dn` — used as dispatch-point names throughout §5.5 and §6, defined nowhere here. Line 5 covers me, but see §5 below.

**15. Line 88 — a whole behavior marked *(proposed)*, i.e. not real.**

> "its run-state line becomes durable at whichever dispatch point comes next *(proposed, along with the run-state file)*."

The run-state file is referenced as a live thing at four separate points (§5.5 twice, §5.7's "Does" list, §5.7's intake list) — three of those carry *(proposed)*, and **line 83's "the run-state file" in the wave-settle bullet does not.** So one of the five dispatch points commits a file that does not exist. Either a missed marker or a real inconsistency; I cannot tell which, and had to jump between four places to find out.

**16. Line 92 — the local adapter's paragraph reverses itself.**

> "it writes nothing at all. Its one write comes at a gate approval"

"Writes nothing at all" then "its one write" in consecutive sentences. Resolvable — the first is scoped to four of five points — but the scoping arrives only after the contradiction. I re-read it.

**17. Line 100 — four criteria as one semicolon-run sentence.** Detailed in (d). Counted them by hand.

**18. Line 102 — "Three things make a revision safe" followed by three sentence fragments.**

> "Staying inside the discretion line (§4.3). Appending to a change record... And re-running the four fixed viewpoints on every revision."

Three list items formatted as prose fragments rather than a list, directly beneath a bolded count that promises a list. The document uses bullets elsewhere; here it does not, for no reason I can see.

**19. Line 104 — three breach traces run together, plural heading, no bolding.**

Every other entry has a bolded "**Breach trace:**". §5.6 has "Breach traces:" unbolded, carrying three. The one consistent scanning anchor in the document breaks here.

**20. §5.7 — no breach trace at all.** The Conductor is the part with the most rules ("Never" lists six prohibitions) and it is the only §5.x entry with no breach-trace line. Line 127 gets close — "the tell is the Conductor citing content that no return delivered" — but it is not labeled, so scanning for the anchor finds nothing.

**21. Line 114 — the enforcement answer is "nothing, today."**

> "A block would have to come from outside — a hook refusing its reads by path, which §7 names as the first hardening to try and which does not ship today."

Fine, and honest. But this same hook appears again at line 161 in §7, saying essentially the same thing in different words. Second occurrence added nothing.

**22. Line 139 vs line 141 — a claim and its contradiction two lines apart.**

> "Record is inside the overhead on purpose"
> "**Nothing is instrumented.**"

Three ratios are defined in a table as if they are measures the system produces. Then: nothing produces them. They are computable *after* a run, by hand, from disk. The table's framing ("Measure | Definition") reads as instrumentation; the prose says otherwise. Same failure shape as the 2,000 bytes.

**23. Line 143 — a number with no owner.**

> "below a 50% keep rate the loop spends more than it saves"

Hedged twice in one sentence ("An opening heuristic, meant for tuning by use rather than treatment as a measured rule"). So it is a number I cannot act on, presented as the section's only threshold.

**24. Line 145 — three sentences saying one thing.**

> "These three measure the loop's efficiency, not a human's productivity. §1.4 answers for the two properties. These ratios answer a separate question: whether that answer earned the Turns it took."

Sentences one and three make the same distinction. Reads as machine-written padding.

**25. §7 — "Shapes discarded" mixes two different kinds of thing.**

Seven bullets. Some are architectural alternatives that were genuinely on the table (a controller program, transcript replay, an agent catalog). Others are restatements of rules already given in §5 (products drafted by the Conductor = §5.7's "Never" list; state written by the party it describes = §5.4's "Third person"). For a lookup on "why was X rejected," I have to first work out whether X was ever a real candidate or is just a rule wearing a rejection's clothes.

**26. Line 157 — a rejection entry that ends on unrelated attribution.**

> "The schema is Bousetouane's (§5.4); the four operating rules are aiya's."

Also: §5.4 lists **five** operating rules as bullets under "What aiya adds is the way it is operated" — third person, after the ruling, replaced not appended, the artifact wins, one per wave, facts only. That is **six** bullets, not four. §7 says four. Neither reconciles. I counted the bullets twice.

**27. Line 166 — "History still grows linearly" contradicts nothing but undercuts §5.4's whole point.**

> "Only the working state is bounded (§4.5)."

Which loops back to (b): the working state is bounded by an advisory ceiling nothing enforces. So "bounded" here means "written whole each wave and, in practice, small."

**28. Repeated bold-lead-in pattern across the document.** Nearly every paragraph opens with a bolded clause that is then argued for. Consistent, but it means the bold text is a *claim*, not an *answer*, and several of the claims (stumbles 9, 22) are later qualified into something weaker. As a scanning aid, the bolding is actively misleading.

---

## 4. Content I did not need

- **§5.1's "The invariant is this contract, not how many definitions exist"** (line 21) — an extensibility argument. Serves someone deciding whether to add a role, not someone doing a lookup.
- **§5.3's last paragraph** (line 41) — "runs whatever can be run," oversized-Step advice. Serves a Step author, not a verify lookup.
- **§5.4's table** (lines 62–74) — nine rows. Serves a Turn(brief) implementer. Did not touch my size question at all.
- **§5.4's Bousetouane citation and arXiv link** (line 45) — serves provenance and prior-art credit, not operation.
- **§6 in its entirety** — three ratios plus the 50% heuristic. Serves whoever has to justify the loop's cost to someone else. None of my five lookups touched it, and given "Nothing is instrumented," it serves that person only after a run, by hand.
- **§7's "Costs paid" — eight bullets** (lines 159–168). Serves a reader deciding whether to adopt aiya at all. Pure argument; the only one that carried a fact I could use was "Local mode is degraded," and that fact is already in §5.5.
- **§7's rejections other than the controller** (lines 152–157) — six bullets serving an architecture reviewer.

Roughly: **§6 and §7's cost list are for a decision-maker; §5 is for an operator.** They are in the same document under the same "find the entry you need" promise, and nothing separates the two audiences.

---

## 5. What I needed that is not here

Terms used, never defined (line 5 discloses this, but it still cost me):

- **`gm`, `on`, `dn`** — three command or event names doing structural work in §5.5 and §6. `gm` in particular appears in two statements that look contradictory until you know what it is.
- **aiya** — the proper noun that *owns the Plan criteria* in lookup (d). Owning something is a role; I cannot check who holds it.
- **"wave", "Step", "attempt ceiling", "re-aim", "gate", "G1/G3", "Planning Gate", "yardstick", "the discretion line", "elicit"** — all load-bearing, all assumed.
- **"the compliance bet"** — named in §7 as the thing a controller program would retire, pointed at §1.4. The bet itself is the crux of lookup (e) and is not stated here.

Promises referenced but not stated:

- **§1.4's "two properties"** — cited twice (lines 145, 161) as the thing the whole design answers for. Never named.
- **§3.3's "what ships in its place"** — line 5 tells me every *(proposed)* item has a shipping substitute in §3.3. Four *(proposed)* markers appear; none says what actually happens today. So for the run-state file, I know the design and not the behavior.
- **§4.4 (versioning/invalidation), §4.3 (discretion line), §4.1 (re-send safety), §4.5 (bounded state)** — four of the most-cited anchors, all outside.
- **The mechanism of rule 4's check.** "Rule 4 the Conductor checks on each return" — what the check is, and what happens on failure, is absent. Directly relevant to lookup (a).
- **Whether a G3 closing settle is idempotent.** Relevant to lookup (c), unanswered.
- **What happens when the 2,000-byte ceiling is crossed.** "The diagnosis of the Step's scope" — diagnosis read by whom, acted on how? Nothing inspects the CCS.

---

## 6. Effort score

**4 out of 5.**

Not because the information is missing — four of five lookups are here and correct. Because getting each one out required reading full paragraphs of argument, and because two of the five answers had to be *revised* after I had already extracted them (the 2,000 bytes, the instrumentation table). A reference that makes me un-learn an answer is worse than one that makes me read for it.

**The one change that would most reduce it: stop bolding claims that the following prose retracts.**

Concretely — "**A ceiling of 2,000 bytes**" under "Three things keep it small," when nothing enforces it and nothing inspects it, and a table headed "Measure | Definition" above "**Nothing is instrumented.**" These are the two places the document lies to a scanner. Lead each entry with the claim that survives the whole paragraph: "The CCS is bounded by replacement, not by size — each wave writes a whole new file; 2,000 bytes is an advisory target nothing checks." Then argue. Every fact I had to revise was a fact where the bold text and the paragraph's conclusion disagreed.

Second, if you want one more: **cut §6 and §7's cost list out of this document.** They serve a different reader than §5 does, and their presence is why "find the entry you need" is a promise this document does not keep.
