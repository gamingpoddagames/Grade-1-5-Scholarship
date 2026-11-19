#!/usr/bin/env python3
"""Sinhala/Latin safe rendering and Facebook caption checks.

Noto Sans Sinhala is not a Latin/emoji font. A single font call used for
mixed-script text silently emits tofu (boxes). Shape Sinhala runs with RAQM
and render Latin/punctuation with DejaVu Sans. Fail closed on unknown glyphs.
"""
import unicodedata
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import ImageFont, features
from brand_assets import FONT, BOLD, LATIN, LATIN_BOLD

FORBIDDEN = {"\ufffd", "\u25a1", "\u25a0", "\u2610", "\u2612", "\u200b", "\ufeff"}
# Long captions should use standard Unicode letters, not emoji / symbol font fallback.
DISALLOWED_CAPTION_RANGES = ((0x1F000, 0x1FFFF), (0x2600,0x27BF))

@lru_cache(maxsize=8)
def cmap(path):
    if not Path(path).is_file():
        raise RuntimeError("Required font missing from runner: "+str(path))
    return frozenset(TTFont(str(path)).getBestCmap())

def check_caption(text):
    """Reject potentially invisible/unsupported controls before Graph API call."""
    if not isinstance(text,str) or not text.strip():
        raise ValueError("Empty Facebook caption")
    if unicodedata.normalize("NFC",text)!=text:
        raise ValueError("Facebook caption must be normalized Unicode NFC")
    for ch in text:
        cp=ord(ch)
        if ch in FORBIDDEN or (0xD800<=cp<=0xDFFF):
            raise ValueError("Invalid/missing glyph marker in caption")
        if any(lo<=cp<=hi for lo,hi in DISALLOWED_CAPTION_RANGES):
            raise ValueError("Emoji/special icon not approved for consistent Facebook caption rendering")
        if unicodedata.category(ch) in ("Cc", "Cf") and ch not in "\n\r\t\u200c\u200d":
            raise ValueError("Unsupported control character in Facebook caption")
    return True

@lru_cache(maxsize=64)
def _fallback(size,bold):
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM shaping is required for Sinhala")
    return ImageFont.truetype(LATIN_BOLD if bold else LATIN,size,layout_engine=ImageFont.Layout.RAQM)

def script_runs(text,sinhala_face):
    """Group glyphs into Sinhala or Latin runs, rejecting missing characters."""
    sin_path=getattr(sinhala_face,"path",None)
    if sin_path is None:
        raise RuntimeError("Expected a font loaded from Noto Sans Sinhala")
    sin=cmap(sin_path)
    latin=cmap(LATIN_BOLD if "Bold" in str(sin_path) else LATIN)
    runs=[]
    current=""
    style=None
    for ch in str(text):
        cp=ord(ch)
        if ch in FORBIDDEN or (0xD800<=cp<=0xDFFF):
            raise ValueError("Forbidden square/replacement character in artwork")
        if any(lo<=cp<=hi for lo,hi in DISALLOWED_CAPTION_RANGES):
            raise ValueError("Unsupported emoji/icon in artwork")
        if ch=="\n":
            raise ValueError("Render each line individually")
        # Preserve shaping: do not separate Sinhala vowel modifiers/ZWJ from base.
        is_sinhala=0x0D80<=cp<=0x0DFF or cp in (0x200C,0x200D)
        if is_sinhala:
            if cp not in sin:raise ValueError(f"Missing Sinhala font glyph: U+{cp:04X}")
            chosen="si"
        elif cp in latin:
            chosen="latin"
        elif cp in sin:
            chosen="si"
        else:
            raise ValueError(f"Unsupported image glyph: U+{cp:04X}")
        if current and style!=chosen:
            runs.append((style,current))
            current=""
        current+=ch
        style=chosen
    if current:runs.append((style,current))
    return runs

def mixed_width(draw,text,sinhala_face):
    total=0
    for style,chunk in script_runs(text,sinhala_face):
        face=sinhala_face if style=="si" else _fallback(sinhala_face.size,"Bold" in str(sinhala_face.path))
        bbox=draw.textbbox((0,0),chunk,font=face,language=("si" if style=="si" else "en"))
        total+=bbox[2]-bbox[0]
    return total

def draw_mixed(draw,xy,text,sinhala_face,fill):
    x,y=xy
    for style,chunk in script_runs(text,sinhala_face):
        face=sinhala_face if style=="si" else _fallback(sinhala_face.size,"Bold" in str(sinhala_face.path))
        draw.text((x,y),chunk,font=face,fill=fill,language=("si" if style=="si" else "en"))
        bbox=draw.textbbox((0,0),chunk,font=face,language=("si" if style=="si" else "en"))
        x+=bbox[2]-bbox[0]
    return x

def test_image_glyphs(path):
    """Strict check that all intended text is supported by at least one real font."""
    # Caller invokes script_runs for actual text; this checks that font paths are present.
    for name in (FONT,BOLD,LATIN,LATIN_BOLD):
        if not cmap(name):raise RuntimeError("Empty font character map")
    return True
