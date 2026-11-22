#!/usr/bin/env python3
"""Screenshot-style Sinhala quiz reels: navy card, four choices, thinking, answer.

The exact question passed in controls the on-screen text, narration, and caption.
No off-topic pictures, unrelated image downloads, or fixed example questions.
"""
from pathlib import Path
import json
import subprocess
from PIL import Image, ImageDraw
from brand_assets import font, latin_font
from font_safety import draw_mixed, mixed_width
from gtts import gTTS

WIDTH, HEIGHT = 1080, 1920
NAVY = "#0b2444"
PANEL = "#17385c"
OPTION = "#27527c"
WHITE = "#f5fbff"
CYAN = "#84d5dc"
YELLOW = "#f1c36d"
GREEN = "#a8efc1"


def validate(question):
    if not isinstance(question, dict):
        raise ValueError("Expected a quiz question")
    choices = question.get("choices", [])
    answer = question.get("answer")
    if (not question.get("q") or not isinstance(choices, list)
            or len(choices) != 4 or not isinstance(answer, int)
            or not 0 <= answer < 4 or any(not str(c).strip() for c in choices)):
        raise ValueError("Quiz needs a question, four choices and an answer index 0-3")
    return question


def lines(draw, text, face, max_width):
    """Sinhala-shaped wrapping: never allow text to overrun its card."""
    result, line = [], ""
    for word in str(text).split():
        candidate = (line + " " + word).strip()
        if mixed_width(draw, candidate, face) <= max_width:
            line = candidate
        else:
            if line:
                result.append(line)
            line = word
            if mixed_width(draw, line, face) > max_width:
                return None
    if line:
        result.append(line)
    return result


def fit_lines(draw, text, sizes, max_width, max_lines):
    for size in sizes:
        face = font(size, True)
        result = lines(draw, text, face, max_width)
        if result is not None and len(result) <= max_lines:
            return face, result
    raise ValueError("Quiz text too long for mobile-safe screenshot layout")


def write_lines(draw, textlines, face, x, y, gap, fill):
    for line in textlines:
        draw_mixed(draw, (x, y), line, face, fill)
        y += gap


def make_frame(question, path, reveal):
    question = validate(question)
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((50, 95, 1030, 1835), radius=36, fill=PANEL)
    grade = int(question.get("grade", 5))
    heading = (f"{grade} ශ්‍රේණිය - ශිෂ්‍යත්ව ප්‍රශ්නය" if grade == 5
               else f"{grade} ශ්‍රේණිය - අලුත් ප්‍රශ්නය")
    face, heading_lines = fit_lines(d, heading, (43, 39, 36), 850, 2)
    write_lines(d, heading_lines, face, 104, 150, 60, CYAN)

    qface, question_lines = fit_lines(
        d, question["q"], (63, 59, 55, 51, 47, 43, 39), 855, 4)
    write_lines(d, question_lines, qface, 105, 440, qface.size + 34, WHITE)

    for i, choice in enumerate(question["choices"]):
        top = 815 + i * 124
        chosen = reveal and i == question["answer"]
        d.rounded_rectangle(
            (95, top, 984, top + 106), radius=17,
            fill="#198268" if chosen else OPTION)
        option_text = f"{chr(65+i)}) {choice}"
        optface, option_lines = fit_lines(
            d, option_text, (47, 44, 41, 38, 35, 32), 795, 1)
        write_lines(d, option_lines, optface, 137, top + 27, 58, WHITE)

    if reveal:
        correct = f'{chr(65 + question["answer"])}) {question["choices"][question["answer"]]}'
        result = "නිවැරදි පිළිතුර: " + correct
        answer_face, answer_lines = fit_lines(
            d, result, (50, 46, 42, 38, 34, 30), 850, 2)
        write_lines(d, answer_lines, answer_face,
                    110, 1460, answer_face.size + 28, GREEN)
    else:
        draw_mixed(d, (110, 1475), "පිළිතුර සිතන්න...", font(53, True), YELLOW)

    draw_mixed(d, (110, 1730), "පුංචි නැණ මඟ", font(36, True), CYAN)
    d.text((110, 1790), "Grade 1-5 | Sinhala Quiz",
           font=latin_font(25), fill="#aac3dd")
    image.save(path, optimize=True)


def audio_seconds(path):
    output = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True)
    value = float(output.strip())
    if not 0.1 < value < 120:
        raise RuntimeError("Unexpected Sinhala narration duration")
    return value


def render_quiz_video(question, outdir):
    """Return the generated MP4. Render source question exactly, no reselection."""
    question = validate(question)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    qtext = (str(question["q"]) + " " +
             " ".join(str(choice) + "." for choice in question["choices"]) +
             " පිළිතුර සිතන්න.")
    correct = str(question["choices"][question["answer"]])
    answer_text = "නිවැරදි පිළිතුර, " + correct + "."
    first = outdir / "question-voice.mp3"
    second = outdir / "answer-voice.mp3"
    gTTS(text=qtext, lang="si", slow=False, timeout=(5, 30)).save(str(first))
    gTTS(text=answer_text, lang="si", slow=False, timeout=(5, 30)).save(str(second))
    question_duration = audio_seconds(first) + 3.0
    answer_duration = audio_seconds(second) + 1.5
    make_frame(question, outdir / "frame-0.png", False)
    make_frame(question, outdir / "frame-1.png", True)
    (outdir / "frames.txt").write_text(
        f"file 'frame-0.png'\nduration {question_duration:.4f}\n"
        f"file 'frame-1.png'\nduration {answer_duration:.4f}\n"
        "file 'frame-1.png'\n", encoding="utf-8")
    output = outdir / "grade5-quiz.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(outdir / "frames.txt"),
        "-i", str(first), "-i", str(second),
        "-filter_complex",
        "[1:a]aformat=sample_rates=44100:channel_layouts=mono[q];"
        "anullsrc=r=44100:cl=mono,atrim=duration=3[s];"
        "[2:a]aformat=sample_rates=44100:channel_layouts=mono[a];"
        "[q][s][a]concat=n=3:v=0:a=1[all];"
        "[all]apad=pad_dur=1.5[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-vf", "fps=24,format=yuv420p",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p",
        "-t", str(question_duration + answer_duration),
        "-movflags", "+faststart", str(output)
    ], check=True, timeout=240)
    if not output.exists() or output.stat().st_size < 10000:
        raise RuntimeError("Quiz MP4 was not rendered")
    (outdir / "quiz.json").write_text(
        json.dumps(question, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Screenshot-style Sinhala quiz video:", output, question["q"])
    return output
