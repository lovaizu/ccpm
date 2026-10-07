/*!
 * postcode-lite v1.4.2
 * (c) 2019 Hollis Brandt
 * Released under the MIT License.
 *
 * Vendored copy. Do not edit here; upstream is unmaintained but stable.
 */
'use strict';

// [from, to, state] on the first three digits of a US ZIP code.
var US_PREFIXES = [
  [10, 27, 'MA'],
  [100, 149, 'NY'],
  [150, 196, 'PA'],
  [200, 205, 'DC'],
  [270, 289, 'NC'],
  [300, 319, 'GA'],
  [320, 349, 'FL'],
  [430, 459, 'OH'],
  [480, 499, 'MI'],
  [550, 567, 'MN'],
  [600, 629, 'IL'],
  [750, 799, 'TX'],
  [800, 816, 'CO'],
  [840, 847, 'UT'],
  [850, 865, 'AZ'],
  [889, 898, 'NV'],
  [900, 961, 'CA'],
  [970, 979, 'OR'],
  [980, 994, 'WA']
];

var ZONES = {
  WEST: ['CA', 'OR', 'WA', 'AZ', 'NV', 'CO', 'UT'],
  CENTRAL: ['TX', 'IL', 'MN', 'MI', 'OH'],
  EAST: ['NY', 'PA', 'MA', 'DC', 'GA', 'FL', 'NC']
};

var CA_PROVINCES = {
  A: 'NL', B: 'NS', C: 'PE', E: 'NB', G: 'QC', H: 'QC', J: 'QC',
  K: 'ON', L: 'ON', M: 'ON', N: 'ON', P: 'ON', R: 'MB', S: 'SK',
  T: 'AB', V: 'BC', X: 'NT', Y: 'YT'
};

function zoneOf(state) {
  for (var zone in ZONES) {
    if (ZONES[zone].indexOf(state) !== -1) return zone;
  }
  return null;
}

function normalize(code, country) {
  if (code == null) return '';
  var c = String(code).toUpperCase().replace(/\s+/g, '');
  country = (country || 'US').toUpperCase();
  if (country === 'US') {
    // ZIP+4 -> ZIP
    c = c.replace(/-\d{4}$/, '');
  }
  if (country === 'CA' && c.length === 6) {
    c = c.slice(0, 3) + ' ' + c.slice(3);
  }
  return c;
}

function isValid(code, country) {
  var c = normalize(code, country);
  country = (country || 'US').toUpperCase();
  if (country === 'US') return /^\d{5}$/.test(c);
  if (country === 'CA') return /^[A-Z]\d[A-Z] \d[A-Z]\d$/.test(c);
  return c.length > 0;
}

/**
 * lookup('94110') -> { country: 'US', state: 'CA', zone: 'WEST' }
 * lookup('K1A 0B1', 'CA') -> { country: 'CA', province: 'ON' }
 * Returns null when the code is not recognised.
 */
function lookup(code, country) {
  country = (country || 'US').toUpperCase();
  if (!isValid(code, country)) return null;
  var c = normalize(code, country);
  if (country === 'US') {
    var prefix = parseInt(c.slice(0, 3), 10);
    for (var i = 0; i < US_PREFIXES.length; i++) {
      var row = US_PREFIXES[i];
      if (prefix >= row[0] && prefix <= row[1]) {
        return { country: 'US', state: row[2], zone: zoneOf(row[2]) };
      }
    }
    return null;
  }
  if (country === 'CA') {
    var province = CA_PROVINCES[c.charAt(0)];
    return province ? { country: 'CA', province: province } : null;
  }
  return null;
}

module.exports = {
  normalize: normalize,
  isValid: isValid,
  lookup: lookup,
  version: '1.4.2'
};
