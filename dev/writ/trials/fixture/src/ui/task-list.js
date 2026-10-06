import { fetchTasks, fetchUsers, changeStatus } from './api-client.js';

const STATUS_LABELS = { open: 'To do', in_progress: 'In progress', done: 'Done' };

function formatDue(due) {
  if (!due) return 'No due date';
  return `${due.getMonth() + 1}/${due.getDate()}`;
}

export async function renderTaskList(container, filter) {
  const [{ tasks, total }, users] = await Promise.all([fetchTasks(filter), fetchUsers()]);
  container.innerHTML = '';

  const heading = document.createElement('p');
  heading.textContent = `${total} tasks`;
  container.appendChild(heading);

  for (const task of tasks) {
    const row = document.createElement('li');
    const assignee = users[task.assigneeId];
    row.textContent = `${task.title} (${assignee ? assignee.name : 'Unassigned'}, ${formatDue(task.due)})`;

    const button = document.createElement('button');
    button.textContent = STATUS_LABELS[task.status];
    button.addEventListener('click', async () => {
      const next = task.status === 'open' ? 'in_progress' : 'done';
      await changeStatus(task.id, next);
      renderTaskList(container, filter);
    });
    row.appendChild(button);
    container.appendChild(row);
  }
}
