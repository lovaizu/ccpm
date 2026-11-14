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

Readers choose what to read by the headings and the first sentence under each, and skip the rest, so a heading and a first sentence that say what the section gives take each reader straight to the parts they need.

1. *While deciding.* Open `{deliverable}`, the file or folder you write in, and read each document in it to its end before you change anything, such as each Markdown file of a folder, noting in a line what each section is for. Where it holds more than one document, take each item of this best practice for each of them. The trace: `{deliverable}` read to its end.
2. *While deciding.* Find the readers: open your cut, and read its goal and each input it names, such as a product vision and the users it names, and read the document's opening where it names its audience. List each kind of reader named there with the purpose they come with, such as `a developer who installs the plugin and wants its first command to run`. Where your cut names no input, take the readers from its goal and the document's opening alone. Where none of these names the readers, or two name different ones, ask the person who owns the document, since a document written for a guessed reader serves someone it wasn't meant for. The trace: `{inputs}` read to its end.
3. *While deciding.* For each reader on the list, write what they already know and what they come to learn, from their role and how close their work is to the subject, such as `knows Claude Code's slash commands, and doesn't know where the plugin keeps its state`.
4. *While deciding.* Split the document into sections of one topic each: for each section, ask whether a reader with one purpose would read part of it and skip the rest, and if so, split it there. For example, split `Setup` into `Install the plugin` and `Configure the proxy` where only readers behind a proxy configure one.
5. *While deciding.* Give each item that a reader looks for, such as a question they have or a command they run, a heading of its own, so that it shows in the outline and a link can point to it.
6. *While making.* Write each heading so that its first words are the words of the reader's purpose: start a task's heading with its verb, such as `Install the plugin` in place of `Plugin installation`, and a reference's heading with the thing's name, such as `Hook timeouts`.
7. *While making.* Write the first sentence under each heading so that it says what the section gives the reader, such as `Run /plugin update to take the newest version, and your settings stay as they are.` under `Update the plugin`, in place of `This section is about updates.`
8. *While making.* Read only the headings and the first sentences for each purpose. Rewrite a heading or first sentence that would make the reader miss a section the purpose needs. Rewrite one that would make them read a section it doesn't need.

### N2

Does the document hold only what its readers need?

Every sentence costs the reader time, and one that carries nothing they need still costs it and hides the sentences that do.

1. *While deciding.* For each sentence, ask which reader on your list needs it, and for what, and mark each sentence that no reader on your list needs.
2. *While deciding.* For each sentence you marked, look for a document whose readers need it: open each document that the document links, and each other document in `{deliverable}`, and take the one whose opening or headings name readers who come for what the sentence tells, such as a changelog for the story of why a tool was rewritten.
3. *While deciding.* Where the document you took lies outside `{deliverable}`, or you took none and the sentence states a fact that a search of the repository finds in no other place, such as the reason for a choice, ask the person who owns the document where the sentence goes, with the place you'd put it, since cutting it loses the fact and writing outside `{deliverable}` changes another document.
4. *While making.* Where the document you took lies in `{deliverable}`, move the sentence into it, under the heading whose topic the sentence is.
5. *While making.* Move each sentence you asked about to the place that the person's answer names in `{deliverable}`, and cut it where the answer puts it outside.
6. *While making.* Cut each other sentence you marked, since another place states its fact, or it states none, such as `As noted above, this matters.`
7. *While making.* Within each sentence you keep, ask the same of each word, and cut each word that no reader needs, such as `in order to` for `to`, or `basically`.
8. *While making.* Keep the small words that show how a sentence is built, such as articles, `that`, and `then`, as the [Google developer documentation style guide](https://developers.google.com/style/translation) lists them, since without them both a reader and a machine translator parse the sentence with more effort.
9. *While making.* After cutting, read the document again from the top as each reader on your list, for their purpose, since a cut in one section can take what a sentence in another needs. Where a reader no longer finds a step, a value, or a condition that their purpose needs, put back the words that told it. The trace: `{deliverable}` read to its end.

### N3

Does each sentence come after everything it depends on?

A reader who has to turn back or read ahead to understand a sentence loses the thread, and a reader in a second language, or of a machine translation, loses it sooner.

1. *While making.* For each sentence, ask what the reader must already know to understand it, beyond what you wrote that each reader knows, and place the sentence after the one that tells them.
2. *While making.* Where a sentence depends on something outside the document, such as an earlier discussion or another page, state it in the sentence, or link to where it's stated.
3. *While making.* Within a sentence, start with what the reader already knows and end with what's new. For example, after `The plugin keeps its state in .rn/.`, write `.rn/ holds one folder for each run.` in place of `One folder for each run lies in .rn/.`
4. *While making.* Put a short condition before its instruction, such as `If you use a proxy, set HTTPS_PROXY.`, so that a reader it doesn't apply to can skip the instruction.
5. *While making.* Put each exception to a rule in the sentence right after the rule, such as `Write each name in lowercase. Write the plugin's own name as its manifest does.`
6. *While making.* Read the document from the top, and mark each place where you had to look back or ahead. Move what the place needed to before it. The trace: `{deliverable}` read to its end.

### N4

Do lists, tables, and diagrams show the steps, the choices, and the relations that prose would make the reader piece together?

A reader takes in at once the steps, the choices, or the relations that a list, a table, or a diagram shows, but has to piece them together from prose.

1. *While deciding.* For each passage, ask what relation it describes, and choose the form by the answer, as the [Google developer documentation style guide](https://developers.google.com/style/lists) chooses a list. Steps in order take a numbered list. Items in no order take a bulleted list. Things compared on the same points take a table. Messages that parts pass one after another, where their order is what the reader needs, take a sequence diagram. Parts and what connects them, where which part connects to which matters and their order doesn't, take a structure diagram. An argument, where one point leads to the next by because or but, stays in prose, since a list drops those links.
2. *While deciding.* Where you chose a sequence diagram, find the place where readers read the document: the site that a site generator builds from the document's folder, where a config in the repository names that folder, such as `docs_dir` in `mkdocs.yml`, and else the host that `git remote -v` names, such as GitHub for a remote on github.com, whose pages show the repository's files. Where neither names a place, ask the person who owns the document where its readers read it, with the place you'd take, since a diagram in a text format that the place doesn't render shows its readers code.
3. *While deciding.* For each sequence diagram you chose, find whether the place that N4.2 found renders a diagram written as text: open that place's documentation on the document's format, such as GitHub's page on creating diagrams for a Markdown file read on GitHub, and note the text format it renders, such as Mermaid in a `mermaid` code block, or that it renders none.
4. *While deciding.* For each diagram that you'll draw as a file, each structure diagram and each sequence diagram whose place renders no text format, choose its path. Where `{deliverable}` is a folder, take a path in it beside the document, named for what the diagram shows, such as `plugin-parts.svg`. Where `{deliverable}` is one file, ask the person who owns the document where the diagram goes, with the path beside the document that you'd give it, since a file outside `{deliverable}` changes what you weren't given.
5. *While making.* Rewrite each passage in the form you chose for it, with one list item, table row, or element of the diagram for each step, choice, or thing that the passage names.
6. *While making.* Write each sequence diagram whose place renders a text format in that format, because its steps run from top to bottom and leave no layout to choose.
7. *While making.* Draw each structure diagram, and each sequence diagram whose place renders no text format, as a file whose layout the writer sets, such as SVG, at the path that N4.4 chose or that the person's answer names, and link it from the document where its passage stood, because the layout of a structure diagram carries meaning, and a page that renders no diagram text still shows an image.

### N5

Does each sentence make one point, with the actor as its subject and an active verb?

A sentence that makes one point, with the actor as its subject, reads one way for every reader and for a machine translator, as the [Google developer documentation style guide](https://developers.google.com/style/translation) asks for readers who read in a second language.

1. *While making.* For each sentence, count the points it makes, and split it into one sentence for each, such as `The script reads the record and, if it's complete, ends the run.` into `The script reads the record. If the record is complete, the script ends the run.`
2. *While making.* Ask who acts, make the actor the subject, and follow it with a verb that carries the action, such as `The guard checks the record.` in place of `The record is checked.`
3. *While making.* For each pronoun, such as `it`, `they`, or `this`, ask whether it could refer to two nouns, or stands more than five words after its noun, and if so, write the noun.
4. *While making.* Turn a noun made from a verb back into the verb, such as `make a decision` into `decide`.
5. *While making.* Keep the object next to its verb, such as `Set the timeout before the first run.` in place of `Set, before the first run, the timeout.`
6. *While making.* Read each sentence as a machine translator would: word by word, with nothing from outside the sentence. If it reads two ways, or would read unnaturally in another language, rewrite it. The trace: `{deliverable}` read to its end.

### N6

Does the document use the words its readers already use, in their usual meaning?

A reader reads each word with the meaning they already know, so a word they don't use, such as a term the team coined, makes them guess what it means.

1. *While deciding.* Find the words the readers use: open the documentation of the product the readers work in, such as Claude Code's documentation for the readers of a Claude Code plugin, and what the readers wrote for the work themselves: each decision of your cut that the user settled, with its words, and each input your cut names that they wrote, such as an issue they opened. Where your cut holds none of their words, take the product's documentation alone.
2. *While deciding.* For each thing the document names, choose its word: take the word the product's documentation uses, since the readers learned it there, such as `subagent` in place of `child agent`. Where that documentation names no such thing, take the word the readers' own writing uses. Where neither has one, keep the document's term, and mark it to define.
3. *While making.* Replace each word that differs from the one you chose with that word, in its usual meaning.
4. *While making.* Define each term you marked where the reader first meets it, or link to a page that defines it, such as `A hook, a command that Claude Code runs at a set point of a session, ...`.
5. *While making.* Write out each abbreviation where the reader first meets it, as the [Google developer documentation style guide](https://developers.google.com/style/abbreviations) does.

### N7

Does the document state each fact in one place, with every other place linking to it?

Two places that state one fact drift apart, and a reader who finds both can't tell which one holds.

1. *While deciding.* List each fact that the document states in more than one place, including one that a figure draws or the work itself shows, such as a command's options, which its `--help` shows.
2. *While deciding.* For each fact on the list, choose the one place that states it: the work itself where it shows the fact, such as a script's `--help` for its options, and else the section whose topic the fact is, where a reader looks for it first.
3. *While deciding.* Where two places state a fact differently, keep both, and ask the person who owns the document which one is right, since choosing one yourself would change what the document says.
4. *While making.* Where the place you chose is a section of the document, state the fact there in full.
5. *While making.* Where the place you chose is a section of the document, replace the fact in every other place with a link to that section and a few words on what the reader finds there, such as `For what each option does, see [Options](#options).`
6. *While making.* Where the place you chose is the work itself, replace the fact in every place with how to see it there, linked to the file that shows it, such as `For what each option does, run check.sh --help.` with `check.sh` linked to the script.

### N8

Does each thing have one name, used the same way throughout, and does each name refer to one thing?

A reader who meets two names takes them for two things, and one name for two things merges them, while one name for each thing lets the reader and a translator keep one picture of it from start to end.

1. *While deciding.* List the names the document uses for things, and group the names that refer to one thing, such as `role`, `agent`, and `subagent` for the same worker, and the things that share one name.
2. *While deciding.* For each thing with more than one name, keep the word you chose for it from the readers' words, and else the name the document uses most, and drop the others.
3. *While deciding.* For each name that refers to two things, keep it for the thing the readers' words use it for, and give the other thing the word its readers use for it, or a term to define where the reader first meets it, such as `run` for one start of the workflow and `try` for one run of a command of the deliverable.
4. *While making.* Replace each dropped name with the kept one, and write each kept name the same way each time, in its spelling, its capitals, and its code format.
