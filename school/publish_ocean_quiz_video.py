#!/usr/bin/env python3
"""Render and publish a new original space quiz as a matching Facebook video."""
import datetime as dt
import os
import subprocess
from gtts import gTTS
from pathlib import Path
from build_resources import video
from facebook_video import upload
from blogger_link_safety import FACEBOOK_LANDING_URL

QUESTION = {
    "grade": 5,
    "topic": "සාමාන්‍ය දැනුම",
    "q": "රතු ග්‍රහලෝකය ලෙස හඳුන්වන්නේ කුමන ග්‍රහලෝකයද?",
    "choices": ["සිකුරු", "බ්‍රහස්පති", "අඟහරු", "සෙනසුරු"],
    "answer": 2,
    "explanation": "රතු ග්‍රහලෝකය ලෙස හඳුන්වන්නේ අඟහරු ග්‍රහලෝකයයි."
}
if __name__ == "__main__":
    output = Path("school/output/red-planet-quiz-video")
    video(output, [QUESTION], dt.date(2026, 11, 22))
    # Use the same Sinhala gTTS voice engine as the SL News 247 project.
    narration = (
        "රතු ග්‍රහලෝකය ලෙස හඳුන්වන්නේ කුමන ග්‍රහලෝකයද? "
        "සිකුරු ද? බ්‍රහස්පති ද? අඟහරු ද? සෙනසුරු ද? "
        "පිළිතුර හිතන්න. නිවැරදි පිළිතුර, අඟහරු ග්‍රහලෝකයයි."
    )
    audio = output / "sinhala-voice.mp3"
    gTTS(text=narration, lang="si", slow=False, timeout=(5,30)).save(str(audio))
    original = output / "grade5-quiz.mp4"
    narrated = output / "red-planet-quiz-narrated.mp4"
    # Preserve the original question/answer frames and fit narration completely.
    subprocess.run([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",str(original),"-i",str(audio),
        "-filter_complex","[0:v]setpts=PTS*3[v]",
        "-map","[v]","-map","1:a","-c:v","libx264","-preset","veryfast",
        "-c:a","aac","-b:a","128k","-pix_fmt","yuv420p",
        "-shortest","-movflags","+faststart",str(narrated)
    ],check=True)
    page = os.getenv("FB_PAGE_ID")
    token = os.getenv("FB_PAGE_ACCESS_TOKEN")
    if not page or not token:
        raise RuntimeError("Missing Facebook Page credentials: video generated but NOT published")
    upload(
        narrated, page, token,
        os.getenv("FB_GRAPH_VERSION", "v27.0"),
        title="පුංචි නැණ මඟ | රතු ග්‍රහලෝකය",
        description=("රතු ග්‍රහලෝකය ලෙස හඳුන්වන්නේ කුමන ග්‍රහලෝකයද? පිළිතුර සිතන්න! "
                     "A) සිකුරු B) බ්‍රහස්පති C) අඟහරු D) සෙනසුරු. "
                     f"තවත් ප්‍රශ්න: {FACEBOOK_LANDING_URL} #SinhalaQuiz #PunchiNenaMaga")
    )
