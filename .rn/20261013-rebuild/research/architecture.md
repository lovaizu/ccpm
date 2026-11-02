# Architecture document: best practice from sources

Each entry gives a source, its URL, a quote copied from the page, and one line on what the quote
says about the document's reader, a part of the document, or a way of making it. Every page was
opened and read on 2026-11-02. Quotes from PDF text keep the words, but ligatures such as "ﬁ" are
written as plain letters.

## The reader and what they use it for

### ISO/IEC/IEEE 42010, what an architecture description is for

- Source: ISO/IEC/IEEE 42010 website, "A Conceptual Model of Architecture Description",
  iso-architecture.org, n.d. (covers the 2011 and 2022 editions).
- URL: http://www.iso-architecture.org/42010/cm/
- Quote: "Architects and other system stakeholders use Architecture Descriptions to understand,
  analyze and compare Architectures, and often as “blueprints” for planning and construction."
- Says: the document's readers use it to understand the architecture and to build from it.

### ISO/IEC/IEEE 42010, stakeholders to consider

- Source: ISO/IEC/IEEE 42010 website, "Architecture Descriptions in ISO/IEC/IEEE 42010", n.d.
- URL: http://www.iso-architecture.org/42010/ads/
- Quote: "When identifying stakeholders, the following are to be considered and included when
  applicable: users of the system; operators of the system; acquirers of the system; owners of the
  system; suppliers of the system; developers of the system; builders of the system; maintainers of
  the system."
- Says: the standard asks the description to name who reads it, builders and maintainers among them.

### ISO/IEC/IEEE 42010, concerns to consider

- Source: ISO/IEC/IEEE 42010 website, "Architecture Descriptions in ISO/IEC/IEEE 42010", n.d.
- URL: http://www.iso-architecture.org/42010/ads/
- Quote: "When identifying concerns, the following are to be considered and included when applicable:
  the purposes of the system; the suitability of the architecture for achieving the system’s
  purposes; the feasibility of constructing and deploying the system; the potential risks and impacts
  of the system to its stakeholders throughout its life cycle; maintainability and evolvability of
  the system."
- Says: the description shows how the architecture serves the system's purpose and how it can
  change.

### arc42, stakeholders

- Source: Peter Hruschka, Gernot Starke, "1. Introduction and Goals", arc42 documentation,
  docs.arc42.org, n.d.
- URL: https://docs.arc42.org/section-1/
- Quote: "have to work with the architecture or with code" and "need the documentation of the
  architecture for their work"
- Says: arc42 counts among the readers those who build with the architecture.

### arc42, the readers set the detail

- Source: Hruschka and Starke, "1. Introduction and Goals", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-1/
- Quote: "These stakeholders determine the extent and the level of detail of your work and its
  results."
- Says: how much the document says follows from who reads it.

### Clements et al., write from the reader's point of view

- Source: Paul Clements, Felix Bachmann, Len Bass, David Garlan, James Ivers, Reed Little, Paulo
  Merson, Robert Nord, Judith Stafford, "Documenting Software Architectures: Views and Beyond", 2nd
  edition, Addison-Wesley, 2010; prologue section P.5 "Seven Rules for Sound Documentation", excerpt
  on InformIT, 2010.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "This rule simply reminds us to keep the end game in mind as we produce our documentation:
  Make your document serve its stakeholders and their intended uses of it."
- Says: the document is judged by whether its readers can do their work with it.

### Clements et al., documents written for the reader are read

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "Documents written for the reader will be read; documents written for the convenience of the
  writer will not."
- Says: a document shaped for the writer is not used.

### matklad, the newcomer's missing map

- Source: matklad, "ARCHITECTURE.md", matklad.github.io, 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "One of the lessons I’ve learned is that the biggest difference between an occasional
  contributor and a core developer lies in the knowledge about the physical architecture of the
  project." and "Roughly, it takes 2x more time to write a patch if you are unfamiliar with the
  project, but it takes 10x more time to figure out where you should change the code."
- Says: the reader who changes the product most needs to know where each thing is.

### Kruchten, each reader finds their view

- Source: Philippe Kruchten, "Architectural Blueprints—The “4+1” View Model of Software
  Architecture", IEEE Software 12 (6), 1995.
- URL: https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf
- Quote: "It actually allowed the various stakeholders to find what they want to know about the
  software architecture."
- Says: views split by concern let each reader go to the part they need.

### Malte Ubl, the first question on an unknown system

- Source: Malte Ubl, "Design Docs at Google", Industrial Empathy, 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "When Google engineers get confronted with a system that they hadn’t previously touched their
  first question often is “Where is the design doc?”."
- Says: the reader who meets a system for the first time looks for its design document.

### Martin Fowler, what architecture is

- Source: Martin Fowler, "Software Architecture Guide", martinfowler.com, 2019.
- URL: https://martinfowler.com/architecture/
- Quote: "It means that the heart of thinking architecturally about software is to decide what is
  important, (i.e. what is architectural), and then expend energy on keeping those architectural
  elements in good condition."
- Says: the document holds what is important to keep, not every detail.

### ISO/IEC/IEEE 42010, the definition of architecture

- Source: ISO/IEC/IEEE 42010 website, "A Conceptual Model of Architecture Description", n.d.
- URL: http://www.iso-architecture.org/42010/cm/
- Quote: "“fundamental concepts or properties of a system in its environment embodied in its elements,
  relationships, and in the principles of its design and evolution”."
- Says: an architecture is its elements, their relations and the principles they are built by.

## The one idea, before the details

### matklad, a bird's eye overview

- Source: matklad, "ARCHITECTURE.md", 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "Start with a bird’s eye overview of the problem being solved."
- Says: the document opens with the problem the product solves.

### rust-analyzer, an example bird's eye view

- Source: rust-analyzer team, "Architecture", rust-analyzer repository,
  docs/book/src/contributing/architecture.md, n.d.
- URL: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md
- Quote: "On the highest level, rust-analyzer is a thing which accepts input source code from the
  client and produces a structured semantic model of the code."
- Says: the example matklad points to opens with the whole product in one sentence.

### Malte Ubl, overview first

- Source: Malte Ubl, "Design Docs at Google", 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "This section should start with an overview and then go into details."
- Says: the design part opens with an overview.

### arc42, solution strategy

- Source: Hruschka and Starke, "4. Solution Strategy", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-4/
- Quote: "A short summary and explanation of the fundamental decisions and solution strategies, that
  shape the system’s architecture." and "These decisions form the cornerstones for your architecture.
  They are the basis for many other detailed decisions or implementation rules."
- Says: a short statement of the core idea comes before the parts that rest on it.

### Martin Fowler, the inverted pyramid

- Source: Martin Fowler, "Architecture Decision Record", martinfowler.com, 2026.
- URL: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
- Quote: "The key is to put the most important material at the start, and push details to later in
  the record."
- Says: the most important point opens the text.

### Malte Ubl, context and scope

- Source: Malte Ubl, "Design Docs at Google", 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "This isn’t a requirements doc. Keep it succinct! The goal is that readers are brought up to
  speed but some previous knowledge can be assumed and detailed info can be linked to."
- Says: the opening links to the requirements rather than repeating them.

### arc42, link to the requirements

- Source: Hruschka and Starke, "1. Introduction and Goals", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-1/
- Quote: "If requirements documents exist this overview should refer to these documents." and "Keep
  these excerpts as short as possible."
- Says: the architecture document points to the requirements, here the UX, and quotes little.

## Principles every part is built by, with their reasons

### arc42, crosscutting concepts

- Source: Hruschka and Starke, "8. Crosscutting Concepts", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-8/
- Quote: "Concepts form the basis for conceptual integrity (consistency, homogeneity) of the
  architecture."
- Says: shared rules make every part be built in the same way.

### arc42, one place for what many parts share

- Source: Hruschka and Starke, "8. Crosscutting Concepts", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-8/
- Quote: "It might be easier to communicate or document such cross-cutting topics at a central
  location, instead of repeating them in the description of the concerned building blocks, hardware
  elements or development processes."
- Says: a rule for several parts is written once, not in each part.

### Kruchten, design guidelines

- Source: Philippe Kruchten, "Architectural Blueprints—The “4+1” View Model of Software
  Architecture", IEEE Software 12 (6), 1995.
- URL: https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf
- Quote: "A Software Design Guidelines, which captures (among other things) the most important design
  decisions that must be respected to maintain the architectural integrity of the system."
- Says: the rules that keep the architecture whole are written for every builder to follow.

### matklad, architectural invariants

- Source: matklad, "ARCHITECTURE.md", 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "Explicitly call-out architectural invariants." and "Often, important invariants are
  expressed as an absence of something, and it’s pretty hard to divine that from reading the code."
- Says: a rule the code cannot show, such as a dependency that must not exist, is written down.

### matklad, boundaries

- Source: matklad, "ARCHITECTURE.md", 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "Point out boundaries between layers and systems as well." and "But finding a boundary by
  just randomly looking at the code is hard — good boundaries have measure zero."
- Says: the document names the boundaries, because the reader cannot find them in the code.

### rust-analyzer, an invariant as written

- Source: rust-analyzer team, "Architecture", rust-analyzer repository, n.d.
- URL: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md
- Quote: "**Architecture Invariant:** `syntax` crate is completely independent from the rest of
  rust-analyzer. It knows nothing about salsa or LSP."
- Says: an invariant is one sentence a builder can check their change against.

### Clements et al., record rationale

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "For the most important decisions, you should record why you made them the way you did. You
  should also record the important or most likely alternatives you rejected and state why."
- Says: each important decision carries its reason and the rejected alternatives.

### Michael Nygard, blind acceptance or blind change

- Source: Michael Nygard, "Documenting Architecture Decisions", Cognitect blog, 2011.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote: "Without understanding the rationale or consequences, this person has only two choices:"
  followed by "Blindly accept the decision." and "Blindly change it."
- Says: a builder without the reason either keeps a stale rule or breaks a sound one.

### Michael Nygard, the cost of decisions kept without understanding

- Source: Michael Nygard, "Documenting Architecture Decisions", 2011.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote: "If the project accumulates too many decisions accepted without understanding, then the
  development team becomes afraid to change anything and the project collapses under its own weight."
- Says: rules without reasons make the product hard to change.

### ISO/IEC/IEEE 42010, architecture rationale

- Source: ISO/IEC/IEEE 42010 website, "A Conceptual Model of Architecture Description", n.d.
- URL: http://www.iso-architecture.org/42010/cm/
- Quote: "Architecture Rationale records the explanation, justification or reasoning about
  Architecture Decisions that have been made and architectural alternatives not chosen."
- Says: the standard asks the description to record why, and what was not chosen.

### Anthropic, an instruction with its reason

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, n.d.
- URL: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Quote: "Providing context or motivation behind your instructions, such as explaining to Claude why
  such behavior is important, can give Claude more information about your goals and help it deliver
  more targeted responses." and "Claude can generalize from the explanation."
- Says: an AI builder carries a principle to a new case from its reason.

## Choices a builder would question

### Malte Ubl, trade-offs

- Source: Malte Ubl, "Design Docs at Google", 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "The design doc is the place to write down the trade-offs you made in designing your
  software. Focus on those trade-offs to produce a useful document with long-term value."
- Says: the lasting value of the document is in the trade-offs it records.

### Malte Ubl, alternatives considered

- Source: Malte Ubl, "Design Docs at Google", 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "While it is fine to be succinct about solution that ended up not being selected, this
  section is one of the most important ones as it shows very explicitly why the selected solution is
  the best given the project goals and how other solutions, that the reader may be wondering about,
  introduce trade-offs that are less desirable given the goals."
- Says: the reader finds why the other way they think of was not taken.

### Malte Ubl, an implementation manual is not a design doc

- Source: Malte Ubl, "Design Docs at Google", 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "If a doc basically says “This is how we are going to implement it” without going into
  trade-offs, alternatives, and explaining decision making (or if the solution is so obvious as to
  mean there were no trade-offs), then it would probably have been a better idea to write the actual
  program right away."
- Says: a document that only lists what to build, without why, adds little over the code.

### Malte Ubl, non-goals

- Source: Malte Ubl, "Design Docs at Google", 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "Note, that non-goals aren’t negated goals like “The system shouldn’t crash”, but rather
  things that could reasonably be goals, but are explicitly chosen not to be goals."
- Says: a non-goal is a goal someone could expect, ruled out on purpose.

### Michael Nygard, the parts of a decision record

- Source: Michael Nygard, "Documenting Architecture Decisions", 2011.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote: "Context This section describes the forces at play, including technological, political,
  social, and project local." and "Consequences This section describes the resulting context, after
  applying the decision. All consequences should be listed here, not just the "positive" ones."
- Says: a choice is given with the forces behind it and all its consequences.

### Michael Nygard, a conversation with a future developer

- Source: Michael Nygard, "Documenting Architecture Decisions", 2011.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote: "We will write each ADR as if it is a conversation with a future developer. This requires
  good writing style, with full sentences organized into paragraphs."
- Says: a choice is written in full sentences for the builder who comes later.

### arc42, architecture decisions

- Source: Hruschka and Starke, "9. Architecture Decisions", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-9/
- Quote: "Please use your judgement to decide whether an architectural decision should be documented
  here in this central section or whether you better document it locally (e.g. within the white box
  template of one building block). Avoid redundant texts."
- Says: a decision may sit next to the part it shapes, written once.

### Martin Fowler, decision records

- Source: Martin Fowler, "Architecture Decision Record", 2026.
- URL: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
- Quote: "Firstly they act as a record of decisions, allowing people months or years later to
  understand why the system is constructed in the way that it is. But perhaps even more valuable, the
  act of writing them helps to clarify thinking, particularly with groups of people."
- Says: writing the reason down serves the later reader and the writer's own thinking.

## From the ways the user uses it, to the parts

### Kruchten, scenarios as the fifth view

- Source: Philippe Kruchten, "Architectural Blueprints—The “4+1” View Model of Software
  Architecture", 1995.
- URL: https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf
- Quote: "The description of an architecture—the decisions made—can be organized around these four
  views, and then illustrated by a few selected use cases, or scenarios which become a fifth view. The
  architecture is in fact partially evolved from these scenarios as we will see later."
- Says: the parts are found from a few uses, and the uses then show the parts working.

### Kruchten, two purposes of scenarios

- Source: Philippe Kruchten, "Architectural Blueprints—The “4+1” View Model of Software
  Architecture", 1995.
- URL: https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf
- Quote: "as a driver to discover the architectural elements during the architecture design as we
  will describe later" and "as a validation and illustration role after this architecture design is
  complete, both on paper and as the starting point for the tests of an architectural prototype."
- Says: scenarios find the parts, check them, and seed the tests.

### arc42, runtime view

- Source: Hruschka and Starke, "6. Runtime View", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-6/
- Quote: "The main criterion for the choice of possible scenarios (sequences, workflows) is their
  architectural relevancy. It is not important to describe a large number of scenarios. You should
  rather document a representative selection."
- Says: the document shows the scenarios that matter, not all of them.

### arc42, map building blocks to the scenario

- Source: Hruschka and Starke, "6. Runtime View", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-6/
- Quote: "Tip 6-1: Always map existing building blocks to the activities within runtime scenarios!"
- Says: each step of a sequence names a part from the structure view.

### C4 model, dynamic diagram

- Source: Simon Brown, "Dynamic diagram", C4 model, c4model.com, n.d.
- URL: https://c4model.com/diagrams/dynamic
- Quote: "A dynamic diagram can be useful when you want to show how elements in the static model
  collaborate at runtime to implement a user story, use case, feature, etc."
- Says: a runtime diagram follows one user story through the parts.

### Mermaid, sequence diagrams

- Source: Mermaid, "Sequence diagrams", mermaid.js.org, n.d.
- URL: https://mermaid.js.org/syntax/sequenceDiagram.html
- Quote: "A Sequence diagram is an interaction diagram that shows how processes operate with one
  another and in what order."
- Says: a sequence diagram shows the order of the steps between parts.

### arc42, system scope and context

- Source: Hruschka and Starke, "3. Context and Scope", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-3/
- Quote: "System scope and context - as the name suggests - delimits your system (i.e. your scope) from
  all its communication partners (neighboring systems and users, i.e. the context of your system)."
- Says: the user stories are drawn where the product meets its users and neighbours.

### Mountain Goat Software, the user story template

- Source: Mountain Goat Software, "User Stories: What They Are, How to Write Them, and Examples",
  mountaingoatsoftware.com, last updated 2026-07-12.
- URL: https://www.mountaingoatsoftware.com/agile/user-stories
- Quote: "A common template is: As a [type of user], I [need/want/am required] to [do something], so
  that [reason or benefit]."
- Says: a user story names who uses the product and what they want of it.

## The parts, and figures a builder can read alone

### C4 model, common diagram problems

- Source: Simon Brown, "Introduction", C4 model, n.d.
- URL: https://c4model.com/introduction
- Quote: "Notation (e.g. colour coding, shapes, element sizes, line styles, etc) is not explained or
  is inconsistent." and "Relationships between elements are unlabelled." and "Technology choices are
  missing." and "Levels of abstraction are mixed."
- Says: these are the faults that stop a reader from reading a figure.

### C4 model, a figure stands alone

- Source: Simon Brown, "Notation", C4 model, n.d.
- URL: https://c4model.com/diagrams/notation
- Quote: "A good way to think about this is to ask yourself whether each diagram can stand alone, and
  be (mostly) understood without a narrative."
- Says: the figure carries its meaning without the text around it.

### C4 model, elements

- Source: Simon Brown, "Notation", C4 model, n.d.
- URL: https://c4model.com/diagrams/notation
- Quote: "Every element should have a short description, to provide an “at a glance” view of key
  responsibilities." and "Every container and component should have a technology explicitly
  specified."
- Says: each box says what it is responsible for and what it is made with.

### C4 model, relationships

- Source: Simon Brown, "Notation", C4 model, n.d.
- URL: https://c4model.com/diagrams/notation
- Quote: "Every line should be labelled, the label being consistent with the direction and intent of
  the relationship (e.g. dependency or data flow). Try to be as specific as possible with the label,
  ideally avoiding single words like, “Uses”."
- Says: each arrow says what one part does to the other.

### C4 model, key or legend

- Source: Simon Brown, "Notation", C4 model, n.d.
- URL: https://c4model.com/diagrams/notation
- Quote: "Any notation used should be as self-describing as possible, but all diagrams should have a
  key/legend to make the notation explicit."
- Says: every figure carries a legend.

### C4 model, review checklist

- Source: Simon Brown, "Software architecture diagram review checklist", C4 model, n.d.
- URL: https://c4model.com/diagrams/checklist
- Quote: "Do you understand what every element does?" and "Does every arrow have a label describing
  the intent of that relationship?"
- Says: a reviewer checks the figure from the reader's side, one yes-or-no question at a time.

### C4 model, what a component is

- Source: Simon Brown, "Component", C4 model, n.d.
- URL: https://c4model.com/abstractions/component
- Quote: "in the C4 model, a component is a grouping of related functionality encapsulated behind a
  well-defined interface."
- Says: a component is a unit of responsibility, not a file or a folder.

### C4 model, component diagram audience

- Source: Simon Brown, "Component diagram", C4 model, n.d.
- URL: https://c4model.com/diagrams/component
- Quote: "Next you can zoom in and decompose a container to describe the components that reside inside
  it; including their responsibilities and the technology/implementation details." and "Software
  architects and developers."
- Says: the component diagram is for those who build, and shows responsibilities and technology.

### C4 model, component diagrams are optional

- Source: Simon Brown, "Component diagram", C4 model, n.d.
- URL: https://c4model.com/diagrams/component
- Quote: "No, only create component diagrams if you feel they add value, and consider automating their
  creation for long-lived documentation."
- Says: C4 asks a component figure to earn its place.

### Clements et al., explain your notation

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "Make it as easy as possible for your reader to determine the meaning of the notation. The
  best way to do this is always to include a key in your diagrams."
- Says: every figure's symbols are explained in a key.

### Kruchten, what boxes and arrows mean

- Source: Philippe Kruchten, "Architectural Blueprints—The “4+1” View Model of Software
  Architecture", 1995.
- URL: https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf
- Quote: "Are the boxes representing running programs? Or chunks of source code? Or physical
  computers? Or merely logical groupings of functionality? Are the arrows representing compilation
  dependencies? Or control flows? Or data flows? Usually it is a bit of everything."
- Says: one figure that mixes kinds of boxes cannot be read, so each view has one kind.

### arc42, building block view

- Source: Hruschka and Starke, "5. Building Block View", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-5/
- Quote: "Maintain an overview of your source code by making its structure understandable through
  abstraction." and "This allows you to communicate with your stakeholder on an abstract level without
  disclosing implementation details."
- Says: the structure view shows the parts above the level of code.

### arc42, motivation for the decomposition

- Source: Hruschka and Starke, "5. Building Block View", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-5/
- Quote: "an overview diagram", "a motivation for the decomposition", "black box descriptions of the
  contained building blocks."
- Says: the structure view gives the figure, why it is split so, and what each part is.

### C4 model, type and technology of every element

- Source: Simon Brown, "Notation", C4 model, n.d.
- URL: https://c4model.com/diagrams/notation
- Quote: "The type of every element should be explicitly specified (e.g. Person, Software System,
  Container or Component)."
- Says: each box says what kind of thing the role is.

### Parnas, one module for each decision likely to change

- Source: David L. Parnas, "On the Criteria to be Used in Decomposing Systems into Modules",
  Department of Computer Science, Carnegie-Mellon University, technical report, 1971; a scan with a
  text layer kept at prl.khoury.northeastern.edu.
- URL: https://prl.khoury.northeastern.edu/img/p-tr-1971.pdf
- Quote: "We propose instead that one begins with a list of difficult design decisions or design
  decisions which are likely to change. Each module is then designed to hide such a decision from
  the others."
- Says: roles are cut so that each decision is made in one role alone.

## The data the parts share

### Malte Ubl, data storage

- Source: Malte Ubl, "Design Docs at Google", 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "Systems that store data should likely discuss how and in what rough form this happens.
  Similar to the advice on APIs, and for the same reasons, copy-pasting complete schema definitions
  should be avoided."
- Says: the document shows the shape of the data, not the full schema.

### Mermaid, entity relationship diagrams

- Source: Mermaid, "Entity Relationship Diagrams", mermaid.js.org, n.d.
- URL: https://mermaid.js.org/syntax/entityRelationshipDiagram.html
- Quote: "Relationships between entities are represented by lines with end markers representing
  cardinality."
- Says: an ER figure shows for each relation how many of each side it joins.

### Mermaid, attributes aid comprehension

- Source: Mermaid, "Entity Relationship Diagrams", mermaid.js.org, n.d.
- URL: https://mermaid.js.org/syntax/entityRelationshipDiagram.html
- Quote: "It can be useful to include attribute definitions on ER diagrams to aid comprehension of the
  purpose and meaning of entities. These do not necessarily need to be exhaustive; often a small
  subset of attributes is enough."
- Says: a few attributes are enough to tell the reader what an entity is.

## Where each part runs

### C4 model, deployment diagram

- Source: Simon Brown, "Deployment diagram", C4 model, n.d.
- URL: https://c4model.com/diagrams/deployment
- Quote: "A deployment diagram allows you to illustrate how instances of software systems and/or
  containers in the static model are deployed on to the infrastructure within a given deployment
  environment (e.g. production, staging, development, etc)."
- Says: the deployment figure puts each part of the structure into the place where it runs.

### C4 model, deployment nodes

- Source: Simon Brown, "Deployment diagram", C4 model, n.d.
- URL: https://c4model.com/diagrams/deployment
- Quote: "A deployment node represents where an instance of a software system/container is running;
  perhaps physical infrastructure (e.g. a physical server or device), virtualised infrastructure (e.g.
  IaaS, PaaS, a virtual machine), containerised infrastructure (e.g. a Docker container), an execution
  environment (e.g. a database server, Java EE web/application server, Microsoft IIS), etc. Deployment
  nodes can be nested."
- Says: the outer boxes are the environments, and they can hold one another.

### arc42, deployment view

- Source: Hruschka and Starke, "7. Deployment view", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-7/
- Quote: "the mapping of (software) building blocks to that infrastructure elements." and "From a
  software perspective it is sufficient to capture those elements of the infrastructure that are
  needed to show the deployment of your building blocks."
- Says: the deployment view shows only the infrastructure the parts need.

### arc42, why the deployment is so

- Source: Hruschka and Starke, "7. Deployment view", arc42 documentation, n.d.
- URL: https://docs.arc42.org/section-7/
- Quote: "important justification or motivation for this deployment structure"
- Says: the deployment figure comes with why it is laid out so.

## Where to make a change

### matklad, the codemap

- Source: matklad, "ARCHITECTURE.md", 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "The codemap should answer “where’s the thing that does X?”." and "It should also answer
  “what does the thing that I am looking at do?”."
- Says: the map of the code answers the builder's two questions in both directions.

### matklad, a map of a country

- Source: matklad, "ARCHITECTURE.md", 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "Avoid going into details of how each module works, pull this into separate documents or
  (better) inline documentation." and "A codemap is a map of a country, not an atlas of maps of its
  states."
- Says: the code map names coarse modules and leaves their insides to other places.

### matklad, check the map against the tree

- Source: matklad, "ARCHITECTURE.md", 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "Are the things you want to put near each other in the codemap adjacent when you run tree .?"
- Says: writing the map is a check that the folders match the parts.

### matklad, name things without links

- Source: matklad, "ARCHITECTURE.md", 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "Do name important files, modules, and types." and "Do not directly link them (links go
  stale)."
- Says: the map names files and types, and the reader finds them by search.

### C4 model, components are not folders

- Source: Simon Brown, "Component", C4 model, n.d.
- URL: https://c4model.com/abstractions/component
- Quote: "The C4 model is about showing the runtime units (containers) and how functionality is
  partitioned across them (components), rather than organisational units such as Java JAR files, C#
  assemblies, DLLs, modules, packages, namespaces or folder structures."
- Says: the file tree is a separate view from the components, and the document maps one to the
  other.

### Kruchten, the development view

- Source: Philippe Kruchten, "Architectural Blueprints—The “4+1” View Model of Software
  Architecture", 1995.
- URL: https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf
- Quote: "the development view, which describes the static organization of the software in its
  development environment."
- Says: how the files are organised is its own view, beside the logical one.

## How each part is tested

### Ham Vocke, two rules from the test pyramid

- Source: Ham Vocke, "The Practical Test Pyramid", martinfowler.com, 2018.
- URL: https://martinfowler.com/articles/practical-test-pyramid.html
- Quote: "Your best bet is to remember two things from Cohn's original test pyramid:" followed by
  "Write tests with different granularity" and "The more high-level you get the fewer tests you
  should have"
- Says: tests come at several scopes, with fewer at the wider ones.

### Ham Vocke, names of the layers

- Source: Ham Vocke, "The Practical Test Pyramid", 2018.
- URL: https://martinfowler.com/articles/practical-test-pyramid.html
- Quote: "Given the shortcomings of the original names it's totally okay to come up with other names
  for your test layers, as long as you keep it consistent within your codebase and your team's
  discussions."
- Says: the document defines its test types once and keeps the names.

### Ham Vocke, unit tests and test doubles

- Source: Ham Vocke, "The Practical Test Pyramid", 2018.
- URL: https://martinfowler.com/articles/practical-test-pyramid.html
- Quote: "Unit tests have the narrowest scope of all the tests in your test suite. The number of unit
  tests in your test suite will largely outnumber any other type of test." and "A unit test typically
  replaces external collaborators with test doubles"
- Says: a unit test fakes the neighbours of the unit.

### Ham Vocke, integration tests

- Source: Ham Vocke, "The Practical Test Pyramid", 2018.
- URL: https://martinfowler.com/articles/practical-test-pyramid.html
- Quote: "For your automated tests this means you don't just need to run your own application but
  also the component you're integrating with."
- Says: an integration test makes the outside part real.

### Ham Vocke, what integration means varies

- Source: Ham Vocke, "The Practical Test Pyramid", 2018.
- URL: https://martinfowler.com/articles/practical-test-pyramid.html
- Quote: "I mentioned before that “unit tests” is a vague term, this is even more true for
  “integration tests”."
- Says: the document must say what each test type makes real and what it fakes.

### Adam Bender, scope of a test

- Source: Adam Bender, "Testing Overview", Software Engineering at Google, chapter 11, abseil.io, 2020.
- URL: https://abseil.io/resources/swe-book/html/ch11.html
- Quote: "Scope refers to the specific code paths we are verifying."
- Says: the columns of the test table run from narrow scope to wide.

### The Scrum Guide, a bar every builder reads one way

- Source: Ken Schwaber and Jeff Sutherland, "The Scrum Guide", scrumguides.org, November 2020.
- URL: https://scrumguides.org/scrum-guide.html
- Quote: "The Definition of Done is a formal description of the state of the Increment when it meets
  the quality measures required for the product."
- Says: when a test passes is written once, for every builder.

### Anthropic, a result that varies from run to run

- Source: Anthropic, "Demystifying evals for AI agents", anthropic.com/engineering, 2026.
- URL: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Quote: "pass^k measures the probability that all k trials succeed."
- Says: a test of what an AI does passes when k runs of k meet the expectation.

## Keeping it short, in one place and true

### matklad, keep it short and stable

- Source: matklad, "ARCHITECTURE.md", 2021.
- URL: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Quote: "Keep it short: every recurring contributor will have to read it." and "This is the main rule
  of thumb for ARCHITECTURE — only specify things that are unlikely to frequently change."
- Says: the document holds what lasts while the code changes.

### Michael Nygard, large documents

- Source: Michael Nygard, "Documenting Architecture Decisions", 2011.
- URL: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Quote: "Large documents are never kept up to date. Small, modular documents have at least a chance at
  being updated." and "Nobody ever reads large documents, either."
- Says: size decides whether the document is read and kept current.

### Clements et al., avoid unnecessary repetition

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "Each kind of information should be recorded in exactly one place."
- Says: each fact has one home, so copies do not drift apart.

### Clements et al., avoid ambiguity

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "The most dangerous kind of ambiguity is undetected ambiguity. Here, each reader will think he
  or she understands the document, but unwittingly each reader will come to different conclusions
  about what it is saying."
- Says: builders who read one sentence two ways build parts that do not fit.

### Clements et al., use a standard organization

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "It helps the reader navigate the document and find specific information quickly."
- Says: a fixed template lets the reader find each thing where they expect it.

### Clements et al., organize for reference

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "Software documentation may be read from cover to cover at most once, probably never. But a
  document is likely to be referenced hundreds or thousands of times."
- Says: the builder looks things up in the document, so it is laid out for looking up.

### Clements et al., no blank sections

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "If the section is blank, the reader will wonder whether the information is coming later or
  whether it is indeed supposed to be blank."
- Says: an empty part says why it is empty.

### Clements et al., keep documentation current

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "Documentation that is incomplete or out of date does not reflect truth, does not obey its own
  rules for form and internal consistency, and is not used."
- Says: an out-of-date document stops being used.

### Clements et al., review for fitness of purpose

- Source: Clements et al., "Documenting Software Architectures: Views and Beyond", 2nd ed., 2010,
  section P.5, InformIT excerpt.
- URL: https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5
- Quote: "Only the intended users of a document will be able to tell you whether it contains the right
  information presented in the right way."
- Says: the document is checked by its readers, here the builders.

### Lima Neto et al., what practitioners find wrong

- Source: Crescencio Rodrigues Lima Neto, Christina von Flach Chavez, Eduardo Santana de Almeida,
  Dominik Rost, Matthias Naab, "Unveiling Architecture Documentation: Brazilian Stakeholders in
  Perspective", arXiv:1510.06229, 2015.
- URL: https://arxiv.org/abs/1510.06229
- Quote: "Outdated architecture documentation;", "Inadequate level of granularity;", "Implementation
  not in sync with architecture; and", "Unnecessary information."
- Says: in a survey of 147 practitioners these were the most frequent problems.

### Lima Neto et al., lost decisions

- Source: Lima Neto et al., "Unveiling Architecture Documentation: Brazilian Stakeholders in
  Perspective", arXiv:1510.06229, 2015.
- URL: https://arxiv.org/abs/1510.06229
- Quote: "The decision making is lost during the project development because there is no concern with
  traceability;"
- Says: without written reasons, the decisions are lost.

### Malte Ubl, update the doc while the design changes

- Source: Malte Ubl, "Design Docs at Google", 2020.
- URL: https://www.industrialempathy.com/posts/design-docs-at-google/
- Quote: "It is strongly recommended to update the design doc in this case. As a rule of thumb: If the
  designed system hasn’t shipped yet, then definitely update the doc."
- Says: the document is changed in place when the design changes.

### Martin Fowler, superseded decisions

- Source: Martin Fowler, "Architecture Decision Record", 2026.
- URL: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
- Quote: "They should not be modified if the decision is changed, but linked to a superseding
  decision."
- Says: for decision records, Fowler keeps the old record and links to the new one.

### ISO/IEC/IEEE 42010, form is free

- Source: ISO/IEC/IEEE 42010 website, "Architecture Descriptions in ISO/IEC/IEEE 42010", n.d.
- URL: http://www.iso-architecture.org/42010/ads/
- Quote: "The Standard does not prescribe the form that an AD takes, as long as it meets certain
  requirements."
- Says: the standard fixes what the description holds, not its layout.

### Martin Fowler, the cost of what no one needs

- Source: Martin Fowler, "Yagni", martinfowler.com, 2015-05-26.
- URL: https://martinfowler.com/bliki/Yagni.html
- Quote: "The code for the presumptive feature adds some complexity to the software, this complexity
  makes it harder to modify and debug that software, thus increasing the cost of other features."
- Says: a story, role or data no step needs makes every later change cost more.

## Not found

- ISO/IEC/IEEE 42010 itself: the standard is sold by ISO and was not opened. The entries cite the
  website iso-architecture.org, which summarises it and says to see the original text for the
  actual requirements.
- Bass, Clements, Kazman, "Software Architecture in Practice": no publisher excerpt was found on
  InformIT, and the O'Reilly chapter page returned 403. No entry cites it. The entries from
  "Documenting Software Architectures: Views and Beyond" share two of its authors.
- TOGAF architecture principles (name, statement, rationale, implications): the Open Group pages for
  TOGAF 9 and TOGAF 9.1 asked for a sign-in. Only third-party summaries were found, and none is cited.
- Kruchten's paper in IEEE Xplore: only the copy on cs.ubc.ca was opened.
- Mike Cohn, "Succeeding with Agile", the source of the test pyramid: not opened. The entries cite
  Ham Vocke's article, which reports it.
- Parnas's paper in Communications of the ACM, 1972: not opened. The entry cites the 1971 Carnegie-Mellon
  report of the same title, whose text layer holds the quote.
- Peter Chen's 1976 entity-relationship paper: the MIT copy returned HTTP 429. The data-model
  entries cite the Mermaid documentation instead.
- A source on test weight per deployment unit, or on a test table by unit and test type: none of the
  pages I opened gives one.
- A source on an architecture document read by an AI builder: none of the pages I opened addresses
  that reader.
