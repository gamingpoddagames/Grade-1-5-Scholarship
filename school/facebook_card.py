#!/usr/bin/env python3
"""Sinhala Unicode-safe original Facebook question image cards and Page photo posts."""
import argparse
import json
import os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

from brand_assets import font,latin_font,logo
from page_branding_upload import multipart

def wrap(draw,text,face,max_width):
    lines=[]
    current=""
    for word in str(text).split():
        line=(current+" "+word).strip()
        w=draw.textbbox((0,0),line,font=face,language="si")[2]
        if w <= max_width:
            current=line
        else:
            if current: lines.append(current)
            current=word
    if current:lines.append(current)
    return lines

def line(draw,text,x,y,face,color,max_width,lineheight):
    for value in wrap(draw,text,face,max_width):
        draw.text((x,y),value,font=face,fill=color,language="si")
        y+=lineheight
    return y

def create_card(question,target):
    canvas=Image.new("RGB",(1080,1350),"#e6f4fc")
    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((45,42,1035,1308),radius=42,fill="#ffffff")
    d.rounded_rectangle((45,42,1035,335),radius=42,fill="#0a477a")
    brand=logo(220).resize((158,158))
    canvas.paste(brand,(88,104))
    d.text((280,105),"පුංචි නැණ මඟ",font=font(58,True),fill="white",language="si")
    d.text((284,210),"Grade 1–5 & Scholarship",font=latin_font(32),fill="#ccecf4")
    d.rounded_rectangle((93,382,987,1140),radius=32,fill="#f4f9ff")
    d.text((139,421),f"{question['grade']} ශ්‍රේණිය - {question['topic']}",font=font(35,True),fill="#0f7774",language="si")
    y=line(d,question["q"],140,522,font(58,True),"#173453",800,89)+40
    for idx,choice in enumerate(question["choices"]):
        if y>1060:
            raise ValueError("Question card exceeds available space; manual review required")
        d.rounded_rectangle((132,y-8,943,y+78),radius=16,fill="#ffffff",outline="#c3d9ea",width=3)
        d.text((157,y+2),f"{chr(65+idx)}) {choice}",font=font(43),fill="#193956",language="si")
        y+=118
    d.rounded_rectangle((93,1170,987,1248),radius=22,fill="#0e837d")
    d.text((140,1184),"නොමිලේ ප්‍රශ්න පත්‍ර සහ පිළිතුරු",font=font(35,True),fill="white",language="si")
    target=Path(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(target,optimize=True)
    print("Sinhala branded card generated:",target)

def publish(image,caption):
    page=os.getenv("FB_PAGE_ID")
    token=os.getenv("FB_PAGE_ACCESS_TOKEN")
    if not page or not token:
        print("Card post skipped: Facebook Page credentials missing.")
        return
    version=os.getenv("FB_GRAPH_VERSION","v27.0")
    url=f"https://graph.facebook.com/{version}/{page}/photos"
    out=multipart(url,{"access_token":token,"message":caption},image)
    if not out.get("id"):
        raise RuntimeError("Facebook Page photo creation did not return a photo ID")
    print("Facebook branded question photo published:",out["id"])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--question",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--caption",required=True)
    parser.add_argument("--publish",action="store_true")
    args=parser.parse_args()
    item=json.loads(Path(args.question).read_text(encoding="utf-8"))
    create_card(item,args.output)
    if args.publish:
        caption=Path(args.caption).read_text(encoding="utf-8")
        publish(args.output,caption)

if __name__=="__main__":main()
