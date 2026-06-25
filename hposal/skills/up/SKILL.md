---
name: up
description: Build a corporate-site (HP) estimate and client proposal across four phases — requirements → proposal design → work breakdown → proposal — each ending in a human review gate (★). Typically launched via /hposal:up. Drives the AI to draft, self-review, and stop for human feedback at each gate. Has side effects (creates files), so run it only on explicit invocation.
disable-model-invocation: true
---

# How this works (the workflow)

This file is the **single procedure** the AI follows. The reasoning and the pitfalls are not split into other files — they are embedded into each step as work instructions, because anything split out is not honored at run time. The "why" for humans lives in `README.md`.

**Output language.** This kit (this file, the templates' structure and guidance) is written in **English** — it is the tool. The **deliverables and the conversation are in the language the user works in — default Japanese**, because the proposal is read by a Japanese client and reviewed by a Japanese proposer. Language is a run-time choice about the output, not part of the method. The one exception that is fixed in a template: the client-facing copy inside `04_proposal.html` (slide text, section titles shown in the PDF) is Japanese, because that file *is* the client touchpoint.

Four phases. Each phase produces one internal document; the last phase produces the deliverable handed to the client. The leading number in each filename = the order to read and to build.

```
01 requirements → 02 proposal design → 03 work breakdown → 04 proposal (.html → .pdf)
   (internal)        (internal)            (internal)          (external → delivered)
```

## Where the work lives (set up once)

Before phase 1, fix where the working files go, so they don't scatter across runs.

- Propose a **project folder** named from the engagement (e.g. the client or site name) and confirm it with the user in one line. All working files live under it:
  `01_requirements.md`, `02_proposal-design.md`, `03_work-breakdown.md`, `inventory/<site>.md`, and `04_proposal.html` → `04_proposal.pdf`.
- Put the final exported PDF (and only the PDF) under a **dated subfolder** of the project folder. Keep internal files (`.md`, spreadsheets) out of the delivery folder.
- **Resuming.** `/hposal:up` is one long run broken by ★ gates, so it can stop mid-way. To pick up: the **presence of each output file plus an approved ★ gate** tells you how far you got. Resume at the **first phase whose output file is missing, or whose ★ gate the human has not yet approved**. Never silently redo an approved phase.

## Internal estimate inputs (gather once, before phase 2)

Phases 2–3 cannot price the work without a few internal values that only the human can supply. Gather them **once, up front in a single ask** (right after the phase-1 ★, or earlier if the human offers them), so the estimate doesn't stall mid-phase or get built on a guessed number.

- **Day rate** (currency/person-day, internal/non-disclosed) / **direction (management) markup %** / **subcontractor tax treatment** (is the subcontractor quote tax-included or -excluded; the subcontractor's invoice & tax status) / **staffing** (who is involved and how much — dedicated/shared).
- **Never invent any of these.** If the human hasn't given a value, hold it as an open question (q) and carry it to the ★ gate, exactly as for any other unconfirmed premise. A fabricated rate silently corrupts every downstream amount and reads as fact — the worst failure mode of this kit.

## Fill-in templates

Each phase's output is made by copying the empty skeleton under `${CLAUDE_PLUGIN_ROOT}/references/templates/` and filling it in. Output-to-template mapping:

| Output file | Skeleton template |
|---|---|
| `01_requirements.md` | `${CLAUDE_PLUGIN_ROOT}/references/templates/01_requirements.md` |
| `02_proposal-design.md` | `${CLAUDE_PLUGIN_ROOT}/references/templates/02_proposal-design.md` |
| `03_work-breakdown.md` | `${CLAUDE_PLUGIN_ROOT}/references/templates/03_work-breakdown.md` |
| `04_proposal.html` | assembled from the slide parts in `${CLAUDE_PLUGIN_ROOT}/references/templates/parts/` per the `${CLAUDE_PLUGIN_ROOT}/references/templates/04_proposal.md` outline (`_head.html` + chosen parts in outline order + `_foot.html`) |
| `inventory/<site>.md` | `${CLAUDE_PLUGIN_ROOT}/references/templates/site-inventory.md` |

## How each phase runs (the AI/human split)

Every phase runs the same loop. This kit assumes **the AI does the work and the human gives direction and feedback**.

1. **The AI drafts.** From the input, it produces that phase's deliverable following the steps below.
2. **The AI self-reviews.** It reviews with an expert-role subagent (a fresh perspective checking accuracy and completeness) and fixes what it can fix itself.
3. **★ Human review = gate.** The human reads and gives feedback. The phase does not advance until the human says OK; keep improving until then.

## Rules for every step (read before you start)

Hold this stance whenever you run any step.

- **Confirm the purpose first.** Don't jump to editing or creating. Before starting, agree the purpose of that document/task with the human in one line. Starting without a settled purpose causes rework. ← always.
- **Don't over-confirm.** Lead with the conclusion; decide details from the purpose and declare them as assumptions. Confirm only the branches that would cause real rework (don't become an order-taker). This is separate from confirming the purpose: always take the purpose; turn details into assumptions.
- **Fact-based.** Don't invent numbers or premises that aren't in the input. Count real things (script / crawl) = don't take a stated number on faith. Where you can't confirm, make it an open question (q), settle it provisionally, and verify before building on it (don't be naively optimistic, and don't pad either).
- **Don't make the human's call.** Tag each fact with a category — [input] / [AI inference] / [needs human decision]. **Leave unconfirmed judgments as q and never let the AI claim "decided (X)"** — the migrate/don't-migrate line, the count denominator, the reading of a request are decided by the human at ★. Don't demote an input fact to a "hypothesis," and don't promote a pure AI inference to a "fact" — keep the category distinction sharp.
- **One fact, one place (single source of truth).** Each fact has exactly one source of truth: counts in 01 (the ledger) / estimate model & premises in 02 / amounts in 03 / terms in 04. **Everything else references that source and never re-counts or re-calculates** (02/03/04/design quote the ledger's value instead of counting again). The source points downstream, so 02/03/04 hold no back-references. Before each ★, reconcile the same metric (counts, amounts, durations) across documents — a split means something re-calculated.
- **Separate internal from external.** Day rates, person-days, %, actual subcontractor costs, and rationale must never appear in the client deliverable (html/PDF). The client needs only quantity/unit (scale), amount, and value. **Sourcing words are internal too** — 内製 / 外注 / 外部 / 二層 (in-house / subcontracted / external / two-layer) are an estimating distinction, not something the client needs; the team section gives the *result* (single point of contact, end-to-end, no hand-off loss), never the procurement structure.
- **Lead with value.** What the client wants to know is that "the problem is solved and the desired result is reached." Translate the maker's words into what the client gets. Build shared understanding starting from the present state, and include only elements that serve the goal. Don't flatly reject the client's existing ideas.
- **Documents show only the should-be.** Write only the current truth. Don't write history ("error → fixed," "old wording"), source tags, or slide-number lists (leave history to git / the conversation). Resolve a contradiction by rewriting the document to the truth, not by adding a note.
- **Console: conclusions only.** Report results; offer detail when asked.

## Traceability (the single picture)

The **requirement list (01) is the hub.** Number every row and trace outward from it. At each junction, count the columns and prove the gaps are zero (impressions leak; columns don't).

```
input ledger (i) ──→ requirement (r) 〔hub〕 ──→ proposal story (p, 02/04) / work (w, 03)
   what was seen        what to make/fix            how it's told           how much
open question (q) ─provisional FIX→ folded into requirement (r)
```

Each requirement has, upstream, an `origin` (which i / which interview), and downstream, a `p` + `w`. So at the end of each phase, check completeness **by counting, not by impression**: a requirement with no origin = a stray idea; with no `w` = a build gap; with no `p` = a story gap. Out-of-scope items are stated explicitly, never silently dropped.

This hub-and-trace model is defined **here, once**. The templates carry only the column that implements it; they do not re-explain it.

---

## Phase 1 — Requirements

**Input**: the client's input material, the current site. **Output**: `01_requirements.md` (+ `inventory/*.md`). Skeleton = copy and fill `${CLAUDE_PLUGIN_ROOT}/references/templates/01_requirements.md` (+ `${CLAUDE_PLUGIN_ROOT}/references/templates/site-inventory.md`).

1. **Build the input ledger and count the real thing.** List everything you'll look at at its smallest unit (page, screen). Crawl each current site **one page = one row** into `inventory/<site>.md`, and classify each page's section (company / services / cases / news / careers / contact …). Reconcile the real count against what the client stated, and record every discrepancy.
   - ⚠️ **Stated counts and real counts diverge** ("about 100" is really 130; "11 shown" is really 14). Migration is one page = one unit of work, so take **the larger real number** as the denominator and leave the gap as an open question (q).
   - ⚠️ **Fix the counting origin in the ledger and keep it identical across all sites** (e.g. if news is "migrate only from YYYY-MM on," count every site from the same origin). Mixed origins make the same "news count" differ per document. **The ledger is the single source of truth for counts.** 02/03/04 and `design/` only *quote* its value; they never re-count.
   - ⚠️ **Crawl, don't eyeball** (sitemap.xml / crawler / script). Eyeballing always misses pages, which surface after work starts.
   - ⚠️ **No sitemap, or a JS-rendered nav, is the normal case — have a fallback, don't stall.** If `sitemap.xml` (and `/sitemap_index.xml`, `robots.txt`'s `Sitemap:` line) is absent, fall back to a link crawl from the top page (e.g. `wget --spider -r -l<depth>`, or fetch and extract `<a href>` recursively). If the nav is rendered by JavaScript so the raw HTML has no links, say so in one line and crawl the rendered DOM (headless browser) instead of under-counting from static HTML. Record which method you used in the ledger's `出どころ`. Whatever the method, the count must still be a **machine count**, not an impression.
   - ⚠️ **Count mechanically.** Get total URLs and per-section counts by machine count (`curl … | grep '<loc>'` / sum child sitemaps for a sitemap index), not a summarization tool (e.g. WebFetch) — summaries make counts wobble (the same site swings 660/1023/1088). Note: cutting by publish date ("migrate only from YYYY-MM on") can't be judged from URLs alone — you need the published-date metadata. State this limit in one line to tighten the round-trips.
   - ⚠️ **Read input images at full resolution.** Reading slides/PDFs directly renders them low-res and misreads them. Reference the image for image-sourced specs; don't transcribe into prose and make a degraded copy.
2. **Structure the requirements and number them.** Sort into confirmed / open / hypothesis. Give each requirement a number (r) and an `origin`. Keep facts and hypotheses apart. For a renewal/consolidation, capture the **target information architecture (how new sections and menus map onto old pages)** as a requirement.
   - ⚠️ **Don't conflate what a quantity means.** "Pages poured into a template," "total site pages," and "pages migrated" are different numbers. Even the same word "page" has a different denominator. Per row, fix what one unit counts.
   - ⚠️ **The current-page count (the denominator, fixed in 01) and the new-site page count are different numbers.** Don't reuse the denominator as the new site's size ("a renewal of all N pages") — splitting one long home into per-purpose pages makes new > current, so the same proposal can say "10 pages" and total 16. The new-site count is derived from the target IA / page list, not from 01's denominator.
3. **Add hypothesis requirements** = latent needs derivable from the facts, written so they're distinguishable from facts — mark them "hypothesis."
4. **Settle the open questions provisionally.** Don't mix them into requirements; manage them as q with "provisional decision + basis + where to confirm." Fold the provisional decision into the requirements so the estimate can proceed, and hand the remaining confirmation targets to 02's basis column.

**Completion criteria**: the ledger's counts match the real counts (zero missed pages) / every requirement has an origin and a category / every open question is provisionally settled (the estimate isn't blocked) / facts, inferences, and needs-confirmation are not mixed.

> **Standard topics to confirm with the human before ★** (asked on every engagement, so the AI gathers them and asks once): ① the migrate/don't-migrate line (newly found pages, out-of-scope candidates) / ② the count denominator and origin (from where do we count) / ③ what the consolidation absorbs vs retires / ④ the migration origin for news etc. (from when) / ⑤ the reading of the client's request (does the paraphrase drift from the original intent) / ⑥ for a migration, whether **preserving SEO assets** (the 301 old→new URL map, the Search Console move) is in scope — name it as a requirement now, or it gets missed in 02. The AI does not "decide" these; it raises them as q to ★.

**★ Human review = gate.**

## Phase 2 — Proposal design

**Input**: `01_requirements.md`. **Output**: `02_proposal-design.md`. Skeleton = copy and fill `${CLAUDE_PLUGIN_ROOT}/references/templates/02_proposal-design.md`.

1. **Lay out all stories (p1…pN), and for each decide its method + basis.** For a corporate site, always include: **information architecture** (sections and menus) / **page templates** (how many kinds, and what gets poured into each) / for each page or piece of content, whether it is **new build / rebuild (rework) / reuse / migration of existing content** (always add the category) / **list search & filter** (cases, news, courses) / **content migration** (what, from which old site, by which method) and **redirects (301)** (old URL → new URL) / the **CMS (site management system)** handed over / **if the site takes on any toC (consumer-facing transactions — booking, future payments)**, the legal pages it then requires (特定商取引法表記 / privacy policy / cancellation policy / license & qualification notices) — a corporate site that leans BtoC drops these silently / the test method — plus the target state, the aim (value gained), the process, the estimate, premises / exclusions, the terms, and the next step. Give concrete items an ID (p6-n etc.). Fill 01's `proposal design (p)` column for every requirement (state out-of-scope explicitly) = zero misses.
   - ⚠️ **Always distinguish "carry the existing" from "build new."** A migration mixes both within one section (cases = new menu but migration of 21 existing items / services = re-placing existing pages + building a new gateway). Listing counts alone gets misread downstream (template count, design effort, verification) as "all newly built," getting the *nature* of the effort wrong. Whenever you give a count, add [existing migration / new build / reuse-rework].
   - ⚠️ **If the basis/CMS is undecided, the basis choice is itself part of the proposal.** Don't write as if "the CMS handed over" is already fixed. Present **2–3 candidates compared on the same axes** — initial cost / running cost / who updates / extensibility / maintenance hands-off — and let the client choose at ★ (#4). Keep it neutral (no recommendation mark) when the client wants flat candidates. This is the design-side framing; the estimate-side mechanics (common effort once + a per-basis branch) are in the estimate-model ⚠️ below — don't duplicate, just cross-reference.
   - ⚠️ **Migration's commonly-missed standard-work checklist** (for each item, write "applies / doesn't + basis" — a gap here becomes a loss after winning the deal): 〔**who builds the 301 old→new URL map** (separate from implementation — real effort at ledger scale)〕〔**who runs the tests, and the effort** (writing the checklist and running it are different)〕〔**multilingual** = built as a language-switch mechanism, or one reused page? (if the global nav has EN it must be designed as a feature)〕〔**cross-domain redirects** from several domains → one, and the handling of retired subdomains〕〔**migrating the path off ending SNS/media** (where note/Wantedly etc. move to)〕〔**ancillary page types** = 404 / search results / HTML sitemap / form-complete screen / product detail〕〔**source-platform 301 feasibility** = if the current site is on a subdomain the client doesn't control (`*.wixsite.com`, `*.studio.site`, an Ameba blog…), a real server-side 301 may be impossible — confirm whether redirects can be set at all and what SEO transfer is actually achievable, before scoping it as work〕.
2. **Decide the estimate model here** (day rate = currency/day, direction %, two-layer structure when subcontracting, rounding, contract form and amount granularity) = this is the source of truth. 03 and 04 follow it.
   - When subcontracting, two layers: in-house = effort × day rate × (1 + direction %) / subcontracted = the subcontractor's quote as the actual-cost source of truth, × (1 + your direction %).
   - ⚠️ **Decide the subcontractor-cost tax treatment up front** = is the subcontractor quote tax-included or tax-excluded, the subcontractor's invoice/tax status, and how it loads onto your total. **Apply the markup to the tax-excluded actual cost, then tax the whole once at the end** (don't apply a markup to a tax-included cost and tax it again = double taxation). If the premise is empty, raise it as q (insufficient input).
   - ⚠️ **"Near-mandatory optional costs" and "variable-price options": cost them only after the in/out decision is fixed** (don't park a plugin annual fee or animation work in "separate" to make the total look lower).
   - ⚠️ **Annual / license / operating costs are a separate category from the initial cost.** Folded into the initial cost (in-house effort + subcontracting), the amount appears nowhere in the figure table and floats free of the quoted price (e.g. writing "plugin annual fee" only as a "costing policy" with no amount shown). Assign each cost to exactly one of [counted in the initial cost / separate under post-launch operation / human to confirm].
   - ⚠️ **Platform-reality gate — pin the basis down before you price it.** Two real failures, both pricing work that doesn't match the platform: (a) a no-code basis (Studio / Wix / ペライチ) absorbs build / responsive / form / 404 / domain-connect into standard features (hours, not days) — don't stack them as person-days as if hand-built; (b) the source platform can make work infeasible (a `wixsite.com` subdomain can't take a real 301), so don't cost work that can't be done. **Before turning anything into effort, list what the chosen basis absorbs and what the source platform makes infeasible, and drop/shrink those from the estimate.**
   - ⚠️ **An ambiguous basis name decides nothing until you resolve the form.** "WordPress" is two opposite cost/effort/maintenance models — **WordPress.com** (managed SaaS: updates, backups, security run by the host → maintenance is hands-off, monthly plan fee) vs **WordPress.org** (self-hosted: server cost, you own all maintenance). Resolve the concrete form and plan tier (with first-party facts — plan/price/who maintains — not memory) **before** pricing; maintenance owner, running cost, and initial effort all flip on it.
   - ⚠️ **"Template basis, so it's cheap" is a trap.** A no-code/template basis compresses **only the initial design**; (a) building & responsive tuning in the editor, (b) pouring every page in, (c) booking flows & legal pages, (d) 301/DNS/Search-Console move all remain regardless of basis. Cost them separately — this is where deals lose money after winning.
   - **When the basis has more than one real candidate, build the estimate as common effort once + a per-basis branch.** Stack the shared work (requirements, design, content prep) a single time, then split only the basis-specific build per candidate, and produce a total per candidate. Presenting candidates flat (no recommendation mark) is allowed — basis choice is the client's call.
   - Match amount granularity to the contract form: quasi-mandate (effort-ratio) → total only (per-item fixed amounts get misread as a contract-for-work) / contract-for-work (fixed scope) → per-category subtotals + total.
   - ⚠️ **The contract form (quasi-mandate vs contract-for-work) is the human's call, not the AI's** — it drives how the amount is shown (total-only vs per-category) and what post-launch care can be. Raise it as a q to ★; **don't default to contract-for-work** (web builds with an unsettled spec are normally quasi-mandate). The AI decides the estimate *model* here, which makes it easy to over-reach and "decide" the contract form too — don't.
3. **Put what can't yet be decided into TODOs** = state what is to be decided, get a ★ human review of the research plan, then research, then reflect the result.

**Completion criteria**: every p has a concrete method / every requirement's `p` column is filled (out-of-scope stated) / the estimate model, premises, exclusions, and terms are written.

**★ Human review = gate** (the research plan of each TODO also gets a ★ review).

## Phase 3 — Work breakdown

**Input**: `02_proposal-design.md`. **Output**: `03_work-breakdown.md`. Skeleton = copy and fill `${CLAUDE_PLUGIN_ROOT}/references/templates/03_work-breakdown.md`.

1. **Decompose the work** along corporate-site stages: **requirements/IA → design → build → migration/launch → post-launch care**. Turn each p (method / concrete items) into work with a work ID (w), quantity, and unit. Fill 01's `work` column for every requirement (state out-of-scope) = zero build gaps. Put search & filter and each form on their own rows so their effort isn't buried. Handle content migration and redirects (301) on independent rows backed by the URL ledger. The items marked "applies" in phase 2's migration checklist (building the 301 map, running tests, multilingual, cross-domain redirects, ancillary page types) each get their own row with effort.
   - ⚠️ **Fill the migration-boundary responsibility matrix** = 〔building the 301 map / running tests / quality check / data extract & load〕 × 〔subcontractor / us / client〕, settling in one table who owns each and for how many person-days. Where the subcontractor scoped a task as "auto-generated" or "checklist only," the downstream execution and map-building fall to us or the client — count that effort on its own row. A blank cell is the red flag of a missed estimate (the main cause of post-deal losses).
2. **Anchor in-house effort** = subcontracting has an anchor (the quote) and is reproducible, but **in-house effort has no anchor and swings high or low**. (a) Decide the staffing (who is involved how much = dedicated/shared) first / (b) where there's subcontracting, limit your side to "direct, accept, manage" and don't double-count implementation effort / (c) sanity-check the total person-days **both ways against staffing × months** (e.g. 70 in-house person-days over 4 months = nearly dedicated, or realistic? conversely a few person-days = enough to accept and test the subcontractor's output?).
3. **Build up the amount** = effort (person-days) × day rate = work estimate. Per the model, apply direction % to reach the estimated amount. Produce per-category and overall totals.
   - ⚠️ **"Create only" is the classic underestimate.** Stack "create + review + feedback" on each row. Manually testing every page is heavy = test the main pages manually, the rest with automated checks.
   - ⚠️ **Don't forget migration and post-launch care** (directly tied to the client's anxiety: "will my content survive / what happens after launch").
   - ⚠️ **On a small / individual-client engagement, settle with the human which rows can be dropped or staged** after the build-up (manual-test scope, post-launch care window, ancillary pages, depth of a basis comparison) — the full big-engagement build-up over-shoots a cost-sensitive small client. If presenting a range, low = after omissions, high = full build-up. The heavy two-layer-subcontracting reconciliation applies only when there's subcontracting.
   - ⚠️ **Round effort uncertainty up** (Fibonacci, round up). Leave a one-line reason so you can explain it later.
   - ⚠️ **Subcontractor quote = actual cost.** Don't discount it to look cheap = it bites after work starts.
   - ⚠️ **The built-up total (03 = internal truth) and the amount presented to the client (04) are different.** Rounding the presented amount and adding contingency is the human's (sales) call, fixed at ★ = the AI doesn't round on its own in 03, nor does it assert "no rounding." Keep the difference internally as contingency. Before ★, raise one question to the human: "present the built-up amount as-is, or round it?"

**Completion criteria**: every requirement is covered by some work (out-of-scope stated) / each row carries "create + review + feedback" effort / per-category and overall totals exist / the amount has been reconciled against the client's budget sense / **the two aggregations inside 03 reconcile by machine** — the sum of the detail rows' work estimate equals the role-based (designer / coder …) subtotal, re-added (`awk`/calculator) to prove they match. A hand roll-up drops a row (one coder-day = a ¥40k gap seen in practice), and that quietly shrinks every downstream figure (direction %, tax, total, budget check); gate it like the phase-4 residue grep.

**★ Human review = gate.**

## Phase 4 — Proposal

**Input**: `02` + `03`. **Output**: `04_proposal.html` → `04_proposal.pdf`. The deck is **assembled from slide parts**, not copied from a monolith. Per the `${CLAUDE_PLUGIN_ROOT}/references/templates/04_proposal.md` outline, pick the part variant for each slot, then **concatenate `${CLAUDE_PLUGIN_ROOT}/references/templates/parts/_head.html` + the chosen parts (in outline order) + `${CLAUDE_PLUGIN_ROOT}/references/templates/parts/_foot.html` into one HTML**, fill the `{{ }}` placeholders and `（…）` markers with the content of 02 and 03, run the export gate, and export via headless Chrome at 16:9. The outline defines the 3-layer backbone, the slot order, which variant each slot takes, and that `.pg` page numbers are assigned at assembly time.

1. **Assemble the proposal** = following `04_proposal.md`: choose each slot's part variant (as-is-to-be 〔single｜multi〕, screen 〔service-cta｜search-filter｜tree-nav〕, estimate 〔total｜range｜compare〕), concatenate `_head.html` + the chosen parts in outline order + `_foot.html` from `${CLAUDE_PLUGIN_ROOT}/references/templates/parts/`, then fill the `{{ }}` / `（…）`. Raise the 3rd layer (the `compare-*` parts + `estimate.compare`) only when the realization means has a real client choice; a 2-layer engagement skips them and uses `estimate.total` or `estimate.range`. Assign `.pg` page numbers at assembly (parts ship with the `{{頁}}` placeholder, not a baked-in number). In the copy, value as the lead, with jargon kept small and placed behind the value ("Ajax search" → "find what you want right away" / "301" → "keep your search ranking"). Translate the maker's words into what the client gets. Check completeness = every requirement (r) is told somewhere (state out-of-scope). Unify terms and add a glossary page.
   - ⚠️ **Put the client's most-valued problem at the head of the value** (the theme they spend the most pages/energy on in the input = hiring, brand, etc.). Close value cards **with the effect; keep the means (IA, taxonomy, 301…) small and behind**. Closing on the means reverts to a "feature tour" and makes value-first only nominal.
   - ⚠️ **Run the most-valued theme as the through-line, not just one value card** = thread the same theme through the cover copy, the as-is (why change now), and the to-be. Even with the top theme on one card, if the opening through the as-is is only "findability / operational efficiency," the lead doesn't stand and the theme looks like a supporting role (if hiring competitiveness is the top concern, make it the lead from the cover, as-is, and to-be).
   - ⚠️ **Always include a "proposer's track record & team" section** = who, with what team, and similar experience (especially experience with high-risk migrations). The client can't entrust the work without knowing who you are. If the input has no track-record info, don't fabricate it — leave a `（…）` marker for the human to fill. **The `why-us` part is mandatory — always include it** in the assembly (track record & team). The `post-launch-care` and `contact` parts are optional: **include them only if in scope** (just don't concatenate them otherwise — no slide-delete, no renumber). `.pg` is assigned at assembly, so adding or dropping a part only changes the assembly-time numbering — see `04_proposal.md` → "必須／任意のパーツ". The CSS lives once in `_head.html` (byte-identical to the old monolith); never touch it.
   - ⚠️ **Label sample images as samples.** If you show a screen/design draft, write clearly "sample image = the real design will differ," so a draft isn't mistaken for the finished product.
   - ⚠️ **Don't machine-replace jargon.** Unifying terms is good, but a blanket replace breaks meaning (leave product names, code identifiers, and formal standard names as-is; explain them in the glossary). Don't repeat proper nouns and first-use terms in the body; move them to the glossary.
2. **Match the amount and contract form** = per the contract form, present either "total only" or "per-category subtotals + total." Don't show internal values (rate, person-days, %). The proposal's figures are based on the work breakdown (03), but **the presented amount isn't necessarily the built-up total as-is** = if the human fixed rounding / contingency at ★, show that amount and keep the difference internal (built-up = internal truth, presented = external; a difference between them is not a contradiction).
3. **Burn-down check** (read with a fresh expert role) = match each hearing item / client input against the proposal one by one — ✅ covered (which page) / ⚠️ partial / ❌ missing. Cross-check by counting the hub's columns. Fill the holes; route what can't be decided to open questions.
   - ⚠️ **Map the proposal's "we will do X" 1:1 to the estimate scope** = check that work the proposal says it "handles / includes" is either stacked as effort in 03 or stated explicitly as a scope call (included / separately quoted). The more you sell value, the more the proposal tends to promise work, and a promise not in the estimate (e.g. "we'll handle minor fixes right after launch," but post-launch care isn't costed) stays gray. Raise the gray ones to the human before ★.
4. **Export to PDF and eyeball it page by page** = even if the screen looks fine, the PDF breaks (footer overlap, cut tables, overflow). **Don't trust the screen preview; look at the exported PDF itself.** Export only when the human says to.
   - ⚠️ **Before exporting, prove zero template residue.** The parts carry many `{{ }}` placeholders and `<!-- 例 … -->` sample rows; any one left behind in the assembled file renders **literally into the client PDF** (the `{{ }}` text shows; the sample rows ship as fake data). Eyeballing 300+ tokens always misses some, so machine-check the **assembled `04_proposal.html`** (not the raw parts — those legitimately keep their `{{ }}`): `grep -c '{{' 04_proposal.html` and `grep -c '<!--[^>]*例' 04_proposal.html` must both be **0** before you export. (Legitimate body copy like "事例" is fine — it matches neither pattern.)
     - **Fill-marker convention (so "the human fills this" survives the gate).** `{{ }}` means "a blank the AI pours 02/03 content into" — it must be 0 at export. A value only a **human** can settle and the AI must not fabricate (proposer name, contact, the name a track record is credited under) is *not* a `{{ }}` blank: write it as a full-width-paren marker `（提案者名）` or `※…は提案者が記入`. That keeps the gate at 0 while leaving an explicit "human fills here," so fact-based ("don't invent") and the export gate don't collide.
   - ⚠️ **Headless export tends to hang** (e.g. Chrome `--print-to-pdf`). Launch it in the background, poll until the file size is stable, then `kill` it. If no headless browser is available, say so and ask the human which exporter to use rather than shipping the raw HTML.
   - ⚠️ **Verify by rasterizing**: render the PDF to PNG (`pdftoppm -png`) and eyeball it, and check the page count (`pdfinfo`). Catch the breakage before the client does.
   - ⚠️ **Submit as a single file.** Don't mix in internal files (md / spreadsheets). Put the output under the dated folder.

**Completion criteria**: the proposal's figures match the work breakdown / no hearing item or requirement is unaddressed (checked by counting, not impression) / no internal value leaks / the exported PDF isn't broken.

**★ Human review = gate** (final, before delivery).
