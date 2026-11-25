---
paths:
  - "**/*.svg"
  - "dev/images/**"
  - "dev/scripts/figures.py"
---

# Figures in ccpm

These rules make every figure of the repository look alike in light and dark themes.

- **Take a figure's whole look from `dev/images/figures.css`: its colors in light and dark, its
  lines, its text sizes, and its fonts.** Put the style into each figure with
  `python3 dev/scripts/figures.py write`, and give each shape and each text a class of that file.
  `dev/scripts/check.sh` fails on a figure whose copy of the style differs from the file. It also
  fails on a figure that sets a font or a color of its own.
  - Rationale: a reader learns from one figure what a color or a dashed line means, and reads the
    next figure by it. With one file, one change reaches every figure.
- **Give each new class its dark color as well, under the file's
  `@media (prefers-color-scheme: dark)`.**
  - Rationale: a figure on GitHub shows in the reader's theme. A color chosen for light alone can
    vanish against a dark page.
- **Name fonts that the reader's machine already has, in the file's list. Don't embed or link a
  font.**
  - Rationale: a page shows a figure through `<img>`, which loads no other file, so a linked font
    never arrives. An embedded font adds its size to every figure, and a Japanese font weighs
    megabytes.
