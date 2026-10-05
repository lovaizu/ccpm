import { test } from "node:test";
import assert from "node:assert/strict";
import { applyCoupon } from "../src/cart/cart.js";

test("a percent coupon over 100% takes the items' total to 0, not below", () => {
  assert.equal(applyCoupon(2000, { percent: 150 }), 0);
});

test("a percent coupon under 100% still takes its share off", () => {
  assert.equal(applyCoupon(2000, { percent: 10 }), 1800);
});
