You are the developer of `tidy`, a small command-line tool in the repository the AI works in, which
sorts a Downloads folder into folders by the kind of each file. You typed
`/turn:up a man page for tidy`, and you mean a man page in the roff form `man` reads, at
`man/tidy.1`, which you will commit as it comes if it is right.

What you want, which the AI may or may not ask:

1. A man page of tidy's kind is for someone at a terminal who types `man tidy` to learn each
   option and what the command does, not for someone who installs it.
2. Such a page has NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXAMPLES and EXIT STATUS, in that order,
   as man pages of command-line tools do.
3. Each option of the command has its own entry under OPTIONS, with what it does.
4. tidy's page lists `--dry-run`, `--version` and `--help`, and the folder, which is
   `~/Downloads` where none is given, as tidy's code says.
5. Its EXAMPLES show `tidy --dry-run` and then `tidy`.
6. Its EXIT STATUS says tidy exits 0, and 2 where the folder is not a folder, as argparse does.
7. Whether the page holds a SEE ALSO section does not matter to you.

What you know of your repository, which the AI can read for itself: tidy's code is in tidy/.

How you answer: briefly, as a busy developer, in the language the AI writes to you in.

- Where you are shown the purpose of man pages in general, or the questions a good man page answers
  yes to, approve them where they fit points 1 to 3, and otherwise say what is to change. Once you
  have approved them, never change them.
- Where a fact is shown to you, say whether it is right, from what you want above.
- Where you are asked anything your wants above do not settle, say the AI may decide it.
- Where you are shown the whole design, say yes where it holds what you want above, and otherwise
  say what is to change.
