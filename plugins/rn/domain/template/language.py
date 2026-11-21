"""Decides what a document's language changes in rn's check of a template: whether the document
keeps the template's own words, and how a sentence's length is counted and bounded."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from fault import Wrong

from template.markdown import characters, words

# The language of a document where none is given, as ccpm's own documents are English.
ENGLISH = "English"
# The most words a sentence takes: the limit that ASD-STE100 sets for procedures, as the user
# judged the 25 of GOV.UK and the Australian Government Style Manual too long to read.
MOST_WORDS = 20
# The most characters a sentence takes in a language written without spaces between words: the
# bound of an easy read that Japanese writing guides name most, as the user decided.
MOST_CHARACTERS = 60
# The languages written without spaces between words, by their names in English, as the design
# tree's context gives a language, such as Japanese. A count of words, which splits at spaces,
# takes a whole sentence of these as one word, so their sentences are bounded by characters. A
# name matches by any of its words, in any case, such as Simplified Chinese.
_UNSPACED = frozenset({"japanese", "chinese", "thai", "lao", "khmer", "burmese"})
# How many of a long sentence's first words, or first characters, a fault shows to find it by.
_BEGIN_WORDS = 6
_BEGIN_CHARACTERS = 20


@dataclass(frozen=True)
class Language:
    """What the check holds a document in its language to: whether it keeps the template's own
    words, such as its headings and labels, where in another language the maker puts them in the
    document's; and the most of `unit`, words or characters, that a sentence takes, with `length`
    giving a sentence's count of them and `begins` its first ones."""

    own_words: bool
    unit: str
    most: int
    length: Callable[[str], int]
    begins: Callable[[str], str]


def of(name: str) -> Language:
    """The language of a document by its name as the design tree's context gives it, such as
    English or Japanese: English keeps the template's own words, and any other doesn't; a language
    written without spaces between words, such as Japanese, Chinese, or Thai, takes at most
    MOST_CHARACTERS characters to a sentence, and any other MOST_WORDS words. Raises Wrong where the
    name is blank."""
    if not name.strip():
        raise Wrong(
            "the language is blank; give the document's language as a word, such as English"
        )
    said = set(re.findall(r"[a-z]+", name.lower()))
    if said & _UNSPACED:
        return Language(False, "characters", MOST_CHARACTERS, characters, _first_characters)
    return Language(ENGLISH.lower() in said, "words", MOST_WORDS, words, _first_words)


def _first_words(sentence: str) -> str:
    """The sentence's first words."""
    return " ".join(sentence.split()[:_BEGIN_WORDS])


def _first_characters(sentence: str) -> str:
    """The sentence's first characters."""
    return sentence[:_BEGIN_CHARACTERS]
