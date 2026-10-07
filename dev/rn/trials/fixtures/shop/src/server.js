import http from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { getConfig } from './config.js';
import { setLogLevel, log } from './logger.js';
import { buildRouter } from './http/handlers.js';
import { restore, snapshot } from './store.js';
import { seedDemoData } from './seed.js';

const SNAPSHOT_FILE = process.env.SNAPSHOT_FILE ||
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'data', 'snapshot.json');

export function createServer() {
  const router = buildRouter();
  return http.createServer(router.handler());
}

function start() {
  const config = getConfig();
  setLogLevel(config.logLevel);

  if (!restore(SNAPSHOT_FILE)) {
    log.info('no snapshot found, seeding demo data', { file: SNAPSHOT_FILE });
    seedDemoData();
  }

  const server = createServer();
  server.listen(config.port, () => {
    log.info('listening', { port: config.port, store: config.store.name });
  });

  const shutdown = (signal) => {
    log.info('shutting down', { signal });
    server.close(() => {
      try {
        snapshot(SNAPSHOT_FILE);
      } catch (err) {
        log.error('snapshot failed', { error: err.message });
      }
      process.exit(0);
    });
  };
  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  start();
}
