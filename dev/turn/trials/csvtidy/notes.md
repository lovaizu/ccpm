# csvtidy notes

csvtidy is a small command-line tool, published in its own repository at
github.com/example/csvtidy.

- What it does: reads a CSV file, trims spaces around every cell, drops rows that are entirely
  empty, and writes the result to standard output. It never changes the input file.
- Who uses it: people who get CSV exports from spreadsheets and other tools and feed them to scripts
  that break on stray spaces and empty rows.
- Why not a spreadsheet: it runs in a pipeline, on files of any size, without opening anything.
- Needs: Python 3.9 or later, nothing else.
- Install: `pip install csvtidy`
- Run: `csvtidy data.csv > clean.csv`. `--delimiter ';'` reads files split by semicolons.
- Sample: `samples/messy.csv` in the repository holds

      name , city
       Ana ,Lisbon

      Bo,  Oslo

  and `csvtidy samples/messy.csv` prints

      name,city
      Ana,Lisbon
      Bo,Oslo

- More: `docs/options.md` lists every option.
