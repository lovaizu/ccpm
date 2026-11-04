"""The kind of a file, by its extension: the folder tidy moves it into."""

import os

KINDS = {
    ".jpg": "images",
    ".jpeg": "images",
    ".png": "images",
    ".gif": "images",
    ".pdf": "documents",
    ".docx": "documents",
    ".txt": "documents",
    ".zip": "archives",
    ".tar": "archives",
    ".gz": "archives",
    ".mp3": "audio",
    ".mp4": "video",
}
# Where a file of an extension tidy does not know goes.
OTHER = "other"


def kind_of(name):
    """The folder a file of the name goes into; None for a file of no extension, which stays."""
    extension = os.path.splitext(name)[1].lower()
    if not extension:
        return None
    return KINDS.get(extension, OTHER)
