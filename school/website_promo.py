#!/usr/bin/env python3
"""Create original Sinhala school website invitation cards and mobile social video slides.

Does NOT post without --publish handled by separate workflow. Only known owned URLs.
No child personal data, false official-exam claims or third-party stock media.
"""
import argparse
import datetime as dt
import json
import pathlib
import subprocess
import unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageOps
from brand_assets import font, latin_font, logo
from voice_video import download, MODEL_URL, CONFIG_URL

BLOG="https://punchinanamaga.blogspot.com/"
RESOURCES="https://gamingpoddagames.github.io/Grade-1-5-Scholarship/"
PROMO_LINK=BLOG+"?utm_source=facebook&utm_medium=social&utm_campaign=school_learning_invitation"
RESOURCE_PROMO=RESOURCES+"?utm_source=facebook&utm_medium=social&utm_campaign=school_learning_invitation"
ROOT=pathlib.Path(__file__).resolve().parents[1]
TOPICS=[
 ("01", "නොමිලේ ඉගෙනුම", "1 සිට 5 ශ්‍රේණිය දක්වා", "ගණිතය • සිංහල • පරිසරය", "දරුවාට ගැළපෙන සිංහල පුහුණු ලිපි සහ පැහැදිලි කළ පිළිතුරු.", "#SinhalaEducation #Grade1to5"),
 ("02", "ශිෂ්‍යත්ව පුහුණුව", "5 ශ්‍රේණියට සූදානම් වෙමු", "Online Quiz • PDF ප්‍රශ්න", "දවසකට කෙටි පුහුණුවකින් ඉගෙනීමේ පුරුද්ද ගොඩනඟන්න.", "#Grade5Scholarship #ScholarshipSriLanka"),
 ("03", "දෙමාපියන්ට උපදෙස්", "නිවසේ ඉගෙනීම පහසුයි", "පුහුණු ප්‍රශ්න • පිළිතුරු", "නිවසේදී දරුවා සමඟ කිරීමට ගැළපෙන අධ්‍යාපනික අදහස්.", "#ParentsSriLanka #SinhalaLearning"),
 ("04", "පාසල් පාඩම්", "නොමිලේ අධ්‍යාපනික සම්පත්", "Grade 1–5 • Scholarship", "අලුත් සිංහල පාඩම් කියවන්න. PDF සහ Online Quiz ද සොයාගන්න.", "#SriLankaEducation #FreeLearning"),
]
BLUE="#103a6b"; TEAL="#087f85"; INK="#173858"; YELLOW="#ffd34f"

def choose(day):
    return TOPICS[(day.toordinal()+1)%len(TOPICS)]

def wrap(draw,text,face,max_width):
    words=text.split()
    lines=[]; current=""
    for word in words:
        trial=(current+" "+word).strip()
        bounds=draw.textbbox((0,0),trial,font=face,language="si")
        if bounds[2]-bounds[0]>max_width and current:
            lines.append(current);current=word
        else:current=trial
    if current:lines.append(current)
    return lines

def text_lines(draw,txt,face,color,x,y,width,spacing=20,max_lines=5):
    lines=wrap(draw,txt,face,width)
    if len(lines)>max_lines:raise ValueError("Caption overflow; shorten copy")
    for line in lines:
        draw.text((x,y),line,font=face,fill=color,language="si",stroke_width=0)
        bb=draw.textbbox((0,0),line,font=face,language="si")
        y+=bb[3]-bb[1]+spacing
    return y

def background(w,h):
    canvas=Image.new("RGB",(w,h),"#edf7fc")
    draw=ImageDraw.Draw(canvas)
    draw.rectangle((0,0,w,int(h*.42)),fill=BLUE)
    draw.ellipse((-int(w*.4),-int(h*.2),int(w*.82),int(h*.5)),fill="#145481")
    draw.ellipse((int(w*.68),int(h*.08),int(w*1.28),int(h*.44)),fill=TEAL)
    return canvas

def branding(im,scale=1):
    d=ImageDraw.Draw(im);w,h=im.size
    x=int(74*scale);y=int(75*scale)
    icon=logo(210).resize((int(118*scale),int(118*scale)))
    if icon.mode=="RGBA": im.paste(icon,(x,y),icon)
    else: im.paste(icon,(x,y))
    d.text((x+int(144*scale),y+int(16*scale)),"පුංචි නැණ මඟ",font=font(int(48*scale),True),fill="white",language="si")
    d.text((x+int(145*scale),y+int(83*scale)),"Grade 1–5 • Scholarship",font=latin_font(int(25*scale)),fill="#d4eaf7")

def card(topic,output):
    number,tag,headline,services,description,hashtags=topic
    im=background(1080,1350);branding(im)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((74,285,1006,1056),radius=38,fill="white",outline="#d7e9f3",width=3)
    d.rounded_rectangle((116,330,964,420),radius=21,fill="#e6f5f6")
    text_lines(d,tag,font(40,True),TEAL,149,345,780,4,1)
    y=text_lines(d,headline,font(61,True),INK,130,478,820,22,3)
    y=text_lines(d,services,font(37,True),TEAL,131,max(y+26,665),825,12,2)
    y=text_lines(d,description,font(37),INK,132,max(y+38,795),815,18,4)
    d.rounded_rectangle((100,1085,980,1248),radius=29,fill=YELLOW)
    d.text((149,1101),"නොමිලේ පාඩම් බලන්න",font=font(46,True),fill=BLUE,language="si")
    d.text((148,1178),"punchinanamaga.blogspot.com",font=latin_font(33),fill=BLUE)
    output.parent.mkdir(parents=True,exist_ok=True);im.save(output,optimize=True)
    return output

def slide(topic,index):
    im=background(1080,1920);branding(im)
    d=ImageDraw.Draw(im)
    if index==0:
        headline="ඔබේ දරුවාට\nනොමිලේ ඉගෙනුම"
        description="පුංචි නැණ මඟ සමඟ"
    elif index==1:
        headline=topic[2]
        description=topic[3]+"\n"+topic[4]
    else:
        headline="අදම පිවිසෙන්න"
        description="සිංහල පාඩම් • PDF • Online Quiz"
    d.rounded_rectangle((60,390,1020,1415),radius=48,fill="white")
    yy=540
    for line in headline.split("\n"):
        yy=text_lines(d,line,font(65,True),BLUE,115,yy,860,30,3)
    yy=max(yy+90,830)
    for line in description.split("\n"):
        yy=text_lines(d,line,font(39),TEAL,113,yy,850,20,4)
    d.rounded_rectangle((67,1500,1015,1760),radius=39,fill=YELLOW)
    d.text((114,1541),"www.punchinanamaga.blogspot.com",font=latin_font(37),fill=BLUE)
    d.text((115,1640),"නොමිලේ ඉගෙනගන්න",font=font(46,True),fill=BLUE,language="si")
    return im

def caption(topic):
    return unicodedata.normalize("NFC", "\n".join([
      "පුංචි නැණ මඟ | "+topic[2],"",
      topic[4],"",
      "📝 1–5 ශ්‍රේණි සිංහල පුහුණු ප්‍රශ්න සහ ලිපි",
      "📚 5 ශ්‍රේණිය ශිෂ්‍යත්ව පුහුණුව හා Quiz",
      "📄 නොමිලේ ප්‍රශ්න සහ පිළිතුරු PDF","",
      "අලුත් පාඩම් සහ කියවිය හැකි ලිපි:",
      PROMO_LINK,
      "PDF සහ Online Quiz:",
      RESOURCE_PROMO,"",
      "මෙම පුහුණු සම්පත් අපගේ මුල් නිර්මාණයි. නිල විභාග ප්‍රශ්න පත්‍ර ලෙස නොසලකන්න.",
      topic[5]+" #PunchiNenaMaga"
    ]))

def make_video(topic,folder,with_voice):
    folder.mkdir(parents=True,exist_ok=True)
    for i in range(3):slide(topic,i).save(folder/f"slide-{i}.png")
    words=["ආයුබෝවන්. පුංචි නැණ මඟ සමඟ, එකේ සිට පහේ ශ්‍රේණිය දක්වා සිංහල ඉගෙනුම නොමිලේ.",
           topic[2]+". "+topic[4],
           "අපේ වෙබ් අඩවියට පිවිසෙන්න. punchinanamaga.blogspot.com. නොමිලේ පාඩම්, ප්‍රශ්න පත්‍ර සහ ඔන්ලයින් ක්විස්."]
    model=folder/"voice"/"si_LK-ashoka-medium.onnx"
    conf=folder/"voice"/"si_LK-ashoka-medium.onnx.json"
    if with_voice:
        download(MODEL_URL,model);download(CONFIG_URL,conf)
    clips=[]
    for i in range(3):
        raw=folder/f"voice-{i}.wav"
        if with_voice:
            subprocess.run(["piper","--model",str(model),"--config",str(conf),"--output_file",str(raw)],
                           input=words[i].encode("utf-8"),check=True,timeout=150)
            probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                "-of","default=noprint_wrappers=1:nokey=1",str(raw)],check=True,capture_output=True,text=True)
            seconds=max(float(probe.stdout.strip())+1.0,5.0)
        else:seconds=6
        clip=folder/f"clip-{i}.mp4"
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate","24","-i",str(folder/f"slide-{i}.png")]
        if with_voice:cmd+=["-i",str(raw)]
        cmd+=["-t",f"{seconds:.2f}","-vf","scale=1080:1920,format=yuv420p","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p"]
        if with_voice:cmd+=["-c:a","aac","-af","apad","-b:a","128k"]
        else:cmd+=["-an"]
        cmd+=["-movflags","+faststart",str(clip)]
        subprocess.run(cmd,check=True,timeout=200);clips.append(clip)
    manifest=folder/"clips.txt";manifest.write_text("".join(f"file '{x.name}'\n" for x in clips),encoding="utf-8")
    out=folder/"school-promo.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
        "-i",manifest.name,"-c","copy","-movflags","+faststart",out.name],cwd=folder,check=True,timeout=90)
    if out.stat().st_size<30000:raise RuntimeError("Promotional video not generated correctly")
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="promo_output")
    p.add_argument("--date",default=None)
    p.add_argument("--video",action="store_true")
    p.add_argument("--voice",action="store_true")
    args=p.parse_args()
    day=dt.date.fromisoformat(args.date) if args.date else (dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=5,minutes=30)).date()
    topic=choose(day);out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=True)
    card(topic,out/"school-website-invite.png")
    (out/"facebook-caption.txt").write_text(caption(topic),encoding="utf-8")
    (out/"topic.json").write_text(json.dumps({"date":day.isoformat(),"number":topic[0],"title":topic[2],"blog":BLOG,"campaign_url":PROMO_LINK},ensure_ascii=False,indent=2),encoding="utf-8")
    print("PROMO CARD READY:",out/"school-website-invite.png")
    if args.video:print("PROMO VIDEO READY:",make_video(topic,out,args.voice))
if __name__=="__main__":main()
