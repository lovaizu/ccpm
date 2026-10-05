#!/bin/bash
# Make the coupon session by hand, as docs/verification.md's coupon part says.
set -e
T=$(cd "$(dirname "$0")" && pwd)
git clone -q https://github.com/lovaizu/rn-try.git "$T/work-coupon"
cd "$T/work-coupon"
B=20261004-coupon-discount; D=.rn/$B
git checkout -q -b $B
mkdir -p $D
python3 - <<'EOF'
s=open('README.md').read()
s=s.replace("}); // → { total: 2300 }\n```\n","}); // → { total: 2300 }\n```\n\nA percent coupon over 100% takes the items' total to 0, not below; shipping is still paid.\n",1)
open('README.md','w').write(s)
d=open('docs/design.md').read()
d=d.replace("A coupon carrying both fields is taken as fixed-amount, as today.\n","A coupon carrying both fields is taken as fixed-amount, as today. A percent coupon over 100% takes\n  the items' total to 0, not below, as a fixed-amount coupon larger than the subtotal already does.\n",1)
open('docs/design.md','w').write(d)
EOF
cat > docs/verification.md <<'EOF'
# shop verification

Run these after any change to coupons to see whether checkout still gives what the
[design document](./design.md) promises.

## Where a run starts

- This repository at the commit under test, with Node 20 or later and `npm install` run.

## How a run goes

- Each scene calls `checkout` from `dist/src/index.js` with the input given, after `npm run build`.

## Scenes

### A1: A coupon never makes an order cost more than without it

- `checkout({ items: [{ price: 1000, quantity: "2" }], coupon: { percent: 150 }, region: "domestic" })`

    Passes when the total is 500: the items' total is 0, and shipping is paid.

## Machine checks

| Check | Command | Criteria | When |
|---|---|---|---|
| The app builds and its tests pass | `npm test` | M1 | Every change |
EOF
cat > $D/steering.md <<'EOF'
---
rn: 0.9.0
pr: PRURL
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
EOF
git add -A
git commit -q -m "rn: start the coupon session

● plan ── started → working out the plan"
git push -q -u origin $B 2>/dev/null
URL=$(gh pr create -R lovaizu/rn-try --draft --base main --head $B --title "Make every coupon a discount" --body "Plan: [steering.md](https://github.com/lovaizu/rn-try/blob/$B/$D/steering.md)")
sed -i '' "s|PRURL|$URL|" $D/steering.md
git commit -q -am "rn: record the pull request

● #1 Plan sign-off ── approved → working out the design"
git commit -q --allow-empty -m "rn: approve the design

● #2 Design sign-off ── approved → #3 Hold a percent coupon's total at 0"
git push -q
echo "$URL"
