#!/usr/bin/env python3
"""Append an original, short, Sinhala-spoken Punchi Nena Maga CTA end-card.

Existing video frames, original questions, answer reveal and narrator are
left untouched. The branded card is added *after* the completed original MP4.
Facebook Follow and YouTube Subscribe use separate messages and visuals.
Videos actually made for kids do not invite YouTube comments (unavailable).

Run only on video source files, not an already CTA-appended file.
Uses the same Noto Sinhala + DejaVu / Pillow RAQM stack as school Reels.
"""
import argparse
import json
from fractions import Fraction
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFilter
from brand_assets import font, latin_font, logo
from font_safety import draw_mixed, mixed_width

CHANNEL="පුංචි නැණ මඟ"
BLOG="punchinanamaga.blogspot.com"
SUPPORTED_PLATFORMS=("youtube","facebook")
PROFILES={
    ("youtube", "general"): {
        "platform":"YOUTUBE",
        "primary":"SUBSCRIBE",
        "secondary":("LIKE","COMMENT","SHARE"),
        "voice":"පුංචි නැණ මඟ. අපේ නාලිකාවට එක්වන්න. ලයික් කරලා අදහසක් ලියා මිතුරන්ට බෙදාහරින්න.",
    },
    ("youtube", "school"): {
        "platform":"YOUTUBE",
        "primary":"SUBSCRIBE",
        "secondary":("LIKE","SHARE"),
        # Child-directed videos may have commenting turned off by YouTube.
        "voice":"පුංචි නැණ මඟ. අපේ නාලිකාවට එක්වන්න. ලයික් කරලා මිතුරන්ට බෙදාහරින්න.",
    },
    ("facebook", "general"): {
        "platform":"FACEBOOK",
        "primary":"FOLLOW",
        "secondary":("LIKE","COMMENT","SHARE"),
        "voice":"පුංචි නැණ මඟ. අපේ පිටුව ෆොලෝ කරන්න. ලයික් කරලා අදහසක් ලියා මිතුරන්ට බෙදාහරින්න.",
    },
    ("facebook", "school"): {
        "platform":"FACEBOOK",
        "primary":"FOLLOW",
        "secondary":("LIKE","COMMENT","SHARE"),
        "voice":"පුංචි නැණ මඟ. පිටුව අනුගමනය කරන්න. ලයික් කරලා අදහසක් ලියා මිතුරන්ට බෙදාහරින්න.",
    },
}


def profile(platform,audience="school"):
    if (platform,audience) not in PROFILES:
        raise ValueError("CTA requires youtube/facebook and school/general audience")
    return PROFILES[(platform,audience)]


def probe_video(path, *, landscape_lesson=False):
    """Return supported dimensions, fps, audio and duration or fail closed."""
    p=Path(path)
    if not p.is_file() or p.stat().st_size<1000:
        raise ValueError("Original video missing or too small")
    x=subprocess.run(
        ["ffprobe","-v","error","-show_streams","-show_format",
         "-of","json",str(p)],
        capture_output=True,text=True,check=True,timeout=30)
    data=json.loads(x.stdout)
    videos=[s for s in data.get("streams",[]) if s.get("codec_type")=="video"]
    audios=[s for s in data.get("streams",[]) if s.get("codec_type")=="audio"]
    if len(videos)!=1 or not audios:
        raise RuntimeError("A single source video and audible soundtrack are required")
    w,h=int(videos[0]["width"]),int(videos[0]["height"])
    allowed_sizes = ((1280, 720),) if landscape_lesson else ((1080, 1920), (720, 1280))
    if (w,h) not in allowed_sizes:
        raise RuntimeError(f"Unexpected source resolution {w}x{h}; no outro added")
    fps=Fraction(videos[0].get("avg_frame_rate") or "24/1")
    if not 20<=float(fps)<=60:
        raise RuntimeError("Unexpected source frame rate")
    secs=float(data.get("format",{}).get("duration",0))
    if not 1 < secs <= (600 if landscape_lesson else 239.999):
        raise RuntimeError("Unexpected source duration")
    return w,h,float(fps),secs


def center(draw,y,text,face,color,width):
    width_text=mixed_width(draw,text,face)
    if width_text>width*.87:
        raise ValueError("CTA title overflow; no incorrectly clipped artwork")
    draw_mixed(draw,((width-width_text)//2,y),text,face,color)


def image_card(destination,platform="youtube",audience="school",size=(1080,1920)):
    """One 9:16 illustration, no network calls and no copyrighted imagery."""
    info=profile(platform,audience)
    w,h=size
    if (w,h) not in ((1080,1920),(720,1280)):
        raise ValueError("Unsupported CTA image resolution")
    scale=w/1080
    sx=lambda n:round(n*scale)
    # All coordinates scale equally with the 9:16 source aspect.
    im=Image.new("RGB",(w,h),"#082643")
    d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/max(h-1,1)
        d.line((0,y,w,y),
               fill=(round(6+9*t),round(26+26*t),round(57+31*t)))
    glow=Image.new("RGBA",(w,h),(0,0,0,0))
    gd=ImageDraw.Draw(glow)
    gd.ellipse((-sx(210),sx(330),sx(330),sx(920)),fill=(24,220,193,100))
    gd.ellipse((sx(760),-sx(190),sx(1360),sx(390)),fill=(39,97,244,130))
    glow=glow.filter(ImageFilter.GaussianBlur(sx(100)))
    im=Image.alpha_composite(im.convert("RGBA"),glow).convert("RGB")
    d=ImageDraw.Draw(im)

    icon=logo(sx(250)).convert("RGBA")
    mask=Image.new("L",icon.size,0)
    ImageDraw.Draw(mask).ellipse((sx(4),sx(4),icon.width-sx(4),icon.height-sx(4)),fill=255)
    icon.putalpha(mask)
    im.paste(icon,((w-icon.width)//2,sx(130)),icon)
    d=ImageDraw.Draw(im)
    center(d,sx(425),CHANNEL,font(sx(75),True),"#ffffff",w)
    center(d,sx(550),"තවත් දැනුමට අප හා එක්වන්න",font(sx(42),True),"#b5eff1",w)

    d.rounded_rectangle((sx(95),sx(705),sx(985),sx(828)),
                        radius=sx(28),fill=("#c43137" if platform=="youtube" else "#1978de"))
    d.text((w//2,sx(759)),info["primary"],font=latin_font(sx(69),True),
           fill="#ffffff",anchor="mm")
    sec=info["secondary"]
    x_margin=sx(85);gap=sx(17)
    item_width=(w-2*x_margin-(len(sec)-1)*gap)//len(sec)
    for ix,value in enumerate(sec):
        x=x_margin+ix*(item_width+gap)
        d.rounded_rectangle((x,sx(880),x+item_width,sx(1010)),
                            radius=sx(21),fill="#164e76",outline="#66d9cf",width=sx(3))
        text_size=36 if len(sec)==3 else 47
        d.text((x+item_width//2,sx(945)),value,
               font=latin_font(sx(text_size),True),fill="#ffffff",anchor="mm")
    center(d,sx(1130),"ඔබේ මිතුරන්ටත් බෙදාහරින්න",font(sx(48),True),"#ffdf85",w)
    center(d,sx(1280),
           ("අලුත් වීඩියෝ සඳහා අප සමඟ එක්වන්න" if audience=="general" else "තවත් නොමිලේ සිංහල පාඩම්"),
           font(sx(42),True),"#e3f5ff",w)
    d.rounded_rectangle((sx(95),sx(1510),sx(985),sx(1680)),
                        radius=sx(30),fill="#0d3559",outline="#2d9eae",width=sx(3))
    d.text((w//2,sx(1591)),BLOG,font=latin_font(sx(36)),
           anchor="mm",fill="#e0f7fb")
    d.text((w//2,sx(1785)),"PUNCHI NENA MAGA",
           font=latin_font(sx(33),True),anchor="mm",fill="#a6d7f3")
    target=Path(destination)
    target.parent.mkdir(parents=True,exist_ok=True)
    im.save(target,optimize=True)
    return target


def voice_for_outro(dest,platform,audience):
    from gtts import gTTS
    text=profile(platform,audience)["voice"]
    target=Path(dest)
    target.parent.mkdir(parents=True,exist_ok=True)
    gTTS(text=text,lang="si",slow=False,timeout=(5,30)).save(str(target))
    if not target.is_file() or target.stat().st_size<100:
        raise RuntimeError("CTA Sinhala narration missing")
    return target


def audio_length(path):
    r=subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1",str(path)],
        capture_output=True,text=True,check=True,timeout=30)
    return float(r.stdout.strip())


def append_outro(original,platform,audience="school",*,output=None):
    """Append branded voice card; use distinct output file to prevent double CTA."""
    profile(platform,audience)
    original=Path(original)
    if original.stem.endswith("-cta") or "-cta-" in original.stem:
        raise ValueError("Refuse adding outro twice; supply original source video")
    if output is None:
        output=original.with_name(original.stem+f"-{platform}-cta.mp4")
    output=Path(output)
    if original.resolve()==output.resolve():
        raise ValueError("Do not overwrite existing Facebook video")
    w,h,fps,original_secs=probe_video(original)
    outro_dir=output.parent/"cta-assets"/(original.stem+"-"+platform+"-"+audience)
    png=image_card(outro_dir/"outro.png",platform,audience,(w,h))
    voice=voice_for_outro(outro_dir/"outro-voice.mp3",platform,audience)
    outro_secs=round(audio_length(voice)+0.9,2)
    if not 2<outro_secs<=18:
        raise RuntimeError("CTA narration duration unexpected; do not trim speech")
    output.parent.mkdir(parents=True,exist_ok=True)
    fps_arg=f"{fps:.6f}"
    filters=(
        f"[0:v]fps={fps_arg},format=yuv420p,setsar=1,setpts=PTS-STARTPTS[v0];"
        f"[1:v]fps={fps_arg},trim=duration={outro_secs},"
        "format=yuv420p,setsar=1,setpts=PTS-STARTPTS[v1];"
        "[0:a:0]aresample=44100,aformat=channel_layouts=mono,asetpts=PTS-STARTPTS[a0];"
        f"[2:a:0]aresample=44100,aformat=channel_layouts=mono,"
        f"apad,atrim=duration={outro_secs},asetpts=PTS-STARTPTS[a1];"
        "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"
    )
    subprocess.run(
        ["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-i",str(original),"-loop","1","-framerate",fps_arg,
         "-i",str(png),"-i",str(voice),
         "-filter_complex",filters,"-map","[v]","-map","[a]",
         "-c:v","libx264","-preset","veryfast","-crf","18",
         "-c:a","aac","-b:a","128k",
         "-pix_fmt","yuv420p","-movflags","+faststart",
         "-shortest",str(output)],
        check=True,timeout=240)
    if not output.exists() or output.stat().st_size<10000:
        raise RuntimeError("Final branded MP4 missing")
    _,_,_,duration=probe_video(output)
    if duration<original_secs+outro_secs-2.5:
        raise RuntimeError("CTA appended video unexpectedly short")
    print(f"Added {platform} {audience} spoken outro: {output} (~{outro_secs}s)")
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--video",help="Original video to append (never modify original)")
    p.add_argument("--platform",choices=SUPPORTED_PLATFORMS,default="youtube")
    p.add_argument("--audience",choices=("school","general"),default="school")
    p.add_argument("--output")
    p.add_argument("--card-only",action="store_true")
    args=p.parse_args()
    if args.card_only:
        image_card(args.output or "school/output/cta-preview.png",args.platform,args.audience)
        print("CTA illustration saved; original video not changed.")
    else:
        if not args.video:
            p.error("--video is required unless --card-only")
        append_outro(args.video,args.platform,args.audience,output=args.output)


if __name__=="__main__":
    main()
