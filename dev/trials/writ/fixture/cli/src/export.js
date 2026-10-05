const fs = require('fs');

const COLUMNS = ['id', 'title', 'status', 'assigneeId', 'dueDate'];

function toCsv(tasks) {
  const escape = (v) => {
    const s = v === null || v === undefined ? '' : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lines = [COLUMNS.join(',')];
  for (const t of tasks) {
    lines.push(COLUMNS.map((c) => escape(t[c])).join(','));
  }
  // Add a BOM so the text is not garbled when opened in Excel
  return '﻿' + lines.join('\r\n') + '\r\n';
}

async function fetchAllTasks(server, status) {
  const params = new URLSearchParams();
  if (status) params.set('status', status);
  const res = await fetch(`${server}/api/tasks?${params}`);
  if (!res.ok) {
    throw new Error(`Could not fetch tasks: ${res.status}`);
  }
  const body = await res.json();
  return body.items;
}

async function exportTasks(config, opts) {
  let tasks = await fetchAllTasks(config.server, opts.status);
  if (opts.since) {
    tasks = tasks.filter((t) => t.dueDate && t.dueDate >= opts.since);
  }
  let output;
  if (opts.format === 'json') output = JSON.stringify(tasks, null, 2) + '\n';
  else if (opts.format === 'csv') output = toCsv(tasks);
  else throw new Error(`Unknown format: ${opts.format}`);

  if (opts.out) {
    fs.writeFileSync(opts.out, output);
    console.error(`Wrote ${tasks.length} tasks to ${opts.out}`);
  } else {
    process.stdout.write(output);
  }
}

module.exports = { exportTasks, toCsv };
