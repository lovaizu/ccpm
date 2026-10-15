"""After a write: when it wrote the record of an open session, the record keeps its form."""

import sys

import record

data = record.event(sys.stdin.read())
record.report(
    [
        sentence
        for rec in record.records(data)
        if record.written(data, rec)
        for sentence in record.form(rec)
    ]
)
