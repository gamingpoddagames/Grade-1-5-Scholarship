#!/usr/bin/env python3
"""Deterministic Sinhala-safe education branding for website and Page images.
No paid API: Pillow + Noto Sinhala/RAQM, original vector shapes and rendered text.
"""
import argparse
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, features

FONT="/usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf"
BOLD="/usr/share/fonts/truetype/noto/NotoSansSinhala-Bold.ttf"
NAME="පුංචි නැණ මඟ"
SUBTITLE="Grade 1–5 & Scholarship"

def font(size,bold=False):
    if not features.check("raqm"):
        raise RuntimeError("Sinhala shaping (libraqm) is required")
    candidate=Path(BOLD if bold else FONT)
    if not candidate.is_file():
        candidate=Path(FONT)
    if not candidate.is_file():
        raise RuntimeError("Noto Sans Sinhala font not installed")
    return ImageFont.truetype(str(candidate),size,layout_engine=ImageFont.Layout.RAQM)

def center(draw,y,message,typeface,color,canvas_width):
    box=draw.textbbox((0,0),message,font=typeface,language="si")
    width=box[2]-box[0]
    draw.text(((canvas_width-width)/2,y),message,fill=color,font=typeface,language="si")

def book(draw,center_x,top,size=1):
    x,y=center_x,top
    # Open book with two distinct leaves, spine and warm yellow underlines
    s=size
    def points(coords): return [(int(x+dx*s),int(y+dy*s)) for dx,dy in coords]
    draw.polygon(points([(-185,34),(-145,-20),(-25,-6),(0,25),(0,148),(-25,120),(-145,111),(-185,136)]),fill="#e7f5ff")
    draw.polygon(points([(185,34),(145,-20),(25,-6),(0,25),(0,148),(25,120),(145,111),(185,136)]),fill="#faffff")
    draw.line(points([(-175,138),(-24,122),(0,151),(24,122),(175,138)]),fill="#21a675",width=max(3,int(11*s)),joint="curve")
    draw.line(points([(0,28),(0,145)]),fill="#0b659e",width=max(2,int(7*s)))
    for yy in (35,61,87):
        draw.line(points([(-145,yy),(-94,yy-5),(-30,yy+4)]),fill="#87b7df",width=max(2,int(4*s)))
        draw.line(points([(30,yy+4),(94,yy-5),(145,yy)]),fill="#87b7df",width=max(2,int(4*s)))
    # cap
    draw.polygon(points([(-110,-68),(0,-118),(110,-68),(0,-24)]),fill="#143f83")
    draw.polygon(points([(-65,-42),(65,-42),(65,-4),(0,15),(-65,-4)]),fill="#174d8e")
    draw.line(points([(110,-68),(136,-22)]),fill="#ffd049",width=max(3,int(7*s)))
    draw.ellipse(points([(125,-20),(145,0)]),fill="#ffd049")

def logo(size=900):
    s=size/900
    canvas=Image.new("RGB",(size,size),"#ffffff")
    d=ImageDraw.Draw(canvas)
    d.ellipse((int(20*s),int(20*s),int(880*s),int(880*s)),fill="#0969aa")
    d.ellipse((int(42*s),int(42*s),int(858*s),int(858*s)),fill="#ffffff")
    d.ellipse((int(84*s),int(84*s),int(816*s),int(816*s)),fill="#f3fbff")
    book(d,size/2,int(340*s),1.23*s)
    center(d,int(570*s),NAME,font(int(61*s),True),"#08376b",size)
    d.rounded_rectangle((int(110*s),int(687*s),int(790*s),int(754*s)),radius=int(30*s),fill="#0a817f")
    center(d,int(695*s),SUBTITLE,font(int(26*s),True),"#ffffff",size)
    d.arc((int(120*s),int(770*s),int(780*s),int(900*s)),180,360,fill="#8fc944",width=max(5,int(22*s)))
    return canvas

def cover(width=1640,height=624):
    im=Image.new("RGB",(width,height),"#0d4885")
    p=im.load()
    # smooth gradient with turquoise foreground; no external image resources
    for y in range(height):
        for x in range(width):
            t=x/max(1,width-1)
            yy=y/max(1,height-1)
            p[x,y]=(int(11+13*t+39*yy),int(76+116*t+30*yy),int(130+40*t+18*yy))
    d=ImageDraw.Draw(im)
    # yellow wave and subtle ruled-paper motifs
    d.polygon([(0,0),(width*.31,0),(width*.23,72),(0,42)],fill="#ffcf34")
    d.ellipse((-95,270,340,720),fill="#0d678e")
    d.ellipse((1310,-170,1820,270),fill="#26ad98")
    d.ellipse((1350,390,1810,850),fill="#ffc948")
    # emblem to the left; clean title panel remains easily readable on mobile
    book(d,230,280,.82)
    d.rounded_rectangle((455,140,1540,515),radius=44,fill="#093f78")
    d.rounded_rectangle((475,164,1518,492),radius=33,outline="#2ce0bb",width=4)
    d.text((525,204),NAME,fill="#ffffff",font=font(91,True),language="si")
    d.text((530,348),SUBTITLE,fill="#ffda62",font=font(54,True),language="si")
    d.text((525,431),"Free Papers  •  Answers  •  Quiz Videos",fill="#e6faff",font=font(27),language="si")
    return im

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="_site/assets")
    args=p.parse_args()
    dest=Path(args.output)
    dest.mkdir(parents=True,exist_ok=True)
    logo(900).save(dest/"logo.png",optimize=True)
    logo(240).save(dest/"favicon.png",optimize=True)
    cover().save(dest/"cover.jpg",quality=87,optimize=True)
    print("Branding generated:",dest/"logo.png",dest/"cover.jpg",dest/"favicon.png")

if __name__=="__main__": main()
