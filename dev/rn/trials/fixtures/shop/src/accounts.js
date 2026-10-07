import { db, nextId } from './store.js';

export class AccountError extends Error {
  constructor(code, message) {
    super(message || code);
    this.code = code;
  }
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function cleanName(value) {
  if (value === undefined || value === null) return null;
  const trimmed = String(value).trim();
  return trimmed === '' ? null : trimmed;
}

/**
 * Create a customer account.
 *
 * Names are optional: the old signup form only asked for an email, and the
 * Apple sign-in flow often gives us no last name.
 */
export function createAccount({ email, firstName, lastName, nickname, marketingOptIn } = {}) {
  const normalized = String(email || '').trim().toLowerCase();
  if (!EMAIL_RE.test(normalized)) throw new AccountError('bad_email');
  if (findByEmail(normalized)) throw new AccountError('email_taken');

  const account = {
    id: nextId('acct'),
    email: normalized,
    firstName: cleanName(firstName),
    lastName: cleanName(lastName),
    nickname: cleanName(nickname),
    marketingOptIn: marketingOptIn === true || marketingOptIn === 'on' || marketingOptIn === 'true',
    isStaff: normalized.endsWith('@larkspur.example'),
    createdAt: new Date().toISOString(),
  };
  db.accounts.set(account.id, account);
  return account;
}

export function getAccount(id) {
  if (!id) return null;
  return db.accounts.get(id) || null;
}

export function findByEmail(email) {
  const wanted = String(email).trim().toLowerCase();
  for (const account of db.accounts.values()) {
    if (account.email === wanted) return account;
  }
  return null;
}

/**
 * Update profile fields. Accounts imported from the old shop can still carry
 * empty strings or nulls in any of these.
 */
export function updateProfile(account, changes) {
  for (const field of ['firstName', 'lastName', 'nickname']) {
    if (field in changes) account[field] = changes[field];
  }
  if ('marketingOptIn' in changes) account.marketingOptIn = Boolean(changes.marketingOptIn);
  return account;
}

/**
 * The name we show to a customer: nickname, else "First Last", else the part
 * of their email before the @.
 *
 * @param {{email: string, firstName?: string|null, lastName?: string|null, nickname?: string|null}|null} account
 * @returns {string}
 */
export function displayName(account) {
  if (!account) return 'Guest';
  const nickname = account.nickname ? String(account.nickname).trim() : '';
  if (nickname) return nickname;
  const parts = [account.firstName, account.lastName]
    .map((p) => (p ? String(p).trim() : ''))
    .filter(Boolean);
  if (parts.length) return parts.join(' ');
  return account.email.split('@')[0];
}

export function publicProfile(account) {
  return {
    id: account.id,
    email: account.email,
    displayName: displayName(account),
    firstName: account.firstName,
    lastName: account.lastName,
    nickname: account.nickname,
  };
}

/** Accounts migrated from the previous platform, as they came out of its export. */
export function importLegacyAccount(row) {
  const account = {
    id: nextId('acct'),
    email: String(row.email).toLowerCase(),
    firstName: row.first_name,
    lastName: row.last_name,
    nickname: row.screen_name,
    marketingOptIn: row.newsletter === '1',
    isStaff: false,
    createdAt: row.created || new Date().toISOString(),
  };
  db.accounts.set(account.id, account);
  return account;
}
