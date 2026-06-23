# Proposal design

Internal document. The bridge between the requirements and the work breakdown.

## What this document is for
- Lay out the proposal's **stories (p1…pN), one at a time**, and for each decide its "**method**" and "**basis** (research result, selection reason, premise q, where to confirm)." `p_n` = proposal story #n (same number as the proposal chapter).
- This becomes the source for the work breakdown (03), and the **source of truth for premises and the estimate model** is here.
- **The trace source of truth is the requirement list (01).** Requirement → p is held by 01's `proposal design (p)` column. **02 holds no back-reference (p → requirement)** (no duplication).
- Give concrete items for design/build/migration an **ID (p6-n etc.)** at a granularity 03 can pull as work (no abstract phrasing). For image-sourced specs, reference the image (don't make a degraded copy).

---

## p1 [story name]

**Method**

**Basis**

(…repeat for p2, p3 … one per proposal story. A p3/p4 contrast can be one table. Write design/build/migration p's with the ID-bearing item table below.)

### Item-table form (p6 how to build, p7 how to migrate, etc.)

For an HP, list as concrete items: **IA (sections & menus) / page templates (how many kinds, what gets poured into each) / new design vs rework vs reuse / list search & filter / content migration (from which old site, by which method) and redirects (301) / the CMS handed over.**

> **Always split "build" from "carry"**: new build / rework (rebuild) / reuse / **migration (carry existing content)** / feature. One section mixes both (cases = new menu, existing content migrated, etc.), so don't let a bare count read as "all new."

| ID | item | kind | content (count) | basis / premise |
|---|---|---|---|---|
| p6-1 |  | new / rework / reuse / migration (existing) / feature |  |  |

---

## Estimate model (source of truth)
> Decided once here; 03 and 04 follow it. (The model's rules and pitfalls — two-layer subcontracting, double-tax, separate annual costs, rounding, contract granularity — are defined in the skill. Record this engagement's chosen values below.)

- **Day rate** (internal value, non-disclosed): [currency/day]
- **Direction (PM) markup**: [%]
- **Two-layer model (when subcontracting)**: in-house = effort × day rate × (1 + direction %) / subcontracted = the subcontractor quote (actual-cost source of truth) × (1 + your direction %)
- **Subcontractor-cost tax**: quote [tax-included / tax-excluded] / invoice/tax status / how it loads (markup on tax-excluded actual cost, tax the whole once at the end)
- **Annual / operating costs (separate category from initial)**: assign each to [counted in initial / separate under post-launch operation / human to confirm]
- **Rounding**: effort uncertainty rounds up (Fibonacci). The presented-amount rounding/contingency is the human's call at ★ (built-up = internal truth / presented = external)
- **Contract form & amount granularity**: [quasi-mandate = total only / contract-for-work (fixed scope) = per-category summary + total]

## Premises / exclusions / terms
> The conditions this estimate stands on, the scope line, and the deal terms. Flows to the proposal (04).

- **Premises (conditions the amount stands on)**:
- **Exclusions (out of estimate scope)**:
- **Terms (payment / acceptance / warranty / rights)**:
- **What the client prepares / decides with us**:

## TODO (research & confirm)
> Things to decide to firm up the method and the estimate basis. For each TODO, write out what to research and **get a ★ human review before** researching.

| # | aspect | what to decide | related p | status |
|---|---|---|---|---|
| t1 | requirement |  |  | open |
| t2 | method |  |  | open |
| t3 | estimate |  |  | open |
