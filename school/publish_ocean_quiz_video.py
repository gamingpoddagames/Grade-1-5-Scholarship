#!/usr/bin/env python3
"""Daily Facebook Reel with exact screenshot-style Sinhala question and answer."""
import datetime as dt
import os
from pathlib import Path
from build_resources import video
from quiz_topics import select
from crosspost import Crossposter
from blogger_link_safety import FACEBOOK_LANDING_URL


def main():
    day = (dt.datetime.now(dt.timezone.utc) +
           dt.timedelta(hours=5, minutes=30)).date()
    question = select(day, offset=0)
    output = Path("school/output/daily-quiz-video")
    movie = video(output, [question], day)
    caption = ("අලුත් ප්‍රශ්නය: " + question["q"] + "\n\n" +
               "\n".join(f'{chr(65+i)}) {c}' for i, c in enumerate(question["choices"])) +
               "\n\nපිළිතුර සිතන්න. නිවැරදි පිළිතුර වීඩියෝවේ අවසානයේ!\n" +
               FACEBOOK_LANDING_URL + "\n#SinhalaQuiz #PunchiNenaMaga")
    (output / "caption.txt").write_text(caption, encoding="utf-8")
    blog_url, fb_id = Crossposter().publish(
        question=question,
        title=f"පුංචි නැණ මඟ | {day.isoformat()} | අලුත් ප්‍රශ්නය",
        media_kind="video",
        media_path=movie,
        caption=caption,
        version=os.getenv("FB_GRAPH_VERSION", "v27.0"))
    print("Crossposted matching daily video:", blog_url, fb_id)


if __name__ == "__main__":
    main()
