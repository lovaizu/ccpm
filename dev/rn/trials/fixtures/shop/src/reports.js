// Admin reports. Finance pulls the sales CSV into their spreadsheet every
// Monday, so column names and order are part of the contract.

import { listOrders } from './orders.js';
import { getAccount, displayName } from './accounts.js';
import { centsToDecimal } from './money.js';
import { db } from './store.js';

export const SALES_COLUMNS = [
  'order_id',
  'date',
  'customer',
  'email',
  'region',
  'items',
  'subtotal',
  'discount',
  'shipping',
  'tax',
  'total',
  'refunded',
  'status',
];

function csvCell(value) {
  if (value === null || value === undefined) return '';
  const s = String(value);
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export function toCsv(columns, rows) {
  const out = [columns.join(',')];
  for (const row of rows) out.push(columns.map((c) => csvCell(row[c])).join(','));
  return out.join('\r\n') + '\r\n';
}

function refundedCents(order) {
  return (order.refunds || []).reduce((sum, r) => sum + r.amountCents, 0);
}

/**
 * One row per order placed between `from` and `to` (inclusive, YYYY-MM-DD).
 */
export function salesRows({ from, to } = {}) {
  return listOrders({ from, to }).map((o) => {
    const account = getAccount(o.accountId);
    return {
      order_id: o.id,
      date: o.createdAt.slice(0, 10),
      customer: account ? displayName(account) : 'Guest',
      email: o.email,
      region: o.region || '',
      items: o.lines.reduce((n, l) => n + l.quantity, 0),
      subtotal: centsToDecimal(o.subtotalCents),
      discount: centsToDecimal(o.discountCents),
      shipping: o.shippingCents === undefined ? '' : centsToDecimal(o.shippingCents),
      tax: centsToDecimal(o.taxCents),
      total: centsToDecimal(o.totalCents),
      refunded: centsToDecimal(refundedCents(o)),
      status: o.status,
    };
  });
}

/**
 * Totals for the summary line at the top of the admin dashboard.
 * @returns {{orders: number, grossCents: number, discountCents: number, shippingCents: number, taxCents: number, refundedCents: number, netCents: number}}
 */
export function salesSummary({ from, to } = {}) {
  const totals = {
    orders: 0,
    grossCents: 0,
    discountCents: 0,
    shippingCents: 0,
    taxCents: 0,
    refundedCents: 0,
    netCents: 0,
  };
  for (const o of listOrders({ from, to })) {
    totals.orders += 1;
    totals.grossCents += o.subtotalCents;
    totals.discountCents += o.discountCents;
    totals.shippingCents += o.shippingCents;
    totals.taxCents += o.taxCents;
    totals.refundedCents += refundedCents(o);
  }
  totals.netCents =
    totals.grossCents - totals.discountCents + totals.shippingCents - totals.refundedCents;
  return totals;
}

export function salesCsv(range) {
  return toCsv(SALES_COLUMNS, salesRows(range));
}

export function inventoryCsv() {
  const rows = [...db.inventory.values()].map((i) => ({
    sku: i.sku,
    on_hand: i.onHand,
    reserved: i.reserved,
    available: i.onHand - i.reserved,
    updated_at: i.updatedAt,
  }));
  return toCsv(['sku', 'on_hand', 'reserved', 'available', 'updated_at'], rows);
}
