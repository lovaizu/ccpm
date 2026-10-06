# Design

Last quarter three production incidents (`docs/incidents.md`) came from a value of the wrong type or
shape reaching code that assumed otherwise. The cart and checkout code is TypeScript so that the
same kind of mistake fails `npm run build`, which is run before every release. `account` has had no
incident and stays JavaScript.

## Structure

```
 caller (server-side code, Node 20)
   │  imports dist/src/index.js
   ▼
 index
   ├─ checkout(form) ─────────────────────────────► { total }
   │     │  form: quantities unparsed, as they arrive from the form
   │     ▼
   │   cart
   │        in:  items with numeric price and quantity; coupon
   │        out: subtotal; total after the coupon
   │
   └─ displayName(user) ──► account (JavaScript, not type-checked) ──► name
```

```
 npm run build:  tsc ── type-checks src/ and test/ ──► fails on any type error
                     └─ emits JavaScript into dist/ ──► what ships (only when there is no error)
 npm test:       npm run build, then node --test on the emitted tests in dist/
 npm install:    runs npm run build (prepare), so the server builds dist/ after git pull
```

- **checkout** takes the form in the shape callers pass today: each item's quantity as it arrives
  from the form, unparsed; price as a number; an optional coupon; and a region as a plain string,
  which is checked against the known regions before the fee is looked up.
- **cart** works only on parsed values: prices and quantities are numbers, and a coupon is a percent
  coupon or a fixed-amount coupon. A coupon carrying both fields is taken as fixed-amount, as today. A percent coupon over 100% takes
  the items' total to 0, not below, as a fixed-amount coupon larger than the subtotal already does.
- **account** is imported as JavaScript and not type-checked; its exports reach callers typed `any`.
  That is the cost of leaving it out.

No new parsing or validation is added: a quantity that is not a number still becomes `NaN`, as
today, so callers get the same results for every input they pass now.

## Decisions

- **Form quantities are `unknown` until parsed.** With them typed `string`, TypeScript accepts
  `quantity + 1` and yields `"21"` (incident 3) without an error, and flags the mistake only later, if
  at all, where a number is required. `unknown` makes any arithmetic on an unparsed value an error on
  that very line.
- **Regions are a closed set, and the fee table is indexed only by it.** Looking up a
  `Record<string, number>` gives `number` even for a missing key, which is how incident 2 slipped by.
  With the table keyed by the known regions, looking it up with an unchecked string is an error.
  `noUncheckedIndexedAccess` covers the other lookups, making any looked-up value possibly
  `undefined` until checked.
- **A coupon is a union of its two shapes.** Reading `percent` from a coupon that has not been
  narrowed to a percent coupon is an error (incident 1).
- **`strict`, `noUncheckedIndexedAccess`, and `exactOptionalPropertyTypes` are on.** Without `strict`
  a missing value passes as any type; the other two close the gaps `strict` leaves for looked-up and
  optional values.
- **The build emits JavaScript.** Production runs Node 20, which cannot load `.ts` files, so what
  ships is the emitted `dist/`, and the caller imports `dist/src/index.js` in place of
  `src/index.js`. Emitting keeps the relative import paths working in `dist/`.
- **`allowJs` on, `checkJs` off.** This lets the TypeScript entry re-export `account` without
  touching `src/account/`, and `tsc` itself writes it into `dist/`, under the same no-emit-on-error
  rule. Without `allowJs` the import fails the build (no declaration file); a hand-written
  declaration or a separate copy step would each be one more thing to keep in step with the code.
- **`dist/` is built on the server, not committed.** The server already runs `npm install` after
  `git pull`, and npm runs the `prepare` script on it, so the server's steps stay as they are. A
  committed `dist/` could go stale when a build is forgotten, and would ship code that was never
  type-checked. TypeScript is a dev dependency, which a plain `npm install` installs.
- **Nothing is emitted when there is a type error** (`noEmitOnError`). Otherwise a failed build still
  writes JavaScript, and the server would run code that did not pass. A failed build on the server
  makes `npm install` fail and leaves the previous `dist/` in place, so the app keeps running the last
  good build.
- **Tests run on the emitted JavaScript.** What the tests pass on is then what ships, and they do not
  depend on the local Node being able to run `.ts` files. `node --test` is given `dist/` explicitly:
  bare, it also picks up the `.ts` tests in `test/`.
- **No lint tool is added.** The type settings above catch all three incidents at the place of the
  mistake, so a second tool would add a dependency and a step without catching more of these kinds.

What the types cannot stop: a type assertion (`as`) or `any` written on purpose overrides the check.
Such a line says plainly that it overrides it, so it is left to review.

## Checks

| Quality | What the user struggles with if it fails | How it is checked | Passes when |
|---|---|---|---|
| The incidents' mistakes fail the build | The next incident of the same kind ships | Put back each incident's mistake, one at a time, in `src/` and run `npm run build` | It fails, with the only error on the line of the mistake |
| The same kinds elsewhere fail the build | A new mistake of the same kind ships | Plant each kind once in `cart` and once in `checkout`, away from the incident spots, and run `npm run build` | Same as above |
| The delivered app builds | The user cannot ship | `npm run build` on the delivered app | It passes with no error |
| The app behaves as before | Callers get different totals or names | `npm test`, covering each behaviour listed in the goal | Every test passes |
| The server builds on install | The server runs old or no code after a pull | On Node 20, in a fresh clone, run `npm install`; then plant a type error and run `npm install` again | The first builds `dist/src/index.js`; the second fails, and `dist/` is byte-for-byte unchanged |
| What ships runs in production | The caller fails to load the app | Import `dist/src/index.js` on Node 20 and call `checkout` and `displayName` | Both return the same results as `npm test` expects |
| Scope holds | `account` changes though it was left out, or JavaScript is left in the moved code | `git diff main -- src/account`, and list `src/` and `test/` | The diff is empty; outside `src/account/` only `.ts` files are left |

The planted mistakes are checked once, at the end, by hand; they are not kept as tests, since a test
that must fail to compile would itself fail the build. That gives up catching a later change to the
type settings that weakens them.
