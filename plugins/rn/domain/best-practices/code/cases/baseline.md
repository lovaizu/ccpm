# Baseline

The shortfalls of code made before this best practice, which its questions must catch, as the
meta's Q10 asks of a best practice made from real cases. Each names the question that catches it.

| Shortfall | Where it shows | Question |
| --- | --- | --- |
| One module holds 1,342 lines and 50 functions: rules, input, and output at once. | `plugins/lane/hooks/lane/domain/guard.py`, and the case [guard](guard.md) | Q1 |
| The tests came after the code, and 237 mutants survived, 11.46%. | rn's tests, CI run [42395544664](https://github.com/lovaizu/ccpm/actions/runs/42395544664) | Q7, Q8, Q13 |
| 14 functions go past the established limits on complexity and size: 8 of McCabe's complexity, 4 of returns, 1 of branches, and 1 of arguments. | `ruff check --select C901,PLR0911,PLR0912,PLR0913,PLR0915 plugins/lane plugins/rn` | Q12 |
