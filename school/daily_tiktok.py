"""Mirror the exact daily educational content to the verified TikTok account."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageOps
from gtts import gTTS
from brand_assets import font
from font_safety import draw_mixed
from sinhala_speech import expand_currency
from quiz_reel_renderer import fit_lines, write_lines, audio_seconds
from tiktok_publish import publish_movie

def poster_video(media, title, narration, answer, folder):
    canvas = Image.new("RGB", (720,1280), "#0b2444")
    if media:
        with Image.open(media) as source:
            picture = ImageOps.contain(source.convert("RGB"), (680,940))
        canvas.paste(picture, ((720-picture.width)//2, 80))
    draw = ImageDraw.Draw(canvas)
    face, lines = fit_lines(draw, "පුංචි නැණ මඟ", (38,34,30), 650, 1)
    write_lines(draw, lines, face, 30, 20, 45, "#ffffff")
    if not media:
        face, lines = fit_lines(draw, title, (42,38,34,30), 650, 5)
        write_lines(draw, lines, face, 30, 300, 60, "#ffffff")
    face, lines = fit_lines(draw, "තවත් දැනුමට අප හා එක්වන්න", (30,28,26), 650, 2)
    write_lines(draw, lines, face, 30, 1160, 40, "#ffffff")
    frame = folder / "poster.png"
    canvas.save(frame)
    audio = folder / "poster.mp3"
    gTTS(text=expand_currency(narration),lang="si",timeout=(8,30)).save(str(audio))
    duration = audio_seconds(audio) + 5
    movie = folder / "poster.mp4"
    subprocess.run(["ffmpeg","-y","-loop","1","-i",str(frame),"-i",str(audio),"-af","apad","-t",str(duration),"-r","24","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart",str(movie)],check=True,timeout=240)
    return movie

def mirror_slot(slot, day, folder, title, caption, question, media, original, blog):
    folder = Path(folder) / "tiktok"
    folder.mkdir(parents=True, exist_ok=True)
    text = title + "\n" + (question["q"] if question else caption) + "\n" + blog + "\n#Sinhala #Education"
    if question and question.get("image_credit"):
        text += "\n" + question["image_credit"]
        from visual_quiz import image_page
        text += "\n" + image_page(question)
    if original:
        movie = original
    else:
        narration = question["q"] + " පිළිතුර සිතන්න." if question else caption
        movie = poster_video(media, title, narration, None, folder)
    return publish_movie(movie, text, day, slot, folder)
