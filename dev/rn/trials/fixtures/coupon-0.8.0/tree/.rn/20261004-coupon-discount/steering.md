Rn version: 0.8.0
Design: .rn/20261004-coupon-discount/design.md

# Goal

Every coupon is a discount, so no coupon makes an order cost more than it would without one. A
coupon once took an order's total below 0, and money went back to the customer by mistake.

# Acceptance criteria

- `checkout` with a percent coupon over 100% gives the shipping fee alone: the items' total is 0,
  never below.
- A coupon that is not a discount refuses the order instead of changing its total.
- Every order without such a coupon totals as before, and `npm test` passes.

# Assumptions

- Fact, read in `src/cart/cart.ts`: `applyCoupon` returns `total * (1 - percent / 100)`, so a
  percent over 100 gives a total below 0; a fixed-amount coupon is already held at 0.
- Fact, decided by the user: a coupon that is not a discount refuses the order.

# Rules

- commit and push every change; one completion marker per task
- Keep the TypeScript settings in tsconfig.json as strict as they are; tests run on the emitted
  JavaScript in `dist/`.

# Tasks

### [x] #1: Plan sign-off

**Purpose**: The user approves the goal, acceptance criteria, and tasks.

**Prerequisites**: none

**Steps**:

- [x] Present the plan on the PR and take the verdict via `/rn:ty` or `/rn:gm`

**Completion criteria**:

- The plan is approved.

### [x] #2: Design sign-off

**Purpose**: The user approves how a coupon is held to a discount.

**Prerequisites**: #1

**Steps**:

- [x] Present `design.md` on the PR and take the verdict via `/rn:ty` or `/rn:gm`

**Completion criteria**:

- `design.md` is approved.

### #3: Hold a percent coupon's total at 0

**Purpose**: A percent coupon over 100% no longer takes the items' total below 0.

**Prerequisites**: #2

**Steps**:

- [x] Add a test for a percent coupon over 100%
- [ ] Clamp the percent coupon's result in `applyCoupon`
- [ ] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [ ] QA expert review (subagent)
- [ ] Craft expert review (subagent, per the task's medium)
- [ ] Verification expert review (subagent, per the task's medium)

**Completion criteria**:

- `checkout` with `{ percent: 150 }` gives the shipping fee alone, and `{ percent: 10 }` still takes
  10% off.
- `npm test` passes, with the new test among those run.

### #4: Refuse a coupon that is not a discount

**Purpose**: A coupon with a negative percent or amount refuses the order.

**Prerequisites**: #3

**Steps**:

- [ ] Make `checkout` throw on a coupon whose percent or amount is below 0, with a test
- [ ] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [ ] QA expert review (subagent)

**Completion criteria**:

- `checkout` with `{ percent: -10 }` or `{ amount: -300 }` throws, and no other order does.

### #5: Evaluation sign-off

**Purpose**: The user approves the result against the acceptance criteria.

**Prerequisites**: #4

**Steps**:

- [ ] Present the result on the PR and take the verdict via `/rn:ty` or `/rn:gm`

**Completion criteria**:

- The result is approved.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: paused
- **Date**: 2026-10-04
- **Last completed**: #2 Design sign-off
- **Next**: #3 — clamp the percent coupon's result in `applyCoupon`; the test for it is in `test/coupon.test.ts` and fails until then
- **Notes**: PR PR_URL
