"""notes: `python3 notes.py list` prints each note as its id, title, tags and updated,
tab-separated, tags joined by commas; updated is the time in UTC."""

import sys

NOTES = [
    ("1", "Groceries", ["home"], "2026-11-01T09:30:00+00:00", "notes/groceries.md"),
    ("2", "Trip plan", ["travel", "family"], "2026-11-02T18:05:00+00:00", "notes/trip-plan.md"),
    ("3", "Dentist", ["health"], "2026-11-03T08:15:00+09:00", "notes/dentist.md"),
]


def main(argv: list[str]) -> int:
    if argv[:1] != ["list"]:
        print("usage: notes.py list")
        return 2
    for number, title, tags, updated, _ in NOTES:
        print("\t".join([number, title, ",".join(tags), updated]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
