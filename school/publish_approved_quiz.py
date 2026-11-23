#!/usr/bin/env python3
"""Publish today's approved, picture-led Sinhala quiz to the authorized Page.

The picture, question and answer are identical to the daily Reel selection.
"""
import datetime as dt
import os
from pathlib import Path

from facebook_card import create_card
from crosspost import Crossposter
from blogger_link_safety import FACEBOOK_LANDING_URL
from visual_quiz import select, image_credit
from social_text import clean_caption


def main():
    day = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)).date()
    item = select(day)
    choices = "\n".join(f"{chr(65+i)}) {c}" for i, c in enumerate(item["choices"]))
    caption = (
        "පුංචි නැණ මඟ\nඅද පින්තූර ප්‍රශ්නය!\n\n"
        + item["q"] + "\n\n" + choices + "\n\n"
        + "පිළිතුර සිතා බලන්න. ඔබේ පිළිතුර A, B, C හෝ D ලෙස Comment කරන්න.\n\n"
        + "ඡායාරූපය: " + image_credit(item) + "\n\n"
        + f"තවත් නොමිලේ අධ්‍යාපනික ප්‍රශ්න: {FACEBOOK_LANDING_URL}\n"
        + "#PunchiNenaMaga #SinhalaPictureQuiz"
    )
    caption = clean_caption(caption)
    output = Path("school/output") / f"approved-visual-quiz-{day.isoformat()}.png"
    create_card(item, output)
    blog_url, fb_id = Crossposter().publish(
        question=item,
        title=f"පුංචි නැණ මඟ | {day.isoformat()} | අද පින්තූර ප්‍රශ්නය",
        media_kind="photo",
        media_path=output,
        caption=caption,
        image_info=item,
        version=os.getenv("FB_GRAPH_VERSION", "v27.0"))
    print("Crossposted approved photo quiz:", blog_url, fb_id)


if __name__ == "__main__":
    main()
