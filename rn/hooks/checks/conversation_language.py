"""Check 14: the conductor's last message in a turn is in the conversation-language, judged by its
script. What it quotes from the record, in the artifact language, does not count."""
import re

from record import front_matter, section, steering

SCRIPTS = (  # script, ranges, whether it spaces its words
    ("latin", ((0x41, 0x5A), (0x61, 0x7A), (0xC0, 0x24F)), True),
    ("cyrillic", ((0x400, 0x4FF),), True),
    ("greek", ((0x370, 0x3FF),), True),
    ("arabic", ((0x600, 0x6FF),), True),
    ("hebrew", ((0x590, 0x5FF),), True),
    ("devanagari", ((0x900, 0x97F),), True),
    ("kana", ((0x3040, 0x30FF),), False),
    ("han", ((0x3400, 0x4DBF), (0x4E00, 0x9FFF)), False),
    ("hangul", ((0x1100, 0x11FF), (0xAC00, 0xD7AF)), False),
    ("thai", ((0xE00, 0xE7F),), False),
)
LANGUAGES = {  # language name, lower-cased, to the scripts its text is written in
    ("japanese", "日本語"): ("kana", "han"),
    ("chinese", "中文", "中国語"): ("han",),
    ("korean", "한국어", "韓国語"): ("hangul",),
    ("russian", "ukrainian", "bulgarian"): ("cyrillic",),
    ("greek",): ("greek",),
    ("arabic", "persian", "urdu"): ("arabic",),
    ("hebrew",): ("hebrew",),
    ("hindi",): ("devanagari",),
    ("thai",): ("thai",),
    ("english", "french", "german", "spanish", "portuguese", "italian", "dutch", "swedish",
     "norwegian", "danish", "finnish", "polish", "czech", "turkish", "vietnamese", "indonesian",
     "英語"): ("latin",),
}


def script_of(ch):
    o = ord(ch)
    for name, ranges, spaced in SCRIPTS:
        if any(a <= o <= b for a, b in ranges):
            return name, spaced
    return None, False


def script_share(text, scripts):
    """How much of the text's prose is in the given scripts: a word of a script that spaces its
    words counts one, a character of one that does not counts a half. None when too short to say."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"^\s*(?:[-*]\s+)?● .*$", " ", text, flags=re.M)  # a decision line quoted from the record
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\S*[/\\]\S*", " ", text)
    units, prev = {}, None
    for ch in text:
        name, spaced = script_of(ch)
        if name and (not spaced or name != prev):
            units[name] = units.get(name, 0) + (1 if spaced else 0.5)
        prev = name
    total = sum(units.values())
    if total < 3:
        return None
    return sum(units.get(n, 0) for n in scripts) / total


def unquoted(text, message):
    """The message without what it quotes from the record, which is in the artifact language: the
    map's goal line, the goal, and the task names."""
    message = re.sub(r"^\s*── .* ──\s*$", " ", message, flags=re.M)
    quoted = [l.strip() for l in section(text, "# Goal", 1) if l.strip()]
    for line in text.splitlines():
        m = re.match(r"^### \[[ x]\] #\d+: (.+)$", line)
        if m:
            quoted.append(m.group(1).strip())
    for q in sorted(quoted, key=len, reverse=True):
        message = message.replace(q, " ")
    return message


def check(sdir, message):
    text = steering(sdir)
    front = front_matter(text) or {}
    lang = front.get("conversation-language", "").strip().lower()
    scripts = next((v for k, v in LANGUAGES.items() if lang in k), None)
    if not scripts or not message:
        return []
    share = script_share(unquoted(text, message), scripts)
    if share is not None and share < 0.5:
        return [f"your message to the user is not in {front['conversation-language']}, the "
                "conversation language steering.md records: say it again in that language"]
    return []
