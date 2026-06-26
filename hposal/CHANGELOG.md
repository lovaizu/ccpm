# Changelog

All notable, user-facing changes to the `hposal` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release — `/hposal:up` drives a four-phase workflow (requirements → proposal design → work breakdown → proposal) for corporate-site (HP) estimates and proposals, with a human review gate at each phase so the direction is checked before moving on.
- Designed 16:9 HTML deck for the final proposal, assembled from selectable slide parts (one part = one slide) following an outline (`references/templates/parts/` + `04_proposal.md`) — pick the variant per slot (single vs multi-site as-is→to-be, the screen-mockup type, total vs range vs multi-candidate estimate) and, when the client is choosing between platforms, lay the comparison out across a whole layer; page numbers are assigned automatically at assembly and a ready-made print stylesheet keeps the look consistent, so the customer-facing proposal looks polished from the first draft instead of being built from scratch each time.
- The workflow now fixes where the working files live (a per-engagement project folder, with the final PDF under a dated subfolder) and how to resume mid-run — so a long run broken by review gates picks up at the right phase instead of scattering files or redoing approved work.
- The workflow now gathers the internal pricing inputs (day rate, direction markup, subcontractor tax, staffing) once up front and forbids inventing them — so amounts aren't silently built on a guessed rate.
- Before exporting the proposal PDF, the workflow now machine-checks that no unfilled `{{ }}` placeholder or sample row remains — so the client never receives a deck with leftover template text or fake sample data.
- The proposal deck ships a mandatory "why us" part (proposer track record & team) plus optional "post-launch care" and "contact" parts, with the outline mapping every chapter to its part — so the required "who we are" section is always built in, and optional parts are simply included only when in scope.
- Site crawling in phase 1 now has a fallback for sites with no sitemap or a JavaScript-rendered menu — so page counting doesn't stall or under-count on common real-world sites.
- The proposal-design template now has ready-made slots for the migration standard-work checklist and the platform-reality gate — so the work the phase requires can't be silently dropped for lack of a place to put it.
- The work-breakdown template now has slots for a multi-candidate basis (common work once + per-platform branch + per-platform total) and a role-based reconciliation table — so a multi-platform estimate is filled in, not rebuilt from scratch.
- The proposal deck gains a `work-detail.common` / `work-detail.branch` part pair — so a multi-platform work-detail appendix that overflows a single slide splits cleanly instead of being hand-split.

### Changed

- The workflow now guards the pitfalls found while using the kit on a real migration project: it confirms SEO/301 preservation as a requirement, flags 301 limits on subdomain-hosted source sites and toC legal pages, pins down an ambiguous basis (e.g. WordPress.com vs .org) and what a no-code basis absorbs before pricing, treats the contract form as the client's call rather than assuming it, machine-checks that the work-breakdown totals reconcile, keeps the current-page count separate from the new-site size, and keeps internal sourcing terms out of the proposal — so the first real run is less likely to mis-scope or mis-price.
- The workflow's edge-case guidance is sharpened from a second dogfood run: how to reconcile counts when the client states none, that a standard confirmation topic may fan out into several questions, the anchor-type single-page case where the new site expands beyond the crawled-URL count, that a managed-SaaS monthly price varies by billing terms and what to do when its pricing page can't be fetched, that the responsibility matrix's quality-check isn't double-counted, and that a range's lower bound comes from staging rows rather than rounding — so these common situations don't stall or mislead a run.
- The proposal outline now spells out that the title placeholder is filled at assembly (CSS stays byte-unchanged) so the export gate is reachable, and that the page-count denominator is set with a single bulk replace at assembly; the multi-candidate estimate part also carries a height-budget hint so its note doesn't overflow the footer — so assembly is faithful and the deck doesn't break on the page.
