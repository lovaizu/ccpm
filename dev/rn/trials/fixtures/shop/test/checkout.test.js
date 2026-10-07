import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { freshShop, CA_ADDRESS } from './helpers.js';
import { createCart, addItem, applyCoupon } from '../src/cart.js';
import { checkout, quote, readAddress } from '../src/checkout.js';
import { available } from '../src/inventory.js';
import { outbox } from '../src/notifications/mailer.js';
import { GatewayClient, FakeTransport } from '../src/payments/gateway.js';

let client;
const noWait = () => 0;

beforeEach(() => {
  freshShop();
  client = new GatewayClient(new FakeTransport());
});

function teaAndMug() {
  const cart = createCart();
  addItem(cart, 'TEA-001', 2);
  addItem(cart, 'MUG-010', 1);
  return cart;
}

test('quote: tea is tax-exempt in CA, the mug is not', () => {
  const q = quote(teaAndMug(), CA_ADDRESS);
  assert.equal(q.subtotalCents, 5300);
  assert.equal(q.shippingCents, 800);
  assert.equal(q.taxCents, 174);
  assert.equal(q.totalCents, 6274);
});

test('quote: fixed coupon is spread over lines before tax', () => {
  const cart = teaAndMug();
  applyCoupon(cart, 'WELCOME5');
  const q = quote(cart, CA_ADDRESS);
  assert.equal(q.discountCents, 500);
  assert.equal(q.taxCents, 158);
  assert.equal(q.totalCents, 4800 + 800 + 158);
});

test('quote: no US sales tax outside the US', () => {
  const q = quote(teaAndMug(), { country: 'DE', postcode: '10115' });
  assert.equal(q.taxCents, 0);
  assert.equal(q.shippingCents, 2500);
});

test('checkout charges, creates the order, and emails the customer', async () => {
  const cart = teaAndMug();
  const order = await checkout(
    cart.id,
    { email: 'mara@example.com', paymentToken: 'tok_visa', address: CA_ADDRESS },
    { client, backoff: noWait },
  );
  assert.equal(order.status, 'paid');
  assert.equal(order.totalCents, 6274);
  assert.match(order.paymentId, /^ch_/);
  assert.equal(cart.status, 'checked_out');
  assert.equal(available('TEA-001'), 48);
  assert.equal(outbox.length, 1);
  assert.equal(outbox[0].to, 'mara@example.com');
  assert.match(outbox[0].text, /Total:\s+\$62\.74/);
});

test('checkout retries a flaky gateway with the same idempotency key', async () => {
  const cart = teaAndMug();
  const order = await checkout(
    cart.id,
    { email: 'mara@example.com', paymentToken: 'tok_flaky', address: CA_ADDRESS },
    { client, backoff: noWait },
  );
  assert.equal(order.status, 'paid');
  const keys = client.transport.calls.map((c) => c.idempotencyKey);
  assert.equal(keys.length, 2);
  assert.equal(keys[0], keys[1]);
});

test('declined card releases the stock', async () => {
  const cart = teaAndMug();
  await assert.rejects(
    checkout(cart.id, { email: 'a@b.co', paymentToken: 'tok_decline', address: CA_ADDRESS }, { client, backoff: noWait }),
    (err) => err.code === 'payment_declined',
  );
  assert.equal(available('TEA-001'), 50);
  assert.equal(cart.status, 'open');
});

test('gateway down gives payment_failed after the retries', async () => {
  const cart = teaAndMug();
  await assert.rejects(
    checkout(cart.id, { email: 'a@b.co', paymentToken: 'tok_down', address: CA_ADDRESS }, { client, backoff: noWait }),
    (err) => err.code === 'payment_failed',
  );
  assert.equal(client.transport.calls.length, 3);
});

test('incomplete address is refused before charging', async () => {
  const cart = teaAndMug();
  await assert.rejects(
    checkout(cart.id, { email: 'a@b.co', paymentToken: 'tok_visa', address: { line1: 'x' } }, { client }),
    (err) => err.code === 'bad_address' && err.details.missing.includes('postcode'),
  );
  assert.equal(client.transport.calls.length, 0);
});

test('readAddress accepts flat form fields', () => {
  const address = readAddress({
    address_name: ' Teo ',
    address_line1: '9 Elm',
    address_city: 'Austin',
    address_state: 'tx',
    address_postcode: '78701',
  });
  assert.deepEqual(address, {
    name: 'Teo',
    line1: '9 Elm',
    city: 'Austin',
    state: 'TX',
    postcode: '78701',
    country: 'US',
  });
});
