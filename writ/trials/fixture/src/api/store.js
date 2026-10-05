// Temporary in-memory store. Replaced by a database in production.
const data = {
  users: [
    { id: 'u1', name: 'Hanako Sato', email: 'hanako.sato@example.com', team: 'platform' },
    { id: 'u2', name: 'Ichiro Suzuki', email: 'ichiro.suzuki@example.com', team: 'web' },
  ],
  tasks: [
    { id: 't1', title: 'Fix the wording on the login screen', status: 'open', assigneeId: 'u2', dueDate: '2026-10-10', createdAt: '2026-09-28T09:00:00Z' },
    { id: 't2', title: 'Add rate limiting to the API', status: 'in_progress', assigneeId: 'u1', dueDate: '2026-10-17', createdAt: '2026-09-29T02:30:00Z' },
    { id: 't3', title: 'Fix garbled text in CSV export', status: 'done', assigneeId: 'u1', dueDate: null, createdAt: '2026-09-20T05:10:00Z' },
  ],
};

let nextTaskNumber = 4;

function newTaskId() {
  return 't' + nextTaskNumber++;
}

module.exports = { data, newTaskId };
