#!/usr/bin/env python3
"""Daily rotating Sinhala quiz reel: one question controls visuals, voice and caption."""
import datetime as dt
import os
import subprocess
from pathlib import Path
from gtts import gTTS
from build_resources import all_questions, video
from facebook_video import upload
from blogger_link_safety import FACEBOOK_LANDING_URL

def choose(day):
    bank = [q for q in all_questions() if len(q.get("choices", [])) == 4]
    # Start from a different question every day; never hard-code the ocean/Mars example.
    index = (day - dt.date(2026, 11, 22)).days % len(bank)
    return bank[index]

def main():
    day = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5,minutes=30)).date()
    q = choose(day)
    output = Path("school/output/daily-quiz-video")
    output.mkdir(parents=True, exist_ok=True)
    # The existing renderer selects index zero when given a single question.
    video(output, [q], day)
    correct = str(q["choices"][q["answer"]])
    narration = (
        f'{q["q"]} ' +
        " ".join(f'{choice} ද?' for choice in q["choices"]) +
        f' පිළිතුර හිතන්න. නිවැරදි පිළිතුර, {correct}.'
    )
    audio = output / "sinhala-voice.mp3"
    gTTS(text=narration, lang="si", slow=False, timeout=(5,30)).save(str(audio))
    original = output / "grade5-quiz.mp4"
    narrated = output / "daily-quiz-narrated.mp4"
    # Extend video if necessary to fit narration, never truncate the spoken answer.
    probe = subprocess.check_output([
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(audio)
    ],text=True)
    duration = max(12.0, float(probe.strip()) + 1.5)
    stretch = duration / 9.0
    subprocess.run([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",str(original),"-i",str(audio),
        "-filter_complex",f"[0:v]setpts=PTS*{stretch:.6f}[v]",
        "-map","[v]","-map","1:a","-c:v","libx264","-preset","veryfast",
        "-c:a","aac","-b:a","128k","-pix_fmt","yuv420p",
        "-t",str(duration),"-movflags","+faststart",str(narrated)
    ],check=True)
    caption = (f'{q["q"]}\n' +
               "\n".join(f'{chr(65+i)}) {choice}' for i,choice in enumerate(q["choices"])) +
               f'\nපිළිතුර හිතන්න!\n{FACEBOOK_LANDING_URL} #SinhalaQuiz #PunchiNenaMaga')
    (output / "question.txt").write_text(caption + f'\nAnswer: {correct}',encoding="utf-8")
    if not os.getenv("FB_PAGE_ID") or not os.getenv("FB_PAGE_ACCESS_TOKEN"):
        raise RuntimeError("Missing Facebook Page credentials; rendered but NOT published")
    upload(narrated,os.environ["FB_PAGE_ID"],os.environ["FB_PAGE_ACCESS_TOKEN"],
           os.getenv("FB_GRAPH_VERSION","v27.0"),
           title=f'පුංචි නැණ මඟ | {day.isoformat()} | අලුත් ප්‍රශ්නය',
           description=caption)

if __name__ == "__main__":
    main()
