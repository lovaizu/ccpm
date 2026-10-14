# Decisions for the csvtidy README

- Reader: developers whose scripts break on CSV exports with stray spaces and empty rows, who now
  fix those files by hand in a spreadsheet.
- Why csvtidy: it tidies a whole folder in one command, and keeps each original beside it as
  `<name>.orig.csv`.
- Installation: not on PyPI; `pip install git+https://github.com/example/csvtidy`.
- Documentation: `csvtidy --help`, and the repository at github.com/example/csvtidy.
- License: MIT; the README names it, and there is no LICENSE file to link to yet.
