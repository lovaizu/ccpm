import { db } from './store.js';
import { getConfig } from './config.js';
import { log } from './logger.js';

export class InventoryError extends Error {
  constructor(code, sku) {
    super(`${code}: ${sku}`);
    this.code = code;
    this.sku = sku;
  }
}

/**
 * @param {Array<{sku: string, onHand: number}>} entries
 */
export function seedInventory(entries) {
  for (const { sku, onHand } of entries) {
    db.inventory.set(sku, { sku, onHand, reserved: 0, updatedAt: new Date().toISOString() });
  }
}

export function getStock(sku) {
  return db.inventory.get(sku) || null;
}

/** Units that can still be sold. Unknown SKUs have none. */
export function available(sku) {
  const item = db.inventory.get(sku);
  if (!item) return 0;
  return item.onHand - item.reserved;
}

/**
 * Hold stock for an order being paid for. All lines or none.
 * @param {Array<{sku: string, quantity: number}>} lines
 */
export function reserve(lines) {
  for (const line of lines) {
    const item = db.inventory.get(line.sku);
    if (!item) continue; // digital goods are not stocked
    if (item.onHand - item.reserved < line.quantity) {
      throw new InventoryError('insufficient_stock', line.sku);
    }
  }
  for (const line of lines) {
    const item = db.inventory.get(line.sku);
    if (item) item.reserved += line.quantity;
  }
}

export function release(lines) {
  for (const line of lines) {
    const item = db.inventory.get(line.sku);
    if (item) item.reserved = Math.max(0, item.reserved - line.quantity);
  }
}

/** Turn a reservation into a sale once payment has gone through. */
export function commit(lines) {
  for (const line of lines) {
    const item = db.inventory.get(line.sku);
    if (!item) continue;
    item.reserved = Math.max(0, item.reserved - line.quantity);
    item.onHand -= line.quantity;
    item.updatedAt = new Date().toISOString();
  }
}

export function restock(sku, quantity) {
  const item = db.inventory.get(sku);
  if (!item) throw new InventoryError('unknown_sku', sku);
  item.onHand += quantity;
  item.updatedAt = new Date().toISOString();
  log.info('restocked', { sku, onHand: item.onHand });
  return item;
}

/** Return units from a refund to the shelf. */
export function putBack(sku, quantity) {
  const item = db.inventory.get(sku);
  if (!item) return;
  item.onHand += quantity;
}

export function lowStock(threshold = getConfig().inventory.lowStockThreshold) {
  const rows = [];
  for (const item of db.inventory.values()) {
    const left = item.onHand - item.reserved;
    if (left <= threshold) rows.push({ sku: item.sku, available: left, onHand: item.onHand });
  }
  return rows.sort((a, b) => a.available - b.available);
}
