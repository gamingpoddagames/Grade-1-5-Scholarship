#!/usr/bin/env python3
"""Original colourful Grade-5 number-wheel puzzle posters for Blogger and Facebook.

Pillow drawings (not copied screenshots), verified deterministic answer key,
Sinhala-shaped type, no paid AI/stock-image APIs. Public card never reveals answer.
"""
import argparse
import datetime as dt
import json
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from brand_assets import font, latin_font
from font_safety import draw_mixed, mixed_width, check_caption
from social_text import clean_caption, clean_quiz_lines
from diverse_puzzles import make_diverse, render_diverse_poster
from blogger_link_safety import FACEBOOK_LANDING_URL
from crosspost import Crossposter, article_content, today_in_sri_lanka

W, H = 1080, 1350
START = dt.date(2026, 11, 22)


def compute(left, top, right, rule=0):
    """Four deterministic puzzle families; every answer is verified by code."""
    if rule == 0:
        return left * right * (top + 1)
    if rule == 1:
        return (left + right) * (top + 2)
    if rule == 2:
        return left * top + right * right
    if rule == 3:
        return (left + top) * right + top
    raise ValueError("Unknown puzzle rule")


RULE_TEXTS = [
    "වම × දකුණ × (ඉහළ + 1)",
    "(වම + දකුණ) × (ඉහළ + 2)",
    "වම × ඉහළ + දකුණ × දකුණ",
    "(වම + ඉහළ) × දකුණ + ඉහළ",
]


def worked_step(left, top, right, rule):
    if rule == 0:
        return f"{left} × {right} × ({top} + 1)"
    if rule == 1:
        return f"({left} + {right}) × ({top} + 2)"
    if rule == 2:
        return f"{left} × {top} + {right} × {right}"
    if rule == 3:
        return f"({left} + {top}) × {right} + {top}"
    raise ValueError("Unknown puzzle rule")


def make_puzzle(day, variant=0):
    """Variant zero is the daily post; variant one is a distinct one-off bonus."""
    if isinstance(day, str):
        day = dt.date.fromisoformat(day)
    day_index = (day - START).days
    if day_index < 0:
        raise ValueError("Date predates the original puzzle series")
    if variant not in (0, 1, 2, 3):
        raise ValueError("Unsupported puzzle post variant")
    if variant in (2, 3) or day >= dt.date(2026, 11, 24):
        return make_diverse(day, variant=variant)
    # Old posts are kept unchanged; new posts use six genuinely different
    # mathematical ideas and original layouts, not another number-wheel image.
    # The bonus uses an independent deterministic sequence rather than
    # repeating today's already-published standard number-wheel puzzle.
    serial = day_index if variant == 0 else 1000 + day_index
    rule = 0 if serial == 1 else serial % len(RULE_TEXTS)

    if serial == 1:  # Launch puzzle: 40, 36, 30, ? with answer 80.
        triples = [(2, 3, 5), (4, 2, 3), (3, 4, 2), (5, 3, 4)]
    else:
        rng = random.Random(20261122 + serial * 1291)
        triples = []
        seen_answers = set()
        attempts = 0
        while len(triples) < 4 and attempts < 800:
            attempts += 1
            triple = (rng.randint(2, 6), rng.randint(2, 5), rng.randint(2, 6))
            value = compute(*triple, rule=rule)
            if triple in triples or value in seen_answers or value > 210:
                continue
            triples.append(triple)
            seen_answers.add(value)
        if len(triples) != 4:
            raise RuntimeError("Could not generate four different valid number wheels")
    wheels = [(left, top, right, compute(left, top, right, rule=rule))
              for left, top, right in triples]
    correct = wheels[3][3]
    delta = max(6, correct // 4)
    distractors = [correct - delta, correct, correct + delta]
    shift = (serial - 1) % 3
    options = distractors[shift:] + distractors[:shift]
    if len(set(options)) != 3 or any(n <= 0 for n in options):
        raise AssertionError("Puzzle distractors must be positive and unique")
    shown_wheels = [[l, t, r, str(b) if i != 3 else "?"]
                    for i, (l, t, r, b) in enumerate(wheels)]
    explanation = (
        "අද ප්‍රශ්නයේ අදහස් කළ රටාව: " + RULE_TEXTS[rule] +
        " = පහළ අංකය.\n" +
        "\n".join(
            f"{i}. {worked_step(l, t, r, rule)} = {value}"
            for i, (l, t, r, value) in enumerate(wheels, 1)) +
        f"\nඒ නිසා නිවැරදි පිළිතුර {correct} යි."
    )
    return {
        "grade": 5,
        "topic": "බුද්ධි පරීක්ෂණය",
        "q": "වට හතරේ සංඛ්‍යා රටාව හඳුනාගෙන ? වෙනුවට එන අංකය සොයන්න.",
        "choices": [str(v) for v in options],
        "option_labels": ["1", "2", "3"],
        "answer": options.index(correct),
        "puzzle_circles": shown_wheels,
        "explanation": explanation,
        "learning_notes": [
            "මෙය 5 ශ්‍රේණිය ශිෂ්‍යත්ව බුද්ධි පරීක්ෂණයට සූදානම් වන දරුවන්ට රටාව හඳුනාගැනීම, ගුණ කිරීම සහ ගැටලුවක් පියවරෙන් පියවර විසඳීම පුහුණු කරන මුල් නිර්මාණ අභ්‍යාසයකි.",
            "මුලින්ම පිළිතුර නොබලා පළමු වට තුනේ ඉහළ, වම් සහ දකුණු අංක අතර සමාන සම්බන්ධය සොයන්න. ඔබ සොයාගත් නියමය වට තුනටම ගැළපෙනවාදැයි තහවුරු කරන්න.",
            "මෙවර විසඳුමේ අදහස් කළ රටාව: " + RULE_TEXTS[rule] + ". අවසන් වටයටත් එම නියමයම යොදන්න. පිළිතුර සොයාගත් ක්‍රමය දරුවාට වචනවලින් පැහැදිලි කරන්න කියන්න."
        ],
        "question_number": day_index + 28 + variant,
        "variant": "bonus" if variant else "daily",
        "rule_index": rule,
        "date": day.isoformat(),
        "format": "illustrated_math_puzzle",
    }


def _gradient():
    image = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(image)
    for y in range(H):
        t = y / H
        r = int(13 + 63 * t)
        g = int(45 - 25 * t)
        b = int(161 + 38 * math.sin(t * math.pi))
        d.line((0, y, W, y), fill=(r, g, b))
    # Colourful, original vector-style glow; no third-party photographs.
    effects = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(effects)
    g.ellipse((-260, 430, 230, 890), fill=(0, 218, 255, 125))
    g.ellipse((850, 70, 1270, 590), fill=(252, 27, 240, 115))
    g.ellipse((250, 890, 900, 1480), fill=(142, 0, 232, 80))
    effects = effects.filter(ImageFilter.GaussianBlur(85))
    return Image.alpha_composite(image.convert("RGBA"), effects).convert("RGB")


def _center_si(d, text, y, size, color, *, max_width=970, outline=True):
    face = font(size, True)
    while mixed_width(d, text, face) > max_width and size > 28:
        size -= 2
        face = font(size, True)
    if mixed_width(d, text, face) > max_width:
        raise ValueError("Sinhala line would overflow poster")
    x = (W - mixed_width(d, text, face)) // 2
    if outline:
        for dx, dy in ((-3, -3), (-3, 3), (3, -3), (3, 3), (4, 5)):
            draw_mixed(d, (x + dx, y + dy), text, face, "#071238")
    draw_mixed(d, (x, y), text, face, color)


def _doodles(d):
    # Math motifs at the margins, never covering the question or wheels.
    cyan, pink = "#44d7fc", "#cb67ee"
    for px, py in ((35, 95), (1010, 180), (54, 720), (1040, 1030)):
        d.arc((px - 44, py - 44, px + 44, py + 44),
              195, 350, fill=cyan, width=4)
    for (x, y, size, colour) in ((63, 366, 29, cyan), (1023, 660, 24, pink),
                                 (70, 1110, 24, cyan), (1013, 925, 28, cyan)):
        d.line((x-size, y, x+size, y), fill=colour, width=6)
        d.line((x, y-size, x, y+size), fill=colour, width=6)
    d.arc((890, 12, 1065, 175), 184, 345, fill=pink, width=6)
    d.line((35, 1100, 105, 1030, 120, 1120), fill=cyan, width=5)


def _wheel(d, cx, cy, radius, wheel):
    left, top, right, bottom = wheel
    bounds = (cx-radius, cy-radius, cx+radius, cy+radius)
    d.ellipse((bounds[0]-10, bounds[1]+10, bounds[2]+10, bounds[3]+20),
              fill="#050f2b")
    d.pieslice(bounds, 180, 240, fill="#ffffff")
    d.pieslice(bounds, 240, 300, fill="#ffe13b")
    d.pieslice(bounds, 300, 360, fill="#ffffff")
    d.pieslice(bounds, 0, 180, fill="#ffffff")
    d.ellipse(bounds, outline="#0b1642", width=10)
    d.line((cx-radius+3, cy, cx+radius-3, cy), fill="#0b1642", width=8)
    for angle in (240, 300):
        rad = math.radians(angle)
        d.line((cx, cy, cx+radius*math.cos(rad),
                cy+radius*math.sin(rad)), fill="#0b1642", width=8)
    face = latin_font(70, True)
    val = "#080f36"
    for x, y, v in (
        (cx-radius*.60, cy-radius*.23, left),
        (cx, cy-radius*.61, top),
        (cx+radius*.60, cy-radius*.23, right),
        (cx, cy+radius*.44, bottom)
    ):
        d.text((round(x), round(y)), str(v), font=face, fill=val, anchor="mm")


def poster(question, destination):
    if question.get("puzzle_kind"):
        return render_diverse_poster(question, destination)
    if len(question["puzzle_circles"]) != 4:
        raise ValueError("Need exactly four puzzle wheels")
    im = _gradient()
    d = ImageDraw.Draw(im)
    _doodles(d)
    d.rounded_rectangle((337, 29, 743, 98), radius=26,
                        fill="#081d7c", outline="#54dcff", width=4)
    _center_si(d, "ප්‍රශ්න අංක " + str(question["question_number"]), 37,
               45, "#ffffff", max_width=390)
    _center_si(d, "බුද්ධි පරීක්ෂණ ගැටලුව", 124, 67,
               "#ffeb37", max_width=1020)
    _center_si(d, "හිස්තැනට ගැළපෙන අංකය සොයන්න!", 224,
               42, "#ffffff", max_width=970)
    _wheel(d, 285, 462, 160, question["puzzle_circles"][0])
    _wheel(d, 795, 462, 160, question["puzzle_circles"][1])
    _wheel(d, 285, 827, 160, question["puzzle_circles"][2])
    _wheel(d, 795, 827, 160, question["puzzle_circles"][3])
    for i, value in enumerate(question["choices"]):
        x = 65 + 335 * i
        d.rounded_rectangle((x, 1026, x+285, 1117), radius=20,
                            fill="#07123d", outline="#ffd944", width=4)
        d.text((x+143, 1069), f"({i+1}) {value}",
               fill="#ffffff", font=latin_font(59, True), anchor="mm")
    d.rounded_rectangle((54, 1168, 1026, 1264), radius=28,
                        fill="#070d44", outline="#f0ca41", width=4)
    _center_si(d, "ඔබේ පිළිතුර කමෙන්ට් කරන්න!", 1183, 56,
               "#ffffff", max_width=920)
    _center_si(d, "පුංචි නැණ මඟ", 1282, 33,
               "#ffd848", max_width=600, outline=False)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    im.save(destination, optimize=True)
    if im.size != (1080, 1350) or destination.stat().st_size < 20000:
        raise RuntimeError("Invalid final puzzle artwork")
    return destination


def facebook_caption(question):
    labels = question["option_labels"]
    opts = "\n".join(
        f"({label}) {answer}" for label, answer in zip(labels, question["choices"]))
    text = (
        clean_quiz_lines(5, "බුද්ධි පරීක්ෂණ ගැටලුව", question["question_number"]) + "\n\n"
        question["q"] + "\n\n" +
        opts + "\n\n"
        "ඔබ තෝරන අංකය (1), (2) හෝ (3) ලෙස comment කරන්න.\n"
        "නිවැරදි පිළිතුර සහ පියවරෙන් පියවර විසඳුම බලන්න:\n" +
        FACEBOOK_LANDING_URL +
        "\n#Grade5Scholarship #SinhalaMaths #PunchiNenaMaga"
    )
    import unicodedata
    text = clean_caption(text)
    check_caption(text)
    return text


def generate(day, outdir, variant=0):
    item = make_puzzle(day, variant=variant)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    graphic = poster(item, outdir/"puzzle-poster.png")
    (outdir/"quiz.json").write_text(
        json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir/"caption.txt").write_text(
        facebook_caption(item), encoding="utf-8")
    (outdir/"blogger-preview.html").write_text(
        article_content(item, media_kind="photo"), encoding="utf-8")
    print("Puzzle preview created:", graphic)
    return item, graphic


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD in Asia/Colombo")
    parser.add_argument("--output", default="school/output/logic-puzzle")
    parser.add_argument("--publish", action="store_true",
                        help="Publish paired Blogger article and Facebook photo")
    parser.add_argument("--bonus", action="store_true",
                        help="New distinct puzzle even when today's daily quiz was posted")
    parser.add_argument("--new-style", action="store_true",
                        help="First new-format example (#31)")
    parser.add_argument("--fresh-grid", action="store_true",
                        help="A different original 3x3 grid puzzle (#32), not another wheel or dot post")
    args = parser.parse_args()
    day = dt.date.fromisoformat(args.date) if args.date else today_in_sri_lanka()
    if sum([args.bonus, args.new_style, args.fresh_grid]) > 1:
        raise ValueError("Select only one extra puzzle variant")
    if args.output == "school/output/logic-puzzle":
        if args.fresh_grid:
            args.output = "school/output/logic-puzzle-fresh-grid"
        elif args.new_style:
            args.output = "school/output/logic-puzzle-new-style"
        elif args.bonus:
            args.output = "school/output/logic-puzzle-bonus"
    variant = 3 if args.fresh_grid else 2 if args.new_style else int(args.bonus)
    item, graphic = generate(day, args.output, variant=variant)
    if not args.publish:
        print("PREVIEW ONLY: no Blogger or Facebook posts sent")
        return
    kind = ("නව 3x3 සංඛ්‍යා ගැටලුව" if args.fresh_grid else
            "නව ආකෘතියේ බුද්ධි පරීක්ෂණය" if args.new_style else
            "අමතර බුද්ධි පරීක්ෂණය" if args.bonus else "බුද්ධි පරීක්ෂණ ගැටලුව")
    title = (f"පුංචි නැණ මඟ | {day.isoformat()} | "
             f"{kind} {item['question_number']}")
    blog, fb_id = Crossposter().publish(
        question=item, title=title, media_kind="photo",
        media_path=graphic, caption=facebook_caption(item),
        version=os.getenv("FB_GRAPH_VERSION", "v27.0"))
    print("Logic puzzle Blogger:", blog)
    print("Logic puzzle Facebook photo ID:", fb_id)


if __name__ == "__main__":
    main()
