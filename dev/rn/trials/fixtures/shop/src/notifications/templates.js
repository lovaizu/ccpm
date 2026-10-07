// Plain-text email templates. Marketing owns the wording; keep the structure.

import { formatCents } from '../money.js';
import { getConfig } from '../config.js';

function greeting(account) {
  if (!account) return 'Hi there,';
  const name = account.nickname || `${account.firstName} ${account.lastName}`;
  return `Hi ${name},`;
}

function formatDate(value) {
  if (!value) return 'soon';
  return new Date(value).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
}

function signature() {
  const { store } = getConfig();
  return [
    '',
    `Questions? Just reply, or write to ${store.supportEmail}.`,
    '',
    `— The ${store.name} team`,
    store.siteUrl,
  ].join('\n');
}

function lineTable(lines, currency) {
  const rows = lines.map((l) => {
    const total = formatCents(l.unitPriceCents * l.quantity, currency);
    return `  ${String(l.quantity).padStart(2)} x ${l.name.padEnd(32)} ${total.padStart(10)}`;
  });
  return rows.join('\n');
}

/**
 * @param {{order: object, account: object|null}} params
 * @returns {{subject: string, text: string}}
 */
export function orderConfirmation({ order, account }) {
  const { currency } = getConfig();
  const money = (c) => formatCents(c, currency);
  const lines = [
    greeting(account),
    '',
    `Thanks for your order ${order.id}. We're packing it now.`,
    '',
    lineTable(order.lines, currency),
    '',
    `  Subtotal: ${money(order.subtotalCents)}`,
  ];
  if (order.coupon) {
    lines.push(`  ${order.coupon.description} (${order.coupon.code}): -${money(order.discountCents)}`);
  }
  lines.push(
    `  Shipping: ${order.shippingCents === 0 ? 'Free' : money(order.shippingCents)}`,
    `  Tax:      ${money(order.taxCents)}`,
    `  Total:    ${money(order.totalCents)}`,
    '',
    `Estimated delivery: ${formatDate(order.estimatedDelivery)}`,
    signature(),
  );
  return { subject: `Your ${getConfig().store.name} order ${order.id}`, text: lines.join('\n') };
}

export function shippedNotice({ order, account }) {
  const { shipment } = order;
  const text = [
    greeting(account),
    '',
    `Good news: order ${order.id} is on its way with ${shipment.carrier}.`,
    `Tracking number: ${shipment.trackingNumber}`,
    '',
    `Estimated delivery: ${formatDate(order.estimatedDelivery)}`,
    signature(),
  ].join('\n');
  return { subject: `Order ${order.id} has shipped`, text };
}

export function refundNotice({ order, account, refund }) {
  const { currency } = getConfig();
  const text = [
    greeting(account),
    '',
    `We've refunded ${formatCents(refund.amountCents, currency)} for ${refund.quantity} x ${refund.sku} from order ${order.id}.`,
    'It can take 5–10 business days to appear on your statement.',
    signature(),
  ].join('\n');
  return { subject: `Refund for order ${order.id}`, text };
}

export function lowStockAlert({ rows }) {
  const text = [
    'These items are at or below the low-stock threshold:',
    '',
    ...rows.map((r) => `  ${r.sku.padEnd(10)} available ${r.available} (on hand ${r.onHand})`),
  ].join('\n');
  return { subject: `[stock] ${rows.length} item(s) running low`, text };
}
