import { db, nextId } from './store.js';
import { getProduct, effectivePrice, isShippable } from './catalog.js';
import { findCoupon, validateCoupon } from './coupons.js';
import { available } from './inventory.js';

export class CartError extends Error {
  constructor(code, message) {
    super(message || code);
    this.code = code;
  }
}

const MAX_QUANTITY_PER_LINE = 20;

export function createCart(accountId = null) {
  const cart = {
    id: nextId('cart'),
    accountId,
    lines: [],
    coupon: null,
    status: 'open',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  db.carts.set(cart.id, cart);
  return cart;
}

export function getCart(id) {
  return db.carts.get(id) || null;
}

function touch(cart) {
  cart.updatedAt = new Date().toISOString();
}

function assertOpen(cart) {
  if (cart.status !== 'open') throw new CartError('cart_closed', `Cart ${cart.id} is ${cart.status}`);
}

/**
 * Add a product to the cart, or increase the quantity if it is already there.
 *
 * @param {object} cart
 * @param {string} sku
 * @param {number|string} quantity  forms send this as a string
 */
export function addItem(cart, sku, quantity = 1) {
  assertOpen(cart);
  const product = getProduct(sku);
  if (!product) throw new CartError('unknown_sku', `No product ${sku}`);

  // Form posts send "2", and "2" + 1 was "21" (incident 2026-09-03).
  const qty = parseInt(quantity, 10);
  if (!Number.isInteger(qty) || qty < 1) throw new CartError('bad_quantity');

  let line = cart.lines.find((l) => l.sku === product.sku);
  const newQty = (line ? line.quantity : 0) + qty;
  if (newQty > MAX_QUANTITY_PER_LINE) throw new CartError('too_many');
  if (isShippable(product) && newQty > available(product.sku)) {
    throw new CartError('out_of_stock', `Only ${available(product.sku)} left of ${product.sku}`);
  }

  if (line) {
    line.quantity = newQty;
  } else {
    line = {
      sku: product.sku,
      name: product.name,
      unitPriceCents: effectivePrice(product),
      quantity: newQty,
      weightGrams: product.weightGrams,
    };
    cart.lines.push(line);
  }
  touch(cart);
  return line;
}

export function updateQuantity(cart, sku, quantity) {
  assertOpen(cart);
  const line = cart.lines.find((l) => l.sku === String(sku).toUpperCase());
  if (!line) throw new CartError('not_in_cart');
  const qty = Number(quantity);
  if (qty === 0) return removeItem(cart, sku);
  if (!Number.isInteger(qty) || qty < 0) throw new CartError('bad_quantity');
  if (qty > MAX_QUANTITY_PER_LINE) throw new CartError('too_many');
  line.quantity = qty;
  touch(cart);
  return line;
}

export function removeItem(cart, sku) {
  assertOpen(cart);
  const before = cart.lines.length;
  cart.lines = cart.lines.filter((l) => l.sku !== String(sku).toUpperCase());
  if (cart.lines.length === before) throw new CartError('not_in_cart');
  touch(cart);
  return null;
}

export function applyCoupon(cart, code, account = null) {
  assertOpen(cart);
  const coupon = findCoupon(code);
  const { subtotalCents } = computeTotals(cart);
  const result = validateCoupon(coupon, { subtotalCents, account });
  if (!result.ok) throw new CartError(result.reason);
  cart.coupon = coupon;
  touch(cart);
  return coupon;
}

export function removeCoupon(cart) {
  cart.coupon = null;
  touch(cart);
}

function discountFor(coupon, subtotalCents) {
  if (!coupon) return 0;
  if (coupon.type === 'shipping') return 0;
  // Fixed-amount coupons have amountCents and no percent (incident 2026-07-14).
  if (coupon.type === 'fixed') return Math.min(coupon.amountCents, subtotalCents);
  return Math.round((subtotalCents * coupon.percent) / 100);
}

/**
 * Merchandise totals for a cart. Shipping and tax depend on the address and
 * are added at checkout.
 */
export function computeTotals(cart) {
  let subtotalCents = 0;
  let weightGrams = 0;
  let itemCount = 0;
  for (const line of cart.lines) {
    subtotalCents += line.unitPriceCents * line.quantity;
    weightGrams += (line.weightGrams || 0) * line.quantity;
    itemCount += line.quantity;
  }
  const discountCents = discountFor(cart.coupon, subtotalCents);
  return {
    subtotalCents,
    discountCents,
    totalCents: subtotalCents - discountCents,
    weightGrams,
    itemCount,
    freeShipping: cart.coupon?.type === 'shipping',
  };
}

export function cartView(cart) {
  return {
    id: cart.id,
    status: cart.status,
    lines: cart.lines.map((l) => ({ ...l, lineTotalCents: l.unitPriceCents * l.quantity })),
    coupon: cart.coupon ? cart.coupon.code : null,
    totals: computeTotals(cart),
  };
}
