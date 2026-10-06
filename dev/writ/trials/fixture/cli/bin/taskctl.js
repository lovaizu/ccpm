#!/usr/bin/env node
const { loadConfig } = require('../src/config');
const { exportTasks } = require('../src/export');

const USAGE = `Usage: taskctl export [--format json|csv] [--status <status>] [--since <YYYY-MM-DD>] [--out <file>]`;

function parseArgs(argv) {
  const opts = { format: 'json' };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--format') opts.format = argv[++i];
    else if (arg === '--status') opts.status = argv[++i];
    else if (arg === '--since') opts.since = argv[++i];
    else if (arg === '--out') opts.out = argv[++i];
    else throw new Error(`Unknown option: ${arg}`);
  }
  return opts;
}

async function main() {
  const [command, ...rest] = process.argv.slice(2);
  if (command !== 'export') {
    console.error(USAGE);
    process.exit(1);
  }
  const config = loadConfig();
  const opts = parseArgs(rest);
  await exportTasks(config, opts);
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
