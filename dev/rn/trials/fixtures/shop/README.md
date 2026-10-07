# Larkspur Supply shop backend

The HTTP API behind shop.larkspur.example, our online tea and teaware store:
products, carts and coupons, checkout with shipping and US sales tax, card
payments through PayGate, order emails, and the admin reports finance uses.

Deploys go out weekly from `main`.

## Run it

Needs Node.js 20 or later. There are no dependencies to install.

```sh
npm start            # http://localhost:3000, seeded with demo data
npm run dev          # same, restarting on file changes
```

Settings come from `config/default.json`; put local overrides in
`config/local.json` (not committed), or use environment variables:

| Variable | Meaning |
| --- | --- |
| `PORT` | Port to listen on |
| `ADMIN_TOKEN` | Token for the `/admin` routes and order shipping/refunds (`x-admin-token` header) |
| `PAYMENT_API_KEY` | PayGate key; without one, payments go to the in-memory fake gateway |
| `PAYMENT_GATEWAY_URL`, `PAYMENT_RETRIES`, `PAYMENT_TIMEOUT_MS` | Gateway connection |
| `FREE_SHIPPING_OVER_CENTS` | Free US shipping above this subtotal |
| `LOW_STOCK_THRESHOLD` | When the low-stock alert fires |
| `MAIL_TRANSPORT` | `log` (default) or `memory` |
| `LOG_LEVEL` | `debug`, `info`, `warn`, `error` or `silent` |

With the fake gateway, use the card token `tok_visa` to pay, `tok_decline` for
a declined card, and `tok_flaky` for a gateway that fails once.

## Tests

```sh
npm test
```

## More

- [docs/architecture.md](docs/architecture.md) — modules and how a request flows
- [docs/incidents.md](docs/incidents.md) — production incidents, last quarter
