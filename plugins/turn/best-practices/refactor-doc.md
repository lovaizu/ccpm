# refactor-doc

## Goal

Whoever reads the document for a purpose, a person or an AI, at any time after it is written and in its own language or through a machine translation into theirs, takes in what it says as its writer meant, reading once from the top, and only the parts that purpose needs.

## Benefits

- **Q1** (the whole): Does the reader find each fact said in one place only, in the document or in what they read beside it, with every other place pointing there, so that two places never tell them different things?
- **Q2** (the whole): Coming to the document for a purpose, can the reader tell from each heading and the sentence under it what the section gives them, so they read the sections their purpose needs and skip the rest?
- **Q3** (the whole): Where the document tells steps in order, choices that depend on a case, or how several things relate, does the reader see it at a glance, without piecing it together from sentences?
- **Q4** (the whole): Reading from the top, can the reader understand each sentence from what they have read before it, without turning back, reading ahead, or knowing what the document neither says nor points to?
- **Q5** (the whole): Reading any sentence once, as written or through a machine translation into their own language, can the reader say who or what does what in it?
- **Q6** (the whole): Each time the reader meets a name, can they tell rightly whether it names a thing they have already met, and which one?
- **Q7** (the whole): When the reader meets a word they have not used themselves, can they tell what it means right where they meet it?
- **Q8** (the whole): Does each word the reader reads carry part of what the document says, so that no word costs them time and gives them nothing?

## Practices

### Q1: Does the reader find each fact said in one place only, in the document or in what they read beside it, with every other place pointing there, so that two places never tell them different things?

**Thinking**: Each fact, including one a figure draws or the work itself shows, is said in the one place where the reader looks for it, and every other place points there, so a change made once reaches every reader.

**Steps**

1. Where two places say a fact in different ways, keep both and send it back to be settled with what the document says, for choosing one would change what it says.
2. Replace each other place's copy with a link to that place, saying in a few words what the reader finds there.

**Grounds**

- [Orthogonality and the DRY Principle](https://www.artima.com/articles/orthogonality-and-the-dry-principle), Venners with Hunt and Thomas, artima.com, 2003: "DRY says that every piece of system knowledge should have one authoritative, unambiguous representation."
- [Orthogonality and the DRY Principle](https://www.artima.com/articles/orthogonality-and-the-dry-principle), Venners with Hunt and Thomas, artima.com, 2003: "The obvious answer is, if you have more than one way to express the same thing, at some point the two or three different representations will most likely fall out of step with each other."
- [Minimize cross-references](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/design/minimize-cross-references.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Be sure that the reference you insert clearly describes the referenced material."

### Q2: Coming to the document for a purpose, can the reader tell from each heading and the sentence under it what the section gives them, so they read the sections their purpose needs and skip the rest?

**Thinking**: The reader picks sections by their headings and first sentences, so each section holds one thing and says at its start what it gives.

**Steps**

1. Start each heading with the words that tell the most.
2. Name the reader and the purposes they come with; for each purpose, read only the headings and first sentences, and where the reader would miss a section the purpose needs, or read one it does not, rewrite that heading or first sentence.

**Grounds**

- [Do your research](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/audience/do-your-research.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Understanding what users are trying to do when visiting your website or reading your communications will help you write clearly and focus on their needs."
- [How Users Read on the Web](https://www.nngroup.com/articles/how-users-read-on-the-web/), Nielsen, Nielsen Norman Group, 1997: "In research on how people read websites we found that 79 percent of our test users always scanned any new page they came across; only 16 percent read word-by-word."
- [Add useful headings](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/organize/add-useful-headings.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Well organized writing will still be difficult for users to follow if they can't see how it's organized. An effective way to reveal your document's organization is to use lots of useful headings."
- [Write short sections](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/concise/write-short-sections.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Long sections are impossible to summarize meaningfully in a heading. When you break up different concepts into short sections, each heading can give the reader a clear picture of what's in that section."
- [F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant (Even on Mobile)](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/), Pernice, Nielsen Norman Group, 2017: "Start headings and subheadings with the words carrying most information: if users see only the first 2 words, they should still get the gist of the following section."
- [Scannable content](https://learn.microsoft.com/en-us/style-guide/scannable-content/), Microsoft, Microsoft Writing Style Guide, 2023: "Lead with what's most important. Place important keywords near the beginning of headings, table entries, and paragraphs so they're easy to spot."
- [Have a topic sentence](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/organize/have-a-topic-sentence.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Readers should be able to get good general understanding of your document by skimming your topic sentences."

### Q3: Where the document tells steps in order, choices that depend on a case, or how several things relate, does the reader see it at a glance, without piecing it together from sentences?

**Thinking**: Order and relations shown by the form of a list, a table or a diagram are seen at once, while the same told in sentences must be pieced together.

**Steps**

1. Choose a form whose shape shows that order or relation, such as a numbered list for steps in order, a bulleted list for items whose order does not matter, a table for things compared on the same points, or a diagram for who passes what to whom.
2. Show the form alone to a reader who has not read the text, and have them say back what it tells; where they say it otherwise, mend the form.

**Grounds**

- [The Science of Scientific Writing](https://human.libretexts.org/Bookshelves/Composition/Technical_Composition/Effective_Technical_Writing_in_the_Information_Age_(Schall)/10%3A_Journal_Articles_about_Writing/10.06%3A_The_Science_of_Scientific_Writing), Gopen and Swan, American Scientist, 1990: "readers make many of their most important interpretive decisions about the substance of prose based on clues they receive from its structure."
- [Global communications: Writing tips](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips), Microsoft, Microsoft Writing Style Guide, 2023: "Replace complex sentences and paragraphs with lists and tables."
- [Highlights](https://developers.google.com/style/highlights), Google, Google developer documentation style guide, 2026: "Use numbered lists for sequences."
- [Highlights](https://developers.google.com/style/highlights), Google, Google developer documentation style guide, 2026: "Use bulleted lists for most other lists."
- [Use lists](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/organize/use-lists.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Help the reader understand the order in which things happen"
- [Use tables to make complex material easier to understand](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/design/use-tables-to-make-complex-material-easier-to-understand.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Tables help your audience see relationships that are often times hidden in dense text."
- [Paraphrase testing](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/test/paraphrase-testing.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Paraphrase testing will tell you what a reader thinks a piece of writing means and will help you know if they're interpreting the message as you intended."

### Q4: Reading from the top, can the reader understand each sentence from what they have read before it, without turning back, reading ahead, or knowing what the document neither says nor points to?

**Thinking**: Each sentence comes after everything it rests on, so the reader never holds a sentence open while they look for what it needs.

**Steps**

1. Where a sentence rests on something outside the document, such as an earlier talk, say it in the sentence or link to where it is written.
2. Start each sentence with what the reader already has, and end it with what is new.
3. Put a rule's conditions and exceptions where the reader takes them in most easily, beside the rule; put a short condition before its instruction, so a reader whose case it is not can skip the instruction.

**Grounds**

- [The Science of Scientific Writing](https://human.libretexts.org/Bookshelves/Composition/Technical_Composition/Effective_Technical_Writing_in_the_Information_Age_(Schall)/10%3A_Journal_Articles_about_Writing/10.06%3A_The_Science_of_Scientific_Writing), Gopen and Swan, American Scientist, 1990: "In general, provide context for your reader before asking that reader to consider anything new."
- [Minimize cross-references](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/design/minimize-cross-references.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "They may also overtax your users' short-term memory."
- [Have a topic sentence](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/organize/have-a-topic-sentence.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Don't make readers hold a lot of information in their heads before getting to the point."
- [Write for a global audience](https://developers.google.com/style/translation), Google, Google developer documentation style guide, 2026: "Provide context. Don't assume that the reader already knows what you're talking about."
- [The Science of Scientific Writing](https://human.libretexts.org/Bookshelves/Composition/Technical_Composition/Effective_Technical_Writing_in_the_Information_Age_(Schall)/10%3A_Journal_Articles_about_Writing/10.06%3A_The_Science_of_Scientific_Writing), Gopen and Swan, American Scientist, 1990: "Put in the topic position the old information that links backward; put in the stress position the new information you want the reader to emphasize."
- [Make it easy to follow](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/organize/make-it-easy-to-follow.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Present the steps chronologically, in the order your user and your agency will follow them."
- [Place the main idea before exceptions and conditions](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/organize/place-the-main-idea-before-exceptions-and-conditions.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "There is no absolute rule about where to put exceptions and conditions. Put them where they can be absorbed most easily."
- [Place the main idea before exceptions and conditions](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/organize/place-the-main-idea-before-exceptions-and-conditions.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "The audience must absorb the exception, then the rule, and then usually has to go back to grasp the relationship between the two."
- [Sentence structure](https://developers.google.com/style/sentence-structure), Google, Google developer documentation style guide, 2024: "If you want to tell the reader to do something, try to mention the circumstance, conditions, or goal before you provide the instruction. Mentioning the circumstance first lets the reader skip the instruction if it doesn't apply."

### Q5: Reading any sentence once, as written or through a machine translation into their own language, can the reader say who or what does what in it?

**Thinking**: A sentence that makes one point, names who acts and keeps plain order is read one way, by the reader and by a machine translator alike.

**Steps**

1. Split a sentence that makes more than one point, or that links more than two clauses with "and", "or" or "but", into one sentence for each point.
2. Follow the subject at once with an active verb that carries the action, keep the object close after it, and turn a noun made from a verb back into the verb.
3. Keep the small words that show how a sentence is built, such as articles, "that", "who", "then" and "of".
4. Replace a pronoun, or a "which", that could point to two nouns with the noun it means, and break a string of nouns apart with prepositions.
5. Read each sentence once as a machine translator would, word by word in its order and with nothing from outside it, and say who does what; where it reads two ways, reword it.
6. Have a reader who did not write the document say a section back in their own words; where they say it otherwise, reword the sentence, and do not correct the reader.

**Grounds**

- [Write short sentences](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/concise/write-short-sentences.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Express only one idea in each sentence."
- [Write short sentences](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/concise/write-short-sentences.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Resist the temptation to put everything in one sentence; break up your idea into its parts and make each one the subject of its own sentence."
- [Global communications: Writing tips](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips), Microsoft, Microsoft Writing Style Guide, 2023: "Avoid linking more than three phrases or clauses by using coordinate conjunctions such as and, or, or but. Better yet, avoid linking more than two."
- [Active voice](https://developers.google.com/style/voice), Google, Google developer documentation style guide, 2024: "In passive voice, it's easy to neglect to indicate who or what is performing a particular action."
- [The Science of Scientific Writing](https://human.libretexts.org/Bookshelves/Composition/Technical_Composition/Effective_Technical_Writing_in_the_Information_Age_(Schall)/10%3A_Journal_Articles_about_Writing/10.06%3A_The_Science_of_Scientific_Writing), Gopen and Swan, American Scientist, 1990: "Follow a grammatical subject as soon as possible with its verb."
- [The Science of Scientific Writing](https://human.libretexts.org/Bookshelves/Composition/Technical_Composition/Effective_Technical_Writing_in_the_Information_Age_(Schall)/10%3A_Journal_Articles_about_Writing/10.06%3A_The_Science_of_Scientific_Writing), Gopen and Swan, American Scientist, 1990: "Articulate the action of every clause or sentence in its verb."
- [Avoid hidden verbs](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/words/avoid-hidden-verbs.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "A hidden verb (or nominalization) is a verb converted into a noun. It often needs an extra verb to make sense."
- [Keep the subject, verb, and object close together](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/concise/keep-the-subject-verb-and-object-close-together.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "When you put modifiers, phrases, or clauses between two or all three of these essential parts, you make it harder for the user to understand you."
- [Global communications: Writing tips](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips), Microsoft, Microsoft Writing Style Guide, 2023: "Writing style affects the quality of machine translation."
- [Global communications: Writing tips](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips), Microsoft, Microsoft Writing Style Guide, 2023: "Write sentences that use standard word order (that is, subject + verb + object) whenever possible."
- [Global communications: Writing tips](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips), Microsoft, Microsoft Writing Style Guide, 2023: "Articles help readers and translation software identify the nouns and modifiers in a sentence."
- [Global communications: Writing tips](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips), Microsoft, Microsoft Writing Style Guide, 2023: "Include that and who. They help to clarify the sentence structure."
- [Write for a global audience](https://developers.google.com/style/translation), Google, Google developer documentation style guide, 2026: "Use helper words. Helper words such as then, that, and of are frequently left out of conversational English. Use these words to avoid ambiguity."
- [Write for a global audience](https://developers.google.com/style/translation), Google, Google developer documentation style guide, 2026: "if a pronoun is ambiguous, then replace it with the appropriate noun."
- [Avoid noun strings](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/words/avoid-noun-strings.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "However, many users will think they've found the noun when they're still reading adjectives, and will become confused."
- [The Science of Scientific Writing](https://human.libretexts.org/Bookshelves/Composition/Technical_Composition/Effective_Technical_Writing_in_the_Information_Age_(Schall)/10%3A_Journal_Articles_about_Writing/10.06%3A_The_Science_of_Scientific_Writing), Gopen and Swan, American Scientist, 1990: "We cannot succeed in making even a single sentence mean one and only one thing; we can only increase the odds that a large majority of readers will tend to interpret our discourse according to our intentions."
- [Paraphrase testing](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/test/paraphrase-testing.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Do not correct the participant. When you review your notes later, wherever participants misunderstood the message, the document has a problem that you should fix."

### Q6: Each time the reader meets a name, can they tell rightly whether it names a thing they have already met, and which one?

**Thinking**: Each thing has one name, the one its reader already uses, written the same way each time, and each name one thing, so the reader, and a translator, keep one picture of each thing from start to end.

**Grounds**

- [Write for a global audience](https://developers.google.com/style/translation), Google, Google developer documentation style guide, 2026: "If you use a particular term for a concept in one place, then use that exact same term elsewhere, including the same capitalization. If you use different names for the same thing, translators might think you're referring to different concepts, and thus might use different translations."
- [Use the same terms consistently](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/words/use-the-same-terms-consistently.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Using a different term may cause the reader to wonder if you're referring to the same group."
- [Use the same terms consistently](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/words/use-the-same-terms-consistently.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "You don't need to use synonyms to make your writing more interesting."
- [Global communications: Writing tips](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips), Microsoft, Microsoft Writing Style Guide, 2023: "Use one word for a concept, and use it consistently. Avoid using synonyms to refer to the same concept or feature. And don’t use the same word to refer to multiple concepts or features."
- [About ASD-STE100](https://www.asd-ste100.org/about.html), ASD STEMG, asd-ste100.org, 2023: "Many readers have limited knowledge of English, and are easily confused by complex sentence structures and by the number of meanings and synonyms which English words can have."
- [About ASD-STE100](https://www.asd-ste100.org/about.html), ASD STEMG, asd-ste100.org, 2023: "In general, there is only one word for one meaning, and one part of speech for one word."

### Q7: When the reader meets a word they have not used themselves, can they tell what it means right where they meet it?

**Thinking**: The reader takes each word with the meaning they already give it, so a word new to them, even one the writer's team uses every day, is replaced by everyday words, or given its meaning where they first meet it.

**Steps**

1. Write each abbreviation out in full where the reader first meets it.
2. Where the document gives a common word a meaning of its own, replace it with a word the reader does not already read another way.

**Grounds**

- [Write for your audience](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/audience/index.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Think about what your audience knows about the situation or topic you're writing about. Then, guide them through the information they need to know."
- [Avoid jargon](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/words/avoid-jargon.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "writers often fail to realize that terms they know well may be difficult or meaningless to their audience."
- [Write for a global audience](https://developers.google.com/style/translation), Google, Google developer documentation style guide, 2026: "Define abbreviations."
- [Minimize definitions](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/words/minimize-definitions.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "readers are likely to forget that you'd assigned some common word a new meaning, and when they come upon the word later in your document they assign the common meaning, rather than your specialized one."

### Q8: Does each word the reader reads carry part of what the document says, so that no word costs them time and gives them nothing?

**Thinking**: A word or a sentence that carries nothing of what the document says still costs the reader time, so it goes, while a word that shows how a sentence is built stays.

**Steps**

1. Read each changed section again from the top, and check that it still says all it said before.

**Grounds**

- [Be concise](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/concise/index.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Unnecessary words waste your audience's time."
- [Be concise](https://github.com/GSA/plainlanguage.gov/blob/main/_pages/guidelines/concise/index.md), PLAIN, plainlanguage.gov archive on GitHub, no date: "Challenge every word—do you need it?"
- [How Users Read on the Web](https://www.nngroup.com/articles/how-users-read-on-the-web/), Nielsen, Nielsen Norman Group, 1997: "As shown in the table, measured usability was dramatically higher for the concise version (58% better) and for the scannable version (47% better)."
