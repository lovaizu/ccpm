# `rn`

What rn must give its users is in [its product vision](product-vision.md). How rn gives it, and how
its tests check it, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/rn/tests` from the repository root. They lie in
  `tests/unit/`, at the path of what each tests, and `tests/architecture/`, a file for each story
  of the architecture, `test_s<n>_*.py`, with a test for each of its paths. The architecture tests
  run rn's lanes and routes as laid, by its hook entries, through Lane's double of Claude Code in
  `dev/lane/testing.py`, on a repository of tidy, the tool of the README's walkthrough, with a
  script on the PATH in place of `gh`. `sh dev/scripts/mutate.sh rn` runs the mutation testing
  set in `cosmic-ray.toml`, as [dev/README.md](../README.md) says.
- Lanes: the `lay.py` of Lane lays rn's lanes and routes from a proposal, as
  [Lane's lanes](../../plugins/lane/docs/lanes.md#the-proposal) say. `python3
  plugins/lane/scripts/lay.py up plugins/rn` prints the lanes laid now, for a proposal that lays
  them again. The adapters it names lie in `plugins/rn/hooks/adapters/` with their cases.
- The best practice of each kind: `python3 dev/scripts/practices.py form <its JSON>` checks it,
  and `markdown` and `example` write its Markdown and the copy of its example.
- Product vision trial: not built yet. The plan is to run it on Lane's trial driver, `dev/lane/trials/trying.py`,
  in `lovaizu/playground`, with tidy's repository as the walkthrough finds it.
