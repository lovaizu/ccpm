// Client for the PayGate card gateway.
//
// The real API speaks JSON over HTTPS with amounts as decimal strings in the
// major unit ("12.50"). In development and tests we use FakeTransport, which
// mimics the responses we have seen from the sandbox.

import { randomUUID } from 'node:crypto';
import { centsToDecimal } from '../money.js';

export class GatewayError extends Error {
  constructor(message, { status, retryable = false, code } = {}) {
    super(message);
    this.status = status;
    this.retryable = retryable;
    this.code = code;
  }
}

export class HttpTransport {
  constructor({ baseUrl, apiKey, timeoutMs }) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
    this.timeoutMs = timeoutMs;
  }

  async post(path, body, idempotencyKey) {
    let res;
    try {
      res = await fetch(`${this.baseUrl}${path}`, {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          authorization: `Bearer ${this.apiKey}`,
          'idempotency-key': idempotencyKey,
        },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(this.timeoutMs),
      });
    } catch (err) {
      throw new GatewayError(`Gateway unreachable: ${err.message}`, { retryable: true });
    }
    const data = await res.json().catch(() => ({}));
    if (res.status >= 500) {
      throw new GatewayError(data.message || 'Gateway error', { status: res.status, retryable: true });
    }
    if (res.status >= 400) {
      throw new GatewayError(data.message || 'Rejected', { status: res.status, code: data.code });
    }
    return data;
  }
}

/**
 * In-memory stand-in for the gateway.
 *
 * Special tokens:
 *   tok_decline  -> card declined
 *   tok_flaky    -> first call fails with a retryable error, then succeeds
 *   tok_down     -> always fails with a retryable error
 */
export class FakeTransport {
  constructor() {
    this.charges = new Map();
    this.calls = [];
    this.seenFlaky = new Set();
  }

  async post(path, body, idempotencyKey) {
    this.calls.push({ path, body, idempotencyKey });
    if (path === '/charges') return this.#charge(body, idempotencyKey);
    if (path.startsWith('/charges/') && path.endsWith('/refunds')) {
      const id = path.split('/')[2];
      return this.#refund(id, body);
    }
    throw new GatewayError(`Unknown path ${path}`, { status: 404 });
  }

  #charge(body, key) {
    for (const charge of this.charges.values()) {
      if (charge.idempotency_key === key) return charge;
    }
    if (body.source === 'tok_down') {
      throw new GatewayError('Service unavailable', { status: 503, retryable: true });
    }
    if (body.source === 'tok_flaky' && !this.seenFlaky.has(key)) {
      this.seenFlaky.add(key);
      throw new GatewayError('Upstream timeout', { status: 504, retryable: true });
    }
    const charge = {
      id: `ch_${randomUUID().slice(0, 12)}`,
      amount: body.amount,
      currency: body.currency,
      status: body.source === 'tok_decline' ? 'declined' : 'succeeded',
      decline_code: body.source === 'tok_decline' ? 'card_declined' : null,
      idempotency_key: key,
      created: Math.floor(Date.now() / 1000),
    };
    this.charges.set(charge.id, charge);
    return charge;
  }

  #refund(id, body) {
    const charge = this.charges.get(id);
    if (!charge) throw new GatewayError('No such charge', { status: 404, code: 'not_found' });
    return { id: `re_${randomUUID().slice(0, 12)}`, charge: id, amount: body.amount, status: 'succeeded' };
  }
}

export class GatewayClient {
  constructor(transport) {
    this.transport = transport;
  }

  /**
   * @param {{amountCents: number, currency: string, source: string, idempotencyKey?: string, description?: string}} req
   */
  async charge({ amountCents, currency, source, idempotencyKey, description }) {
    return this.transport.post(
      '/charges',
      { amount: centsToDecimal(amountCents), currency: currency.toLowerCase(), source, description },
      idempotencyKey || randomUUID(),
    );
  }

  async refund(chargeId, amountCents) {
    return this.transport.post(
      `/charges/${chargeId}/refunds`,
      { amount: centsToDecimal(amountCents) },
      randomUUID(),
    );
  }
}
