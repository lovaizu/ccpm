// Coupon definitions and validation.
//
// Three kinds:
//   percent  - { percent: 10 }        10% off the merchandise subtotal
//   fixed    - { amountCents: 500 }   $5 off the merchandise subtotal
//   shipping - {}                     free shipping

const COUPONS = [
  { code: 'SPRING10', type: 'percent', percent: 10, label: '10% off spring teas' },
  { code: 'STAFF25', type: 'percent', percent: 25, minSubtotalCents: 0, staffOnly: true },
  { code: 'WELCOME5', type: 'fixed', amountCents: 500, minSubtotalCents: 2000 },
  { code: 'KETTLE15', type: 'fixed', amountCents: 1500, minSubtotalCents: 6000, expiresAt: '2026-12-31' },
  { code: 'SHIPFREE', type: 'shipping', label: 'Free shipping' },
  { code: 'SUMMER20', type: 'percent', percent: 20, expiresAt: '2026-08-31' },
];

export function findCoupon(code) {
  if (!code) return null;
  const wanted = String(code).trim().toUpperCase();
  return COUPONS.find((c) => c.code === wanted) || null;
}

/**
 * Check whether a coupon can be used on a cart.
 *
 * @param {object} coupon
 * @param {{subtotalCents: number, account?: object|null, now?: Date}} ctx
 * @returns {{ok: true} | {ok: false, reason: string}}
 */
export function validateCoupon(coupon, { subtotalCents, account = null, now = new Date() }) {
  if (!coupon) return { ok: false, reason: 'unknown_coupon' };
  if (coupon.expiresAt && new Date(coupon.expiresAt + 'T23:59:59Z') < now) {
    return { ok: false, reason: 'expired' };
  }
  if (coupon.staffOnly && !(account && account.isStaff)) {
    return { ok: false, reason: 'not_eligible' };
  }
  if (coupon.minSubtotalCents && subtotalCents < coupon.minSubtotalCents) {
    return { ok: false, reason: 'below_minimum' };
  }
  return { ok: true };
}

/** Short text for receipts and emails, e.g. "10% off". */
export function describeCoupon(coupon) {
  if (coupon.label) return coupon.label;
  if (coupon.type === 'shipping') return 'Free shipping';
  return `${coupon.percent}% off`;
}

/** The fields we copy onto an order so later changes to COUPONS don't rewrite history. */
export function couponSnapshot(coupon) {
  const { code, type, percent, amountCents } = coupon;
  return { code, type, percent, amountCents, description: describeCoupon(coupon) };
}

export function listCoupons() {
  return COUPONS.map((c) => ({ ...c }));
}
