import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findCoupon, validateCoupon, describeCoupon } from '../src/coupons.js';

test('finds coupons regardless of case and spaces', () => {
  assert.equal(findCoupon(' spring10 ').code, 'SPRING10');
  assert.equal(findCoupon('nope'), null);
  assert.equal(findCoupon(''), null);
});

test('expired coupons are refused', () => {
  const coupon = findCoupon('SUMMER20');
  const result = validateCoupon(coupon, { subtotalCents: 5000, now: new Date('2026-09-15T00:00:00Z') });
  assert.deepEqual(result, { ok: false, reason: 'expired' });
  const before = validateCoupon(coupon, { subtotalCents: 5000, now: new Date('2026-08-01T00:00:00Z') });
  assert.equal(before.ok, true);
});

test('staff coupons need a staff account', () => {
  const coupon = findCoupon('STAFF25');
  assert.equal(validateCoupon(coupon, { subtotalCents: 1000 }).reason, 'not_eligible');
  assert.equal(validateCoupon(coupon, { subtotalCents: 1000, account: { isStaff: true } }).ok, true);
});

test('describes labelled and percent coupons', () => {
  assert.equal(describeCoupon(findCoupon('SPRING10')), '10% off spring teas');
  assert.equal(describeCoupon(findCoupon('SHIPFREE')), 'Free shipping');
  assert.equal(describeCoupon({ code: 'X', type: 'percent', percent: 15 }), '15% off');
});
