"""csvtidy: reads a CSV file and writes it back tidied: every cell trimmed of the spaces around it,
blank rows dropped, and the header's names in lower case with spaces as underscores."""

import csv
import sys


def tidy(rows):
    rows = [[cell.strip() for cell in row] for row in rows]
    rows = [row for row in rows if any(row)]
    if rows:
        rows[0] = [name.lower().replace(" ", "_") for name in rows[0]]
    return rows


def main(argv):
    if len(argv) != 2:
        print("usage: python3 csvtidy.py <in.csv> <out.csv>", file=sys.stderr)
        return 1
    with open(argv[0], newline="", encoding="utf-8") as f:
        rows = tidy(list(csv.reader(f)))
    with open(argv[1], "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
