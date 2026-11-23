#!/usr/bin/env python3
"""Facebook/Blogger safe Sinhala captions (do not strip valid Sinhala joiners).

Facebook Desktop and mobile choose their own fonts. We can fix malformed
payloads and awkward mixed-script headlines, not force Facebook's UI font.
"""
import re
import unicodedata

# Remove accidental clipboard/HTML format artifacts, not U+200C/U+200D.
STRIP = "\ufeff\u200b\u2060\u00ad"
BIDI = "".join(chr(n) for n in list(range(0x202a, 0x202f)) + list(range(0x2066, 0x206a)))


def clean_caption(value):
    if not isinstance(value, str):
        raise TypeError("Facebook caption must be text")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("\u00a0", " ")
    value = value.translate({ord(char): None for char in STRIP + BIDI})
    # The pipe separator is not needed in headings; mobile/desktop line
    # breaking looks more consistent with real paragraph boundaries.
    value = re.sub(r"(?<=\S)[ \t]*[|｜][ \t]*(?=\S)", "\n", value)
    value = "\n".join(re.sub(r"[ \t]{2,}", " ", line).strip()
                      for line in value.split("\n"))
    value = re.sub(r"\n{3,}", "\n\n", value).strip()
    value = unicodedata.normalize("NFC", value)
    from font_safety import check_caption
    check_caption(value)
    return value


def clean_title(value):
    value = clean_caption(value)
    # Use a compact one-line title. Keep the full details in the caption.
    return " - ".join(part.strip() for part in value.splitlines() if part.strip())


def clean_quiz_lines(grade, topic, number=None):
    result = f"{grade} ශ්‍රේණිය\n{topic}"
    if number is not None:
        result += f"\nප්‍රශ්න අංක {int(number)}"
    return clean_caption(result)
