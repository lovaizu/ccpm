// Demo data for local development. Production restores from the snapshot.

import { allSkus } from './catalog.js';
import { seedInventory } from './inventory.js';
import { createAccount, importLegacyAccount } from './accounts.js';

const STARTING_STOCK = {
  'TEA-001': 40,
  'TEA-002': 25,
  'TEA-003': 12,
  'MUG-010': 18,
  'POT-020': 6,
  'KTL-200': 4,
  'BK-101': 30,
};

export function seedDemoData() {
  seedInventory(
    allSkus()
      .filter((sku) => sku in STARTING_STOCK)
      .map((sku) => ({ sku, onHand: STARTING_STOCK[sku] })),
  );

  createAccount({ email: 'mara@example.com', firstName: 'Mara', lastName: 'Okafor', nickname: 'mara' });
  createAccount({ email: 'teo@example.com', firstName: 'Teo', lastName: 'Lindqvist' });
  createAccount({ email: 'kit@larkspur.example', firstName: 'Kit', lastName: 'Ames' });
  importLegacyAccount({
    email: 'June.Park@example.com',
    first_name: 'June',
    last_name: null,
    screen_name: '',
    newsletter: '1',
    created: '2023-04-11T09:30:00Z',
  });
}
