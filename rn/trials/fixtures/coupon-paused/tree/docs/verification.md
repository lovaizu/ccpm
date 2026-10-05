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
