const { data, newTaskId } = require('./store');

const STATUSES = ['open', 'in_progress', 'done'];

function toResponse(task) {
  return {
    id: task.id,
    title: task.title,
    status: task.status,
    assigneeId: task.assigneeId,
    dueDate: task.dueDate,
  };
}

function list(req, res) {
  let result = data.tasks;
  if (req.query.status) {
    result = result.filter((t) => t.status === req.query.status);
  }
  if (req.query.assignee) {
    result = result.filter((t) => t.assigneeId === req.query.assignee);
  }
  result = result.slice().sort((a, b) => (a.dueDate || '9999') < (b.dueDate || '9999') ? -1 : 1);
  res.json({ items: result.map(toResponse), total: result.length });
}

function get(req, res) {
  const task = data.tasks.find((t) => t.id === req.params.id);
  if (!task) {
    return res.status(404).json({ error: 'task not found' });
  }
  res.json(toResponse(task));
}

function create(req, res) {
  const { title, assigneeId, dueDate } = req.body;
  if (!title) {
    return res.status(400).json({ error: 'title is required' });
  }
  const task = {
    id: newTaskId(),
    title,
    status: 'open',
    assigneeId: assigneeId || null,
    dueDate: dueDate || null,
    createdAt: new Date().toISOString(),
  };
  data.tasks.push(task);
  res.status(201).json(toResponse(task));
}

function update(req, res) {
  const task = data.tasks.find((t) => t.id === req.params.id);
  if (!task) {
    return res.status(404).json({ error: 'task not found' });
  }
  const { title, status, assigneeId, dueDate } = req.body;
  if (status !== undefined && !STATUSES.includes(status)) {
    return res.status(400).json({ error: 'invalid status' });
  }
  if (title !== undefined) task.title = title;
  if (status !== undefined) task.status = status;
  if (assigneeId !== undefined) task.assigneeId = assigneeId;
  if (dueDate !== undefined) task.dueDate = dueDate;
  res.json(toResponse(task));
}

module.exports = { list, get, create, update };
