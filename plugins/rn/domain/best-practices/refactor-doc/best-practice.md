# `refactor-doc`

## Goal

Whether they read the original or a machine translation, readers understand the document as its writer meant, in one read of only the parts they need.

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The reader finds the parts they need without reading the rest. |
| C2 | The reader understands each sentence and figure on the first read. |
| C3 | Every part of the document says the same thing about each fact and uses the same name for each thing. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Do each heading and the first sentence under it say what the section gives the reader? | the whole |
| N2 | C1 | Does the document hold only what its readers need? | the whole |
| N3 | C2 | Does each sentence come after everything it depends on? | the whole |
| N4 | C2 | Do lists, tables, and diagrams show the steps, the choices, and the relations that prose would make the reader piece together? | the whole |
| N5 | C2 | Does each sentence make one point, with the actor as its subject and an active verb? | the whole |
| N6 | C2 | Does the document use the words its readers already use, in their usual meaning? | the whole |
| N7 | C3 | Does the document state each fact in one place, with every other place linking to it? | the whole |
| N8 | C3 | Does each thing have one name, used the same way throughout, and does each name refer to one thing? | the whole |

## Practices

### N1

Do each heading and the first sentence under it say what the section gives the reader?

**Thinking**

Each section covers one topic, and its heading and first sentence say what the reader gets from it. Readers choose sections by their headings and first sentences, and skip the rest. Readers scan the first words of [headings](https://www.nngroup.com/articles/headings-pickup-lines/), so put the most telling words first.

**Steps**

1. Name the readers and the purposes they come with. Read only the headings and the first sentences for each purpose. Rewrite a heading or first sentence that would make the reader miss a section the purpose needs. Rewrite one that would make them read a section it doesn't need.
2. Give each item that a reader looks for, such as a question they have, a heading of its own, so that it shows in the outline and a link can point to it.

### N2

Does the document hold only what its readers need?

**Thinking**

Remove each word, sentence, and section that gives the reader nothing they need. Text that carries nothing still costs the reader time, as Strunk and White's rule to omit needless words puts it. Keep the small words that show the structure of a sentence, such as articles and `that`.

**Steps**

1. After cutting, read each changed section again from the top, and check that it still says everything it said before. The trace: `{deliverable}` read to its end.

### N3

Does each sentence come after everything it depends on?

**Thinking**

Put each sentence after everything it depends on, so that the reader never has to turn back or read ahead. Start each sentence with what the reader already knows, and end it with what's new. Linguists call this the given-new order of [information structure](https://en.wikipedia.org/wiki/Information_structure).

**Steps**

1. If a sentence depends on something outside the document, such as an earlier discussion, state it in the sentence or link to where it's stated.
2. Put the conditions and exceptions of a rule next to the rule. Put a short condition before its instruction, so that a reader it doesn't apply to can skip the instruction.

### N4

Do lists, tables, and diagrams show the steps, the choices, and the relations that prose would make the reader piece together?

**Thinking**

Show steps, choices, and relations in a form whose shape shows them. A reader takes in at once what a list, a table, or a diagram shows, but has to assemble the same thing from sentences.

**Steps**

1. Choose the form by what it shows: a numbered list for steps in order, a bulleted list for items in no order, a table for things compared on the same points, and a diagram for who passes what to whom.
2. Draw a sequence diagram as text that the page renders, such as Mermaid, because its steps run from top to bottom and leave no layout to choose.
3. Draw a structure diagram, such as parts and what passes between them, as a file whose layout the writer sets, such as SVG, because its layout carries meaning.

### N5

Does each sentence make one point, with the actor as its subject and an active verb?

**Thinking**

A sentence that makes one point, names the actor as its subject, and follows it with an active verb has one meaning for both a reader and a machine translator. [Simplified Technical English](https://www.asd-ste100.org) and the [Google developer documentation style guide](https://developers.google.com/style/translation) both write this way for readers who read in a second language.

**Steps**

1. Split a sentence that makes more than one point into one sentence for each point.
2. Follow the subject with a verb that carries the action, and keep the object close to the verb. Turn a noun made from a verb, such as `decision`, back into the verb.
3. If a pronoun or `which` could refer to two nouns, replace it with the noun it means.
4. Read each sentence as a machine translator would: word by word, with nothing from outside the sentence. If it reads two ways, or would read unnaturally in another language, rewrite it. The trace: `{deliverable}` read to its end.

### N6

Does the document use the words its readers already use, in their usual meaning?

**Thinking**

Use the words that readers in the field commonly use for each thing, in their usual meaning. A reader reads each word with the meaning they already know, so any other word makes them guess, such as a term the team coined. The [Federal Plain Language Guidelines](https://www.plainlanguage.gov/guidelines/) call for familiar words for the same reason.

**Steps**

1. For each word, ask whether a reader in the field would use it for this thing, in this meaning. If not, use the word they would use, or define it where the reader first meets it.
2. Write out each abbreviation where the reader first meets it, as the [Google developer documentation style guide](https://developers.google.com/style/abbreviations) does.

### N7

Does the document state each fact in one place, with every other place linking to it?

**Thinking**

State each fact, including one that a figure draws or the work itself shows, in the one place where the reader looks for it, and link to it from every other place. A change made in that place then reaches every reader, and no two places can disagree. This is the principle of a [single source of truth](https://en.wikipedia.org/wiki/Single_source_of_truth).

**Steps**

1. If two places state a fact differently, keep both, and ask whoever owns the document which is right. Choosing one yourself would change what the document says.
2. Replace every other copy with a link to that place, with a few words on what the reader finds there.

### N8

Does each thing have one name, used the same way throughout, and does each name refer to one thing?

**Thinking**

Give each thing one name, the one its readers already use, spelled the same way each time, and use each name for one thing only. The reader, and a translator, then keep one picture of each thing from start to end.

**Steps**

1. List the names the document uses. If two names refer to one thing, keep the one readers already use. If one name refers to two things, give one of them another name.
