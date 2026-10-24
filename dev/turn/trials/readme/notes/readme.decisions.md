# What the README says

- csvtidy is for someone who exports CSV files from spreadsheets or services and feeds them to
  their own scripts, and is tired of cleaning stray spaces, blank rows and header names by hand.
- The example: a file `contacts.csv` exported with ` Full Name , Email ` as its header, spaces
  around cells and blank rows, tidied with `python3 csvtidy.py contacts.csv clean.csv`, giving
  `full_name,email` and trimmed rows.
- Why csvtidy: one command, no library to install, and it changes nothing but spaces, blank rows
  and the header's names, so the data stays as it was.
- Needs Python 3.9 or later; nothing else. Installing is copying `csvtidy.py`.
- There are no other documents yet.
