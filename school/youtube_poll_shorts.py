#!/usr/bin/env python3
"""Turn the same daily FB+Blogger text/image quiz into a private YouTube Short.

Uses the *same* existing approved 1080x1350 Facebook image source, without
editing its renderer. Adds only a separate readable 1080x1920 companion
with a question stage, answer-reveal and original Sinhala narration.
Native Community polls are not created through the YouTube upload API.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw
from gtts import gTTS

from brand_assets import font, latin_font
from font_safety import draw_mixed, mixed_width
from social_poll_pack import build_pack
from youtube_shorts import build_metadata, today_sri_lanka, upload


def fit_text(draw, message, maximum=910):
    for size in (54,49,44,39,34,30):
        face=font(size,True)
        if mixed_width(draw,message,face)<=maximum:
            return face
    raise ValueError("Answer line too wide for Shorts safe-area")


def frame(original, question, reveal, destination):
    with Image.open(original) as src:
        if src.size!=(1080,1350):
            raise ValueError("Expected exact validated Facebook quiz art 1080x1350")
        art=src.convert("RGB")
    img=Image.new("RGB",(1080,1920),"#09264b")
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((23,30,1057,1880),radius=32,fill="#15416a")
    img.paste(art,(0,85))
    d.rounded_rectangle((55,1485,1025,1690),radius=28,
                        fill=("#156f58" if reveal else "#204f88"))
    if reveal:
        correct=question["choices"][question["answer"]]
        msg="නිවැරදි පිළිතුර: " + chr(65+question["answer"]) + ") " + str(correct)
    else:
        msg="පිළිතුර සිතා බලන්න..."
    face=fit_text(d,msg)
    draw_mixed(d,(90,1540),msg,face,"#ffffff")
    draw_mixed(d,(87,1740),"පුංචි නැණ මඟ",font(36,True),"#9aefdf")
    d.text((87,1806),"punchinanamaga.blogspot.com",
           font=latin_font(31),fill="#e6f2fa")
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    img.save(destination,optimize=True)
    return destination


def duration(path):
    result=subprocess.run([
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(path)
    ],capture_output=True,text=True,check=True,timeout=35)
    secs=float(result.stdout.strip())
    if not .1<secs<120:
        raise RuntimeError("Unexpected voice duration")
    return secs


def render(question, art, folder):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    frame(art,question,False,folder/"poll-frame-0.png")
    frame(art,question,True,folder/"poll-frame-1.png")
    spoken_question=(question["q"] + " " +
                     " ".join(str(c)+"." for c in question["choices"]) +
                     " පිළිතුර සිතන්න.")
    spoken_answer="නිවැරදි පිළිතුර, "+str(question["choices"][question["answer"]])+"."
    audio_question=folder/"poll-question.mp3"
    audio_answer=folder/"poll-answer.mp3"
    gTTS(text=spoken_question,lang="si",slow=False,timeout=(5,30)).save(str(audio_question))
    gTTS(text=spoken_answer,lang="si",slow=False,timeout=(5,30)).save(str(audio_answer))
    q_sec=duration(audio_question)+3.0
    a_sec=duration(audio_answer)+1.5
    (folder/"poll-frames.txt").write_text(
        f"file 'poll-frame-0.png'\nduration {q_sec:.3f}\n"
        f"file 'poll-frame-1.png'\nduration {a_sec:.3f}\n"
        "file 'poll-frame-1.png'\n",encoding="utf-8")
    out=folder/"social-poll-short.mp4"
    subprocess.run([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","concat","-safe","0","-i",str(folder/"poll-frames.txt"),
        "-i",str(audio_question),"-i",str(audio_answer),
        "-filter_complex",
        "[1:a]aformat=sample_rates=44100:channel_layouts=mono[q];"
        "anullsrc=r=44100:cl=mono,atrim=duration=3[s];"
        "[2:a]aformat=sample_rates=44100:channel_layouts=mono[a];"
        "[q][s][a]concat=n=3:v=0:a=1[all];"
        "[all]apad=pad_dur=1.5[aout]",
        "-map","0:v","-map","[aout]",
        "-vf","fps=24,format=yuv420p",
        "-c:v","libx264","-preset","veryfast","-crf","23",
        "-c:a","aac","-b:a","128k","-pix_fmt","yuv420p",
        "-t",str(q_sec+a_sec),"-movflags","+faststart",str(out)
    ],check=True,timeout=240)
    if not out.is_file() or out.stat().st_size<10_000:
        raise RuntimeError("Poll video was not rendered")
    return out


def metadata_for_poll(question,day,kind):
    meta=build_metadata(question,day,privacy="private")
    old=meta["_marker"]
    unique=f"PNM-POLL-{day.strftime('%Y%m%d')}-{kind.upper()}"
    grade=question["grade"]
    title=("පින්තූර ප්‍රශ්නය" if kind=="image" else "දැනුම විමසුම")
    new_title=f"{grade} ශ්‍රේණිය | {title} | {question['q']} #Shorts"
    if len(new_title)>100:
        new_title=f"{grade} ශ්‍රේණිය | {title} | සිංහල Quiz #Shorts"
    meta["snippet"]["title"]=new_title
    meta["snippet"]["description"]=meta["snippet"]["description"].replace(old,unique)
    meta["_marker"]=unique
    return meta


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--date",help="Sri Lanka YYYY-MM-DD")
    p.add_argument("--kind",choices=["text","image","rotate"],default="rotate")
    p.add_argument("--upload",action="store_true")
    p.add_argument("--output",default="school/output/youtube-social-poll")
    args=p.parse_args()
    day=dt.date.fromisoformat(args.date) if args.date else today_sri_lanka()
    kind=("text" if day.toordinal()%2==0 else "image") if args.kind=="rotate" else args.kind
    output=Path(args.output)/day.isoformat()/kind
    q,art,_=build_pack(day,kind,output)
    meta=metadata_for_poll(q,day,kind)
    (output/"youtube-poll-metadata.json").write_text(
        json.dumps({"snippet":meta["snippet"],"status":meta["status"],
                    "unique_marker":meta["_marker"]},ensure_ascii=False,indent=2),
        encoding="utf-8")
    original_movie=render(q,art,output)
    from video_cta import append_outro
    movie=append_outro(original_movie,"youtube","school")
    print("YouTube poll companion Short with branded CTA:",movie,meta["_marker"])
    if args.upload:
        try:
            report=upload(movie,meta,output)
        except RuntimeError as exc:
            if "already uploaded" not in str(exc):
                raise
            print("Existing poll companion video detected; no duplicate posted.")
        else:
            print("Confirmed owner YouTube privacy:",report["privacy"])
    else:
        print("PREVIEW ONLY: generated YouTube Short, not posted")


if __name__=="__main__":
    main()
