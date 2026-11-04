You are the developer of `tidy`, a small command-line tool in the repository the AI works in, which
sorts a Downloads folder into folders by the kind of each file. You asked the caller for tidy's
README with `/caller:readme`, and yesterday you told the caller who the README is for, that it
installs tidy with pipx, and that it shows none of tidy's Python modules. Being asked any of these
again wastes your time.

What you want, which the AI may or may not ask:

1. The README is for someone with a cluttered Downloads folder who installs tidy and sorts it.
2. It installs tidy with pipx, `pipx install .` from a clone.
3. It shows none of tidy's Python modules.
4. Its walkthrough runs `tidy --dry-run` first and then `tidy`.
5. It says that a file with no extension stays where it is.
6. It says tidy needs Python 3.9 or later.
7. The names of the files in the walkthrough's folder do not matter to you.

How you answer: briefly, as a busy developer, in the language the AI writes to you in.

- Where a fact is shown to you, say whether it is right, from what you want above.
- Where you are asked which run the walkthrough shows, take `--dry-run` first.
- Where you are asked anything your wants above do not settle, say the AI may decide it.
- Where you are shown the whole design, say yes where it holds what you want above, and otherwise
  say what is to change.
