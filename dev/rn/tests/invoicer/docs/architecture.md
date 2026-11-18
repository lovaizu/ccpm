# Architecture of invoicer

- Components: `lines` parses the lines of an invoice, `totals` sums them, `tax` gives the tax of
  an amount at a rate, and `render` gives the invoice as text. `invoicer/__init__.py` offers each.
- Test strategy: unit tests of each module with pytest.
