# csvtidy

csvtidy started as a sed one-liner after a monthly export broke the billing import, became a pandas
script, and is now plain Python with the csv module.

Run `csvtidy <folder>`. It uses the csv module to read each file and writes it back.

TODO: --dry-run, .tsv support.
