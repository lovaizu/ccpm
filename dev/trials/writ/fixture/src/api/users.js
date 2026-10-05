const { data } = require('./store');

function toResponse(user) {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
  };
}

function list(req, res) {
  let result = data.users;
  if (req.query.team) {
    result = result.filter((u) => u.team === req.query.team);
  }
  res.json({ items: result.map(toResponse) });
}

function get(req, res) {
  const user = data.users.find((u) => u.id === req.params.id);
  if (!user) {
    return res.status(404).json({ error: 'user not found' });
  }
  res.json(toResponse(user));
}

module.exports = { list, get };
