// Product catalog. The list is small and changes with each season's drop, so
// it lives in code and ships with the weekly deploy.

const PRODUCTS = [
  {
    sku: 'TEA-001',
    name: 'Sencha green tea, 100 g',
    priceCents: 1450,
    weightGrams: 120,
    category: 'grocery',
  },
  {
    sku: 'TEA-002',
    name: 'Earl Grey, tin of 40 bags',
    priceCents: 1200,
    salePriceCents: 990,
    weightGrams: 150,
    category: 'grocery',
  },
  {
    sku: 'TEA-003',
    name: 'Hojicha roasted tea, 80 g',
    priceCents: 1300,
    weightGrams: 100,
    category: 'grocery',
  },
  {
    sku: 'MUG-010',
    name: 'Stoneware mug, ash glaze',
    priceCents: 2400,
    weightGrams: 450,
    category: 'kitchen',
  },
  {
    sku: 'POT-020',
    name: 'Cast iron teapot, 0.8 L',
    priceCents: 5800,
    weightGrams: 1600,
    category: 'kitchen',
  },
  {
    sku: 'KTL-200',
    name: 'Gooseneck kettle',
    priceCents: 6900,
    weightGrams: 1300,
    category: 'kitchen',
  },
  {
    sku: 'BK-101',
    name: 'The Quiet Cup (book)',
    priceCents: 1800,
    weightGrams: 400,
    category: 'books',
  },
  {
    sku: 'GFT-050',
    name: 'Gift card, $50',
    priceCents: 5000,
    weightGrams: 0,
    category: 'giftcard',
    shippable: false,
    taxable: false,
  },
];

const bySku = new Map(PRODUCTS.map((p) => [p.sku, p]));

export function getProduct(sku) {
  return bySku.get(String(sku).toUpperCase()) || null;
}

export function listProducts({ category } = {}) {
  if (!category) return [...PRODUCTS];
  return PRODUCTS.filter((p) => p.category === category);
}

/**
 * The price a customer pays today.
 * @param {{priceCents: number, salePriceCents?: number}} product
 */
export function effectivePrice(product) {
  return product.salePriceCents ?? product.priceCents;
}

export function isShippable(product) {
  return product.shippable !== false;
}

export function allSkus() {
  return PRODUCTS.map((p) => p.sku);
}
