import postcode from '../vendor/postcode-lite/index.cjs';
import { getConfig } from './config.js';

// Flat fee per region, in cents, for parcels up to config.shipping.includedWeightGrams.
const REGION_FEES = {
  'US-WEST': 800,
  'US-CENTRAL': 900,
  'US-EAST': 1000,
  CA: 1800,
  EU: 2500,
  UK: 2200,
};

// Business days from dispatch to delivery, as quoted by the carrier.
const REGION_DAYS = {
  'US-WEST': 3,
  'US-CENTRAL': 4,
  'US-EAST': 5,
  CA: 7,
  EU: 10,
  UK: 9,
};

const EU_COUNTRIES = new Set([
  'AT', 'BE', 'DE', 'DK', 'ES', 'FI', 'FR', 'IE', 'IT', 'LU', 'NL', 'PL', 'PT', 'SE',
]);

/**
 * Work out the shipping region for an address.
 * Returns null when we can't place it (unknown ZIP prefix, unsupported country).
 *
 * @param {{country?: string, postcode?: string}} address
 * @returns {string|null}
 */
export function regionForAddress(address) {
  const country = (address.country || 'US').toUpperCase();
  if (country === 'US') {
    const info = postcode.lookup(address.postcode, 'US');
    if (!info || !info.zone) return null;
    return `US-${info.zone}`;
  }
  if (country === 'CA') return 'CA';
  if (country === 'GB' || country === 'UK') return 'UK';
  if (EU_COUNTRIES.has(country)) return 'EU';
  return null;
}

export function canShipTo(address) {
  const country = (address.country || 'US').toUpperCase();
  return country === 'US' || country === 'CA' || country === 'GB' || country === 'UK' || EU_COUNTRIES.has(country);
}

/**
 * Shipping fee in cents.
 *
 * @param {string|null} region
 * @param {{subtotalCents?: number, weightGrams?: number, freeShipping?: boolean}} [opts]
 */
export function shippingFee(region, { subtotalCents = 0, weightGrams = 0, freeShipping = false } = {}) {
  const cfg = getConfig().shipping;
  if (freeShipping) return 0;
  if (region && region.startsWith('US-') && subtotalCents >= cfg.freeOverCents) return 0;

  // A region missing from the table made this undefined and the checkout total NaN
  // (incident 2026-08-02). Unknown regions pay the default fee.
  const base = REGION_FEES[region] ?? cfg.defaultFeeCents;

  const extraGrams = Math.max(0, weightGrams - cfg.includedWeightGrams);
  const extraKg = Math.ceil(extraGrams / 1000);
  return base + extraKg * cfg.surchargePerKgCents;
}

/**
 * Expected delivery date for an order dispatched on `from`.
 * @param {string|null} region
 * @param {Date} [from]
 */
export function estimateDelivery(region, from = new Date()) {
  const businessDays = REGION_DAYS[region];
  const d = new Date(from);
  // Orders placed after 2pm go out the next day.
  if (d.getHours() >= 14) d.setDate(d.getDate() + 1);
  // Carriers quote business days; add the weekends in between.
  const calendarDays = businessDays + Math.floor(businessDays / 5) * 2;
  d.setDate(d.getDate() + calendarDays);
  return d;
}
