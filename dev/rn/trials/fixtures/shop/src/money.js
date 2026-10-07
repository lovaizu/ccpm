// Money helpers.
//
// Inside the app we keep amounts as integer cents. Amounts that come in from
// forms, CSV imports and the payment gateway are decimal strings in dollars
// ("12.50"), so anything crossing that boundary goes through toCents().

const MONEY_RE = /^-?\d+(\.\d{1,2})?$/;

/**
 * Convert an incoming amount to integer cents.
 *
 * A number is taken to be cents already; a string is taken to be dollars.
 *
 * @param {number|string} value
 * @returns {number}
 */
export function toCents(value) {
  if (value === null || value === undefined || value === '') {
    throw new TypeError('Amount is required');
  }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) throw new TypeError(`Invalid amount: ${value}`);
    return Math.round(value);
  }
  const cleaned = String(value).trim().replace(/^\$/, '').replace(/,/g, '');
  if (!MONEY_RE.test(cleaned)) {
    throw new TypeError(`Invalid amount: ${value}`);
  }
  const negative = cleaned.startsWith('-');
  const [whole, frac = ''] = cleaned.replace('-', '').split('.');
  const cents = parseInt(whole, 10) * 100 + parseInt(frac.padEnd(2, '0'), 10);
  return negative ? -cents : cents;
}

/** Cents to a plain decimal string, e.g. 1250 -> "12.50". */
export function centsToDecimal(cents) {
  const sign = cents < 0 ? '-' : '';
  const abs = Math.abs(cents);
  return `${sign}${Math.floor(abs / 100)}.${String(abs % 100).padStart(2, '0')}`;
}

const formatters = new Map();

export function formatCents(cents, currency = 'USD') {
  if (!formatters.has(currency)) {
    formatters.set(currency, new Intl.NumberFormat('en-US', { style: 'currency', currency }));
  }
  return formatters.get(currency).format(cents / 100);
}

export function sumCents(values) {
  return values.reduce((total, v) => total + v, 0);
}

/**
 * Split `totalCents` across `weights` so the parts always add back up to the total.
 * Used to spread an order-level discount over its lines.
 */
export function allocate(totalCents, weights) {
  const weightSum = weights.reduce((a, b) => a + b, 0);
  if (weightSum === 0) return weights.map(() => 0);
  const parts = weights.map((w) => Math.floor((totalCents * w) / weightSum));
  let remainder = totalCents - parts.reduce((a, b) => a + b, 0);
  for (let i = 0; remainder > 0; i = (i + 1) % parts.length) {
    if (weights[i] > 0) {
      parts[i] += 1;
      remainder -= 1;
    }
  }
  return parts;
}
