import { test, before, after, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { freshShop, ADMIN_TOKEN, CA_ADDRESS } from './helpers.js';
import { createServer } from '../src/server.js';
import { setGatewayClient, getGatewayClient } from '../src/payments/index.js';
import { GatewayClient, FakeTransport } from '../src/payments/gateway.js';

let server;
let base;

before(async () => {
  server = createServer();
  await new Promise((resolve) => server.listen(0, resolve));
  base = `http://127.0.0.1:${server.address().port}`;
});

after(() => new Promise((resolve) => server.close(resolve)));

beforeEach(() => {
  freshShop();
  setGatewayClient(new GatewayClient(new FakeTransport()));
});

async function call(method, path, { json, form, admin } = {}) {
  const headers = {};
  let body;
  if (json) {
    headers['content-type'] = 'application/json';
    body = JSON.stringify(json);
  }
  if (form) {
    headers['content-type'] = 'application/x-www-form-urlencoded';
    body = new URLSearchParams(form).toString();
  }
  if (admin) headers['x-admin-token'] = ADMIN_TOKEN;
  const res = await fetch(base + path, { method, headers, body });
  const type = res.headers.get('content-type') || '';
  const data = type.includes('json') ? await res.json() : await res.text();
  return { status: res.status, data };
}

test('health and 404', async () => {
  assert.deepEqual((await call('GET', '/health')).data, { ok: true });
  assert.equal((await call('GET', '/nope')).status, 404);
  assert.equal((await call('DELETE', '/health')).status, 405);
});

test('form posts with string quantities add up as numbers', async () => {
  const { data: cart } = await call('POST', '/carts', { json: {} });
  await call('POST', `/carts/${cart.id}/items`, { form: { sku: 'TEA-001', quantity: '2' } });
  const { status, data } = await call('POST', `/carts/${cart.id}/items`, { form: { sku: 'TEA-001', quantity: '1' } });
  assert.equal(status, 201);
  assert.equal(data.lines[0].quantity, 3);
  assert.equal(data.totals.subtotalCents, 4350);
});

test('domain errors map to HTTP statuses', async () => {
  const { data: cart } = await call('POST', '/carts', { json: {} });
  const res = await call('POST', `/carts/${cart.id}/items`, { json: { sku: 'NOPE', quantity: 1 } });
  assert.equal(res.status, 404);
  assert.equal(res.data.error, 'unknown_sku');
  const bad = await call('POST', `/carts/${cart.id}/coupon`, { json: { code: 'BOGUS' } });
  assert.equal(bad.status, 400);
});

test('checkout over HTTP, then the order shows in the admin CSV', async () => {
  const { data: cart } = await call('POST', '/carts', { json: {} });
  await call('POST', `/carts/${cart.id}/items`, { json: { sku: 'MUG-010', quantity: 1 } });
  const res = await call('POST', `/carts/${cart.id}/checkout`, {
    json: { email: 'teo@example.com', paymentToken: 'tok_visa', address: CA_ADDRESS },
  });
  assert.equal(res.status, 201);
  assert.equal(res.data.totalCents, 2400 + 800 + 174);
  assert.ok(getGatewayClient().transport.calls.length >= 1);

  const order = await call('GET', `/orders/${res.data.id}`);
  assert.equal(order.data.email, 'teo@example.com');

  assert.equal((await call('GET', '/admin/reports/sales.csv')).status, 401);
  const csv = await call('GET', '/admin/reports/sales.csv', { admin: true });
  assert.equal(csv.status, 200);
  assert.match(csv.data, new RegExp(`^${res.data.id},`, 'm'));
});

test('admin can ship and refund', async () => {
  const { data: cart } = await call('POST', '/carts', { json: {} });
  await call('POST', `/carts/${cart.id}/items`, { json: { sku: 'MUG-010', quantity: 2 } });
  const { data: order } = await call('POST', `/carts/${cart.id}/checkout`, {
    json: { email: 'teo@example.com', paymentToken: 'tok_visa', address: CA_ADDRESS },
  });

  const shipped = await call('POST', `/orders/${order.id}/ship`, {
    admin: true,
    json: { carrier: 'UPS', trackingNumber: '1Z999' },
  });
  assert.equal(shipped.data.status, 'shipped');

  const refund = await call('POST', `/orders/${order.id}/refunds`, {
    admin: true,
    form: { sku: 'mug-010', quantity: '1' },
  });
  assert.equal(refund.status, 201);
  assert.equal(refund.data.amountCents, 2400 + 174);

  const after = await call('GET', `/orders/${order.id}`);
  assert.equal(after.data.status, 'partially_refunded');
});
