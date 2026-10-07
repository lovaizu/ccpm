const LEVELS = { debug: 10, info: 20, warn: 30, error: 40, silent: 100 };

// Keep `node --test` output readable unless someone asks for logs explicitly.
let threshold = LEVELS[process.env.LOG_LEVEL] ?? (process.env.NODE_TEST_CONTEXT ? LEVELS.silent : LEVELS.info);

export function setLogLevel(level) {
  if (!(level in LEVELS)) throw new Error(`Unknown log level: ${level}`);
  threshold = LEVELS[level];
}

function write(level, msg, fields) {
  if (LEVELS[level] < threshold) return;
  const line = JSON.stringify({ t: new Date().toISOString(), level, msg, ...fields });
  if (LEVELS[level] >= LEVELS.warn) process.stderr.write(line + '\n');
  else process.stdout.write(line + '\n');
}

export const log = {
  debug: (msg, fields = {}) => write('debug', msg, fields),
  info: (msg, fields = {}) => write('info', msg, fields),
  warn: (msg, fields = {}) => write('warn', msg, fields),
  error: (msg, fields = {}) => write('error', msg, fields),
};
