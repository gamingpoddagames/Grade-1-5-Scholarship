#!/usr/bin/env python3
"""Build Sinhala practice PDFs and original, silent quiz video; no AI needed."""
import argparse
import datetime as dt
import html
import json
import pathlib
import random
import subprocess

from weasyprint import HTML
from PIL import Image, ImageDraw, ImageFont, features

HERE = pathlib.Path(__file__).resolve().parent
FONT = pathlib.Path("/usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf")
BOLD = pathlib.Path("/usr/share/fonts/truetype/noto/NotoSansSinhala-Bold.ttf")
SITE = "https://gamingpoddagames.github.io/Grade-1-5-Scholarship/"

def font_path(bold=False):
    candidates = [
        BOLD if bold else FONT,
        pathlib.Path("/usr/share/fonts/truetype/noto/NotoSansSinhalaUI-Regular.ttf"),
        pathlib.Path("/usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf")
    ]
    for path in candidates:
        if path.is_file():
            return str(path)
    raise RuntimeError("Sinhala Noto font missing: install fonts-noto-core")

def all_questions():
    bank = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    for grade in range(1, 6):
        # Deterministic mathematics questions: correct options are computed.
        for num in range(1, 21):
            if grade == 1:
                left, right = 2 + num % 8, 1 + num % 7
                question, result = f"{left} + {right} = කීයද?", left + right
            elif grade == 2:
                left, right = 20 + num * 2, 2 + num % 9
                question, result = f"{left} - {right} = කීයද?", left - right
            elif grade == 3:
                left, right = 3 + num % 9, 2 + (num * 3) % 9
                question, result = f"{left} × {right} = කීයද?", left * right
            elif grade == 4:
                left, right = 4 + num % 9, 2 + num % 7
                question, result = f"{left*right} ÷ {right} = කීයද?", left
            else:
                left, right = 20 + num * 5, 2 + num % 8
                question, result = f"රු. {left} බැගින් පොත් {right}ක මුළු මිල කීයද?", left * right
            choices = [result, result + 2, result + 5, result + 10]
            rng = random.Random(grade * 100 + num)
            rng.shuffle(choices)
            answer = choices.index(result)
            bank.append({
                "grade": grade,
                "topic": "ශිෂ්‍යත්ව ගණිතය" if grade == 5 else "ගණිතය",
                "q": question,
                "choices": [str(v) for v in choices],
                "answer": answer,
                "explanation": f"නිවැරදි පිළිතුර {result}යි."
            })
    return bank

CSS = """
@page { size: A4; margin: 18mm; }
@font-face {font-family: NotoSinhala; src: url('file:///usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf');}
body {font-family: NotoSinhala, sans-serif; color: #183153; font-size: 12px; line-height: 1.65;}
h1 {font-size:20px; margin:0 0 8px;}
h2 {font-size:14px;}
.item {break-inside:avoid; margin: 0 0 12px; border-bottom:1px solid #e0e7ee;padding-bottom:8px;}
.choice {display:inline-block;margin:2px 14px 2px 0;}
.meta {color:#52687f; margin-bottom:18px;}
"""

def write_pdfs(folder, questions):
    folder.mkdir(parents=True, exist_ok=True)
    for grade in range(1,6):
        rows = [q for q in questions if q["grade"] == grade][:25]
        title = f"{grade} ශ්‍රේණිය - " + ("ශිෂ්‍යත්ව පුහුණුව" if grade == 5 else "ගණිත පුහුණුව")
        for answers in (False, True):
            body = [f"<h1>{html.escape(title)}</h1><p class='meta'>පුංචි නැණ මඟ | මුල් නිර්මාණ අභ්‍යාස | නිල විභාග පත්‍රයක් නොවේ</p>"]
            for i,q in enumerate(rows,1):
                body.append(f"<section class='item'><b>{i}. {html.escape(q['q'])}</b>")
                for j,choice in enumerate(q['choices']):
                    body.append(f"<span class='choice'>{chr(65+j)}) {html.escape(str(choice))}</span>")
                if answers:
                    body.append(f"<p>පිළිතුර: {chr(65+q['answer'])}) {html.escape(str(q['choices'][q['answer']]))} — {html.escape(q['explanation'])}</p>")
                body.append("</section>")
            name = f"grade-{grade}-" + ("answers" if answers else "paper") + ".pdf"
            page = "<html lang='si'><meta charset='utf-8'><style>" + CSS + "</style><body>" + "".join(body) + "</body></html>"
            HTML(string=page, base_url=str(HERE)).write_pdf(folder / name)
            print("Built", name)

def draw_text(draw, xy, text, font, fill, width=900, spacing=14):
    # draw multiline strings with real Sinhala glyph shaping (Pillow RAQM).
    words = str(text).split(" ")
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0,0), candidate, font=font, language="si")[2] <= width:
            line = candidate
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    x,y = xy
    for line in lines:
        draw.text((x,y), line, font=font, fill=fill, language="si")
        y += font.size + spacing
    return y

def video(outdir, questions, day):
    if not features.check("raqm"):
        raise RuntimeError("Pillow RAQM shaping is required for Sinhala video")
    filtered = [q for q in questions if q["grade"] == 5]
    q = filtered[day.toordinal() % len(filtered)]
    outdir.mkdir(parents=True, exist_ok=True)
    f32 = ImageFont.truetype(font_path(), 42, layout_engine=ImageFont.Layout.RAQM)
    f48 = ImageFont.truetype(font_path(), 48, layout_engine=ImageFont.Layout.RAQM)
    f58 = ImageFont.truetype(font_path(), 58, layout_engine=ImageFont.Layout.RAQM)
    sequence=[]
    for i,(show_answer,duration) in enumerate([(False,5),(True,4)]):
        im=Image.new("RGB",(1080,1920),"#0c2343")
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((60,105,1020,1815),radius=42,fill="#16375c")
        y=draw_text(d,(112,170),"පුංචි නැණ මඟ",f58,"#ffffff")
        y=draw_text(d,(112,310),"5 ශ්‍රේණිය - ශිෂ්‍යත්ව ප්‍රශ්නය",f42,"#80e6d7")
        y=draw_text(d,(112,530),q["q"],f48,"#ffffff",width=860,spacing=26)+75
        for k,ch in enumerate(q["choices"]):
            d.rounded_rectangle((105,y-8,980,y+86),radius=15,fill="#244d75")
            y=draw_text(d,(145,y+10),f"{chr(65+k)}) {ch}",f42,"#ffffff",width=790)+40
        if show_answer:
            y=draw_text(d,(112,min(y+110,1470)),f"පිළිතුර: {chr(65+q['answer'])}) {q['choices'][q['answer']]}",f48,"#7ff0ba")
        else:
            y=draw_text(d,(112,min(y+110,1470)),"පිළිතුර සිතන්න...",f48,"#ffc85c")
        draw_text(d,(112,1710),"Grade 1–5 Free Papers | Punchi Nena Maga",f32,"#d9e9fa")
        frame=outdir / f"frame-{i}.png"
        im.save(frame)
        sequence.append((frame,duration))
    manifest=outdir / "frames.txt"
    manifest.write_text("".join(f"file '{p.name}'\nduration {duration}\n" for p,duration in sequence) + f"file '{sequence[-1][0].name}'\n",encoding="utf-8")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",manifest.name,"-vf","fps=24,format=yuv420p","-movflags","+faststart","-c:v","libx264","-preset","veryfast","grade5-quiz.mp4"],cwd=outdir,check=True)
    print("Built grade5-quiz.mp4 (silent, 9 seconds)")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf-dir")
    p.add_argument("--video-dir")
    args=p.parse_args()
    questions=all_questions()
    if args.pdf_dir: write_pdfs(pathlib.Path(args.pdf_dir), questions)
    if args.video_dir: video(pathlib.Path(args.video_dir),questions,dt.datetime.now(dt.timezone.utc).date())

if __name__=="__main__": main()
