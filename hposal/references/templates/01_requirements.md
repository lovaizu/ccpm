# Requirements

Internal document. Organize facts from the client's input material and current site into an estimable state. **The hub of the whole kit** — every later document traces back to a requirement number here. (Hub-and-trace model: see "Traceability" in the skill.)

## Input ledger
List every source and current site you base the estimate on, showing confirmation and requirement extraction. First list the targets in "Input list" with circled numbers (①②…); the table's `target` column references that number (don't repeat long names on every row). Crawl the current site one page = one row; put the full per-page rows in `inventory/*.md` (this table can be a site × section roll-up). Use a line break (`<br>`) when a cell holds several items.

**Input list (targets)**

- ① [source name / file path]
- ② [site name / URL (CMS etc.) / all URLs → `inventory/xxx.md`]

| # | type | target | location/content | confirmed | requirement-ized |
|---|---|:-:|---|:-:|---|
| i1 | source | ① |  |  |  |
| i2 | current | ② |  |  |  |

## Requirement list
> Requirements read from the input. `origin` traces the basis; `category` splits [input (fact)] / [AI inference (hypothesis)] / [needs human decision]. Leave unconfirmed judgments as **q** and don't self-claim "decided (X)" (the human decides at ★). **This table is the downstream-trace hub**: `proposal design (p)` = which p (proposal story #n) decided the method / `work` = which w covered it (filled in phase 3). These two columns are the only downstream trace; 02/03 hold no back-reference.
>
> For an HP (corporate-site) renewal/consolidation, also capture the **new IA** (the new section structure, and how the menu maps onto old pages) as a requirement.

| # | requirement | category | origin | proposal design (p) | work |
|---|---|:-:|---|---|---|
| r1 |  | input |  |  |  |
| r2 |  | AI inference |  |  |  |
| r3 |  | needs human decision |  |  |  |

## Open-question list
> Facts you can't confirm yet / things to check. Don't mix these into the requirements; manage them here. Decide each **provisionally** within this document (handling column) and fold it into the requirements to FIX it for the proposal. Hand remaining confirmation targets to 02's basis column.

| # | open question | origin | handling (provisional decision / where to confirm) |
|---|---|---|---|
| q1 |  |  |  |
