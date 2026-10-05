// The single place the UI calls the API from. UI code does not use fetch directly; it goes through here.

async function request(path, options) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(body.error || `request failed: ${res.status}`);
  }
  return body;
}

function toTask(raw) {
  return {
    id: raw.id,
    title: raw.title,
    status: raw.status,
    assigneeId: raw.assigneeId,
    due: raw.dueDate ? new Date(raw.dueDate) : null,
  };
}

export async function fetchTasks(filter) {
  const params = new URLSearchParams();
  if (filter && filter.status) params.set('status', filter.status);
  if (filter && filter.assignee) params.set('assignee', filter.assignee);
  const body = await request('/api/tasks?' + params.toString());
  return { tasks: body.items.map(toTask), total: body.total };
}

export async function createTask(title, assigneeId, dueDate) {
  const body = await request('/api/tasks', {
    method: 'POST',
    body: JSON.stringify({ title, assigneeId, dueDate }),
  });
  return toTask(body);
}

export async function changeStatus(taskId, status) {
  const body = await request('/api/tasks/' + taskId, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
  return toTask(body);
}

export async function fetchUsers() {
  const body = await request('/api/users');
  const byId = {};
  for (const u of body.items) {
    byId[u.id] = { id: u.id, name: u.name };
  }
  return byId;
}
