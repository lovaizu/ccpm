# `light`

## Goal tree

- The people that a deliverable is made for get it soon, doing what a concrete check says, where a best practice of its own would cost more than it gives them, or the user wants it at once.
  - **C1** The deliverable does for its people what a concrete check says, and holds nothing more.
    - **N1** Does the check name a command to run or a record to read that shows the deliverable done? (the whole)
    - **N2** Does the deliverable pass its check, run or read as its people meet it? (the whole)
    - **N3** Does each part of the deliverable carry out its check or a decision of the deliverable or of an input? (the whole)
    - **N4** Does the deliverable say what each deliverable it rests on says, wherever it carries it? (the whole)

## Practices

### N1

Does the check name a command to run or a record to read that shows the deliverable done?

A light deliverable is as good as its check alone, as no best practice holds it, so a check that names no way to show it done, such as `it works`, holds it to nothing. Acceptance test-driven development writes the acceptance test before the work, and Gojko Adzic's [Specification by Example](https://gojko.net/books/specification-by-example/) states it as the key examples its people would check.

1. *While deciding.* Open the decisions of your cut and each deliverable that its inputs name, and read each to its end. The trace: `{inputs}` read to its end.
2. *While deciding.* Read the check, the decision about `The check`, and name who meets the deliverable and what they do with it, such as a person who installs two plugins from one pull request.
3. *While deciding.* Name the command to run or the record to read that shows the check met, such as `claude plugin validate` on each plugin's folder. Where the check names none and its people's use gives none, end with the point, naming the one you'd take, since only the user says what shows it done.

### N2

Does the deliverable pass its check, run or read as its people meet it?

The people get what they're after only where the deliverable passes the check as they'd meet it, not as its maker sees it.

1. *While making.* Make the deliverable in the format that the program or the person who reads it takes, such as the JSON that a tool loads or the Markdown that a person reads.
2. *While making.* Run the command or read the record that N1 names, as its people meet the deliverable, such as in a fresh checkout, and mend the deliverable until it passes.

### N3

Does each part of the deliverable carry out its check or a decision of the deliverable or of an input?

A part that carries out neither is one that the people reach their aim without, and that each later change must carry.

1. *While making.* For each part of the deliverable, such as a section, a key, or a step, name the words of the check or the decision that it carries out, and remove each part that carries out none.

### N4

Does the deliverable say what each deliverable it rests on says, wherever it carries it?

A deliverable that says otherwise than what it rests on leaves its people to find which one holds.

1. *While making.* For each input whose content the deliverable carries, such as a README whose walkthrough the deliverable repeats, compare the two where they meet, and change the deliverable where they differ, since the input decides.
