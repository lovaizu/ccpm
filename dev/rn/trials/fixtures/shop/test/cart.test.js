import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { freshShop } from './helpers.js';
import {
  createCart,
  addItem,
  updateQuantity,
  removeItem,
  applyCoupon,
  computeTotals,
  CartError,
} from '../src/cart.js';

beforeEach(() => freshShop());

test('adds items and totals them', () => {
  const cart = createCart();
  addItem(cart, 'TEA-001', 2);
  addItem(cart, 'MUG-010', 1);
  const totals = computeTotals(cart);
  assert.equal(totals.subtotalCents, 2 * 1450 + 2400);
  assert.equal(totals.itemCount, 3);
  assert.equal(totals.weightGrams, 2 * 120 + 450);
});

test('uses the sale price when there is one', () => {
  const cart = createCart();
  const line = addItem(cart, 'TEA-002', 1);
  assert.equal(line.unitPriceCents, 990);
});

test('quantity from a form string is added as a number', () => {
  const cart = createCart();
  addItem(cart, 'TEA-001', '2');
  const line = addItem(cart, 'TEA-001', '1');
  assert.equal(line.quantity, 3);
});

test('rejects bad quantities and unknown products', () => {
  const cart = createCart();
  assert.throws(() => addItem(cart, 'TEA-001', 0), CartError);
  assert.throws(() => addItem(cart, 'TEA-001', 'lots'), CartError);
  assert.throws(() => addItem(cart, 'NOPE-1', 1), (err) => err.code === 'unknown_sku');
});

test('cannot add more than is in stock', () => {
  freshShop({ stock: 3 });
  const cart = createCart();
  assert.throws(() => addItem(cart, 'KTL-200', 4), (err) => err.code === 'out_of_stock');
});

test('update to zero removes the line', () => {
  const cart = createCart();
  addItem(cart, 'TEA-001', 2);
  updateQuantity(cart, 'tea-001', 0);
  assert.equal(cart.lines.length, 0);
  assert.throws(() => removeItem(cart, 'TEA-001'), (err) => err.code === 'not_in_cart');
});

test('percent coupon takes a share of the subtotal', () => {
  const cart = createCart();
  addItem(cart, 'MUG-010', 2);
  applyCoupon(cart, 'spring10');
  const totals = computeTotals(cart);
  assert.equal(totals.discountCents, 480);
  assert.equal(totals.totalCents, 4320);
});

test('fixed-amount coupon gives a number, not NaN', () => {
  const cart = createCart();
  addItem(cart, 'MUG-010', 1);
  applyCoupon(cart, 'WELCOME5');
  const totals = computeTotals(cart);
  assert.equal(totals.discountCents, 500);
  assert.equal(totals.totalCents, 1900);
});

test('coupon minimums are enforced', () => {
  const cart = createCart();
  addItem(cart, 'TEA-001', 1);
  assert.throws(() => applyCoupon(cart, 'WELCOME5'), (err) => err.code === 'below_minimum');
});

test('free-shipping coupon does not touch the subtotal', () => {
  const cart = createCart();
  addItem(cart, 'TEA-001', 1);
  applyCoupon(cart, 'SHIPFREE');
  const totals = computeTotals(cart);
  assert.equal(totals.discountCents, 0);
  assert.equal(totals.freeShipping, true);
});
