# writ — design notes

Not read at runtime — for whoever maintains the design and needs to judge whether a decision is
still right when the instruction or the target axes change.

## 1. Background & Goals

### 1.1 What is the goal?

A document that reads as if a person wrote it, not an AI — least reader effort, taken in top to
bottom, graspable at a glance. Packaged as a Claude Code plugin `writ` (skill `up`) so the procedure
applies on demand to any draft, run by a human or by Claude itself.

### 1.2 What goes wrong without this?

Without an ordered, reader-derived procedure, output either stays a direct edit of the input's own
wording (dragging its problems along and reading as patched) or reaches for generic AI patterns by
reflex — padding, restatement, retreat into generalities, flavorless connectives, reflexive
bulleting, a wavering voice, hedging. Any one of these instantly reads as "an AI wrote this,"
regardless of how much polish is layered on top.

### 1.3 What does reaching it require?

Primary mode: brush up an existing draft (read for intent, not reused verbatim). Authoring from
scratch runs the same procedure but is secondary. The procedure must build both quality tiers in by
construction, then verify — never edit the draft in place, since that drags the old wording (and its
problems) along.

### 1.4 What is out of scope?

One plugin (`writ`), one skill (`up`). How the body is laid out — one file, or a body plus
`references/` — is not a scope line; §5.2 owns it. Not a general prose generator: it
does not originate content on its own; it takes only the input's intent and what it must convey, and
derives structure/voice from a reader definition rather than memorizing a template's wording.

## 2. Assumptions & Constraints

### 2.1 What do we take as true?

- Official skills are model-invocable by default; `rn` disables it because its skills are meant for a
  human to drive — `up` is meant for a human or Claude itself, so it stays model-invocable.
- Skills are invoked as `/{plugin}:{skill}`; plugin and skill names are independent slots (`rn:gm` is
  the precedent), so `writ` + `up` is valid.
- `instruction.md` is the verbatim source of record for the skill's pillars, except the five-axis
  skeletons, which D-6 deliberately supersedes with externally sourced structures.

### 2.2 What binds the solution?

Inherited from the repo: version lives only in `writ/.claude-plugin/plugin.json` (not
`marketplace.json`); shipped artifacts are English except `instruction.md` itself, kept verbatim as
the source of record; `README.md` is scenario-style. Marketplace `category` is a free string
(unverified assumption) — used `"writing"`. `claude plugin validate` / `claude -p … --plugin-dir`
availability in the environment is likewise an unverified assumption; task #3 falls back to manual
verification if absent.

## 3. Design overview

### 3.1 What is the core idea, and why does it solve the problem?

An ordered writing procedure in `SKILL.md` rebuilds the document fresh from the input's intent
rather than editing it in place. Instructions to the model and rules for the produced document are
not separated into layers: each rule sits at the step that applies it, so reading the body top to
bottom is doing the work (D-13). One line before the first step puts every rule in the body under the
same addressee — the work, the produced document or the outline built toward it, never the prompt —
so no rule needs a local marker to be read correctly (4.1). Building fresh means the AI tells never
take hold in the first place; a final floor-net pass (after the ceiling is built) catches only the
stragglers.
Voice, form, and axis are all derived from a reader definition captured early in the procedure, so
the output actually varies with who is reading rather than reproducing one memorized shape.

### 3.2 What are the pieces, and what is each responsible for?

| Actor | What it is |
|---|---|
| `instruction.md` | Verbatim source of record for the skill's pillars (except the five-axis skeletons, superseded by D-6 research). |
| `SKILL.md` — the ordered steps | Instructions to the model running the skill: understand → define reader → outline → fill → check story → decide voice/form → write → brush up → clear floor → self-check → reader trial & deliver. |
| `SKILL.md` — the rules inside the steps | Constraints on the produced document, each carried by the step that applies it: voice and form at step 6, the three claim statuses at step 7, the ceiling at step 8, the seven-tell floor at step 9. One line before step 1 puts all of them under the same addressee — the work, never the prompt. |
| `references/axes.md` | The five axis skeletons. Step 3 orders the read and quotes the chosen skeleton's slots; step 10 re-reads the file and checks that quotation word for word. The pointer carries no summary. |
| The writer (human or Claude) | Runs the skill against an input draft (or a topic, from scratch), producing the document plus a "what changed and why" note. |
| Fresh-context reader (subagent) | Reads the produced document as the step-2 reader (one per part, for a declared composite), given only the document and that reader definition; reports stumbles and content the reader did not need. Delivery is gated on its prose defects being cleared (D-8, D-10). |
| Produced document | The end artifact judged against the floor/ceiling bar — never the prompt itself. |

### 3.3 How does work move?

```mermaid
flowchart TD
  a["Understand the input"] --> b["Define reader & purpose<br/>(one person, one reading stance)"]
  b --> c["Outline from purpose<br/>(pick one of five axes, no mixing)"]
  c --> d["Fill outline with the message"]
  d --> e["Check the story as the reader"]
  e --> f["Decide voice & form<br/>(derived from purpose+story)"]
  f --> g["Write"]
  g --> h["Brush up to the ceiling<br/>(minimal reader effort to the purpose)"]
  h --> i["Clear the floor (final net)<br/>scrub the seven AI tells"]
  i --> j["Self-check the mechanics"]
  j --> k["Reader trial<br/>fresh-context subagent: document + reader only"]
  k -->|"prose defect<br/>or unneeded content"| l["Fix, re-run steps 10–11<br/>(three rounds at most)"]
  l --> j
  k -->|"subject defect"| m
  k -->|"no prose defect left"| m["Deliver<br/>document + what-changed note<br/>(subject defects named, not patched)"]
  b -. "admission gate<br/>(headings, points, rendering, ceiling)" .-> c
  b -. .-> d
  b -. .-> g
  b -. .-> h
```

## 4. Detailed design

### 4.1 What keeps a rule about the produced document from being read as a rule about this prompt?

The guarantee: a rule about the *produced document* (e.g. "render structure/flow as mermaid") is
never misread as a property of the *prompt itself* — the original SKILL.md embedded a procedure
flowchart in its own body, which was exactly this category error (D-3). It first rested on one
sentence at the head of a `## Reference` section — a section D-13 dissolved; it then rested on that
sentence repeated verbatim at five blocks, which cost more than it bought. Five identical bolded
sentences are the restatement the floor's tell 2 forbids and the decoration step 8 rules against, one
of them had no antecedent to attach to, and enumeration still missed three rule blocks: the
composite's per-part reader and axis heads, step 10's checklist, and step 11's reader brief.

It now rests on **scope rather than enumeration, cut by grammar rather than by topic**. `SKILL.md:12`,
before the first step, states once that the imperatives address the run and none of them acts on this
prompt; orders every rule — in this file and in the files the steps order the run to read — read as a
rule for the work, the produced document or the outline built toward it, never for this file; and
states that steps 10 and 11 test that document.

**Coverage is over every rule, not over every sentence.** A declarative that describes the procedure
rather than constraining an artifact — "the author cannot simulate ignorance" (`:124`), "the floor is
table-stakes" (`:90`) — has no addressee to get wrong, so it needs none assigned. The wording this
replaced claimed that *every* non-imperative statement in the body described the produced document,
which was false of at least eight of them, and of itself: a scope sentence that mis-states what it
covers commits, one level up, the category error the guarantee exists to prevent. Naming the work's
two artifacts — the document, and the outline built toward it — is what makes the claim true without
reintroducing a classification step: a rule's own wording already says which of the two it acts on
(`:47` fills bullets, `:78` governs the rendered claims), and the scope line only has to exclude the
third candidate, this file.

The first version of the scope line cut by topic instead ("every rule below about how a document
should read"), which asked the run to classify a block before applying the rule to it — and
misclassifying a block's addressee is the very error the guarantee prevents. It also delivered the
scope as a list of five terms defined 70-odd lines further down, reintroducing at sentence level the
enumeration gap the move to scope had just closed. A grammatical cut needs no classification and no
list, so no rule can sit outside the statement, including rules added later, and `references/axes.md`
needs no head note of its own. Where the misreading actually happened the addressee also rides in the
rule's own sentence, at no repetition cost: the form rule that produced D-3 reads "choose the form
that carries it fastest in the document you produce" (`:64`).

The breach-catch is in the body, where completion criterion 2 requires it: step 10's last item
(`:120`) makes the run confirm that the ceiling, the floor, the forms and the claim statuses were
judged on the produced document — not on this prompt, and not on the outline it was built from. It is
worded against those four rule families rather than against "every rule above" because steps 3 to 5
carry rules that are *about* the working outline (one fact per bullet, walk the filled outline), so a
blanket claim that no rule was judged against the outline is false for a correct run.

Two greps back the item from outside the run, scoped to `writ/skills/`. The first detects D-3's
actual failure rather than asking the run to attest anything, and costs nothing to run:

````
grep -rn '```mermaid' writ/skills/   # empty: no diagram sits in the prompt body
grep -rn "not of this prompt" writ/skills/   # exits 1: no verbatim addressee marker survives
````

Unscoped, the second command matches this file and `checks/12.md`, which quote the marker to record
its removal — the claim holds only under the skill directory. Neither grep is what the guarantee
rests on, but the mermaid one would have caught D-3 on its own, so it is no longer left to whoever
remembers to type it: steering's `# Rules` puts it in the validation gate beside the two
`claude plugin validate` runs, where every task already runs it.

It is deliberately not an acceptance criterion — the criteria state what a run achieves, and where
the addressee sentence physically sits is a decision, not an end (D-12).

### 4.2 What does the floor-as-final-net ordering guarantee, and how is a breach caught?

Guarantees that ceiling work (density, concreteness, one thread, earned figures, consistent voice —
step 8) is never wasted by being layered onto a draft's uncleared AI tells, without paying the cost
of a separate pre-scrub pass: because the document is rebuilt fresh rather than edited in place, the
old draft's tells do not propagate into the new prose to begin with, so the floor pass (step 9) only
has to catch stragglers introduced during writing, not the input's original problems. A breach — a
tell surviving into the delivered document — is caught by step 10's self-check, which re-verifies
"none of the seven tells remain" before delivery, and by the what-changed note's closing line naming
any tell the net caught.

### 4.3 What does the five-axis, single-axis outline guarantee, and how is a breach caught?

Guarantees the document has one coherent shape suited to how its reader actually reads (through, or
looking one thing up) rather than a blend of incompatible structures. Guaranteed by step 3 ("exactly
one axis... off-axis material stays out"), with 4.11's declared composite as the one sanctioned
exception — parts, each with its own reader and axis, never a blend. A breach — a document mixing
axes inside a part, or carrying off-axis material — is caught by step 10's self-check item "One axis,
no mixing," and off-axis material is named (not authored) in the what-changed note.

One skeleton contradicted the ceiling it serves. The article axis read *the question → the substance
→ in closing*, which distributes the answer through the middle and sums it at the end, while step
8's ceiling asks for "the conclusion first." Slot 1 now carries the question **and its answer**; "In
closing" is limits and pointers, explicitly not a recap. The other four were re-checked under the
same lens and already lead with their answer — the guide with the goal, the reference with the map,
the ADR with the decision as the headline, the evaluation with the recommendation.

That fix lives in `references/axes.md:6` alone, and the skeletons are the one block a model can
produce a plausible version of from memory (D-13) — a from-memory article skeleton reverts slot 1
while "One axis, no mixing" still passes. So the skeleton is now quoted, not recalled: step 3's emit
(`:43`) carries the chosen axis's slots **as they stand in the file**, next to the headings
specialized from them, and step 10 (`:110`) re-reads `axes.md` and checks that quotation word for
word. A breach — a confabulated skeleton — is visible in the produced run's own output, since the
quoted slots and the file can be set side by side by anyone reading the transcript.

What is checked is the **fidelity of the quotation**, not identity between the outline and the
skeleton. An earlier wording demanded the outline match the skeleton "slot for slot", which
contradicted step 3 in the same breath: step 3 drops a heading the reader does not need (`:34`),
raises a **proposed slot** the skeleton has no counterpart for (`:35`), and forbids filling an
unjustifiable slot (`:37`), so a correctly specialized outline failed the check every time. The
skeleton is a starting shape the reader may argue against; what may not vary is the file's own words,
which is where confabulation shows. So the item now compares the quotation to the file and requires
every departure of the outline from the quoted slots to be one the step-3 admission argued for, and
`axes.md:3` names the numbered items as slots so the two files use one word for the same thing.

Where the read itself fails, step 3 (`:41`) forbids falling back on memory silently: say so, ask for
the file, and headless, outline anyway, quote no slots, and record the outline as unverified against
`axes.md`. That path needs a verdict at step 10, since the item orders a re-read the environment
cannot serve and "any FAIL, fix and re-check" is an unsatisfiable loop when the file is unreadable.
Step 10's lead (`:106`) defines one: an item whose evidence sits in a file the run cannot read is
marked UNVERIFIED and named in the note, never settled from memory. It is defined once, at the place
the verdicts are defined, and covers a failed re-read at step 10 as well as a failed read at step 3.

### 4.4 What does the reader-definition gate guarantee, and how is a breach caught?

Guarantees voice, form, and axis are derived from an actual reader rather than assumed or memorized —
the acceptance criteria specifically require that two different reader definitions change the
output's voice and axis, proving derivation rather than memorization (D-6's five-axis re-sourcing
exists in service of this same guarantee: the skeletons come from external best practice, not from
`instruction.md`'s fixed wording). Guaranteed by step 2's gate: "if a line cannot be answered from the
input, ask the user" (or, headless, infer and disclose via `Assumed reader: …`) — never leave a line
blank. A breach — an inferred-but-undisclosed reader, or a document whose voice/axis does not track
its stated reader — is caught by step 10's self-check items "Assumed reader: line present iff the
reader was inferred" and "Voice and closing fit the step-2 reader."

### 4.5 What does reader-gated content admission guarantee, and how is a breach caught?

Guarantees that no sentence ships because someone once wanted it there. The step-2 reader is not
only the source of voice and axis (4.4) but the **admission criterion for content**: a heading
(step 3), a point (step 4), a sentence that first appears at rendering (step 7), or an example added
while reaching for the ceiling (step 8) enters only if that reader needs it to reach the purpose.
Material serving a different reader — a re-reader, a past reviewer, an approver — is routed to the
what-changed note (whose it is, where it belongs) instead of shipping as noise. A user-supplied
outline or format faces the same test slot by slot: an unjustifiable slot is an axis conflict, raised
with the user (headless: recorded in the note) and never silently filled. A breach — noise surviving
into the delivered document — is caught twice: by step 10's admission self-check item, and by the
step-11 reader trial reporting content it did not need.

**The test runs both ways.** As first written every verdict it could return was removal, so a reader
need the format had no slot for had nowhere to go. Four fresh readers, across two rounds and two
independently written documents, then prescribed the same single change in near-identical words —
put the discharge at the front — and writ *detected* it every time: step 11's headings question, all
three trial rounds, the ceiling's own "conclusion first." What it could not do was act. The supplied
format assigned the properties to chapter 1 and their discharge to no chapter at all, so the run did
what writ said — recorded three axis conflicts and proceeded — and its only structural repair was
renaming a heading inside chapter 2, which the reader answered with "contradicted by its own second
sentence."

Step 3 now tests in both directions. *Slot → reader* is the original subtraction. *Reader → slot*
lists what the reader must have to reach the purpose and names the slot carrying each — and a slot
that defers the thing elsewhere does not carry it, which is the same field failure in its second
form: a chapter declared "Format definitions live here" that both documents emptied, and both
readers dead-ended in. A need with no slot is raised as a **proposed slot**, with its position and
the reader evidence attached; headless, it is placed where the reader needs it and recorded as a
proposal on the format. Step 11 gained the matching stumble class (4.9) so a trial's finding routes
there instead of being absorbed as prose under the nearest heading. A breach — an unslotted need
buried — is caught by step 10's admission item, now stated in both directions, and by the next
trial reporting the same stumble.

Origin: a real run (PR #15 comment 5353396410) delivered a document its owner judged noise-ridden
while every writ check passed — because the reader governed only form, so content for other readers
passed straight through. The additive direction came from the round-3 re-run
(`worktree-aiya:.rn/20260813-aiya/writ-feedback-3.md`), where a defect survived every round of a
procedure that correctly diagnosed it.

### 4.6 What does verification independence guarantee, and how is a breach caught?

Guarantees that the experiential claims — the document reaches the purpose read top to bottom, and
the headings alone carry the argument — are judged by someone the curse of knowledge cannot blind.
The author, having built the outline, cannot un-know it, so those two checks move out of step 10 and
into step 11: a fresh-context subagent given **only** the produced document and the step-2 reader
definition — no outline, no draft, no history. Its prose stumbles come back as fixes and the
document re-runs steps 10–11 until none remain (4.9 sorts them; 4.10 bounds the loop). Mechanical
checks (single axis, skeleton fidelity, `Assumed reader:` line, claim statuses) stay with the author,
where knowledge of the draft is no handicap.

A breach — the trial run with extra context, or its stumbles waved through — is caught in the body at
`SKILL.md:141`, which makes the what-changed note list what each trial was handed, item by item, and
every stumble it reported with its class and what was done about it. Both breaches then sit in the
run's own output: a brief carrying more than the document and the reader definition is a listed item
that should not be there, and a stumble waved through is one with no disposition beside it. For the
stumbles that is a detection — the trial reports are committed beside the note, so a third party can
read one against the other. For the brief it is an **attestation**: the note carries the run's own
description of what each trial was handed, not the brief itself, so a run that over-briefed lists two
items anyway and nothing contradicts it. Making that half a detection too would take one clause —
reproduce each trial's brief verbatim in the note, so what the trial quotes back can be compared
against what it was given — and it is not taken here, because the note already carries the reports it
would be compared with. Undetected, the breach shows up after the fact as the same field failure 4.5
records: checks pass, the reader still struggles.

The trial's brief also asks what read as machine-written. A delivered document that had passed step
9, step 10 and three trial rounds still carried, for a fresh reader, a sentence repeated near-verbatim
thirty words later in the same paragraph and a mermaid arrow running the wrong way in a diagram the
last round had just edited. Both are the class the curse of knowledge hides — the author re-reads the
intended sentence, not the written one — so noticing them belongs with the reader, not the author's
own pass.

Where the environment cannot launch a subagent at all, the gate cannot run. Step 11 forbids the
author standing in for it — that substitution is precisely what the step exists to prevent — and
requires the delivery note to state that the trial did not run, so an unverified document is never
mistaken for a gated one — `SKILL.md:139` carries that fallback. The frontmatter used to restate it
in a `compatibility:` field, which has been removed: the field never reaches the run. A probe skill
carrying one unique token in `compatibility:`, one in `description:` and one in its body heading was
invoked headlessly and asked to quote its instructions verbatim. What came back was a
harness-generated `Base directory for this skill: <path>` line and then the body from its `#`
heading: the body token present, the `compatibility:` token reported absent from the whole context,
and the `description:` token present only in the available-skills listing, not in the instructions.
So the body is what reaches the run as instructions and `description` reaches discovery; no
frontmatter field declares a runtime dependency to the run — a dependency has to be stated in the
body, and this one is.

### 4.7 What makes "build fresh" a mechanism rather than an intention, and how is a breach caught?

Step 1's "you will not reuse its sentences" is an instruction, and an instruction is not a
mechanism. A controlled rebuild measured what actually happened: **127 maximal shared 8-token spans
with the source, several 15–24 tokens long** — whole clauses reproduced verbatim by a run that had
been told to build fresh. Three things now carry the load the instruction was carrying alone. Step 4
requires the outline's bullets to be in the writer's own words, so the input's phrasing has no
vehicle into the draft. Step 7 **closes the input**: from rendering onward the filled outline is the
only source, the draft is not open. Step 10 adds a mechanical item that reads the two texts side by
side and confirms nothing survives but names, identifiers, defined terms, and deliberate quotation —
"having been told to rebuild is not evidence that you did." A breach is caught at that item, by an
author for whom this check carries no curse of knowledge.

The measurement then moved earlier. Built as above it worked: the step-10 item **failed a rebuild's
first render** — 177 maximal shared 8-token spans, the longest 312 tokens, 70.87% of the document
inside a shared span — and forced a second render from meaning that ended at 6 spans, longest 13
tokens, 0.64%. But the leak was in step 4, not step 7: the outline had been filled with the input
open and had transcribed the source's sentences, so closing the input at step 7 protected nothing
already inside the outline. Step 5 now reads the filled outline against the input, where a failure
costs one re-fill; step 10's side-by-side stays as the backstop, and is the expensive one — by then
a whole document has been rendered from the leak, and a second render is what a tired run skips.

Stakes: a rebuild that silently carries its source's wording is not independent of the source, so a
comparison between the two measures the document, not the procedure.

### 4.8 What does reading the input's claim statuses guarantee, and how is a breach caught?

Guarantees that a proposal in the input survives as a proposal, instead of being deleted for failing
to match a world that has not caught up with it. The asymmetry was live: the output rules already
demanded that every claim in the **produced** document carry a status (fact / hypothesis /
decision), with no counterpart for reading the **input**. In the field run, the rebuild checked a
design's claims against the shipped plugin, found the described file absent from disk, and dropped a
design that was deliberately ahead of the build and awaiting approval — a filename, a ledger row,
four fields, six rules, gone. Step 1 now sorts the input's assertions into in force / proposed /
hypothesis and emits the proposed ones, and states that content leaves only through the step-3
reader admission — never on the ground that reality has not caught up. The decision status (now at
step 7) gained "and one not yet in force says so," so the status survives into the output. A breach —
a proposal dropped, or shipped unmarked — is caught by step 10's claim-status item and by the note's
list of what was kept out.

### 4.9 What does stumble triage guarantee, and how is a breach caught?

Guarantees the procedure never smooths over a defect in the thing being described. Step 11 said "fix
every stumble," which forces a rewrite onto stumbles no rewrite can reach. The field run shows the
failure exactly: a reader reported that a mechanism count did not add up, a reconciling clause was
added, and the next fresh reader flagged **that clause** as its own stumble — *"So the 'two
mechanisms' I was just handed are six legs"* — while a second reader, on a different document and
unable to see the first, prescribed the real fix: strike the claim, do not gloss it. Six further
objections came back identically from two readers who could not see each other's document; they are
properties of the subject, and no rewrite of either document removes one. Step 11 now sorts each
stumble into **prose defect** (writ's, fix it) and **subject defect** (named in the note for whoever
owns the subject, left standing or struck, never patched). A breach — a subject defect quietly
glossed — surfaces as the same thing it surfaced as here: the next fresh reader stumbling on the
gloss.

A third class followed from 4.5. A **format defect** is a document arranged as a supplied format
demands where the reader needs an arrangement that format cannot express — the answer stranded at the
back being the standard case. No rewrite inside the slots reaches it, and the field attempt at one, a
heading rename, drew "contradicted by its own second sentence." It routes to 4.5's proposed slot,
carrying the reader's own words as evidence, and ships named if the owner has not ruled on it.

### 4.10 What gives the delivery gate a termination, and how is a breach caught?

Guarantees the gate can actually open. "A clean pass — no stumbles, no unneeded content — gates
delivery" had never once been reached: under a head-to-head prompt two readers reported **20 and 18
stumbles**, and an earlier run had to invent a 3-iteration cap locally and close with two residuals
flagged, because writ offered no termination rule. A gate that never opens is not the gate — the
operator's improvised cap is, which means the real rule lived outside the procedure and varied by
run. Two changes make it terminate: delivery is gated on **no prose defect remaining**, so subject
defects (4.9) ship named rather than blocking forever; and the fix-and-retrial loop stops after
three rounds either way, delivering with any survivor named. A breach — an unbounded loop, or
delivery with an unnamed prose defect — is caught by the note, which must carry every residual.

The cap then showed its own edge: as written it permitted the last action of a run to be an
**unverified edit**. A field run repaired a width-versus-size contradiction after round 3 reported
it, with no fourth trial; the later head-to-head found the repair had not worked — one line said a
2,000-byte ceiling governs the file "however wide the wave was — it fails nothing", the next that
growth stays sub-linear "under a ceiling that stays put" — and the reader called it the sharpest
confusion in the document, sitting on the very property it was asked to judge. The loop now ends on a
trial, never on an edit: when the cap falls after a fix, one fresh reader gets the changed passages
and only those, and whatever that read cannot confirm ships named as unverified. The last round's
stumbles are the hardest ones, which is exactly why the last edit must not go out unread.

### 4.11 What does the declared composite guarantee, and how is a breach caught?

Guarantees writ has a legal answer for a document that genuinely serves two readers, instead of
failing by design. "Match the reader and purpose to exactly one axis. Do not mix axes" met a
ratified design document that is argument in its first half and reference in its second: the
rebuild's own step-10 self-check recorded a **FAIL it declared unfixable at that level**, and both
readers, on both documents, rejected the same chapters as not theirs. A self-check that fails by
design tells the author nothing. Step 3 now names the split as the first answer — two axes means two
documents, say so — and, where the owner keeps one file, sanctions a **declared composite**: each
part carries its own step-2 reader line and its own axis at its head, every admission runs per part
against that part's reader, and step 11 runs one trial per part given only that part. Readers are
never blended inside a part. Step 10's axis item was rewritten to accept exactly this shape and
nothing looser. A breach — a blended part, or an undeclared mix — is caught by that item, and by the
per-part trial reporting material its reader did not need.

Declaring the parts made the boundary explicit without making the parts separable. In the round-3
rebuild, part 1 deferred into chapter 5 about two dozen times (§5.1, §5.3–§5.7), and the part-1
reader's *first* stumble was that: "I had to decide on every deferral whether the argument was still
complete without it." Both part-1 readers, in both rounds, then left chapters 1–4 unable to decide,
because the bound they needed sat in §5.4. So the composite now has to earn its declaration:
step 5 (`:51`) walks each part alone in its own reader's order: a part whose reader cannot reach its
purpose without crossing into the other is not a part, and the split goes back to the owner as the
answer. The separability rule is written at step 5, where it is performed. Step 3 (`:39`) mandates the
declaration itself — each part's own step-2 reader line and axis at its head, every admission run per
part, and the composite and the refused split recorded in the note — and states that a composite has
to be two documents in fact, naming step 5 as the test. Without that test, "declared composite"
is available as the cheaper option at exactly the moment the split is the right one.

The composite also had to reach the quotation rules. Step 3's emit (`:43`) and step 10's fidelity
item (`:110`) were both written in the singular — "the axis chosen", "the slots quoted at step 3" —
so a two-axis run had no wording telling it to quote and re-check two skeletons, while `:109` next to
it explicitly accommodated one axis per part. Both now read one per part.


## 5. Alternatives considered

### 5.1 Why this shape, and not another?

- **(D-1) Plugin `writ` / skill `up`, not matching names** — chosen over the official same-name
  convention, because the skill name is typed often (keep it short) and plugin/skill names are
  independent slots (`rn:gm` is the precedent); "up" fits the primary brush-up-a-level mode.
- **(D-2) Model-invocable (no `disable-model-invocation`)** — chosen over `rn`'s pattern of disabling
  model invocation, because the distinguishing axis is who the skill is for, not side effects: `rn`
  is meant for a human to drive, `up` is meant for a human or Claude itself.
- **(D-3) Two layers physically separated in the body** — chosen over the original SKILL.md, which
  embedded a procedure flowchart in the prompt body (see 4.1). **Superseded by D-13:** the
  process/output distinction stands, but the physical separation is gone — and so is the per-block
  marker that briefly replaced it. One scope line before step 1 now addresses every rule in the body
  (4.1).
- **(D-5) Rebuild fresh from the input's intent, floor as a final net** — chosen over an edit-the-
  draft-in-place runbook (scrub first, reorder later), which drags the old wording along, reads as
  patched, and behaves as a checklist rather than a writing procedure.
- **(D-6) Five-axis skeletons re-sourced to researched best practice** — chosen over `instruction.md`'s
  verbatim outlines, per the user's ask for the current recommended structures. Source of truth:
  Diátaxis (explanation/reference/tutorials), MADR 4.0, AWS ADR guidance, Google/Microsoft procedure
  style guides, GitLab task types, and Google SRE postmortems — not `instruction.md`. `instruction.md`
  stays the source of record for the other pillars; only the five skeletons deviate.
- **(D-7) Renamed `techting` → `writ`, skill stays `up`** — chosen over keeping the name and just
  rewording the framing, because the plugin name itself was the one thing still narrowing scope to
  "technical" writing. D-6's sourcing already showed the five axes are general document genres, not
  technical-writing-specific — the mechanism was general from the start; only the label lagged.
  `writ` + skill `up` gives `/writ:up`, read as "write it up", with no redundant "up up".
- **(D-8) The reader gates content, and a fresh reader gates delivery** — chosen over adding more
  checks to the author's own self-check list, after a real run (PR #15) shipped a noise-ridden
  document with every check passing. Two structural changes rather than nets: the step-2 reader
  becomes the admission criterion for content, not just the source of voice and axis (4.5), and the
  experiential checks move to a fresh-context subagent whose pass gates delivery (4.6). Consequence:
  the ceiling's target is restated as minimal reader effort to the purpose, with density demoted to a
  means.
- **(D-10) Field round 2 — turn the standing instructions into mechanisms, and give writ a legal
  composite** — chosen after a controlled experiment (PR #15 comment 5469096123) in which a
  blank-page writ rebuild was judged against the hand-patched document by two fresh readers under an
  identical prompt: both QUALIFIED, and **the rebuild read easier — effort 3 vs 4 — despite being 27%
  longer**. The procedure's output won on the thing the procedure exists for, so the five changes
  taken are about the places it got there despite writ. Three of them are the same shape — an
  instruction with no mechanism behind it — and are fixed by giving each one: "build fresh" (4.7),
  "fix every stumble" (4.9), "a clean pass gates delivery" (4.10). The other two are about what the
  input actually is: its claims have statuses writ never read (4.8), and its shape may legitimately
  serve two readers, which writ forbade without offering an alternative (4.11).
  **Then declined — a length measure.** The evidence offered for it was the same 27% growth, uniform
  across all seven chapters (+59/24/17/31/26/41/21%), which no step in the procedure noticed. But the
  document that grew was the one that read *easier*, so the growth was the good case, and the reader
  trial is already the instrument that told the two cases apart. A recorded length ratio with no bar
  attached would put a proxy next to the real target — minimal reader effort — where it can only
  compete with it. The decline named the evidence that would reopen it: growth the reader trial
  passes that a human still judges bloated. **Round 3 produced it** — see D-11.
- **(D-9) Retire the self-imposed 2,000-word cap, keep the official <500-line bound** — chosen over
  holding the cap, because it had no external basis and had started driving the edits: task #7 paid
  for its additions with twelve meaning-preserving trims and a three-word recast (`checks/7.md`), and
  step 11 had compressed into a single 670-character paragraph. The official numbers are not one
  figure: `plugin-dev/agents/skill-reviewer.md:68` gives 1,000–3,000 words for the body, while
  `plugin-dev/skills/skill-development/SKILL.md:190` and `:220` set a tighter target of 1,500–2,000
  words for the same thing. The body is 2,677 words over 137 lines — inside the reviewer's band,
  well above the leaner target, and at a quarter of the 500-line bound. The 1,500–2,000 figure is
  stated as a target rather than a limit and is not being met; the constraint held here is the line
  count, which is where the reader's cost actually shows, and the word budget the cap imposed was
  a third tighter than the reviewer's ceiling — 2,000 words against 3,000. Traded away: an explicit
  stop against creeping length — replaced by a bound with room to say things once, clearly.

- **(D-11) Field round 3 — the admission test runs in both directions, and each check moves to where
  its failure is cheap** — chosen after the round-2 re-run
  (`worktree-aiya:.rn/20260813-aiya/writ-feedback-3.md`), the first honest head-to-head writ has had.
  D-10's carryover mechanism is what made it honest: it failed the rebuild's first render at 70.87%
  shared text and forced a rebuild from meaning, which also retired round 1's "the rebuild won on
  effort 3" — that document had silently inherited most of its predecessor's phrasing, so the number
  measured the source, not the procedure. The honest comparison is **a tie**: both QUALIFIED, both
  effort 4, the rebuild 43% longer. Six changes follow, and the first is the one the tie is about.
  The admission test was subtractive only, so a defect four readers named in near-identical words
  survived every round of a procedure that diagnosed it correctly (4.5); writ's own article skeleton
  disagreed with its own ceiling about where the answer goes (4.3); the carryover measurement sat one
  step downstream of the leak (4.7); the trial's brief left floor-level tells to the author who cannot
  see them (4.6); the three-round cap let a run end on an unverified edit (4.10); and a declared
  composite could be declared without being separable (4.11).
  **Reopened from D-10 — record the size and argue for it, still no bar.** The same procedure that
  bought easier reading with 27% in round 1 spent **43% for no gain at all** in round 2 — effort 4
  against effort 4, and the story chapters grew fastest (+52/58/19/54/46/32/11%), so this was not
  contract detail. The argument against a *bar* stands unchanged: a number competing with reader
  effort is a bad instrument. What the round supports is a **recorded ratio the author must argue
  for**, which surfaces the growth during the run, while a fill can still be un-admitted, instead of
  after delivery. Step 10 records it; there is nothing to pass or fail, and growth no one can argue
  for is unadmitted fill.

- **(D-12) Acceptance criteria state ends; the means live here** — chosen after the criteria had
  accreted ten implementation clauses out of sixteen: a physically separated `## Reference` section, a
  1,000–3,000 word body, no mermaid in the prompt body, and three field-feedback rounds written as
  step-numbered checklists of `SKILL.md`. Means in a criterion invert the relationship they are
  supposed to serve: any change to how the skill is built fails the criteria, so the document that
  judges the results ends up freezing the construction. The criteria are now nine ends — eight on what
  a run produces, one on reach — and every mechanism they used to name lives in this file, §4 for what
  it guarantees and §5 for why it was chosen. Traded away: the criteria are no longer checkable by
  reading `SKILL.md`, so the sign-off needs a real run to judge criteria 1–8, and each field round has
  to be traced through §4 and the `checks/` files rather than read off its own criterion line. That is
  the intended cost — a criterion satisfiable by inspecting the prompt was never evidence that a
  reader was served.
- **(D-13) Every rule at the step that uses it; the axis skeletons in `references/`** — chosen over
  the catalog-and-pointers shape, a `## Reference` section the steps pointed into. A rule the run
  has to go fetch is a rule the run can shorten, skip, or supply from memory, which is the drift
  writ exists to fight running inside writ itself. Each block now sits at its moment: voice and form
  at step 6, the three claim statuses at step 7, the ceiling at step 8, the seven-tell floor at step
  9. The five axis skeletons moved out to `references/axes.md`, which step 3 orders the run to read
  before it picks an axis — the pointer names the file and says nothing about its contents, since a
  summary at a handoff is exactly what lets the read be skipped. **The criterion for what may move
  out is memory-substitution risk, not length.** Length and a single use-site were what this
  decision first recorded, and they answer a different question: the risk a split runs is the
  fetched block being supplied from recall instead of read. Ranked by that risk the axes are the
  *worst* candidate on offer, not the best. The seven tells, the voice table and the ceiling are
  writ-specific lists a model cannot confabulate, so a split would have been cheap there; the five
  skeletons are Diátaxis/MADR-shaped, so a plausible reconstruction is precisely what a model can
  produce — and it would silently revert 4.3's slot-1 fix with every check still passing. What buys
  the split is therefore not the size argument but the fidelity check taken with it (4.3): step 3
  quotes the chosen skeleton's slots as they stand in the file, step 10 re-reads and checks that
  quotation word for word, and a failed read may not fall back on memory silently — it is marked
  UNVERIFIED and named in the note. Exposure is bounded on the other side too: the frontmatter
  `description` already names all five axes, so the pointer withholds only the skeletons — the names
  stay in the description, since skill discovery depends on them. The addressee guarantee did not
  move with the rules; it moved to scope (4.1). Traded away: reading every output rule in one place
  — recoverable only by reading the procedure, which is the point. Measured effect on the body
  (everything after the closing `---`): 185 lines / 2,864 words → 137 / 2,677, against the official
  bound of under 500 lines (`skill-creator/skills/skill-creator/SKILL.md`) and the two official word
  figures D-9 records.

### 5.2 What did we trade away?

- **(D-4) Purpose reframed as a human-readable end, quality in two tiers** — chosen over treating
  "reader-first procedure" as the end goal in itself; the procedure is the *means*, not the point.
  Traded away: a simpler one-tier "just make it good" bar, in exchange for an explicit floor/ceiling
  split that makes "cleared but unremarkable" a distinct, nameable state from "actually worth
  reading."
- Splitting the axis skeletons out (D-13) trades a skill that reads start to finish without following
  a link for a body that carries every rule at the step that applies it. The one link is ordered, not
  offered: step 3 reads `references/axes.md` before it picks an axis, and step 10 re-reads it to check
  the step-3 quotation against the file. Body: 137 of the official 500 lines.
- Round 3 had left the body at 2,864 words against the official 1,000–3,000 band, with the next
  addition owing a trim. D-13's rebuild spent that debt rather than deferring it, landing the body at
  2,439 words with 384 words of axis skeletons moved to `references/axes.md` (that file is 372 words
  now, after its head note came out and the slot definition went in); three fix rounds since —
  reworking 4.1, 4.3, 4.6 and 4.11 — left the body at 2,677 words over 137 lines (body only — the
  whole file, frontmatter included, is 2,780 words and 141 lines). Word count is no longer the
  binding constraint on what the body may say.
- Re-sourcing the five axes to external best practice (D-6) trades fidelity to the user's original
  verbatim `instruction.md` outlines for current, externally-validated structures — accepted because
  the user explicitly asked for the current recommended shapes over the original wording.
