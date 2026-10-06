# Coupons are discounts

## Decisions

- **A percent coupon's result is held at 0, as a fixed-amount coupon's already is.** `applyCoupon`
  returns `Math.max(0, total * (1 - percent / 100))`. Shipping is outside the coupon, so it is still
  paid. Not chosen: refusing a percent over 100, since such coupons are already in circulation and
  the user wants them to keep working as "free items".
- **A coupon below 0 refuses the order.** `checkout` throws before totaling when a coupon's percent
  or amount is below 0. Not chosen: treating it as no coupon, since the order would go through at a
  price the customer did not see.
