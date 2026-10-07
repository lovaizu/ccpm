# Architecture

One Node.js process, no framework, no database yet: state lives in memory
(`src/store.js`) and is written to `data/snapshot.json` on shutdown.

## Modules

| Area | File | Role |
| --- | --- | --- |
| HTTP | `src/http/router.js` | Route matching, body parsing (JSON or form), JSON/text responses |
| HTTP | `src/http/handlers.js` | All routes; maps domain error codes to HTTP statuses |
| Catalog | `src/catalog.js` | Products, prices (cents), sale prices |
| Cart | `src/cart.js` | Lines, quantities, coupon on the cart, merchandise totals |
| Coupons | `src/coupons.js` | Percent, fixed-amount and free-shipping coupons |
| Shipping | `src/shipping.js` | Region from address (via `vendor/postcode-lite`), region fee table, delivery estimate |
| Tax | `src/tax.js` | US state sales tax, grocery exemptions |
| Inventory | `src/inventory.js` | Stock, reservations during payment, restock, low-stock list |
| Checkout | `src/checkout.js` | Address, quote, reserve, charge, create order, email |
| Orders | `src/orders.js` | Orders, shipping, refunds, import from the old platform |
| Payments | `src/payments/` | PayGate client (real and fake transport), retries |
| Accounts | `src/accounts.js` | Customers, display names |
| Notifications | `src/notifications/` | Plain-text email templates and the mail transport |
| Reports | `src/reports.js` | Sales CSV and summary for finance, inventory CSV |
| Config | `src/config.js` | `config/default.json`, then `config/local.json`, then env vars |

## Money

Amounts inside the app are integer cents. Forms, CSV imports and the payment
gateway use decimal dollar strings; `src/money.js` converts at the edge.

## A checkout request

1. `POST /carts/:id/checkout` reaches `router.js`, which parses the body. A
   form post gives every field as a string; a JSON post keeps its types.
2. `handlers.js` calls `checkout()` in `checkout.js`.
3. `checkout()` reads the address, finds the shipping region, and prices the
   cart: `cart.computeTotals` → `shipping.shippingFee` → `tax.computeTax`.
4. Stock is reserved (`inventory.reserve`), the card is charged through
   `payments.chargeWithRetry`, and the reservation is committed or released.
5. `orders.createOrder` stores the order with the prices and a copy of the
   coupon, and `mailer.sendOrderConfirmation` sends the receipt.
6. The order goes back as JSON with status 201.
