import { getConfig } from '../config.js';
import { log } from '../logger.js';
import { toCents } from '../money.js';
import { GatewayClient, GatewayError, HttpTransport, FakeTransport } from './gateway.js';

let defaultClient = null;

export function getGatewayClient() {
  if (!defaultClient) {
    const { gatewayUrl, apiKey, timeoutMs } = getConfig().payments;
    const transport = apiKey ? new HttpTransport({ baseUrl: gatewayUrl, apiKey, timeoutMs }) : new FakeTransport();
    defaultClient = new GatewayClient(transport);
  }
  return defaultClient;
}

export function setGatewayClient(client) {
  defaultClient = client;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function backoffMs(attempt) {
  return Math.min(2000, 100 * 2 ** attempt);
}

function normalizeCharge(raw) {
  return {
    id: raw.id,
    status: raw.status,
    amountCents: toCents(raw.amount),
    declineCode: raw.decline_code || null,
  };
}

/**
 * Charge a card, retrying gateway errors that are safe to retry. The same
 * idempotency key is used for every attempt, so a retry can never charge twice.
 *
 * @param {{amountCents: number, currency: string, source: string, idempotencyKey: string, description?: string}} req
 * @param {{client?: GatewayClient, backoff?: (attempt: number) => number}} [opts]
 */
export async function chargeWithRetry(req, { client = getGatewayClient(), backoff = backoffMs } = {}) {
  const attempts = getConfig().payments.retries + 1;
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      const raw = await client.charge(req);
      return normalizeCharge(raw);
    } catch (err) {
      if (!(err instanceof GatewayError) || !err.retryable) throw err;
      lastError = err;
      log.warn('charge attempt failed', { attempt, attempts, error: err.message });
      if (attempt < attempts) await sleep(backoff(attempt));
    }
  }
  throw lastError;
}

export async function refundCharge(chargeId, amountCents, { client = getGatewayClient() } = {}) {
  const raw = await client.refund(chargeId, amountCents);
  return { id: raw.id, status: raw.status, amountCents: toCents(raw.amount) };
}
