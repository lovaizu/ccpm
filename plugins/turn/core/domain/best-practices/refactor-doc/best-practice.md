# refactor-doc

## Goal

The reader is a person or an AI who reads the document for a purpose, at any time after it is written. They read it in its own language or through a machine translation into theirs. The reader reads once from the top and only the parts their purpose needs, and takes in what the document says as its writer meant.

## User benefits

- **Q1** (the whole): Does the reader find each fact said in one place only, in the document or in what they read beside it, with every other place pointing there, so that two places never tell them different things?
- **Q2** (the whole): Coming to the document for a purpose, can the reader tell from each heading and the sentence under it what the section gives them, so they read the sections their purpose needs and skip the rest?
- **Q3** (the whole): Where the document tells steps in order, choices that depend on a case, or how several things relate, does the reader see it at a glance, without piecing it together from sentences?
- **Q4** (the whole): Reading from the top, can the reader understand each sentence from what they have read before it, without turning back, reading ahead, or knowing what the document neither says nor points to?
- **Q5** (the whole): When the reader reads any sentence once, as written or through a machine translation into their own language, can they say who or what does what in it?
- **Q6** (the whole): Each time the reader meets a name, can they tell rightly whether it names a thing they have already met, and which one?
- **Q7** (the whole): When the reader meets a word they have not used themselves, can they tell what it means right where they meet it?
- **Q8** (the whole): Does each word the reader reads carry part of what the document says, so that no word costs them time and gives them nothing?

## Practices

### Q1: Does the reader find each fact said in one place only, in the document or in what they read beside it, with every other place pointing there, so that two places never tell them different things?

**Thinking**: The document says each fact, including one that a figure draws or the work itself shows, in the one place where the reader looks for it. Every other place points there. A change made in that one place then reaches every reader.

**Steps**

1. Where two places say a fact in different ways, keep both, and send the difference back to be settled with what the document says. Choosing one would change what the document says.
2. Replace each other place's copy with a link to that place, saying in a few words what the reader finds there.

### Q2: Coming to the document for a purpose, can the reader tell from each heading and the sentence under it what the section gives them, so they read the sections their purpose needs and skip the rest?

**Thinking**: The reader picks sections by their headings and first sentences. So each section holds one thing and says at its start what it gives.

**Steps**

1. Start each heading with the words that tell the most.
2. Name the reader and the purposes they come with. For each purpose, read only the headings and first sentences. Where the reader would miss a section that the purpose needs, or read one that it does not need, rewrite that heading or first sentence.

### Q3: Where the document tells steps in order, choices that depend on a case, or how several things relate, does the reader see it at a glance, without piecing it together from sentences?

**Thinking**: The reader sees at once an order or a relation that the form of a list, a table or a diagram shows. When sentences tell the same, the reader must piece it together.

**Steps**

1. Choose a form whose shape shows that order or relation, such as a numbered list for steps in order, a bulleted list for items whose order does not matter, a table for things compared on the same points, or a diagram for who passes what to whom.
2. Draw a sequence diagram in Mermaid inside the document: its steps go from top to bottom, so it has no layout to choose, and the page draws it. Draw a diagram of structure, such as parts and what passes between them, as an SVG file beside the document, and show it as an image: its layout carries its meaning. Draw a table the reader takes in whole at a glance, such as which tests cover which part, as an SVG in the same way, so its marks and groups line up. Keep a table the reader looks a row up in as Markdown, so they can search and copy it. Set the SVG's colours under prefers-color-scheme, so that it follows the page's light or dark scheme.
3. Show the form alone to a reader who has not read the text, and have them say back what it tells. Where they say it otherwise, mend the form.

### Q4: Reading from the top, can the reader understand each sentence from what they have read before it, without turning back, reading ahead, or knowing what the document neither says nor points to?

**Thinking**: Each sentence comes after everything it rests on, so the reader never holds a sentence open while they look for what it needs.

**Steps**

1. Where a sentence rests on something outside the document, such as an earlier talk, say it in the sentence or link to where it is written.
2. Start each sentence with what the reader already has, and end it with what is new.
3. Put a rule's conditions and exceptions beside the rule, where the reader takes them in most easily. Put a short condition before its instruction, so that a reader whose case it is not can skip the instruction.

### Q5: When the reader reads any sentence once, as written or through a machine translation into their own language, can they say who or what does what in it?

**Thinking**: A sentence that makes one point, names who acts and keeps plain order has one reading, for the reader and for a machine translator alike.

**Steps**

1. Split a sentence that makes more than one point, or that links more than two clauses with "and", "or" or "but", into one sentence for each point.
2. Follow the subject at once with an active verb that carries the action. Keep the object close after the verb. Turn a noun made from a verb back into the verb.
3. Keep the small words that show how a sentence is built, such as articles, "that", "who", "then" and "of".
4. Where a pronoun, or a "which", could point to two nouns, replace it with the noun it means. Break a string of nouns apart with prepositions.
5. Read each sentence once as a machine translator would, word by word in its order and with nothing from outside it, and say who does what. Where the sentence reads two ways, reword it.
6. Have a reader who did not write the document say a section back in their own words. Where they say it otherwise, reword the sentence, and do not correct the reader.

### Q6: Each time the reader meets a name, can they tell rightly whether it names a thing they have already met, and which one?

**Thinking**: Each thing has one name, the one its reader already uses, written the same way each time. Each name names one thing. The reader, and a translator, then keep one picture of each thing from start to end.

### Q7: When the reader meets a word they have not used themselves, can they tell what it means right where they meet it?

**Thinking**: The reader takes each word with the meaning they already give it. So the writer replaces a word new to the reader with everyday words, even a word the writer's team uses every day, or gives its meaning where the reader first meets it.

**Steps**

1. Write each abbreviation out in full where the reader first meets it.
2. Where the document gives a common word a meaning of its own, replace it with a word the reader does not already read another way.

### Q8: Does each word the reader reads carry part of what the document says, so that no word costs them time and gives them nothing?

**Thinking**: A word or a sentence that carries nothing of what the document says still costs the reader time, so it goes. A word that shows how a sentence is built stays.

**Steps**

1. Read each changed section again from the top, and check that it still says all it said before.
