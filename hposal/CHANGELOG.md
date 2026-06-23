# Changelog

All notable, user-facing changes to the `hposal` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release — `/hposal:up` drives a four-phase workflow (requirements → proposal design → work breakdown → proposal) for corporate-site (HP) estimates and proposals, with a human review gate at each phase so the direction is checked before moving on.
- Designed 16:9 slide template for the final proposal (`references/templates/04_proposal.html`) — a fill-in-the-blank HTML deck (cover → as-is/to-be → screen mockups → value → estimate → terms → appendix) with a ready-made print stylesheet, so the customer-facing proposal looks polished from the first draft instead of being built from scratch each time.
