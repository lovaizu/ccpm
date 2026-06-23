# Work breakdown (estimate)

Internal document. The source of truth for the amount.

> Give each task a **work ID (w1, w2…)**. The requirement → work trace is 01's `work` column pointing at this ID (**03 holds no back-reference**). Work content lands the p's (method / concrete items) from 02. Classify by HP stage = **requirements/IA → design → build → migration/launch → post-launch care**.

## Line items

| work ID | category | task | content | qty | unit | effort (person-days) | day rate (/day) | work estimate | estimated amount | status | comment |
|---|---|---|---|--:|:-:|--:|--:|--:|--:|:-:|---|
| w1 | **requirements** | requirements & IA | sitemap, etc. | – | set | – | – | – | – | – | – |
| w2 | **design** | top / lower-page design | – | – | item | – | – | – | – | – | – |
| w3 | **build** | page production (template pour-in) | – | – | page | – | – | – | – | – | – |
| w4 | | features | contact form / search & filter, etc. | – | set | – | – | – | – | – | – |
| w5 | **migration/launch** | content migration / redirects (301) / launch | – | – | item/set | – | – | – | – | – | – |
| w6 | **post-launch care** | handling defects & minor fixes for a while after launch | – | – | month | – | – | – | – | – | – |
| w7 | [other] | copywriting / photography, etc. | – | – | set | – | – | – | – | – | – |
| | | | **subtotal (ex-tax)** | | | | | – | – | | |
| | | | **consumption tax** | | | | | | – | | |
| | | | **total (inc-tax)** | | | | | | – | | |

> If part of the build is subcontracted, set that row's amount as the subcontractor quote (actual cost) × (1 + direction %), and roll it up in a separate "subcontract detail" block at the end. Estimate model: see 02.

## Internal vs external columns
Only some columns go to the client.

| column | shown to the client (proposal appendix)? |
|---|:-:|
| category / task / content / qty / unit | shown |
| estimated amount / total | shown |
| **effort (person-days) / day rate / work estimate** | **not shown (internal)** |
| **work ID / status / comment** | **not shown (internal)** |

- **Don't expose the day rate.** It reveals the person-day rate and invites back-calculation (qty × rate) into a negotiation lever. The client only needs scale from qty/unit and the estimated amount.
- Whether to add "*direction included*" on the external table is per engagement (do as decided in 02).

## Estimate premises / risks
- **Premises (conditions the amount stands on)**:
- **Risks (what moves the amount)**:
- **Awaiting confirmation (to firm up premises)**:
- **Out of scope (not stacked)**:
