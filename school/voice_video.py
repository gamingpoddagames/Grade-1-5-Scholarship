#!/usr/bin/env python3
"""Create original Sinhala narration for a rendered Grade 5 quiz using MIT-licensed Piper TTS."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import urllib.request

from build_resources import all_questions
from visual_quiz import select

MODEL_URL="https://huggingface.co/unicef/piper-si_LK-ashoka-medium/resolve/main/si_LK-ashoka-medium.onnx"
CONFIG_URL="https://huggingface.co/unicef/piper-si_LK-ashoka-medium/resolve/main/si_LK-ashoka-medium.onnx.json"

def download(url,dest):
    if dest.exists() and dest.stat().st_size>1000:
        return
    dest.parent.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(url,headers={"User-Agent":"School-Original-Sinhala-TTS/1.0"})
    with urllib.request.urlopen(req,timeout=180) as source,open(dest,"wb") as output:
        while True:
            block=source.read(1024*1024)
            if not block:
                break
            output.write(block)
    if dest.stat().st_size<1000:
        raise RuntimeError("Voice model file did not download successfully")

def seconds(path):
    p=subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1",str(path)],
        text=True,capture_output=True,check=True)
    return float(p.stdout.strip())

# Convert written maths and abbreviations into natural Sinhala before TTS.
# The video artwork retains the original question; only narration is adjusted.
import re

_DIGITS = ("බිංදුව", "එක", "දෙක", "තුන", "හතර", "පහ", "හය", "හත", "අට", "නවය")
_TEENS = ("දහය", "එකොළහ", "දොළහ", "දහතුන", "දහහතර", "පහළොව", "දහසය", "දහහත", "දහඅට", "දහනවය")
_TENS = ("", "", "විස්ස", "තිහ", "හතළිහ", "පනහ", "හැට", "හැත්තෑව", "අසූව", "අනූව")

def spoken_number(value):
    number = int(value)
    if number < 0:
        return "ඍණ " + spoken_number(-number)
    if number < 10:
        return _DIGITS[number]
    if number < 20:
        return _TEENS[number - 10]
    if number < 100:
        tens, ones = divmod(number, 10)
        return _TENS[tens] if not ones else _TENS[tens] + " " + _DIGITS[ones]
    # Larger numbers: speak digit-by-digit to avoid the TTS reading English digits.
    return " ".join(_DIGITS[int(d)] for d in str(number))

def speech_ready(text):
    """Prepare Sinhala speech text; refuse unknown Latin words/symbols."""
    text = str(text)
    for english, sinhala in (("Online Quiz", "අන්තර්ජාල ප්‍රශ්නාවලි"),
                             ("Quiz", "ප්‍රශ්නාවලිය"), ("PDF", "පී ඩී එෆ්"),
                             ("website", "අන්තර්ජාල අඩවිය"), ("question", "ප්‍රශ්නය")):
        text = re.sub(re.escape(english), sinhala, text, flags=re.IGNORECASE)
    text = re.sub(r"රු\.", "රුපියල් ", text)
    # Fractions are read as numerator over denominator, not a URL or date.
    text = re.sub(r"(?<![\d/])(\d+)\s*/\s*(\d+)(?![\d/])",
                  lambda m: spoken_number(m.group(1)) + " බෙදූ " + spoken_number(m.group(2)), text)
    text = re.sub(r"\d+", lambda m: spoken_number(m.group()), text)
    for old, new in (("×", " ගුණ කිරීම "), ("÷", " බෙදීම "), ("+", " එකතු කිරීම "),
                     ("=", " සමානයි "), ("-", " අඩු කිරීම "), ("...", " "),
                     ("?", " ද? ")):
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text).strip()
    if re.search(r"[A-Za-z]|[×÷=+]|\d", text):
        raise ValueError("Unsupported token remains in Sinhala narration: " + text)
    return text

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--video-dir",required=True)
    parser.add_argument("--model-dir",default="school/.voice-cache")
    args=parser.parse_args()
    folder=Path(args.video_dir)
    model_dir=Path(args.model_dir)
    model=model_dir/"si_LK-ashoka-medium.onnx"
    config=model_dir/"si_LK-ashoka-medium.onnx.json"
    download(MODEL_URL,model)
    download(CONFIG_URL,config)
    # Colombo date matches the photo card and narrated Reel.
    day=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=5,minutes=30)).date()
    question=select(day)
    correct=question["choices"][question["answer"]]
    scripts=[
        "ආයුබෝවන්! පුංචි නැණ මඟ සමඟ අද ශිෂ්‍යත්ව පුහුණු ප්‍රශ්නය අසමු. "
        + speech_ready(question["q"]) + " ටිකක් සිතා බලන්න.",
        "පිළිතුර " + speech_ready(str(correct)) + ". " + speech_ready(question["explanation"]) +
        " තවත් අධ්‍යාපනික ලිපි සහ පුහුණු ප්‍රශ්න සඳහා පුංචි නැණ මඟ බ්ලොග් අඩවියට පිවිසෙන්න."
    ]
    clips=[]
    for i,text in enumerate(scripts):
        slide=folder/f"frame-{i}.png"
        if not slide.is_file():
            raise FileNotFoundError(f"Original video frame unavailable: {slide}")
        wav=folder/f"narration-{i}.wav"
        subprocess.run(["piper","--model",str(model),"--config",str(config),"--output_file",str(wav)],
                       input=text.encode("utf-8"),check=True,timeout=120)
        duration=max(seconds(wav)+1.3,5.0)
        clip=folder/f"voiced-{i}.mp4"
        subprocess.run([
            "ffmpeg","-hide_banner","-loglevel","error","-y",
            "-loop","1","-framerate","24","-i",str(slide),
            "-i",str(wav),"-t",f"{duration:.2f}",
            "-vf","scale=1080:1920,format=yuv420p",
            "-c:v","libx264","-preset","veryfast",
            "-c:a","aac","-b:a","128k","-af","apad",
            "-movflags","+faststart",str(clip)
        ],check=True,timeout=180)
        clips.append(clip)
    manifest=folder/"narration-clips.txt"
    manifest.write_text("".join(f"file '{p.name}'\n" for p in clips),encoding="utf-8")
    out=folder/"grade5-quiz-voiced.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                    "-f","concat","-safe","0","-i",manifest.name,"-c","copy",out.name],cwd=folder,check=True,timeout=180)
    if out.stat().st_size<10000:
        raise RuntimeError("Voiced MP4 too small or invalid")
    print("Sinhala voiced Grade 5 quiz successfully rendered:",out.name,"bytes:",out.stat().st_size)

if __name__=="__main__": main()
