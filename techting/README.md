# techting — technical writing, up a level

A draft reads badly when it forgets who's reading it. `techting` fixes that the way a good editor
would: it pins down the reader first — who they are, what they need to walk away able to do, and how
they read — and then derives the tone, the diagrams, the closing, and the outline from that. One
skill, `/techting:up`, brushes an existing draft up a level (or writes one from scratch through the
same steps).

## Install

`techting` ships from the `ccpm` marketplace. In Claude Code, add the marketplace once, then install
the plugin:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install techting@ccpm
```

That makes `/techting:up` available — to you, and to Claude itself while it's drafting.

## Brushing a draft up

Say you've got a rough README section and you want it to land. Point `/techting:up` at it.

```console
> /techting:up tighten up docs/setup.md — it's a mess

● First, who reads this? I'll write it down before touching a word:
    Reader      a new teammate setting the project up for the first time
    Must do     get from clone to a running app, once, without getting stuck
    How they read   top to bottom, following along as they go

  That makes this a **guide** — goal & prerequisites → ordered steps with the
  expected result of each → how to tell it worked + the usual snags. Warm and
  plain, since they're reading along. Here's the revised docs/setup.md:
  …

● What I changed, and why:
    · Led with "you'll have X running" + prerequisites — a guide reader needs the
      goal and what to have ready before step 1 (was buried at the bottom).
    · Turned the install paragraph into ordered steps, each with its expected
      result — they're doing this live, not reading about it.
    · Drew the service dependencies as a mermaid graph — three paragraphs of
      "X needs Y" is a diagram, not prose.
    · Cut the architecture tangent — noise for someone who just wants it running;
      linked it out instead.
```

It won't guess past a blank. If it can't tell who the reader is, it stops and asks rather than
writing for no one in particular:

```console
> /techting:up make this page better

● I can't pin down the reader yet, and everything downstream depends on it:
    · Who's reading — someone evaluating whether to adopt this, or someone
      already committed and setting it up?
    · After reading, what should they be able to decide or do?
  Tell me those two and I'll brush it up against them.
```

## The five shapes a document can take

`/techting:up` won't mix roles in one document — a mixed role is the fastest way to lose a reader. It
picks the one that fits your reader and commits to it:

- **Article** — someone reading to understand. Stumbling point → why → what to do.
- **Guide** — someone doing it right now. Ordered steps, each with its expected result.
- **Reference** — someone looking a thing up. Unique, exhaustive, built for lookup, not for reading
  through.
- **Record / ADR** — someone tracing how a decision was reached. The rejected options and the reasons
  are the main act.
- **Evaluation** — someone making a call. Measurements and judgment kept apart, closing on a
  recommendation.

Whichever it picks, the same finish applies: headings that carry the argument on their own, structure
and flow shown as diagrams instead of prose, fact kept separate from hypothesis, and no hedging or
filler left behind. You get the revised document and a short note of what moved and why.
