import { test } from 'node:test';
import assert from 'node:assert/strict';
import { toCents, centsToDecimal, formatCents, allocate } from '../src/money.js';

test('toCents treats numbers as cents and strings as dollars', () => {
  assert.equal(toCents(1250), 1250);
  assert.equal(toCents('12.50'), 1250);
  assert.equal(toCents('12.5'), 1250);
  assert.equal(toCents('$1,024'), 102400);
  assert.equal(toCents('-3.05'), -305);
});

test('toCents rejects junk', () => {
  assert.throws(() => toCents('abc'), TypeError);
  assert.throws(() => toCents('1.234'), TypeError);
  assert.throws(() => toCents(''), TypeError);
  assert.throws(() => toCents(undefined), TypeError);
  assert.throws(() => toCents(NaN), TypeError);
});

test('centsToDecimal pads cents', () => {
  assert.equal(centsToDecimal(5), '0.05');
  assert.equal(centsToDecimal(1200), '12.00');
  assert.equal(centsToDecimal(-150), '-1.50');
});

test('formatCents formats as currency', () => {
  assert.equal(formatCents(123456), '$1,234.56');
});

test('allocate keeps the total', () => {
  const parts = allocate(500, [2900, 2400]);
  assert.deepEqual(parts, [274, 226]);
  assert.equal(parts[0] + parts[1], 500);
  assert.deepEqual(allocate(100, [0, 0]), [0, 0]);
  assert.deepEqual(allocate(10, [1, 0, 1]), [5, 0, 5]);
});
