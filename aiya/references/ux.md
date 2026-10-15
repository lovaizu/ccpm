# Writing the UX

The document that fixes the product as its users see it. **One per product.** One of generation's prerequisites — until who uses it and how they touch it are fixed, neither the Deliverable's shape nor the Success Criteria can be written. If the project has no UX, write one in this format before running. A product with no screens still has a surface: a library's is its public API, a CLI's its command vocabulary — that is what this document fixes.

Public presentation — a README, a docs site — does not belong here: that is a delivery format, the project's own business. If needed, put a conversion Step at the end of Delivery that consumes this UX.

## What each heading is for

**users — who uses it.**
The intended users and their assumed knowledge. Saying who it is *not* for sharpens every judgment after.

**install — how it is set up.**
The steps, including prerequisites (environment, permissions).

**usage — how it is used.**
The representative flows, shown as real dialogue, screens, or commands. Examples over explanation — write exactly what the user will see. This heading is the main source of Success Criteria.

**vocabulary — the words users touch.**
Command names, on-screen words, and their meanings. Every name a user's eyes will meet is decided here — never let a name be born during implementation.

## Worked example

The worked example of this format is aiya itself — [aiya's README](../README.md) is this UX format dressed as a repository's face. The mapping: the opening paragraph and "aiya or rn" = users; "Install" = install; "Try it" = usage; "Two words" and "About the name" = vocabulary.
