import { getProduct } from './catalog.js';
import { allocate } from './money.js';

// State sales tax rates for the states where we have nexus. Rates are the
// state base rate only; local add-ons are not collected (per our accountant,
// 2025 review).
const STATE_RATES = {
  CA: 0.0725,
  WA: 0.065,
  OR: 0,
  NV: 0.0685,
  AZ: 0.056,
  CO: 0.029,
  UT: 0.061,
  TX: 0.0625,
  IL: 0.0625,
  NY: 0.04,
  PA: 0.06,
  MA: 0.0625,
  FL: 0.06,
  GA: 0.04,
};

// Groceries (loose-leaf tea counts) are exempt in these states.
const GROCERY_EXEMPT = new Set(['CA', 'TX', 'NY', 'PA', 'MA', 'FL', 'WA', 'NV', 'AZ']);

/**
 * Sales tax rate for an address. Orders shipped outside the US are not
 * charged US sales tax; import duties are the buyer's.
 *
 * @param {{country?: string, state?: string}} address
 */
export function taxRateFor(address) {
  const country = (address.country || 'US').toUpperCase();
  if (country !== 'US') return 0;
  return STATE_RATES[(address.state || '').toUpperCase()];
}

function isTaxable(product, state) {
  if (!product) return true;
  if (product.taxable === false) return false;
  if (product.category === 'grocery' && GROCERY_EXEMPT.has(state)) return false;
  return true;
}

/**
 * Tax in cents for cart lines shipped to `address`. An order-level discount is
 * spread over the lines first, so tax is charged on what the customer pays.
 *
 * @param {Array<{sku: string, unitPriceCents: number, quantity: number}>} lines
 * @param {{country?: string, state?: string}} address
 * @param {{discountCents?: number}} [opts]
 */
export function computeTax(lines, address, { discountCents = 0 } = {}) {
  const rate = taxRateFor(address);
  if (rate === 0) return 0;
  const state = (address.state || '').toUpperCase();

  const lineTotals = lines.map((l) => l.unitPriceCents * l.quantity);
  const discounts = allocate(discountCents, lineTotals);

  let taxable = 0;
  lines.forEach((line, i) => {
    if (isTaxable(getProduct(line.sku), state)) {
      taxable += lineTotals[i] - discounts[i];
    }
  });
  return Math.round(taxable * rate);
}

export function supportedStates() {
  return Object.keys(STATE_RATES);
}
