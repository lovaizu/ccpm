# Head-to-head reader trials — current design vs. writ rebuild

Both documents were put to a fresh-context reader under the **same** prompt, the same ratified reader
definition, and neutral filenames (`doc-A.md` / `doc-B.md` in a scratchpad) so neither reader could
tell which document it held or that a second document existed. Neither could read any other file.

- **doc-A** = `aiya/docs/design.md` at `d7b63f9` (6,557 words) — the current document, with the eight
  round-4 residuals fixed.
- **doc-B** = `.rn/20260813-aiya/checks/4-rebuild/design.md` (8,334 words) — the writ blank-page
  rebuild, built from doc-A's intent plus the shipped files.

The prompt asked for: the one decision (do the two mechanisms discharge the two properties), a
headings-only read, every stumble, content the reader did not need, and an effort score — and told
the reader not to be polite. This is a harder prompt than the four earlier trials on the current
document, which is why both readers land short of the plain YES those recorded; the comparison is
still like-for-like because both got the identical prompt.

## Result at a glance

| | doc-A (current, 6,557w) | doc-B (rebuild, 8,334w) |
|---|---|---|
| Verdict | QUALIFIED | QUALIFIED |
| Effort (1 effortless – 5 struggle) | **4** | **3** |
| Stumbles reported | 20 | 18 |
| Headings alone carry the argument | 3 breaks | 4 breaks, "above average" |
| Path to a confident answer | §1–2 → jump to §4.6 → two backward passes | one full pass + two targeted re-reads |
| Provisional verdict before the qualifications | YES at §4.6 | YES at §4.6 |

Both readers reached the same ruling by the same route: §4.6 reads as closure, and what downgraded
them to QUALIFIED lived in chapter 5 (the wall's admission, the CCS's soft cap and unshown schema)
and in §4.5's last paragraph.

## What both readers found independently — design-level, not writing-level

These are the same objections raised against two documents written from different sentences. They
are therefore properties of the design, not of the prose, and no rewrite will remove them.

1. **The stated property is narrower than the pain that motivates it.** §1's context-bloat bullet is
   about cumulative growth ("old mistakes ride along in the transcript"); the property bounds only
   width. §4.5 concedes the transcript still grows linearly and hands the remedy to the human's
   `dn` → `/clear` → `up`. Both readers called this legitimate scoping that the document never
   admits out loud at §1.
2. **The CCS's bound is a soft cap and its schema is a citation.** "Bounded by construction" is the
   heading; the body gives a soft cap that signals when breached, and nine components adopted from a
   paper the reader cannot see. Both readers: cannot check boundedness against a schema not shown.
   Both also asked "sub-linear in *what*".
3. **The no-reading wall is not structural.** §4.6 leans on it; §5.7/§5.1 admits it cannot be made
   physical. Reader B added the sharper form: nobody reads the trace — there is no auditor role and
   §6 counts no wall breaches.
4. **Nothing measures whether drift detection works.** §6 counts cost (keep rate, escalation,
   overhead). Neither a drift-caught rate nor a false-negative signal exists. Reader B: "For the
   property whose whole point is catching something, the design ships no way to learn whether it
   caught anything."
5. **The 1:1 mechanism map does not survive contact with §4.6.** Reader A: the count changing (two
   properties → two mechanisms → two supports each → §4.6's three legs → "legs"/"supports"/"things")
   cost a jump every time. Reader B: "§2's 'each of the two required properties gets one primary
   mechanism' is the sentence I would strike — §4.6's three-legs-each account is the true one, and it
   is better."
6. **The two properties are named in no heading** before §4.6 announces their discharge. Both
   readers, independently, in the headings-only pass. This is the standing residual from round 4,
   now confirmed twice more.

### Raised by one reader only, and worth ruling on

- **A-2 / A-3 (current doc):** drift's second form — a stale plan completed faithfully — is guarded
  only by "re-plan from zero", and §5 names **no trace** for a Conductor that skips it. A Conductor
  re-emitting yesterday's Plan is indistinguishable from one that rebuilt it and converged. Paired
  with: the CCS defends against over-claim but not **omission**, and re-planning runs off the CCS —
  so a dropped discovery is exactly the input that makes re-planning-from-zero return the old plan.
  The two failures compound in the same direction.
- **A-4:** whether Turn(brief) reads the previous CCS is never stated. If no, memory dies one wave
  back; if yes, the CCS accumulates and boundedness needs an argument it does not get.
- **B-(b):** the verifier's aim is set by the party that would drift — the Conductor composes the
  work order and so chooses which yardstick criteria bear on a Step. §5.4 hardens verify against
  persuasion, nothing hardens it against omission.
- **B-(h):** Turn(generate)'s Report carries "what it tried and abandoned", and only Turn(brief)
  reads it — after the wave settles. So attempts 2 and 3 of a Step cannot see what attempt 1
  abandoned. The document writes down the exact information that would prevent repeated dead ends
  and routes it away from the only party who needs it inside the retry window.

## Findings against the eight residual fixes applied today (d7b63f9)

Two of today's fixes were read as defects by the trials.

- **R3 backfired.** The added clause "Each mechanism carries two supports alongside it; §4.6 states
  the full discharge" is reader A's stumble 5: "So the 'two mechanisms' I was just handed are six
  legs. This sent me to §4.6 immediately, out of order, because I no longer trusted the count." The
  reconcile the residual asked for made the count *more* visible without making it *true*. Reader B,
  reading the rebuild's version of the same claim, independently prescribes the real fix: strike
  §2's one-mechanism-each sentence and let §4.6's account stand.
- **R1 is half-right.** Dropping the blanket "structural" was correct, but the examples it names —
  fresh contexts, the omitted spawn tool — are Turn-contract properties, not legs of either
  discharge. Reader B (§4.6 in the rebuild, which inherited the wording): "Neither cited structural
  item is among the six legs the section just enumerated," and §5.2 then discounts the spawn tool
  itself, since every Turn that does real work carries Bash. The sentence borrows structural
  credibility from a rule that is structural almost nowhere.
- **R8 is contested.** Naming the Conductor as the party that notices a missing viewpoint is reader
  A's stumble 9: "How does the Conductor notice a concern is missing without knowing what the product
  is? §4.3's own attribution test is 'does this act require reading the real work?'" The gloss is
  faithful to `conductor/SKILL.md:79`, so the tension is in the design, not the sentence.
- R2, R4, R5, R6, R7 drew no finding in either trial.

## Where the two documents differ as documents

**doc-B reads easier despite being 27% longer** (effort 3 vs 4). Reader A's drivers for the extra
point, in its own order of weight: front-loaded term density (nine vocabulary items in one block,
three of them used in the prose above the block that defines them); the changing count; "compression
into ambiguity" on four specific lines, each past the point where a first reader can recover the
parse; and load-bearing content deferred off-document. Reader B's headings-only pass called the
rebuild's `label — gloss` headings "above average — I could reconstruct the machine".

**Both readers rejected the same chapters as not theirs**: §3.3's tree and backend detection, §3.4's
inventory, §5's implementer material, §6's ratios, most of §7's rejected shapes. That is the standing
FB3 cluster, unchanged, confirmed against a differently-written document — so it is the ratified
seven-chapter format's cost, not either document's fault.

**doc-B's own disclosed defects** (from its note): the step-10 self-check carries one honest FAIL —
the ratified format mixes two axes (article for 1–4, reference for 5–7) — recorded per writ step 3
as an axis conflict rather than resolved; and writing directly after a full read produced 127 shared
8-token spans with doc-A, reduced over two rewrite passes to a 7.3% residue in which every span of
10+ tokens is an identifier (the Bousetouane citation, the directory tree, table headers, the ratio
formulas, the fixed vocabulary). Exactly one full line is identical between the documents: the
verification-overhead formula.

**What doc-B drops**, in full, with dispositions, is its note's "Decisions I did not carry" section.
The material item: the entire run-state file (`state.yaml`), dropped because no shipped file carries
it — the plugin ships a one-line `backend` file (`conductor/SKILL.md:26`, `up/SKILL.md:15`). That
drop is a rebuild error of context, not of fact: the run-state revision is deliberately ahead of the
build, awaiting the PR #19 verdict, with the ripple explicitly deferred until after approval. The
finding underneath it stands, though — the current document marks only the first of eight mentions
"(proposed)" and asserts it as shipped in the other seven, so an evaluating reader cannot tell which
parts of the document are live and which are pending.
