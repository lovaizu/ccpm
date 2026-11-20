# `light`

## Goal tree

- The people that a deliverable is made for use it toward their aim soon after the user asks for it.
  - **C1** The deliverable gives its people what its name says, and holds nothing more.
    - **N1** Does the deliverable give its people what its name says as they meet it? (the whole)
    - **N2** Does each part of the deliverable give its people something they need for what its name says? (the whole)
    - **N3** Does the deliverable say what each deliverable it rests on says, wherever it carries it? (the whole)

## Practices

### N1

Does the deliverable give its people what its name says as they meet it?

A light deliverable has no best practice behind it, so its people get what they're after only where a concrete check, written before it's made, shows it: acceptance test-driven development writes the acceptance test before the work, and Gojko Adzic's [Specification by Example](https://gojko.net/books/specification-by-example/) states it as the key examples its people would check.

1. *While deciding.* Open the decisions of your cut and each deliverable that its inputs name, and read each to its end. The trace: `{inputs}` read to its end.
2. *While deciding.* Read the check, the decision about `The check`, and name who meets the deliverable and what they do with it, such as a person who installs two plugins from one pull request.
3. *While deciding.* Name the command to run or the record to read that shows the check met, such as `claude plugin validate` on each plugin's folder. Where the check names none and its people's use gives none, end with the point, naming the one you'd take, since a check that shows nothing, such as `it works`, holds the deliverable to nothing.
4. *While making.* Make the deliverable in the format that the program or the person who reads it takes, such as the JSON that a tool loads or the Markdown that a person reads.
5. *While making.* Run the command or read the record that you named, as the deliverable's people meet it, such as in a fresh checkout, and mend the deliverable until it passes.

### N2

Does each part of the deliverable give its people something they need for what its name says?

A part that its people don't need slows the deliverable's making and their reading, and each later change must carry it.

1. *While making.* For each part of the deliverable, such as a section, a key, or a step, name the words of the check or the decision that it carries out, and remove each part that carries out none.

### N3

Does the deliverable say what each deliverable it rests on says, wherever it carries it?

A deliverable that says otherwise than what it rests on leaves its people to find which one holds.

1. *While making.* For each input whose content the deliverable carries, such as a README whose walkthrough the deliverable repeats, compare the two where they meet, and change the deliverable where they differ, since the input decides.
