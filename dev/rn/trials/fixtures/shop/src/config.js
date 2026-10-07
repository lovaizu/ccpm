import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function readJson(file) {
  try {
    return JSON.parse(readFileSync(file, 'utf8'));
  } catch (err) {
    throw new Error(`Could not read config file ${file}: ${err.message}`);
  }
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

/**
 * Merge `extra` into `base` recursively. Arrays and scalars from `extra` win.
 */
function deepMerge(base, extra) {
  const out = { ...base };
  for (const [key, value] of Object.entries(extra || {})) {
    if (isPlainObject(value) && isPlainObject(out[key])) {
      out[key] = deepMerge(out[key], value);
    } else {
      out[key] = value;
    }
  }
  return out;
}

/**
 * Build the runtime configuration.
 *
 * Order of precedence (last wins):
 *   1. config/default.json (or the file named by SHOP_CONFIG)
 *   2. config/local.json, when present (not committed)
 *   3. environment variables
 *
 * @param {Record<string, string | undefined>} [env]
 */
export function loadConfig(env = process.env) {
  const file = env.SHOP_CONFIG || path.join(ROOT, 'config', 'default.json');
  let cfg = readJson(file);

  const localFile = path.join(ROOT, 'config', 'local.json');
  if (!env.SHOP_CONFIG && existsSync(localFile)) {
    cfg = deepMerge(cfg, readJson(localFile));
  }

  if (env.PORT) cfg.port = parseInt(env.PORT, 10);
  if (env.LOG_LEVEL) cfg.logLevel = env.LOG_LEVEL;
  if (env.ADMIN_TOKEN) cfg.adminToken = env.ADMIN_TOKEN;
  if (env.SITE_URL) cfg.store.siteUrl = env.SITE_URL;

  if (env.PAYMENT_GATEWAY_URL) cfg.payments.gatewayUrl = env.PAYMENT_GATEWAY_URL;
  if (env.PAYMENT_API_KEY) cfg.payments.apiKey = env.PAYMENT_API_KEY;
  if (env.PAYMENT_RETRIES) cfg.payments.retries = env.PAYMENT_RETRIES;
  if (env.PAYMENT_TIMEOUT_MS) cfg.payments.timeoutMs = Number(env.PAYMENT_TIMEOUT_MS);

  if (env.FREE_SHIPPING_OVER_CENTS) {
    cfg.shipping.freeOverCents = Number(env.FREE_SHIPPING_OVER_CENTS);
  }
  if (env.LOW_STOCK_THRESHOLD) {
    cfg.inventory.lowStockThreshold = Number(env.LOW_STOCK_THRESHOLD);
  }

  if (env.MAIL_TRANSPORT) cfg.mail.transport = env.MAIL_TRANSPORT;
  if (env.MAIL_FROM) cfg.mail.from = env.MAIL_FROM;

  return cfg;
}

let current = null;

export function getConfig() {
  if (!current) current = loadConfig();
  return current;
}

/** Replace the active configuration. Used by tests and by the server bootstrap. */
export function setConfig(cfg) {
  current = cfg;
}
