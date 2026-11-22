#!/usr/bin/env python3
"""Publish today's approved, picture-led Sinhala quiz to the authorized Page.

The picture, question and answer are identical to the daily Reel selection.
"""
import datetime as dt
import os
from pathlib import Path

from facebook_card import create_card, publish
from blogger_link_safety import FACEBOOK_LANDING_URL
from visual_quiz import select, image_credit


def main():
    day = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)).date()
    item = select(day)
    choices = "\n".join(f"{chr(65+i)}) {c}" for i, c in enumerate(item["choices"]))
    caption = (
        "පුංචි නැණ මඟ | අද පින්තූර ප්‍රශ්නය!\n\n"
        + item["q"] + "\n\n" + choices + "\n\n"
        + "පිළිතුර සිතා බලන්න. ඔබේ පිළිතුර A, B, C හෝ D ලෙස Comment කරන්න.\n\n"
        + "ඡායාරූපය: " + image_credit(item) + "\n\n"
        + f"තවත් නොමිලේ අධ්‍යාපනික ප්‍රශ්න: {FACEBOOK_LANDING_URL}\n"
        + "#PunchiNenaMaga #SinhalaPictureQuiz"
    )
    output = Path("school/output") / f"approved-visual-quiz-{day.isoformat()}.png"
    create_card(item, output)
    if not os.getenv("FB_PAGE_ID") or not os.getenv("FB_PAGE_ACCESS_TOKEN"):
        raise RuntimeError("Facebook Page credentials unavailable: picture quiz generated but NOT published")
    publish(output, caption)


if __name__ == "__main__":
    main()
