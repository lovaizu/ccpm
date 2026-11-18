# Software design of invoicer

- Each module of `invoicer/` holds one decision: `lines` the form of a line, `totals` how lines
  add up, `tax` how tax rounds, and `render` the invoice's layout.
- The package's `__init__.py` offers each public name, and nothing of its own.
