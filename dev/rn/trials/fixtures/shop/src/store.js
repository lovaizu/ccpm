// In-memory persistence. Production runs a single instance and snapshots the
// store to disk on shutdown (see server.js); the Postgres move is tracked
// separately.

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import path from 'node:path';

export const db = {
  accounts: new Map(),
  carts: new Map(),
  orders: new Map(),
  inventory: new Map(),
};

const counters = { acct: 1000, cart: 1, ord: 50000 };

export function nextId(prefix) {
  if (!(prefix in counters)) counters[prefix] = 1;
  counters[prefix] += 1;
  return `${prefix}_${counters[prefix]}`;
}

export function resetStore() {
  for (const table of Object.values(db)) table.clear();
  counters.acct = 1000;
  counters.cart = 1;
  counters.ord = 50000;
}

export function snapshot(file) {
  const data = {
    counters,
    tables: Object.fromEntries(
      Object.entries(db).map(([name, table]) => [name, [...table.entries()]]),
    ),
  };
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, JSON.stringify(data));
}

export function restore(file) {
  if (!existsSync(file)) return false;
  const data = JSON.parse(readFileSync(file, 'utf8'));
  Object.assign(counters, data.counters);
  for (const [name, rows] of Object.entries(data.tables)) {
    if (!db[name]) continue;
    db[name].clear();
    for (const [key, value] of rows) db[name].set(key, value);
  }
  return true;
}
