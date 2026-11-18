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
    # Same UTC date selection as the independent video renderer.
    day=dt.datetime.now(dt.timezone.utc).date()
    qs=[q for q in all_questions() if q["grade"]==5]
    question=qs[day.toordinal()%len(qs)]
    correct=question["choices"][question["answer"]]
    scripts=[
        "ආයුබෝවන්! පුංචි නැණ මඟ සමඟ, අද ශිෂ්‍යත්ව පුහුණු ප්‍රශ්නය. "
        +question["q"]+" ටිකක් සිතා බලන්න.",
        "නිවැරදි පිළිතුර " +str(correct)+". "+question["explanation"]+
        " තවත් පුහුණු ප්‍රශ්න සඳහා අපගේ වෙබ් අඩවියට පිවිසෙන්න."
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
