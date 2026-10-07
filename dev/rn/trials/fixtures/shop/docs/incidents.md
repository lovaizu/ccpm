# Production incidents, last quarter

Q3 2026 (July–September). Each of these was a value of the wrong type that
reached production: our tests passed, review passed, and customers found it.

## 1. Cart total NaN with fixed-amount coupons — 2026-07-14

- **What happened:** we launched `WELCOME5`, the first coupon worth a fixed
  amount ($5) instead of a percentage. The discount code in
  `src/cart.js` (`discountFor`) read `coupon.percent` for every coupon. Fixed
  coupons have `amountCents` and no `percent`, so the discount was `undefined`,
  the arithmetic gave `NaN`, and the cart showed a total of `$NaN`.
- **Impact:** about 6 hours. Customers who applied the coupon could not check
  out; the payment gateway rejected the amount `NaN.NaN`. Roughly 140 abandoned
  carts during the welcome campaign.
- **Fix:** hotfixed in `src/cart.js`: fixed coupons now use `amountCents`.
  Regression test added in `test/cart.test.js`.

## 2. Checkout total NaN for addresses outside the region table — 2026-08-02

- **What happened:** a customer in El Paso, TX (ZIP 88510) checked out. The
  vendored postcode library does not know that ZIP prefix, so
  `regionForAddress` returned `null`. `shippingFee` in `src/shipping.js` looked
  up `REGION_FEES[null]`, got `undefined`, and the checkout total became `NaN`.
- **Impact:** about 2 days before support connected the reports. Every
  customer whose ZIP prefix is not in the table got an error at the payment
  step.
- **Fix:** hotfixed in `src/shipping.js`: a region missing from the table now
  pays `shipping.defaultFeeCents`. Test added in `test/shipping.test.js`.

## 3. Quantity "2" + 1 = "21" — 2026-09-03

- **What happened:** the new no-JavaScript product page posts the add-to-cart
  form as `application/x-www-form-urlencoded`, so `quantity` arrives as the
  string `"2"`. `addItem` in `src/cart.js` added it to the existing quantity
  with `+`, which joined the strings: a customer adding 1 more of a line that
  had 2 got a quantity of `"21"`.
- **Impact:** customers adding more of an item got "too many" errors, or, when
  the joined number stayed under the per-line limit (`1` + `"1"` = `"11"`),
  carts with ten times what they wanted. Seven orders went through that way;
  they were refunded by hand, and one oversold the cast iron teapot.
- **Fix:** hotfixed in `src/cart.js`: `addItem` parses the quantity with
  `parseInt`. Test added in `test/cart.test.js` and `test/http.test.js`.

## What we have not fixed

Each fix went where the bug showed up. Nothing stops the next one of the same
kind: any other function that gets a form string, an optional field, or a
lookup that can miss is just as exposed, and we only find out in production.
