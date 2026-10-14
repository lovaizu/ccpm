"""Tidies every CSV file in a folder: trims the spaces around each cell and drops empty rows.
Each original is kept beside its tidied file as <name>.orig.csv."""

import argparse
import csv
import os
import shutil


def tidy(path, delimiter):
    with open(path, newline="") as f:
        rows = [[c.strip() for c in row] for row in csv.reader(f, delimiter=delimiter)]
    shutil.copyfile(path, path[: -len(".csv")] + ".orig.csv")
    with open(path, "w", newline="") as f:
        csv.writer(f, delimiter=delimiter).writerows(r for r in rows if any(r))


def main():
    parser = argparse.ArgumentParser(prog="csvtidy")
    parser.add_argument("folder")
    parser.add_argument("--delimiter", default=",")
    args = parser.parse_args()
    for name in sorted(os.listdir(args.folder)):
        if name.endswith(".csv") and not name.endswith(".orig.csv"):
            tidy(os.path.join(args.folder, name), args.delimiter)
            print(f"tidied {name}")
