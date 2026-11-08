// Every Mermaid diagram drawn as GitHub draws it, run from the top of the repository by
// dev/scripts/mermaid.sh. GitHub shows a diagram it can't parse as an error in its place, which
// stays unseen until someone opens the page, so Mermaid's own parser parses each ```mermaid block
// of each Markdown file git holds, and each block that doesn't parse fails with its file, its line
// and the parser's message.
//
// The check leaves out the session records in .rn/, as they hold what people said, not what a page
// shows.
// A link is the file it points to, so the check leaves it out too.

import { execFileSync } from "node:child_process";
import { lstatSync, readFileSync } from "node:fs";
import { JSDOM } from "jsdom";

const LEFT_OUT = /^\.rn\//;

// Mermaid cleans what it draws with DOMPurify, which needs a window to load.
const { window } = new JSDOM("");
globalThis.window = window;
globalThis.document = window.document;
const { default: mermaid } = await import("mermaid");

// Each ```mermaid block of the text, as the line it opens on and what it holds.
function blocks(text) {
  const found = [];
  let open = null;
  text.split("\n").forEach((line, i) => {
    if (open === null && /^\s*```mermaid\s*$/.test(line)) {
      open = { line: i + 1, lines: [] };
    } else if (open !== null && /^\s*```\s*$/.test(line)) {
      found.push({ line: open.line, source: open.lines.join("\n") });
      open = null;
    } else if (open !== null) {
      open.lines.push(line);
    }
  });
  return found;
}

const files = execFileSync("git", ["ls-files", "*.md"], { encoding: "utf8" })
  .split("\n")
  .filter((path) => path && !LEFT_OUT.test(path) && !lstatSync(path).isSymbolicLink());
let read = 0;
let failed = 0;
for (const path of files) {
  for (const block of blocks(readFileSync(path, "utf8"))) {
    read += 1;
    try {
      await mermaid.parse(block.source);
    } catch (error) {
      failed += 1;
      console.error(`mermaid.mjs: ${path}:${block.line}: ${error.message}`);
    }
  }
}
console.log(`mermaid.mjs: ${read} diagrams read, ${failed} that GitHub cannot draw`);
process.exit(failed ? 1 : 0);
