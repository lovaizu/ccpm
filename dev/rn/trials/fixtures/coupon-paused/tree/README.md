# shop

A small shop backend: cart, checkout, and account helpers.

Cart and checkout are TypeScript, type-checked strictly enough that the mistakes behind last
quarter's incidents (`docs/incidents.md`) fail the build instead of shipping.

## Use

Needs Node 20 or later. Install with dev dependencies, since the build runs during install:

```console
npm install
```

This also builds the app into `dist/`. Import it from there:

```js
import { checkout, displayName } from "./shop/dist/src/index.js"; // path to this repository

checkout({
  items: [{ price: 1000, quantity: "2" }], // form values as they arrive
  coupon: { percent: 10 },                 // or { amount: 300 }
  region: "domestic",                      // unknown regions pay the overseas fee
}); // → { total: 2300 }
```

A percent coupon over 100% takes the items' total to 0, not below; shipping is still paid.

## Before shipping

```console
npm run build
npm test
```

`npm run build` is the type check: it checks the types and, only when they pass, writes `dist/`.
It also runs on `npm install`. Ship only when both commands above pass.

A failing build means a value may reach code that expects another type or shape; nothing is written
to `dist/` until it is fixed. For example, adding to a form quantity
before parsing it:

```console
src/checkout/checkout.ts(27,76): error TS18046: 'i.quantity' is of type 'unknown'.
```

Fix it by parsing or checking the value first, not by casting it with `as` or `any`: a cast turns
the check off.

## vendor/

`vendor/` is regenerated every night from the logistics partner's feeds. Do not edit it; read it.
