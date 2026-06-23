# hposal — corporate-site (HP) estimates & proposals

From the client's input material and the current site, build a corporate-site (HP) estimate and proposal end to end — from organizing requirements to the final deliverable. The AI drafts and self-reviews; you pass a gate at each phase.

It fits multi-section information sites — company info, services, cases, news, careers, and the like. Most involve content migration from an old site and information architecture. It does not handle single-page LPs or web apps with auth/business logic (there, implementation complexity drives the estimate, which needs a different method).

> **Output language.** The deliverables and the conversation default to **Japanese** (the proposal is read by a Japanese client); this kit's own files are in English. The console snippets below are shown in English for documentation.

## Install

`hposal` ships from the `ccpm` marketplace. In Claude Code, add the marketplace once, then install the plugin:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install hposal@ccpm
```

Now `/hposal:up` is available.

## How it works

`/hposal:up` runs four phases top to bottom. Each produces one internal document; the last produces the client deliverable (PDF).

```
01 requirements → 02 proposal design → 03 work breakdown → 04 proposal
   (internal)        (internal)           (internal)          (deliverable)
```

Every phase is the same loop: the AI drafts, self-reviews with an expert-role subagent and fixes what it can, then stops for your review. It does not advance until you say OK.

## Getting started

Say you want to renew a current site and produce a proposal.

Launch `/hposal:up` and pass where the input material is and the current site URL. The AI first crawls the site and counts pages, organizes the requirements, and raises a ★ for your confirmation.

```console
> /hposal:up Renewal engagement. Material in input/, current site https://example.co.jp

● Phase 1 Requirements — draft and self-review done.
    Ledger: work/inventory/example.md (312 URLs total / real 312 — client said "about 280")
    Requirements: r1–r24 (every row has an origin and a category / open questions q1–q6 provisionally settled)

  ★ Please review. Points to confirm first:
    ① the migrate/don't-migrate line (how to handle the 18 newly found pages)
    ② the news migration origin (from when to migrate)

  On your OK, I proceed to Phase 2 Proposal design.
```

You read it and give feedback. On OK it moves to proposal design, firms up the stories and the estimate model the same way, builds up the amount in the work breakdown, and finally assembles the proposal in HTML and exports it to PDF. Each phase's ★ is the break, so it never advances in the wrong direction.

```console
● Phase 4 Proposal — exported 04_proposal.pdf (output/2026-06-15/).
    Every requirement r1–r24 is told somewhere in the proposal (checked by counting).
    Internal values (rate, person-days, %) are not shown in the deliverable.

  ★ Please do the final review (before delivery).
```

---

The rules the AI follows in each phase and the template contents live in the procedure the AI reads after launch (`skills/up/SKILL.md`). This README is the entry point.
