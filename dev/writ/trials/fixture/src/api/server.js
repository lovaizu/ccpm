const express = require('express');
const tasks = require('./tasks');
const users = require('./users');

const app = express();
app.use(express.json());
app.use(express.static('src/ui'));

app.get('/api/tasks', tasks.list);
app.get('/api/tasks/:id', tasks.get);
app.post('/api/tasks', tasks.create);
app.patch('/api/tasks/:id', tasks.update);

app.get('/api/users', users.list);
app.get('/api/users/:id', users.get);

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`taskboard listening on ${port}`);
});
