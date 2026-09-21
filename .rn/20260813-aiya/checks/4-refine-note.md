# What changed — noise-removal refinement of aiya/docs/design.md

A second pass over the writ rebuild (486a1af, note in `4-writ-note.md`), applying the four
findings fed back to writ (PR #15 comment, 2026-08-20). The seven-chapter format is kept — axis
changes are FB3 territory and the format (`aiya/references/design.md`) is a ratified artifact.
No ratified decision is lost: every cut below is **carried** (lives in a named shipped artifact,
verified by grep this pass) or **derivable** (reads off a principle the document states).

## The lens applied (FB1: whom does the sentence serve? / FB4: weight)

- **Opening abstract** (Conductor/Turn/gates before definition — served a re-reader) → replaced
  with one plain-language sentence a first-timer can parse.
- **§1 Out of scope** (forward refs answering a past reviewer) → one line: "measuring the 10×
  itself." The §4.6/§6 mapping is derivable — those sections state their own scope.
- **§2 "The skeleton is borrowed… industry standard"** (provenance for an approver, placed as
  Core's first claim) → the two platform facts moved into Wall 2, where they do the work; the
  provenance survives as one clause inside the bet paragraph.
- **§2 three claims** → merged into two paragraphs under the bet; every substantive sentence
  survives except "fast streams without a structure that catches straying are a liability"
  (motive restatement — derivable from the same paragraph's mechanism list).
- **§2 vocabulary paragraph** (~250 words of packed prose) → a definition list (form change
  only; every term kept).
- **Intake-list duplication** (§2 wall 1 vs §5.7) → stated once in §5.7; wall 1 points there.
- **§3.3 run.yaml defense** ("the CCS cannot absorb the job — wrong cadence / writer / nature")
  → cut; the writer choice and its load-bearing reason (only party present at every boundary
  event) survive.
- **§4.2 "three structural reasons"** → two kept in prose (serial by construction; record reads
  what it commits); the third (side-effect-free Turns stay re-sendable) is carried by §5.5's
  idempotency rule.
- **Weight discipline (FB4)** — bold now marks load-bearing principles only; footnote-grade
  values moved out (below) or unformatted.

## Cut details and their verified homes (all grep-confirmed this pass)

| Cut from design prose | Home |
|---|---|
| Platform concurrency cap (20), slicing | `aiya/skills/conductor/SKILL.md:72` |
| Attempt counter resets on settle | `conductor/SKILL.md:80` |
| Missing-viewpoint mechanics (add to Plan; fail starts re-aim) | `conductor/SKILL.md:79` |
| Conversion Step at end of Delivery | `conductor/SKILL.md:53` |
| Version header exact format `vN (YYYY-MM-DD HH:MM:SS)`, invalidation grep on `yardstick:` | `conductor/SKILL.md:51`, `aiya/agents/turn-generate.md:25` |
| Bare-`gm` absent under local ("feedback rides the argument") | `conductor/SKILL.md:102`, `turn-record-local.md:16` |
| Output-Gate feedback file unread by the Conductor | `conductor/SKILL.md:13,102` |
| Verdict worked YAML example | `aiya/agents/turn-verify.md:34-37` |
| Nine CCS component names, `type` vocabularies, worked example | `aiya/agents/turn-brief.md` |
| CCS size-cap value (2,000 bytes) | `turn-brief.md:53` |
| `history/` naming example (`purpose@G1-v1.md`) | `turn-record-local.md:16` |
| Backend detection tests (repo / host / CLI) | `conductor/SKILL.md:39` |
| consumes semantics (ordering excluded, premise docs excluded, same-file guard) | `aiya/references/plan.md:9-15` |
| Report format and honesty rationale | `aiya/references/report.md` |
| Per-backend local behavior at `on` / G3 | `turn-record-local.md`, `conductor/SKILL.md:39,51` |
| Local observability counts (CCS chain length, `history/` archives, `dn` traceless) | `conductor/SKILL.md:110,118` |
| Progress-board contents | `conductor/SKILL.md` §8 |

Derivable (no home needed, principle stated in the document): re-planning "match means same
plan, not no change judged" (§4.3's from-zero rule); "a doubt that fits neither is not yet
concrete" (steering-verbs paragraph); Delivery's dual Verdict citation (§4.4 dual yardstick +
§5.3 edition pinning); "Plans carry no version header, so the log is the only ledger" (§5.6
change-record rule); wave-not-lockstep (the §4.2 diagram's per-Step pipelines); split items'
partial products entering consumes (§5.6 split rule + consumes definition); the cap's check
method (a byte cap is checked by counting bytes — trivial; the value ships in turn-brief.md:53).

Kept although reference-grade, with reason: the `run.yaml` block (pending ratification at the
gate — no shipped home may exist before the verdict); the §3.2 ledger table, §3.3 layout tree,
§5 per-part promises and breach traces, §6 ratios (all format-mandated chapters/slots).

## Axis-side conflicts, for ruling (FB3 — not applied)

None forced a cut this pass; flagged for a future format ruling: the format mandates "Out of
scope" in ch.1 and per-part rules in ch.5 — both kept. If the owner later rules the format
itself leaner, §5 is the chapter that shrinks to pointers.

## Fresh-reader check (FB2)

Run after the rewrite by a zero-context subagent given only the document and the reader
definition (first-time reader; chapters 1–4 straight through; 5–7 consulted). Result:
**VERDICT YES** — after one straight read it retold both problems, both properties, and the
mechanism discharging each, accurately. Four stumbles reported, all fixed:

1. **Garden-path sentence** (§2): "What the skeleton does not supply — … — is a mechanism for
   not straying" first parsed as the design *lacking* one → split into two sentences
   ("The skeleton itself … is standard practice. What aiya adds is …").
2. **Six-vs-three gate mismatch carried for two sections**: §2 promised six gates but §3 shows
   only G1–G3 plus an unexplained "Planning Gate"; the decomposition arrived only in §4.4 →
   the §2 Gates vocabulary entry now states it up front (Plan in = Planning Gate; product out
   = G1/G2/G3).
3. **"viewpoint" used before defined** (§3.2, §4.1; definition sat in §5.3) → added to §2's
   vocabulary, one line, pointing at §5.3.
4. **"dispatch rounds" unrelated to "wave"** (§4.4) → the sentence now states the relation
   (one continuous run from stop to stop, typically spanning several waves).
