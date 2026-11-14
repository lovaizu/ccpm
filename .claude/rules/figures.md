---
paths:
  - "**/*.svg"
  - "dev/images/**"
  - "dev/scripts/figures.py"
---

# Figures in ccpm

These rules make every figure of the repository look alike in light and dark themes, and in both
English and Japanese.
[The refactor-doc best practice](../../plugins/rn/domain/best-practices/refactor-doc/best-practice.md)
says which form a figure takes, in its practice on lists, tables, and diagrams. These rules say only how an SVG figure looks.

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
- **Make the Japanese copy of a figure in `.review/ja` from the English figure, and change only its
  text.** `figures.py` gives the copy the same style and checks it too. Render the copy, and check
  that no text runs out of its box or across a line.
  - Rationale: a label takes another width in Japanese than in English, so one that fits in English
    can overflow in Japanese.
