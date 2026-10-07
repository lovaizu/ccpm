import { loadConfig, setConfig } from '../src/config.js';
import { resetStore } from '../src/store.js';
import { seedInventory } from '../src/inventory.js';
import { clearOutbox } from '../src/notifications/mailer.js';

export const ADMIN_TOKEN = 'test-admin-token';

/** Fresh config, empty store, plenty of stock. Call from beforeEach. */
export function freshShop({ stock = 50 } = {}) {
  setConfig(loadConfig({ MAIL_TRANSPORT: 'memory', ADMIN_TOKEN }));
  resetStore();
  clearOutbox();
  seedInventory(
    ['TEA-001', 'TEA-002', 'TEA-003', 'MUG-010', 'POT-020', 'KTL-200', 'BK-101'].map((sku) => ({
      sku,
      onHand: stock,
    })),
  );
}

export const CA_ADDRESS = {
  name: 'Mara Okafor',
  line1: '1 Valencia St',
  city: 'San Francisco',
  state: 'CA',
  postcode: '94110',
  country: 'US',
};
