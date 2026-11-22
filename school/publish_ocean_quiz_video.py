#!/usr/bin/env python3
"""Render and publish the approved ocean quiz as a matching Facebook video."""
import datetime as dt
import os
from pathlib import Path
from build_resources import video
from facebook_video import upload
from blogger_link_safety import FACEBOOK_LANDING_URL

QUESTION = {
    "grade": 5,
    "topic": "සාමාන්‍ය දැනුම",
    "q": "ලෝකයේ විශාලතම සාගරය කුමක්ද?",
    "choices": ["අත්ලාන්තික් සාගරය", "පැසිෆික් සාගරය", "ඉන්දියානු සාගරය", "ආක්ටික් සාගරය"],
    "answer": 1,
    "explanation": "ලෝකයේ විශාලතම සාගරය පැසිෆික් සාගරයයි."
}
if __name__ == "__main__":
    output = Path("school/output/ocean-quiz-video")
    video(output, [QUESTION], dt.date(2026, 11, 22))
    page = os.getenv("FB_PAGE_ID")
    token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    if not page or not token:
        raise RuntimeError("Missing Facebook Page credentials: video generated but NOT published")
    upload(
        output / "grade5-quiz.mp4", page, token,
        os.getenv("FB_GRAPH_VERSION", "v27.0"),
        title="පුංචි නැණ මඟ | ලෝකයේ විශාලතම සාගරය",
        description=("ලෝකයේ විශාලතම සාගරය කුමක්ද? පිළිතුර සිතන්න! "
                     "A) අත්ලාන්තික් B) පැසිෆික් C) ඉන්දියානු D) ආක්ටික්. "
                     f"තවත් ප්‍රශ්න: {FACEBOOK_LANDING_URL} #SinhalaQuiz #PunchiNenaMaga")
    )
