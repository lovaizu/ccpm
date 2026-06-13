# Marketplace rules (ccpm)

This repository is a plugin marketplace. A plugin only counts as shipped once it is reachable both by the machine manifest and by a human reader.

## Registering a plugin

- **Add every plugin to `.claude-plugin/marketplace.json`** — one entry under `plugins` with `name`, `description`, `source` (e.g. `./rn`), and `category`. This is what Claude Code reads to install the plugin.
- **List every plugin in the root `README.md`** with a link to its own README (e.g. `[rn](./rn/README.md)`) and a one-line description. This is the human entry point.
- **Keep the two in sync** — when you add, rename, or remove a plugin, update `marketplace.json` and the root `README.md` in the same change.
