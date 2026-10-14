# Notes on csvtidy

I started this in March after the third time a monthly export broke the billing import script on
stray spaces. First version was a sed one-liner, then a pandas script, which was too slow to start
on the build server, so now it is plain Python with the csv module.

- `csvtidy <folder>` tidies every .csv file in the folder: trims spaces around cells, drops rows
  that are entirely empty.
- `--delimiter ';'` for files split by semicolons.
- samples/messy.csv is the file from the first bug report.
- TODO: maybe a --dry-run; maybe handle .tsv; Kim asked about Excel files, said no for now.
- Renamed from tidycsv to csvtidy in 0.2 because of a name clash on PyPI.
