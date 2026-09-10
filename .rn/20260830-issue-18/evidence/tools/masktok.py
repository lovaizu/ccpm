"""Load probe tokens from a directory and mask them out of text.

Tokens are never typed into a command or into the evidence document: they are read
from one file per token and replaced by <name> in anything printed. Import this from
the other tools in this directory rather than repeating the preamble inline.
"""
import os


def load(token_dir, names=None):
    """Return {name: value} for every token file in token_dir (or just `names`)."""
    if names is None:
        names = sorted(n for n in os.listdir(token_dir)
                       if os.path.isfile(os.path.join(token_dir, n)))
    return {n: open(os.path.join(token_dir, n)).read().strip() for n in names}


def mask(text, tokens):
    """Replace every token value in `text` with <name>."""
    for name, value in sorted(tokens.items()):
        if value:
            text = text.replace(value, '<%s>' % name)
    return text
