#!/usr/bin/env python3
"""Genuine educational comment invitations and safe, optional ad disclosure.

No false 'comment to reveal the answer' claim, forced ad interstitials, fake
publisher links, automatic redirects, or JavaScript injected into Blogger posts.
"""
import html
import os
from urllib.parse import urlsplit

from social_text import clean_caption


PROMPTS = {
    "sequence": "ඔබ ඊළඟ අංකය ගණන් කළේ කොහොමද? එකතු වන අගයන් පෙන්වන්න.",
    "magic_grid": "ඔබ තෝරාගත් අංකය පේළියකටත් තීරුවකටත් ගැළපෙන හැටි පැහැදිලි කරන්න.",
    "balance": "රවුම සහ කොටුවේ අගයන් ඔබ සොයාගත්තේ කොහොමද? හේතුව ලියන්න.",
    "dot_pattern": "තිත් ගණන වැඩි වන ආකාරය ඔබ දැක්කේ කොහොමද? පේළි සහ තීරු ගණන් කරන්න.",
    "clocks": "ඔරලෝසු අතර විනාඩි පරතරය කීයද? ඔබේ ගණනයත් ලියන්න.",
    "pyramid": "ඉහළ ගඩොලේ අංකය ලැබුණේ කොහොමද? පහළ පේළිවලින් පෙන්වන්න.",
}


def comment_invitation(question):
    choices = question.get("choices", [])
    labels = question.get("option_labels") or [chr(65+i) for i in range(len(choices))]
    if len(choices) not in (3, 4) or len(labels) != len(choices):
        raise ValueError("Genuine quiz invitation requires valid choices")
    reply = ", ".join(f"({label})" if str(label).isdigit() else str(label)
                      for label in labels)
    hint = PROMPTS.get(
        question.get("puzzle_kind"),
        "ඔබ ඒ පිළිතුර තෝරාගත්තේ ඇයි? එක් හේතුවක් ලියන්න.")
    return clean_caption(
        f"ඔබේ පිළිතුර {reply} අතරින් තෝරන්න.\n"
        f"{hint}\n"
        "අදහස් දක්වන විට අනිත් අයගේ පිළිතුරුවලටත් ගෞරව කරන්න."
    )


def improve_facebook_caption(original, question):
    """Append substantive discussion question; keep the owned Blogger URL."""
    text = clean_caption(original)
    invitation = comment_invitation(question)
    # This is a genuine educational prompt, not a demand to comment for access.
    if invitation not in text:
        lines = text.splitlines()
        url_pos = next(
            (i for i,line in enumerate(lines)
             if line.strip().startswith("https://punchinanamaga.blogspot.com/")),
            len(lines)
        )
        lines[url_pos:url_pos] = ["", invitation, ""]
        text = clean_caption("\n".join(lines))
    return text


def get_approved_sponsor_url(environ=None):
    """Only a separate, explicitly approved, real Direct Link can be shown.

    The previously supplied bicea.org URL is a JavaScript source, NOT
    a SmartLink/Direct Link destination, and must never be inserted here.
    """
    env = os.environ if environ is None else environ
    if env.get("ADSTERRA_SPONSORED_LINK_ENABLED", "").lower() != "true":
        return None
    if env.get("ADSTERRA_AGE_APPROPRIATE_REVIEWED", "").lower() != "true":
        raise ValueError("Ad must be reviewed for this child-facing education site")
    url = env.get("ADSTERRA_DIRECT_LINK", "").strip()
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or
            parsed.username or parsed.password or
            any(ch.isspace() for ch in url) or
            parsed.hostname.lower() in {"bicea.org", "www.bicea.org"} or
            parsed.path.lower().endswith(".js")):
        raise ValueError("Expected a verified HTTPS Adsterra Direct Link, not an ad script URL")
    return url


def optional_sponsored_block(environ=None):
    """Optional separate ad beneath Blogger content, never in its answer link."""
    url = get_approved_sponsor_url(environ)
    if not url:
        return ""
    safe_url = html.escape(url, quote=True)
    return (
        '<aside class="punchi-sponsored" aria-label="දැන්වීම" '
        'style="margin:24px 0;padding:12px;border:1px solid #d4d4d4;">'
        '<p><strong>දැන්වීම / Sponsored</strong></p>'
        '<p>මෙය අධ්‍යාපනික ප්‍රශ්නයෙන් වෙන් වූ බාහිර අනුග්‍රාහක සබැඳියකි. '
        'ප්‍රශ්නයේ පිළිතුර බැලීමට මෙම සබැඳිය විවෘත කිරීම අවශ්‍ය නැහැ.</p>'
        '<a href="' + safe_url + '" rel="sponsored nofollow noopener noreferrer" '
        'target="_blank">අනුග්‍රාහක සබැඳිය විවෘත කරන්න</a>'
        '</aside>'
    )
