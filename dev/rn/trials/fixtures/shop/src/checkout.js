import { getCart, computeTotals } from './cart.js';
import { getProduct, isShippable } from './catalog.js';
import { couponSnapshot } from './coupons.js';
import { regionForAddress, canShipTo, shippingFee, estimateDelivery } from './shipping.js';
import { computeTax } from './tax.js';
import { reserve, release, commit, lowStock } from './inventory.js';
import { chargeWithRetry } from './payments/index.js';
import { createOrder } from './orders.js';
import { getAccount } from './accounts.js';
import { sendOrderConfirmation, sendLowStockAlert } from './notifications/mailer.js';
import { getConfig } from './config.js';
import { log } from './logger.js';

export class CheckoutError extends Error {
  constructor(code, message, details = {}) {
    super(message || code);
    this.code = code;
    this.details = details;
  }
}

const REQUIRED_ADDRESS_FIELDS = ['name', 'line1', 'city', 'postcode'];

/**
 * Accepts either a nested `address` object (JSON clients) or flat
 * `address_*` fields (the HTML checkout form).
 */
export function readAddress(input) {
  const src = input.address || {
    name: input.address_name,
    line1: input.address_line1,
    line2: input.address_line2,
    city: input.address_city,
    state: input.address_state,
    postcode: input.address_postcode,
    country: input.address_country,
  };
  const address = {};
  for (const [key, value] of Object.entries(src)) {
    if (typeof value === 'string') address[key] = value.trim();
    else if (value !== undefined && value !== null) address[key] = value;
  }
  address.country = (address.country || 'US').toUpperCase();
  if (address.state) address.state = address.state.toUpperCase();
  return address;
}

function validateAddress(address) {
  const missing = REQUIRED_ADDRESS_FIELDS.filter((f) => !address[f]);
  if (address.country === 'US' && !address.state) missing.push('state');
  if (missing.length) throw new CheckoutError('bad_address', 'Address is incomplete', { missing });
  if (!canShipTo(address)) throw new CheckoutError('cannot_ship', `We don't ship to ${address.country}`);
}

/**
 * Price a cart for an address without charging anything. Used by the
 * checkout page to show the final total before the customer pays.
 */
export function quote(cart, address) {
  const totals = computeTotals(cart);
  const region = regionForAddress(address);
  const needsShipping = cart.lines.some((l) => isShippable(getProduct(l.sku)));
  const shippingCents = needsShipping
    ? shippingFee(region, {
        subtotalCents: totals.totalCents,
        weightGrams: totals.weightGrams,
        freeShipping: totals.freeShipping,
      })
    : 0;
  const taxCents = computeTax(cart.lines, address, { discountCents: totals.discountCents });
  return {
    region,
    subtotalCents: totals.subtotalCents,
    discountCents: totals.discountCents,
    shippingCents,
    taxCents,
    totalCents: totals.totalCents + shippingCents + taxCents,
  };
}

/**
 * Turn an open cart into a paid order.
 *
 * @param {string} cartId
 * @param {{email?: string, paymentToken: string, address?: object}} input
 * @param {{client?: object, backoff?: Function}} [deps]  payment client overrides, for tests
 */
export async function checkout(cartId, input, deps = {}) {
  const cart = getCart(cartId);
  if (!cart) throw new CheckoutError('cart_not_found');
  if (cart.status !== 'open') throw new CheckoutError('cart_closed');
  if (!cart.lines.length) throw new CheckoutError('empty_cart');
  if (!input.paymentToken) throw new CheckoutError('missing_payment');

  const account = getAccount(cart.accountId);
  const email = (input.email || account?.email || '').trim();
  if (!email) throw new CheckoutError('missing_email');

  const address = readAddress(input);
  validateAddress(address);

  const priced = quote(cart, address);
  if (priced.totalCents <= 0) throw new CheckoutError('nothing_to_charge');

  try {
    reserve(cart.lines);
  } catch (err) {
    throw new CheckoutError('out_of_stock', err.message, { sku: err.sku });
  }

  let payment;
  try {
    payment = await chargeWithRetry(
      {
        amountCents: priced.totalCents,
        currency: getConfig().currency,
        source: input.paymentToken,
        idempotencyKey: `checkout-${cart.id}`,
        description: `Cart ${cart.id}`,
      },
      deps,
    );
  } catch (err) {
    release(cart.lines);
    log.error('payment failed', { cartId, error: err.message });
    throw new CheckoutError('payment_failed', 'We could not reach the payment provider. Please try again.');
  }

  if (payment.status !== 'succeeded') {
    release(cart.lines);
    throw new CheckoutError('payment_declined', 'Your card was declined.', { declineCode: payment.declineCode });
  }

  commit(cart.lines);
  cart.status = 'checked_out';

  const order = createOrder({
    accountId: account?.id,
    email,
    lines: cart.lines,
    address,
    region: priced.region,
    subtotalCents: priced.subtotalCents,
    discountCents: priced.discountCents,
    shippingCents: priced.shippingCents,
    taxCents: priced.taxCents,
    totalCents: priced.totalCents,
    coupon: cart.coupon ? couponSnapshot(cart.coupon) : null,
    paymentId: payment.id,
    estimatedDelivery: estimateDelivery(priced.region).toISOString(),
  });

  log.info('order placed', { orderId: order.id, totalCents: order.totalCents });
  await sendOrderConfirmation(order, account);
  await sendLowStockAlert(lowStock());
  return order;
}
