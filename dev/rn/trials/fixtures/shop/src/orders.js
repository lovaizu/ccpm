import { db, nextId } from './store.js';
import { toCents } from './money.js';
import { putBack } from './inventory.js';
import { refundCharge } from './payments/index.js';

export class OrderError extends Error {
  constructor(code, message) {
    super(message || code);
    this.code = code;
  }
}

export const ORDER_STATUSES = ['paid', 'shipped', 'delivered', 'refunded', 'partially_refunded', 'cancelled'];

export function createOrder(fields) {
  const order = {
    id: nextId('ord'),
    status: 'paid',
    accountId: fields.accountId || null,
    email: fields.email,
    lines: fields.lines.map((l) => ({ ...l })),
    address: { ...fields.address },
    region: fields.region,
    subtotalCents: fields.subtotalCents,
    discountCents: fields.discountCents || 0,
    shippingCents: fields.shippingCents,
    taxCents: fields.taxCents,
    totalCents: fields.totalCents,
    coupon: fields.coupon || null,
    paymentId: fields.paymentId,
    estimatedDelivery: fields.estimatedDelivery || null,
    shipment: null,
    refunds: [],
    createdAt: new Date().toISOString(),
  };
  db.orders.set(order.id, order);
  return order;
}

export function getOrder(id) {
  return db.orders.get(id) || null;
}

/**
 * @param {{from?: string, to?: string, status?: string, accountId?: string}} [filter]
 *   from/to are ISO dates, inclusive
 */
export function listOrders({ from, to, status, accountId } = {}) {
  const fromTs = from ? Date.parse(from) : -Infinity;
  const toTs = to ? Date.parse(to + 'T23:59:59.999Z') : Infinity;
  return [...db.orders.values()]
    .filter((o) => {
      const ts = Date.parse(o.createdAt);
      if (ts < fromTs || ts > toTs) return false;
      if (status && o.status !== status) return false;
      if (accountId && o.accountId !== accountId) return false;
      return true;
    })
    .sort((a, b) => a.createdAt.localeCompare(b.createdAt));
}

export function markShipped(order, { carrier, trackingNumber }) {
  if (order.status !== 'paid') throw new OrderError('not_shippable', `Order is ${order.status}`);
  order.status = 'shipped';
  order.shipment = { carrier, trackingNumber, shippedAt: new Date().toISOString() };
  return order;
}

function refundedQuantity(order, sku) {
  return order.refunds
    .filter((r) => r.sku === sku)
    .reduce((n, r) => n + r.quantity, 0);
}

/** What a customer actually paid per unit after the order's coupon. */
function paidUnitCents(order, line) {
  if (!order.coupon) return line.unitPriceCents;
  return Math.round(line.unitPriceCents * (1 - order.coupon.percent / 100));
}

/**
 * Refund some units of one line. Tax on those units is refunded too;
 * shipping is not.
 */
export async function refundItems(order, { sku, quantity, reason = '' }, deps = {}) {
  if (!['paid', 'shipped', 'delivered', 'partially_refunded'].includes(order.status)) {
    throw new OrderError('not_refundable');
  }
  const line = order.lines.find((l) => l.sku === sku);
  if (!line) throw new OrderError('not_in_order');
  const qty = parseInt(quantity, 10);
  if (!Number.isInteger(qty) || qty < 1) throw new OrderError('bad_quantity');
  if (refundedQuantity(order, sku) + qty > line.quantity) throw new OrderError('over_refund');

  const itemsCents = paidUnitCents(order, line) * qty;
  const taxShare = order.subtotalCents > 0
    ? Math.round((order.taxCents * line.unitPriceCents * qty) / order.subtotalCents)
    : 0;
  const amountCents = itemsCents + taxShare;

  const result = await refundCharge(order.paymentId, amountCents, deps);
  const refund = {
    id: result.id,
    sku,
    quantity: qty,
    amountCents: result.amountCents,
    reason,
    createdAt: new Date().toISOString(),
  };
  order.refunds.push(refund);
  if (order.status !== 'paid') putBack(sku, qty);

  const allBack = order.lines.every((l) => refundedQuantity(order, l.sku) === l.quantity);
  order.status = allBack ? 'refunded' : 'partially_refunded';
  return refund;
}

/**
 * Orders carried over from the previous platform's CSV export. Amounts there
 * are dollar strings; shipping was folded into the total.
 */
export function importLegacyOrder(row) {
  const order = {
    id: `legacy_${row.order_no}`,
    status: row.state === 'refunded' ? 'refunded' : 'delivered',
    accountId: null,
    email: row.email,
    lines: JSON.parse(row.items || '[]').map((i) => ({
      sku: i.sku,
      name: i.title,
      unitPriceCents: toCents(i.price),
      quantity: Number(i.qty),
    })),
    address: { country: row.country || 'US', state: row.state_code, postcode: row.zip },
    region: null,
    subtotalCents: toCents(row.subtotal),
    discountCents: row.discount ? toCents(row.discount) : 0,
    taxCents: toCents(row.tax || '0'),
    totalCents: toCents(row.total),
    coupon: null,
    paymentId: null,
    refunds: [],
    createdAt: new Date(row.placed_at).toISOString(),
    legacy: true,
  };
  db.orders.set(order.id, order);
  return order;
}
