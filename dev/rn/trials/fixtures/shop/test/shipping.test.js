import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { freshShop } from './helpers.js';
import { regionForAddress, shippingFee, estimateDelivery } from '../src/shipping.js';

beforeEach(() => freshShop());

test('places US addresses by ZIP', () => {
  assert.equal(regionForAddress({ country: 'US', postcode: '94110' }), 'US-WEST');
  assert.equal(regionForAddress({ country: 'US', postcode: '60614-1234' }), 'US-CENTRAL');
  assert.equal(regionForAddress({ postcode: '10001' }), 'US-EAST');
  assert.equal(regionForAddress({ country: 'de', postcode: '10115' }), 'EU');
  assert.equal(regionForAddress({ country: 'CA', postcode: 'K1A 0B1' }), 'CA');
});

test('unknown places have no region', () => {
  assert.equal(regionForAddress({ country: 'US', postcode: '07030' }), null);
  assert.equal(regionForAddress({ country: 'JP', postcode: '100-0001' }), null);
});

test('fee comes from the region table', () => {
  assert.equal(shippingFee('US-WEST', { subtotalCents: 1000 }), 800);
  assert.equal(shippingFee('EU', { subtotalCents: 1000 }), 2500);
});

test('a region missing from the table pays the default fee', () => {
  assert.equal(shippingFee(null, { subtotalCents: 1000 }), 1200);
  assert.equal(shippingFee('MARS', { subtotalCents: 1000 }), 1200);
});

test('US orders over the threshold ship free; others do not', () => {
  assert.equal(shippingFee('US-EAST', { subtotalCents: 7500 }), 0);
  assert.equal(shippingFee('CA', { subtotalCents: 9000 }), 1800);
  assert.equal(shippingFee('CA', { freeShipping: true }), 0);
});

test('heavy parcels pay per extra kilo', () => {
  assert.equal(shippingFee('US-WEST', { weightGrams: 2000 }), 800);
  assert.equal(shippingFee('US-WEST', { weightGrams: 2001 }), 950);
  assert.equal(shippingFee('US-WEST', { weightGrams: 4500 }), 800 + 3 * 150);
});

test('delivery estimate adds the weekends', () => {
  const monday9am = new Date(2026, 9, 5, 9, 0);
  const d = estimateDelivery('US-WEST', monday9am);
  assert.equal(d.getDate(), 8);
  const late = estimateDelivery('EU', new Date(2026, 9, 5, 15, 0));
  assert.equal(late.getDate(), 6 + 10 + 4);
});
