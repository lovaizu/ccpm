# How taskboard is put together

taskboard is an internal web app that lists the team's tasks by assignee and due date. A single Node.js process serves both the API and the files for the UI.

## Directories

- `src/api/` is the API. `server.js` registers the routes, and `tasks.js` and `users.js` each handle their own endpoints. For now the data lives in memory in `store.js`; moving it to a database is a separate piece of work.
- `src/ui/` is the UI that runs in the browser. Only `api-client.js` calls the API; the UI code gets its data through it.
- `cli/` is an internal CLI (taskctl) that exports tasks to CSV or JSON files. It calls the API to do so, and is used by people who want totals without opening the UI. It ships as a package separate from the app.

## The contract between the API and the UI

The UI reads the fields of an API response by name. For example, it reads a task's due date from the `dueDate` field. When you change the name or shape of a field on the API side, fix `src/ui/api-client.js` in the same PR.

Lists are returned in the form `{ items: [...] }`, with `total` added where a count is needed. Errors are returned as an HTTP status with `{ error: "..." }`.
