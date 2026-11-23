#!/usr/bin/env python3
"""Additive three-reel publisher; preserves all existing school workflows."""
import argparse
import datetime as dt
import html
import os
from pathlib import Path
from build_resources import video
from quiz_topics import select
from crosspost import Crossposter
from facebook_video import upload
from blogger_link_safety import FACEBOOK_LANDING_URL
from social_text import clean_caption

def run(day, output, publish=False):
    # Three different reviewed questions from the same curated daily bank.
    selected = [select(day, offset=i + 1) for i in range(3)]
    if len({q["q"] for q in selected}) != 3:
        raise RuntimeError("Daily reel questions repeated")
    crossposter = Crossposter() if publish else None
    for i, q in enumerate(selected, 1):
        folder = output / ("reel-" + str(i))
        # Render precisely the selected question, not an unrelated date-indexed one.
        video(folder, [q], day)
        # The shared renderer has already created synchronized Sinhala narration.
        movie = folder / "grade5-quiz.mp4"
        if not movie.is_file() or movie.stat().st_size < 1000:
            raise RuntimeError("MP4 render failed")
        title = f"පුංචි නැණ මඟ | {day.isoformat()} | ප්‍රශ්නය {i}"
        options = "".join(f"<li>{chr(65+j)}) {html.escape(str(choice))}</li>" for j,choice in enumerate(q["choices"]))
        body = (f"<h2>{html.escape(q['q'])}</h2><ol>{options}</ol>"
                "<p>පිළිතුර තෝරාගෙන ඔබේ දැනුම පරීක්ෂා කරන්න.</p>"
                f"<details><summary>නිවැරදි පිළිතුර බලන්න</summary><p>{html.escape(str(q['choices'][q['answer']]))}</p>"
                f"<p>{html.escape(q['explanation'])}</p></details>"
                "<p>මෙය ස්වාධීන අධ්‍යාපනික පුහුණු ප්‍රශ්නයකි. නිල විභාග ප්‍රශ්නයක් නොවේ.</p>"
                "<p>පුංචි නැණ මඟ වෙතින් නොමිලේ අධ්‍යාපනික අන්තර්ගතය ලබාගන්න.</p>")
        (folder / "blogger-preview.html").write_text(body, encoding="utf-8")
        print("Rendered reel", i, movie)
        if not publish:
            continue
        caption = (
            q["q"] + "\n\n" +
            "\n".join(f'{chr(65+j)}) {choice}' for j, choice in enumerate(q["choices"])) +
            "\n\nපිළිතුර සිතන්න. වීඩියෝව අවසානයේ නිවැරදි පිළිතුර!\n" +
            FACEBOOK_LANDING_URL)
        caption = clean_caption(caption)
        blog_url, fb_id = crossposter.publish(
            question=q, title=title, media_kind="video",
            media_path=movie, caption=caption,
            version=os.getenv("FB_GRAPH_VERSION", "v27.0"))
        print("Crossposted reel", i, blog_url, fb_id)

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--publish",action="store_true")
    p.add_argument("--date")
    p.add_argument("--output",default="school/output/three-reels")
    args=p.parse_args()
    today=dt.date.fromisoformat(args.date) if args.date else (dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=5,minutes=30)).date()
    run(today,Path(args.output),args.publish)
