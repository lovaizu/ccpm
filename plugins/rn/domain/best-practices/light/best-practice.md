# `specific`

## Goal tree

- The people that a deliverable is made for, where no field's established kind fits it, do with it what they're after, as its check says.
  - **C1** The deliverable does for its people what its check says.
    - **N1** Does the deliverable pass its check, run or read as its people meet it? (the whole)
  - **C2** The deliverable holds only what its check and its decisions call for, and agrees with what it rests on.
    - **N2** Does each part of the deliverable carry out its check or a decision of the deliverable or of an input? (the whole)
    - **N3** Does the deliverable say what each deliverable it rests on says, wherever it carries it? (the whole)

## Practices

### N1

Does the deliverable pass its check, run or read as its people meet it?

The check is the one statement of what the people get from a deliverable that no established kind describes, written before the deliverable is made, as acceptance test-driven development writes the acceptance test first and Gojko Adzic's [Specification by Example](https://gojko.net/books/specification-by-example/) states it as the key examples its people would check.

1. *While deciding.* Open the decisions of your cut and each deliverable that its inputs name, and read each to its end. The trace: `{inputs}` read to its end.
2. *While deciding.* Read the check, the decision about `The check`, and name who meets the deliverable and what they do with it, such as a person who installs two plugins from one pull request.
3. *While deciding.* Where the check names no way to show that it passes, such as a command to run or a record to read, end with the point, naming the way you'd take, since only the user says what passes.
4. *While making.* Make the deliverable in the format that the program or the person who reads it takes, such as the JSON that a tool loads or the Markdown that a person reads.
5. *While making.* Run or read the check as its people meet the deliverable, such as by running the command that it names in a fresh checkout, and mend the deliverable until it passes.

### N2

Does each part of the deliverable carry out its check or a decision of the deliverable or of an input?

A part that carries out neither is one that the people reach their aim without, and that each later change must carry.

1. *While making.* For each part of the deliverable, such as a section, a key, or a step, name the words of the check or the decision that it carries out, and remove each part that carries out none.

### N3

Does the deliverable say what each deliverable it rests on says, wherever it carries it?

A deliverable that says otherwise than what it rests on leaves its people to find which one holds.

1. *While making.* For each input whose content the deliverable carries, such as a README whose walkthrough the deliverable repeats, compare the two where they meet, and change the deliverable where they differ, since the input decides.
