#!/usr/bin/env python3
"""Sinhala Unicode-safe original Facebook question image cards and Page photo posts."""
import argparse
from blogger_link_safety import validate_blogger_links
import json
import os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

from brand_assets import font,latin_font,logo
from font_safety import draw_mixed, mixed_width, check_caption
from page_branding_upload import multipart

def wrap(draw,text,face,max_width):
    lines=[]
    current=""
    for word in str(text).split():
        line=(current+" "+word).strip()
        w=mixed_width(draw,line,face)
        if w <= max_width:
            current=line
        else:
            if current: lines.append(current)
            current=word
    if current:lines.append(current)
    return lines

def line(draw,text,x,y,face,color,max_width,lineheight):
    for value in wrap(draw,text,face,max_width):
        draw_mixed(draw,(x,y),value,face,color)
        y+=lineheight
    return y

def create_card(question,target):
    if question.get("image_title"):
        from visual_quiz import draw_card
        return draw_card(question, target)
    canvas=Image.new("RGB",(1080,1350),"#e6f4fc")
    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((45,42,1035,1308),radius=42,fill="#ffffff")
    d.rounded_rectangle((45,42,1035,335),radius=42,fill="#0a477a")
    brand=logo(220).resize((158,158))
    canvas.paste(brand,(88,104))
    draw_mixed(d,(280,105),"පුංචි නැණ මඟ",font(58,True),"white")
    d.text((284,210),"Grade 1–5 & Scholarship",font=latin_font(32),fill="#ccecf4")
    d.rounded_rectangle((93,382,987,1140),radius=32,fill="#f4f9ff")
    draw_mixed(d,(139,421),f"{question['grade']} ශ්‍රේණිය - {question['topic']}",font(35,True),"#0f7774")
    # Fit the entire question and four options inside the reserved panel.
    # Try progressively smaller type rather than allowing text to overlap.
    choices = question["choices"]
    if len(choices) != 4:
        raise ValueError("Quiz card requires exactly four answer options")
    fitted = False
    for qsize, osize, row_height, qheight in ((48,36,100,68),(42,33,94,61),(36,29,88,54),(31,26,82,48)):
        qface = font(qsize, True)
        oface = font(osize)
        qlines = wrap(d, question["q"], qface, 780)
        if any(mixed_width(d, value, qface) > 780 for value in qlines):
            continue
        option_lines = [wrap(d, f"{chr(65+i)}) {choice}", oface, 730) for i,choice in enumerate(choices)]
        if any(len(lines) > 2 or any(mixed_width(d, value, oface)>730 for value in lines) for lines in option_lines):
            continue
        option_heights = [max(row_height, len(lines)*(osize+8)+20) for lines in option_lines]
        top = 518 + len(qlines)*qheight + 28
        if top + sum(option_heights) + 8 <= 1130:
            fitted = True
            break
    if not fitted:
        raise ValueError("Question and options do not fit even at minimum readable font size")
    y = 518
    for value in qlines:
        draw_mixed(d,(140,y),value,qface,"#173453")
        y += qheight
    y += 28
    for lines, height in zip(option_lines, option_heights):
        d.rounded_rectangle((132,y,943,y+height-9),radius=15,fill="#ffffff",outline="#c3d9ea",width=3)
        ty = y + 10
        for value in lines:
            draw_mixed(d,(157,ty),value,oface,"#193956")
            ty += osize+8
        y += height
    d.rounded_rectangle((93,1170,987,1248),radius=22,fill="#0e837d")
    draw_mixed(d,(140,1184),"නොමිලේ ප්‍රශ්න පත්‍ර සහ පිළිතුරු",font(35,True),"white")
    target=Path(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(target,optimize=True)
    print("Sinhala branded card generated:",target)

def validate_card(image):
    """Fail closed if the final image is absent, corrupt or the wrong size."""
    path = Path(image)
    if not path.is_file() or path.stat().st_size < 10000:
        raise RuntimeError("Facebook image quality gate failed: missing or empty artwork")
    with Image.open(path) as rendered:
        if rendered.size != (1080, 1350) or rendered.mode != "RGB":
            raise RuntimeError("Facebook image quality gate failed: invalid dimensions or color mode")
        rendered.verify()
    print("Facebook card quality gate passed: 1080x1350 RGB PNG")


def publish(image,caption):
    check_caption(caption)
    validate_blogger_links(caption)
    validate_card(image)
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
    return str(out["id"])

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
