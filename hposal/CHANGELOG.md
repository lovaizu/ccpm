# Changelog

All notable, user-facing changes to the `hposal` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release — `/hposal:up` drives a four-phase workflow (requirements → proposal design → work breakdown → proposal) for corporate-site (HP) estimates and proposals, with a human review gate at each phase so the direction is checked before moving on.
- Designed 16:9 slide template for the final proposal (`references/templates/04_proposal.html`) — a fill-in-the-blank HTML deck (cover → as-is/to-be → screen mockups → value → estimate → terms → appendix) with a ready-made print stylesheet, so the customer-facing proposal looks polished from the first draft instead of being built from scratch each time.
- The workflow now fixes where the working files live (a per-engagement project folder, with the final PDF under a dated subfolder) and how to resume mid-run — so a long run broken by review gates picks up at the right phase instead of scattering files or redoing approved work.
- The workflow now gathers the internal pricing inputs (day rate, direction markup, subcontractor tax, staffing) once up front and forbids inventing them — so amounts aren't silently built on a guessed rate.
- Before exporting the proposal PDF, the workflow now machine-checks that no unfilled `{{ }}` placeholder or sample row remains — so the client never receives a deck with leftover template text or fake sample data.
- The proposal slide template now ships with ready-made slides for "why us" (proposer track record & team), post-launch care, and contact, and the chapter guide maps every chapter to the deck — so the required "who we are" section is built in instead of reconstructed each time, and optional slides are simply deleted when out of scope.
- Site crawling in phase 1 now has a fallback for sites with no sitemap or a JavaScript-rendered menu — so page counting doesn't stall or under-count on common real-world sites.

### Changed

- The workflow now guards the pitfalls found while using the kit on a real migration project: it confirms SEO/301 preservation as a requirement, flags 301 limits on subdomain-hosted source sites and toC legal pages, pins down an ambiguous basis (e.g. WordPress.com vs .org) and what a no-code basis absorbs before pricing, treats the contract form as the client's call rather than assuming it, machine-checks that the work-breakdown totals reconcile, keeps the current-page count separate from the new-site size, and keeps internal sourcing terms out of the proposal — so the first real run is less likely to mis-scope or mis-price.
- The proposal deck is now assembled from selectable slide parts (one part = one slide) following an outline, instead of editing one big template — so you pick the right variant per slot (single vs multi-site as-is/to-be, the screen mockup type, total vs range vs multi-candidate estimate) and, when the client is choosing between platforms, lay the comparison out across a whole layer, rather than hand-deleting slides, hand-renumbering pages, or hand-building two columns. Page numbers are assigned automatically at assembly, and the print stylesheet stays identical so the look is unchanged.
