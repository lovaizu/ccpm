import { Router, HttpError, ok, created, sendText } from './router.js';
import { getConfig } from '../config.js';
import { listProducts, getProduct } from '../catalog.js';
import * as carts from '../cart.js';
import { checkout, quote, readAddress, CheckoutError } from '../checkout.js';
import { getOrder, markShipped, refundItems, listOrders, OrderError } from '../orders.js';
import { createAccount, getAccount, publicProfile, updateProfile, AccountError } from '../accounts.js';
import { restock, lowStock, available, InventoryError } from '../inventory.js';
import { salesCsv, salesSummary, inventoryCsv } from '../reports.js';
import { sendShippedNotice, sendRefundNotice } from '../notifications/mailer.js';

// Domain errors carry a `code`; map them onto HTTP statuses in one place.
const STATUS_BY_CODE = {
  cart_not_found: 404,
  not_in_cart: 404,
  not_in_order: 404,
  unknown_sku: 404,
  email_taken: 409,
  cart_closed: 409,
  out_of_stock: 409,
  over_refund: 409,
  not_shippable: 409,
  not_refundable: 409,
  payment_declined: 402,
  payment_failed: 502,
};

function wrap(handler) {
  return async (ctx) => {
    try {
      return await handler(ctx);
    } catch (err) {
      if (
        err instanceof carts.CartError ||
        err instanceof CheckoutError ||
        err instanceof OrderError ||
        err instanceof AccountError ||
        err instanceof InventoryError
      ) {
        throw new HttpError(STATUS_BY_CODE[err.code] || 400, err.code, err.message, err.details);
      }
      throw err;
    }
  };
}

function requireAdmin(req) {
  const token = getConfig().adminToken;
  if (!token || req.headers['x-admin-token'] !== token) {
    throw new HttpError(401, 'unauthorized');
  }
}

function loadCart(id) {
  const cart = carts.getCart(id);
  if (!cart) throw new HttpError(404, 'cart_not_found');
  return cart;
}

function loadOrder(id) {
  const order = getOrder(id);
  if (!order) throw new HttpError(404, 'order_not_found');
  return order;
}

export function buildRouter() {
  const r = new Router();

  r.get('/health', () => ok({ ok: true }));

  // --- catalog -------------------------------------------------------------

  r.get('/products', ({ query }) =>
    ok(listProducts({ category: query.category }).map((p) => ({ ...p, available: available(p.sku) }))),
  );

  r.get('/products/:sku', ({ params }) => {
    const product = getProduct(params.sku);
    if (!product) throw new HttpError(404, 'unknown_sku');
    return ok({ ...product, available: available(product.sku) });
  });

  // --- accounts ------------------------------------------------------------

  r.post('/accounts', wrap(({ body }) => created(publicProfile(createAccount(body)))));

  r.get('/accounts/:id', ({ params }) => {
    const account = getAccount(params.id);
    if (!account) throw new HttpError(404, 'account_not_found');
    return ok(publicProfile(account));
  });

  r.patch('/accounts/:id', wrap(({ params, body }) => {
    const account = getAccount(params.id);
    if (!account) throw new HttpError(404, 'account_not_found');
    return ok(publicProfile(updateProfile(account, body)));
  }));

  // --- carts ---------------------------------------------------------------

  r.post('/carts', ({ body }) => created(carts.cartView(carts.createCart(body.accountId || null))));

  r.get('/carts/:id', ({ params }) => ok(carts.cartView(loadCart(params.id))));

  r.post('/carts/:id/items', wrap(({ params, body }) => {
    const cart = loadCart(params.id);
    carts.addItem(cart, body.sku, body.quantity ?? 1);
    return created(carts.cartView(cart));
  }));

  r.patch('/carts/:id/items/:sku', wrap(({ params, body }) => {
    const cart = loadCart(params.id);
    carts.updateQuantity(cart, params.sku, body.quantity);
    return ok(carts.cartView(cart));
  }));

  r.delete('/carts/:id/items/:sku', wrap(({ params }) => {
    const cart = loadCart(params.id);
    carts.removeItem(cart, params.sku);
    return ok(carts.cartView(cart));
  }));

  r.post('/carts/:id/coupon', wrap(({ params, body }) => {
    const cart = loadCart(params.id);
    carts.applyCoupon(cart, body.code, getAccount(cart.accountId));
    return ok(carts.cartView(cart));
  }));

  r.delete('/carts/:id/coupon', ({ params }) => {
    const cart = loadCart(params.id);
    carts.removeCoupon(cart);
    return ok(carts.cartView(cart));
  });

  r.post('/carts/:id/quote', wrap(({ params, body }) => {
    const cart = loadCart(params.id);
    return ok(quote(cart, readAddress(body)));
  }));

  r.post('/carts/:id/checkout', wrap(async ({ params, body }) => {
    const order = await checkout(params.id, {
      email: body.email,
      paymentToken: body.paymentToken || body.payment_token,
      address: body.address,
      ...body,
    });
    return created(order);
  }));

  // --- orders --------------------------------------------------------------

  r.get('/orders/:id', ({ params }) => ok(loadOrder(params.id)));

  r.post('/orders/:id/ship', wrap(async ({ req, params, body }) => {
    requireAdmin(req);
    const order = markShipped(loadOrder(params.id), {
      carrier: body.carrier,
      trackingNumber: body.trackingNumber || body.tracking_number,
    });
    await sendShippedNotice(order, getAccount(order.accountId));
    return ok(order);
  }));

  r.post('/orders/:id/refunds', wrap(async ({ req, params, body }) => {
    requireAdmin(req);
    const order = loadOrder(params.id);
    const refund = await refundItems(order, {
      sku: String(body.sku || '').toUpperCase(),
      quantity: body.quantity,
      reason: body.reason,
    });
    await sendRefundNotice(order, getAccount(order.accountId), refund);
    return created(refund);
  }));

  // --- admin ---------------------------------------------------------------

  r.get('/admin/orders', ({ req, query }) => {
    requireAdmin(req);
    return ok(listOrders({ from: query.from, to: query.to, status: query.status }));
  });

  r.post('/admin/inventory/:sku/restock', wrap(({ req, params, body }) => {
    requireAdmin(req);
    if (!body.quantity) throw new HttpError(400, 'bad_quantity');
    return ok(restock(params.sku.toUpperCase(), body.quantity));
  }));

  r.get('/admin/inventory/low-stock', ({ req, query }) => {
    requireAdmin(req);
    return ok(lowStock(query.threshold === undefined ? undefined : Number(query.threshold)));
  });

  r.get('/admin/reports/summary', ({ req, query }) => {
    requireAdmin(req);
    return ok(salesSummary({ from: query.from, to: query.to }));
  });

  r.get('/admin/reports/sales.csv', ({ req, res, query }) => {
    requireAdmin(req);
    const name = `sales-${query.from || 'all'}-${query.to || 'now'}.csv`;
    sendText(res, 200, salesCsv({ from: query.from, to: query.to }), 'text/csv; charset=utf-8', {
      'content-disposition': `attachment; filename="${name}"`,
    });
  });

  r.get('/admin/reports/inventory.csv', ({ req, res }) => {
    requireAdmin(req);
    sendText(res, 200, inventoryCsv(), 'text/csv; charset=utf-8');
  });

  return r;
}
