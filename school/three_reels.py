#!/usr/bin/env python3
"""Additive three-reel publisher; preserves all existing school workflows."""
import argparse
import datetime as dt
import html
import os
from pathlib import Path
from build_resources import all_questions, video
from blogger_publisher import access_token_from_env, authenticate_blog, list_existing, request_json, API, EXPECTED_BLOG_ID
from facebook_video import upload
from blogger_link_safety import FACEBOOK_LANDING_URL

def run(day, output, publish=False):
    questions = all_questions()
    grade5 = [q for q in questions if q["grade"] == 5]
    if len(grade5) < 3:
        raise RuntimeError("Need at least three Grade 5 questions")
    # Distinct, deterministic rotating questions; reruns remain reproducible.
    start = day.toordinal() % len(grade5)
    selected = [grade5[(start + i * 7) % len(grade5)] for i in range(3)]
    if len({q["q"] for q in selected}) != 3:
        raise RuntimeError("Daily questions are not unique")
    blogger_token = None
    existing = {}
    if publish:
        blogger_token = access_token_from_env()
        authenticate_blog(blogger_token)
        existing = list_existing("posts", blogger_token)
    for i, q in enumerate(selected, 1):
        folder = output / ("reel-" + str(i))
        # Existing renderer chooses question from date index; pass a matching day.
        target_idx = grade5.index(q)
        offset = (target_idx - day.toordinal()) % len(grade5)
        render_day = day + dt.timedelta(days=offset)
        video(folder, questions, render_day)
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
        if not os.getenv("FB_PAGE_ID") or not os.getenv("FB_PAGE_ACCESS_TOKEN"):
            raise RuntimeError("Missing Facebook Page credentials; publishing stopped")
        # Publish Blogger content first; never overwrite an existing post.
        if title not in existing:
            result = request_json(f"{API}/blogs/{EXPECTED_BLOG_ID}/posts?isDraft=false",
                access_token=blogger_token, method="POST",
                payload={"kind":"blogger#post","blog":{"id":EXPECTED_BLOG_ID},
                         "title":title,"content":body,"labels":["සිංහල ප්‍රශ්න","ශිෂ්‍යත්ව"]})
            if not result.get("id"):
                raise RuntimeError("Blogger did not confirm post")
            print("Blogger post published:", result.get("url","(URL unavailable)"))
            existing[title] = {"id":str(result["id"]),"status":"live"}
        else:
            print("Blogger post already exists; preserving:",title)
        upload(movie, os.environ["FB_PAGE_ID"], os.environ["FB_PAGE_ACCESS_TOKEN"],
               os.getenv("FB_GRAPH_VERSION","v27.0"), title=title,
               description=f"{q['q']} පිළිතුර සිතා බලන්න. {FACEBOOK_LANDING_URL}")
if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--publish",action="store_true")
    p.add_argument("--date")
    p.add_argument("--output",default="school/output/three-reels")
    args=p.parse_args()
    today=dt.date.fromisoformat(args.date) if args.date else (dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=5,minutes=30)).date()
    run(today,Path(args.output),args.publish)
