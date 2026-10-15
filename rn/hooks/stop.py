"""At each end of the conductor's turn: the record of each open session keeps its form."""

import sys

import record

data = record.event(sys.stdin.read())
record.report([sentence for rec in record.records(data) for sentence in record.form(rec)])
