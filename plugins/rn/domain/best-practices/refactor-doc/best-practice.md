# `refactor-doc`

## Goal tree

- Whether they read the original or a machine translation, readers understand the document as its writer meant, in one read of only the parts they need.
  - **C1** The reader finds the parts they need without reading the rest.
    - **N1** Do each heading and the first sentence under it say what the section gives the reader? (the whole)
    - **N2** Does the document hold only what its readers need? (the whole)
  - **C2** The reader understands each sentence and figure on the first read.
    - **N3** Does each sentence come after everything it depends on? (the whole)
    - **N4** Do lists, tables, and diagrams show the steps, the choices, and the relations that prose would make the reader piece together? (the whole)
    - **N5** Does each sentence make one point, with the actor as its subject and an active verb? (the whole)
    - **N6** Does the document use the words its readers already use, in their usual meaning? (the whole)
  - **C3** Every part of the document says the same thing about each fact and uses the same name for each thing.
    - **N7** Does the document state each fact in one place, with every other place linking to it? (the whole)
    - **N8** Does each thing have one name, used the same way throughout, and does each name refer to one thing? (the whole)

## Practices

### N1

Do each heading and the first sentence under it say what the section gives the reader?

Readers choose what to read by the headings and the first sentences, and skip the rest. Nielsen Norman Group found that readers scan the first words of [headings](https://www.nngroup.com/articles/headings-pickup-lines/).

1. *While deciding.* List the readers with the purposes they come with.
2. *While deciding.* Split the document so that each section serves one topic: a reader with a given purpose reads a section whole or skips it whole.
3. *While deciding.* Give each item that a reader looks for, such as a question they have, a heading of its own, so that it shows in the outline and a link can point to it.
4. *While making.* Write each heading so that its first words are the ones the reader scans for.
5. *While making.* Make the first sentence under the heading say what the section gives.
6. *While making.* Read only the headings and the first sentences for each purpose. Rewrite a heading or first sentence that would make the reader miss a section the purpose needs. Rewrite one that would make them read a section it doesn't need.

### N2

Does the document hold only what its readers need?

Every word costs the reader time, and words that carry nothing still cost it. The method is the rule to omit needless words in William Strunk and E. B. White's The Elements of Style.

1. *While making.* For each sentence, ask which reader needs it, at this point, and for what. If no reader does, cut it, or move it to a linked document where a reader does.
2. *While making.* Within a sentence, ask the same of each word.
3. *While making.* Keep the small words that show the structure of a sentence, such as articles and `that`, since without them both a reader and a machine translator parse the sentence with more effort.
4. *While making.* After cutting, read each changed section again from the top as its reader, and check that it still says everything it said before. The trace: `{deliverable}` read to its end.

### N3

Does each sentence come after everything it depends on?

A reader who has to turn back or read ahead loses the thread. The method is the given-new order of [information structure](https://en.wikipedia.org/wiki/Information_structure): what the reader already knows comes before what's new.

1. *While making.* For each sentence, ask what the reader must already know to understand it, and place it after that.
2. *While making.* If a sentence depends on something outside the document, such as an earlier discussion, state it in the sentence or link to where it's stated.
3. *While making.* Within a sentence, start with what the reader already knows and end with what's new.
4. *While making.* Put a short condition before its instruction, so that a reader it doesn't apply to can skip the instruction.
5. *While making.* Put the exceptions of a rule next to the rule.
6. *While making.* Read the document from the top, and mark each place where you had to look back or ahead. Move what the place needed to before it.

### N4

Do lists, tables, and diagrams show the steps, the choices, and the relations that prose would make the reader piece together?

A reader takes in at once a relation that a form shows, but has to assemble it from sentences. Jill Larkin and Herbert Simon, in their study of why a diagram is worth ten thousand words, found that a diagram puts by place what sentences make the reader search for.

1. *While deciding.* For each passage, ask what relation it describes, and choose the form by the answer. Steps in order take a numbered list. Items in no order take a bulleted list. Things compared on the same points take a table. Who passes what to whom takes a diagram. An argument, where one point leads to the next by because or but, stays in prose, since a list drops those links.
2. *While making.* Draw a sequence diagram as text that the page renders, such as Mermaid, because its steps run from top to bottom and leave no layout to choose.
3. *While making.* Draw a structure diagram, such as parts and what passes between them, as a file whose layout the writer sets, such as SVG, because its layout carries meaning.

### N5

Does each sentence make one point, with the actor as its subject and an active verb?

A sentence with one meaning reads the same for every reader, and for a machine translator. [Simplified Technical English](https://www.asd-ste100.org) and the [Google developer documentation style guide](https://developers.google.com/style/translation) give the rules for this, for readers who read in a second language.

1. *While making.* For each sentence, ask how many points it makes, and split it into one sentence for each.
2. *While making.* Ask who acts, make the actor the subject, and follow it with a verb that carries the action.
3. *While making.* Ask whether each pronoun could refer to two nouns, and if so, use the noun.
4. *While making.* Turn a noun made from a verb, such as `decision`, back into the verb.
5. *While making.* Keep the object close to the verb.
6. *While making.* Read each sentence as a machine translator would: word by word, with nothing from outside the sentence. If it reads two ways, or would read unnaturally in another language, rewrite it. The trace: `{deliverable}` read to its end.

### N6

Does the document use the words its readers already use, in their usual meaning?

A reader reads each word with the meaning they already know, so any other word makes them guess, such as a term the team coined. The [Federal Plain Language Guidelines](https://www.plainlanguage.gov/guidelines/) call for familiar words for the same reason.

1. *While making.* For each word, ask whether a reader in the field would use it for this thing, in this meaning. If not, use the word they would use. If no such word exists, define the term where the reader first meets it.
2. *While making.* Write out each abbreviation where the reader first meets it, as the [Google developer documentation style guide](https://developers.google.com/style/abbreviations) does.

### N7

Does the document state each fact in one place, with every other place linking to it?

Two places that state one fact drift apart, and the reader can't tell which one holds. It's the principle of a [single source of truth](https://en.wikipedia.org/wiki/Single_source_of_truth).

1. *While making.* For each fact, including one that a figure draws or the work itself shows, ask where a reader would look for it first, and state it there.
2. *While making.* If two places state a fact differently, keep both, and ask whoever owns the document which is right, since choosing one yourself would change what the document says.
3. *While making.* In every other place, link to the place that states the fact, with a few words on what the reader finds there.

### N8

Does each thing have one name, used the same way throughout, and does each name refer to one thing?

A reader who meets two names takes them for two things, and one name used for two things merges them, while one name for each thing lets the reader and a translator keep one picture of it from start to end. [Simplified Technical English](https://www.asd-ste100.org) gives each word one meaning for the same reason.

1. *While making.* List the names the document uses for things.
2. *While making.* For each thing, keep the name its readers already use, spelled the same way each time.
3. *While making.* If two names refer to one thing, keep one.
4. *While making.* If one name refers to two things, give one of them another name.
