# Site inventory — [site name]

The full-URL ledger for one current site. **One page = one row, every page.** It is the evidence that "the whole site was actually looked at," and the source of truth for the migration-volume denominator. Collect it by crawling (sitemap.xml / crawler / script), not by eyeballing = count facts, don't guess.

One file per site (`inventory/<site>.md`). The roll-up in `01_requirements.md` references this.

- **Source**: [sitemap.xml / crawl date / counting method]
- **Total pages**: [n] ← reconcile against the client's stated count and record any discrepancy

| # | URL | page name / type | section | migrate | note |
|---|---|---|---|:-:|---|
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |

> `migrate` = yes / no / TBD. When the client's stated count differs from the real count, take **the larger real number** as the denominator and leave the gap as an open question (q) in 01.
> `section` = company / services / cases / news / careers / contact … used to sort into the new HP IA.
