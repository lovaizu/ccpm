import { getConfig } from '../config.js';
import { log } from '../logger.js';
import * as templates from './templates.js';

// Sent mail when the transport is "memory". Tests read this.
export const outbox = [];

const OPS_ADDRESS = 'ops@larkspur.example';

async function deliver(message) {
  const { transport, from } = getConfig().mail;
  const full = { from, ...message, sentAt: new Date().toISOString() };
  switch (transport) {
    case 'memory':
      outbox.push(full);
      return full;
    case 'log':
      log.info('mail', { to: full.to, subject: full.subject });
      return full;
    case 'smtp':
      // The SMTP relay is configured on the host; we hand off through sendmail.
      throw new Error('smtp transport is not available in this build');
    default:
      throw new Error(`Unknown mail transport: ${transport}`);
  }
}

/**
 * Mail failures must never fail the request that triggered them.
 */
async function safeSend(kind, message) {
  try {
    return await deliver(message);
  } catch (err) {
    log.error('mail failed', { kind, to: message.to, error: err.message });
    return null;
  }
}

export function sendOrderConfirmation(order, account) {
  const { subject, text } = templates.orderConfirmation({ order, account });
  return safeSend('order_confirmation', { to: order.email, subject, text });
}

export function sendShippedNotice(order, account) {
  const { subject, text } = templates.shippedNotice({ order, account });
  return safeSend('shipped', { to: order.email, subject, text });
}

export function sendRefundNotice(order, account, refund) {
  const { subject, text } = templates.refundNotice({ order, account, refund });
  return safeSend('refund', { to: order.email, subject, text });
}

export function sendLowStockAlert(rows) {
  if (!rows.length) return Promise.resolve(null);
  const { subject, text } = templates.lowStockAlert({ rows });
  return safeSend('low_stock', { to: OPS_ADDRESS, subject, text });
}

export function clearOutbox() {
  outbox.length = 0;
}
