// A small router on top of node:http. We outgrew a single switch statement
// but not enough to want a framework.

import { log } from '../logger.js';

export class HttpError extends Error {
  constructor(status, code, message, details) {
    super(message || code);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

const MAX_BODY_BYTES = 1_000_000;

function compile(pattern) {
  const names = [];
  const source = pattern
    .split('/')
    .map((part) => {
      if (part.startsWith(':')) {
        names.push(part.slice(1));
        return '([^/]+)';
      }
      return part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    })
    .join('/');
  return { regex: new RegExp(`^${source}/?$`), names };
}

/**
 * Read and parse the request body.
 *
 * JSON bodies keep their types. Form posts (application/x-www-form-urlencoded)
 * come through as an object of strings, the way the browser sent them.
 */
export async function readBody(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw new HttpError(413, 'body_too_large');
    chunks.push(chunk);
  }
  const raw = Buffer.concat(chunks).toString('utf8');
  if (!raw) return {};
  const type = (req.headers['content-type'] || '').split(';')[0].trim();
  if (type === 'application/x-www-form-urlencoded') {
    return Object.fromEntries(new URLSearchParams(raw));
  }
  if (type === 'application/json' || type === '') {
    try {
      return JSON.parse(raw);
    } catch {
      throw new HttpError(400, 'bad_json');
    }
  }
  throw new HttpError(415, 'unsupported_media_type');
}

export function sendJson(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(payload),
  });
  res.end(payload);
}

export function sendText(res, status, text, contentType = 'text/plain; charset=utf-8', extraHeaders = {}) {
  res.writeHead(status, { 'content-type': contentType, 'content-length': Buffer.byteLength(text), ...extraHeaders });
  res.end(text);
}

export const ok = (body) => ({ status: 200, body });
export const created = (body) => ({ status: 201, body });

export class Router {
  constructor() {
    this.routes = [];
  }

  add(method, pattern, handler) {
    this.routes.push({ method, pattern, handler, ...compile(pattern) });
    return this;
  }

  get(pattern, handler) { return this.add('GET', pattern, handler); }
  post(pattern, handler) { return this.add('POST', pattern, handler); }
  patch(pattern, handler) { return this.add('PATCH', pattern, handler); }
  delete(pattern, handler) { return this.add('DELETE', pattern, handler); }

  match(method, pathname) {
    let pathMatched = false;
    for (const route of this.routes) {
      const m = route.regex.exec(pathname);
      if (!m) continue;
      pathMatched = true;
      if (route.method !== method) continue;
      const params = {};
      route.names.forEach((name, i) => {
        params[name] = decodeURIComponent(m[i + 1]);
      });
      return { route, params };
    }
    return pathMatched ? { methodNotAllowed: true } : null;
  }

  /** Returns a request listener for http.createServer. */
  handler() {
    return async (req, res) => {
      const started = Date.now();
      const url = new URL(req.url, 'http://localhost');
      try {
        const found = this.match(req.method, url.pathname);
        if (!found) throw new HttpError(404, 'not_found');
        if (found.methodNotAllowed) throw new HttpError(405, 'method_not_allowed');
        const body = ['POST', 'PATCH', 'PUT'].includes(req.method) ? await readBody(req) : {};
        const ctx = { req, res, params: found.params, query: Object.fromEntries(url.searchParams), body };
        const result = await found.route.handler(ctx);
        if (!res.writableEnded) {
          if (result === undefined) {
            res.writeHead(204);
            res.end();
          } else {
            sendJson(res, result.status, result.body);
          }
        }
      } catch (err) {
        if (err instanceof HttpError) {
          sendJson(res, err.status, { error: err.code, message: err.message, details: err.details });
        } else {
          log.error('unhandled error', { method: req.method, path: url.pathname, error: err.stack });
          sendJson(res, 500, { error: 'internal_error' });
        }
      } finally {
        log.debug('request', { method: req.method, path: url.pathname, ms: Date.now() - started, status: res.statusCode });
      }
    };
  }
}
