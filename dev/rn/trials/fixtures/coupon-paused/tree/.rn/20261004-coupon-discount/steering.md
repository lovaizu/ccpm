---
rn: 0.9.0
pr: PR_URL
status: running
artifact-language: English
conversation-language: Japanese
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

Every coupon is a discount, so no coupon makes an order cost more than it would without one.

# Acceptance criteria

## Attractive quality

- A1: A percent coupon over 100% takes the items' total to 0, not below.

## Must-be quality

- M1: The app builds and its tests pass as before.

# Assumptions

- Fact, read in src/cart/cart.ts: `applyCoupon` returns `total * (1 - percent / 100)`, so a percent
  over 100 gives a total below 0; a fixed-amount coupon is already held at 0.

# Rules

- Keep the TypeScript settings in tsconfig.json as strict as they are; tests run on the emitted
  JavaScript in `dist/`.

# Tasks

### [x] #1: Plan sign-off
### [x] #2: Design sign-off
### [ ] #3: Hold a percent coupon's total at 0

Purpose: a percent coupon over 100% no longer takes the items' total below 0.

Serves: A1, M1

Completion criteria:

- Attractive quality: `checkout` with `{ percent: 150 }` gives the shipping fee alone, and
  `{ percent: 10 }` still takes 10% off.
- Must-be quality: `npm test` passes, with a test for a percent coupon over 100%.

### [ ] #4: Deliverable sign-off

# Not yet specified
