import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { freshShop } from './helpers.js';
import { createAccount, displayName, findByEmail, AccountError } from '../src/accounts.js';

beforeEach(() => freshShop());

test('creates an account with a normalized email', () => {
  const account = createAccount({ email: ' Mara@Example.com ', firstName: 'Mara' });
  assert.equal(account.email, 'mara@example.com');
  assert.equal(findByEmail('MARA@example.com').id, account.id);
});

test('refuses duplicates and bad emails', () => {
  createAccount({ email: 'a@example.com' });
  assert.throws(() => createAccount({ email: 'A@example.com' }), (e) => e.code === 'email_taken');
  assert.throws(() => createAccount({ email: 'not-an-email' }), AccountError);
});

test('empty names are stored as null', () => {
  const account = createAccount({ email: 'b@example.com', firstName: '  ', lastName: '' });
  assert.equal(account.firstName, null);
  assert.equal(account.lastName, null);
});

test('displayName prefers nickname, then full name, then email', () => {
  assert.equal(displayName({ email: 'x@y.z', nickname: 'Kit', firstName: 'K', lastName: 'A' }), 'Kit');
  assert.equal(displayName({ email: 'x@y.z', nickname: '', firstName: 'June', lastName: null }), 'June');
  assert.equal(displayName({ email: 'x@y.z', firstName: 'Teo', lastName: 'Lindqvist' }), 'Teo Lindqvist');
  assert.equal(displayName({ email: 'june.park@example.com', firstName: null }), 'june.park');
  assert.equal(displayName(null), 'Guest');
});

test('staff are recognised by domain', () => {
  assert.equal(createAccount({ email: 'kit@larkspur.example' }).isStaff, true);
  assert.equal(createAccount({ email: 'kit@example.com' }).isStaff, false);
});
