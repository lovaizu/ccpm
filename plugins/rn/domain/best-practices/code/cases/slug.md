# Slug, tested late

A command that makes a page's address from its title, in JavaScript. Its design is sound, and its
tests came after the code. It's a kept case of the [code best practice](../best-practice.md): a
deliverable with the verdict on each question that someone who knows the maintainer's work gives, so
that an evaluator proves itself on it before anyone trusts its verdicts, here in a language other
than the others'.

## Specification

- `slug <title>` prints the slug of the title and exits 0.
- A slug holds the title's letters from a to z and digits from 0 to 9, in lower case, with each run
  of anything else as one hyphen and no hyphen at either end.
- A slug is at most 50 characters, with no hyphen at its end after the cut.
- A title with no letter or digit, or any number of arguments other than one, prints what to fix on
  standard error, and the command exits 2.

## Setup

Node.js 18 or later, with nothing else to install. The tests run by `node --test`.

## Code

`slug.mjs`:

```javascript
// The slug of a title, the one place that holds what a slug may be: what a page's address ends in.

// The longest slug, in characters.
export const LONGEST = 50;

// A title the slug can't be made of, with the message that says why.
export class NoSlug extends Error {}

// The slug of the title: its ASCII letters and digits in lower case, each run of anything else as
// one hyphen, none at either end, cut to LONGEST characters. Refuses, by NoSlug, a title that holds
// no letter or digit.
export function slug(title) {
  const made = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  if (made === "") {
    throw new NoSlug(`the title ${JSON.stringify(title)} holds no letter or digit to make a slug of`);
  }
  return made.slice(0, LONGEST).replace(/-$/, "");
}
```

`cli.mjs`:

```javascript
// The slug command: prints the slug of the title it's given, or what to fix.

import { NoSlug, slug } from "./slug.mjs";

export function main(args, out = process.stdout, err = process.stderr) {
  if (args.length !== 1) {
    err.write("usage: slug <title>\n");
    return 2;
  }
  try {
    out.write(`${slug(args[0])}\n`);
    return 0;
  } catch (why) {
    if (!(why instanceof NoSlug)) throw why;
    err.write(`slug: ${why.message}\n`);
    return 2;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) process.exitCode = main(process.argv.slice(2));
```

## Tests

`slug.test.mjs`:

```javascript
import assert from "node:assert/strict";
import { test } from "node:test";

import { main } from "./cli.mjs";
import { NoSlug, slug } from "./slug.mjs";

const seen = [];

test("slug", () => {
  const s = slug("  Hello, World!  ");
  assert.equal(s, "hello-world");
  assert.equal(slug("Déjà vu"), "d-j-vu");
  seen.push(s);
});

test("long titles", () => {
  assert.ok(slug("word ".repeat(40)).length <= 50);
});

test("same slug again", () => {
  assert.equal(slug("Hello World"), seen[0]);
});

test("no letters", () => {
  assert.throws(() => slug("!!!"), NoSlug);
});

test("cli", () => {
  main(["A title"], { write() {} }, { write() {} });
});
```

## How the maker worked

1. The maker wrote `slug.mjs` and `cli.mjs`, ran the command by hand, then wrote the tests and saw
   them pass.
2. Coverage showed the command's lines unrun, and the maker added the test `cli` to run them.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | yes | `slug.mjs` hides what a slug may be, and `cli.mjs` how the command reads its arguments. Each says so at its top. |
| Q2 | yes | `slug.mjs` imports nothing, and only the command's edge touches the process. |
| Q3 | yes | No problem here calls for a pattern, and the code uses none. |
| Q4 | yes | The longest slug lives in `LONGEST` alone, and the rule of what a slug holds lives in `slug` alone. |
| Q5 | yes | Each line answers a line of the specification. |
| Q6 | yes | The command checks its arguments first, and each refusal says what to fix. |
| Q7 | no | No test takes a slug of 50 or 51 characters, a cut that ends on a hyphen, or more than one argument. |
| Q8 | no | The tests came after the code, so none of them has shown that it fails without its behavior. |
| Q9 | no | The test named `slug` checks three behaviors, and the names `long titles` and `cli` say no behavior. |
| Q10 | yes | The tests call `slug` and `main` as their callers do, with stand-ins only for the output streams. |
| Q11 | no | `same slug again` reads what `slug` left in `seen`, so it fails when it runs alone. |
| Q12 | yes | Each function says in a sentence what it does, and each name says what it holds. |
| Q13 | no | The maker answered the coverage gap with `cli`, which asserts nothing, and traced it to no case. |
| Q14 | no | A newcomer who changes the longest slug finds no test of it, so they can't know from the tests that every other behavior still holds. |
