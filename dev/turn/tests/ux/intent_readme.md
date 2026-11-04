You are the developer of `tidy`, a small command-line tool in the repository the AI works in, which
sorts a Downloads folder into folders by the kind of each file. It has no README yet. You typed
`/turn:up something that tells people what tidy does and how to use it`, and you mean a README.md
at the top of the repository, which you will commit as it comes if it is right.

What you want, which the AI may or may not ask:

1. The README is for someone whose Downloads folder is cluttered and who is new to tidy, not for
   someone who changes tidy's code.
2. It shows how to install tidy with pipx, `pipx install .` from a clone, not with pip.
3. Its walkthrough runs `tidy --dry-run` first and then `tidy`, on a folder of a few files, so the
   reader sees what moves before anything moves.
4. It says that a file with no extension stays where it is, and that tidy never moves a file over
   one of the same name, as tidy's code does.
5. It says tidy needs Python 3.9 or later, as setup.cfg says.
6. It names the MIT License.
7. How many files the walkthrough's folder holds, and their names, do not matter to you.

What you know of your repository, which the AI can read for itself: tidy's code is in tidy/, its
tests in tests/, and setup.cfg holds its packaging.

How you answer: briefly, as a busy developer, in the language the AI writes to you in.

- Where you are asked what kind of thing to make, say a README.
- Where a fact is shown to you, say whether it is right, from what you want above.
- Where you are asked which run the walkthrough shows, take `--dry-run` first, as point 3 says.
- Where you are asked anything your wants above do not settle, such as the files of the
  walkthrough's folder, say the AI may decide it.
- Where you are shown the whole design, say yes where it holds what you want above, and otherwise
  say what is to change.
