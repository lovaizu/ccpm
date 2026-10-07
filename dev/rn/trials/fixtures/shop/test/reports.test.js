import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { freshShop } from './helpers.js';
import { createOrder } from '../src/orders.js';
import { createAccount } from '../src/accounts.js';
import { salesCsv, salesSummary, toCsv } from '../src/reports.js';
import { db } from '../src/store.js';

beforeEach(() => freshShop());

function placeOrder(fields) {
  return createOrder({
    email: 'mara@example.com',
    lines: [{ sku: 'MUG-010', name: 'Stoneware mug, ash glaze', unitPriceCents: 2400, quantity: 2 }],
    address: { country: 'US', state: 'CA', postcode: '94110' },
    region: 'US-WEST',
    subtotalCents: 4800,
    discountCents: 0,
    shippingCents: 800,
    taxCents: 348,
    totalCents: 5948,
    paymentId: 'ch_test',
    ...fields,
  });
}

test('csv cells with commas and quotes are escaped', () => {
  const csv = toCsv(['a', 'b'], [{ a: 'x, y', b: 'say "hi"' }, { a: null, b: 3 }]);
  assert.equal(csv, 'a,b\r\n"x, y","say ""hi"""\r\n,3\r\n');
});

test('sales csv has one row per order with dollar amounts', () => {
  const account = createAccount({ email: 'mara@example.com', firstName: 'Mara', lastName: 'Okafor' });
  const order = placeOrder({ accountId: account.id });
  const lines = salesCsv({}).trim().split('\r\n');
  assert.equal(lines.length, 2);
  assert.ok(lines[0].startsWith('order_id,date,customer'));
  assert.equal(
    lines[1],
    `${order.id},${order.createdAt.slice(0, 10)},Mara Okafor,mara@example.com,US-WEST,2,48.00,0.00,8.00,3.48,59.48,0.00,paid`,
  );
});

test('summary adds up orders in the range', () => {
  placeOrder({});
  placeOrder({ discountCents: 480, totalCents: 5468 });
  const old = placeOrder({});
  old.createdAt = '2025-01-02T10:00:00.000Z';
  db.orders.set(old.id, old);

  const today = new Date().toISOString().slice(0, 10);
  const s = salesSummary({ from: today, to: today });
  assert.equal(s.orders, 2);
  assert.equal(s.grossCents, 9600);
  assert.equal(s.discountCents, 480);
  assert.equal(s.shippingCents, 1600);
  assert.equal(s.netCents, 9600 - 480 + 1600);
});
