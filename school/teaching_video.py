"""Generate narrated Sinhala teaching videos."""
import random
import subprocess
import time
from datetime import date

from gtts import gTTS
from sinhala_speech import expand_currency
from gtts.tts import gTTSError
from PIL import Image, ImageDraw, ImageFont

from brand_assets import BOLD, FONT
from font_safety import mixed_width, draw_mixed
from video_cta import audio_length, probe_video
from lesson_topics import LESSONS


TOPICS = (
    ("ගුණ කිරීම", "එකම ප්‍රමාණය ඇති කණ්ඩායම් කිහිපයක් ගණන් කරන්න ගුණ කිරීම භාවිත කරනවා."),
    ("බෙදීම", "එකතුවක් සමාන කණ්ඩායම්වලට බෙදන විට එක් කණ්ඩායමකට ලැබෙන ප්‍රමාණය සොයන්න පුළුවන්."),
)
NUMBERS = ("බිංදුව", "එක", "දෙක", "තුන", "හතර", "පහ", "හය", "හත", "අට", "නවය")


ROTATION_START = date(2026, 11, 26)


def lesson(day: date):
    slot = (day - ROTATION_START).days % (len(LESSONS) + 2)
    if day >= ROTATION_START and slot < len(LESSONS):
        title, subject, chapter = LESSONS[slot]
        scenes = [(heading, text, None, False, 12) for heading, text in chapter]
        scenes.append(OUTRO)
        return title, subject, scenes
    title, scenes = mathematics_lesson(day)
    return title, "ගණිතය", scenes


OUTRO = (
    "පුංචි නැණ මඟ සමඟ ඉගෙන ගනිමු",
    "තවත් පාඩම් සඳහා පුංචි නැණ මඟ සබ්ස්ක්‍රයිබ් කරන්න. වීඩියෝවට ලයික් කරන්න. හැකි නම් ඔබේ පිළිතුර කමෙන්ට් කරන්න. අපේ ෆේස්බුක් පිටුවත් ෆලෝ කරන්න.",
    None, False, 3,
)


def mathematics_lesson(day: date):
    rng = random.Random(day.toordinal())
    division = day.toordinal() % 2
    title, rule = TOPICS[division]
    pairs = rng.sample([(a, b) for a in range(2, 8) for b in range(2, 9)], 10)
    scenes = [(title, f"අද පුංචි නැණ මඟ පාඩම {title} ගැනයි. {rule} රූපයේ වර්ණ බෝල ගණන් කරමින් අපි උදාහරණ බලමු.", None, False, 3)]
    for index, (a, b) in enumerate(pairs):
        total = a * b
        if division:
            question = f"වර්ණ බෝල {total} ක් කණ්ඩායම් {a} කට සමානව බෙදමු. එක් කණ්ඩායමකට වර්ණ බෝල කීයක් ලැබෙනවා ද?"
            solution = f"හැම කණ්ඩායමකටම එක බැගින් වර්ණ බෝල දෙන්න. වර්ණ බෝල අවසන් වන තුරු එහෙම බෙදාගෙන යන්න. දැන් එක් කණ්ඩායමක වර්ණ බෝල {NUMBERS[b]} ක් තියෙනවා. කණ්ඩායම් {a} ටම එකම ගණන ලැබිලා."
            formula = f"{total} ÷ {a} = {b}"
        else:
            question = f"එක් කණ්ඩායමක වර්ණ බෝල {b} ක් තියෙනවා. ඒ වගේ කණ්ඩායම් {a} ක වර්ණ බෝල කීයක් තියෙනවා ද?"
            solution = f"එක් එක් කණ්ඩායමේ වර්ණ බෝල {NUMBERS[b]} බැගින් තියෙනවා. ඒ නිසා {b} කියන ගණන {a} වතාවක් එකතු කරන්න. එකතුව {total} යි. රූපයේ වර්ණ බෝල එකින් එක ගණන් කර පිළිතුර පරීක්ෂා කරන්න."
            formula = f"{a} × {b} = {total}"
        heading = f"{index + 1}. " + ("උදාහරණය" if index < 3 else "ඔබම විසඳන්න")
        scenes.append((heading, question, (a, b), not division, 10))
        scenes.append((formula, solution, (a, b), True, 2))
    scenes.extend([
        ("අද පාඩම මතක් කරමු", f"{rule} ගෙදරදී කඩදාසි කැබලි යොදාගෙන මේ ගණන් තවත් පුහුණු වෙන්න.", None, False, 3),
        OUTRO,
    ])
    return title, scenes


def wrap(draw, text, font):
    lines = [""]
    for word in text.split():
        candidate = (lines[-1] + " " + word).strip()
        if lines[-1] and mixed_width(draw, candidate, font) > 1130:
            lines.append(word)
        else:
            lines[-1] = candidate
    return lines


def ball(draw, x, y, size, color="#e92760"):
    draw.ellipse((x+2,y+2,x+size-2,y+size-2),fill=color,outline="#25204b",width=max(1,size//25))
    draw.ellipse((x+size*.18,y+size*.12,x+size*.55,y+size*.36),fill="#ffffff")

def topic_panel(draw, box, heading):
    x,y,X,Y=box
    draw.rounded_rectangle(box,24,fill="#183d91",outline="#ffffff",width=3)
    draw.rounded_rectangle((x+10,y+10,X-10,y+28),8,fill="#6d9df5")
    for i in range(3):
        f=ImageFont.truetype(BOLD, max(18,min(42,(X-x)//20)),layout_engine=ImageFont.Layout.RAQM)
        words=heading.split()
        if i>=len(words): break
        draw_mixed(draw,(x+30,y+45+i*55),words[i],f,"#ffe34d")


def frame(path, scene, number, count):
    heading, narration, groups, reveal, _ = scene
    image = Image.new("RGB", (1280, 720), "#19265d")
    draw = ImageDraw.Draw(image)
    faces = [ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
             for path, size in ((BOLD, 30), (BOLD, 56), (FONT, 32))]
    draw.rounded_rectangle((24, 22, 1256, 478), 30, fill="#ffffff", outline="#76c9e8", width=3)
    draw.rounded_rectangle((44, 37, 1236, 104), 22, fill="#123da0")
    draw_mixed(draw, (72, 51), "පුංචි නැණ මඟ", faces[0], "#ffffff")
    heading_face = faces[1]
    while mixed_width(draw, heading, heading_face) > 1130 and heading_face.size > 30:
        heading_face = ImageFont.truetype(BOLD, heading_face.size - 2, layout_engine=ImageFont.Layout.RAQM)
    draw_mixed(draw, (72, 117), heading, heading_face, "#123da0")
    if groups:
        a, b = groups
        if reveal:
            colors = ("#fff0c7","#ffd8e8","#fce1ed","#e0edff")
            card_width = 1120 // a
            for group in range(a):
                x = 72 + group * card_width
                draw.rounded_rectangle((x, 213, x+card_width-8, 455), 18, fill=colors[group%4], outline="#6395c4", width=2)
                size = min(52, (card_width-22)//2)
                for index in range(b):
                    ball(draw, x+(card_width-8-2*size)//2+(index%2)*size, 224+(index//2)*55, size)
        else:
            # One bear per item; do not add any decorative animals to counting scenes.
            cols = min(14, a*b)
            rows = (a*b+cols-1)//cols
            size = min(76, 1120//cols-5, 230//rows-5)
            for index in range(a*b):
                ball(draw, 72+(index%cols)*(1120//cols), 214+(index//cols)*(230//rows), size)
    else:
        topic_panel(draw,(72,205,1208,451),heading)
    draw.rounded_rectangle((24, 488, 1256, 694), 24, fill="#fff0fa", outline="#ffcc22", width=2)
    y = 500
    for line in wrap(draw, narration, faces[2]):
        draw_mixed(draw, (72, y), line, faces[2], "#233753")
        y += 44
    if y > 720:
        raise RuntimeError("Lesson subtitle exceeds its safe area")
    draw.rectangle((44, 704, 44 + round(1192 * number / count), 709), fill="#e92760")
    image.save(path)


def portrait_frame(path, scene, number, count):
    heading, narration, groups, reveal, _ = scene
    image = Image.new("RGB", (720,1280), "#19265d")
    draw = ImageDraw.Draw(image)
    def face(size, bold=False):
        return ImageFont.truetype(BOLD if bold else FONT, size, layout_engine=ImageFont.Layout.RAQM)
    def lines(text, f, width):
        out = [""]
        for word in text.split():
            candidate = (out[-1] + " " + word).strip()
            if out[-1] and mixed_width(draw,candidate,f)>width:
                out.append(word)
            else:
                out[-1]=candidate
        return out
    draw.rounded_rectangle((24,35,696,1200),30,fill="#ffffff",outline="#76c9e8",width=3)
    draw.rounded_rectangle((44,58,676,140),22,fill="#123da0")
    draw_mixed(draw,(64,80),"පුංචි නැණ මඟ",face(34,True),"#ffffff")
    for size in (48,44,40,36,32,28):
        f=face(size,True)
        heading_lines=lines(heading,f,592)
        if len(heading_lines)<=3: break
    for i,line in enumerate(heading_lines):
        draw_mixed(draw,(64,167+i*58),line,f,"#123da0")
    top=350
    bottom=846
    if groups:
        a,b=groups
        if reveal:
            cols=min(3,a)
            rows=(a+cols-1)//cols
            cw=608//cols
            ch=(bottom-top)//rows
            colors=("#fff0c7","#ffd8e8","#fce1ed","#e0edff")
            for g in range(a):
                x=56+(g%cols)*cw
                y=top+(g//cols)*ch
                draw.rounded_rectangle((x,y,x+cw-8,y+ch-8),14,fill=colors[g%4],outline="#6395c4",width=2)
                inner_cols=min(4,b)
                inner_rows=(b+inner_cols-1)//inner_cols
                size=min((cw-20)//inner_cols,(ch-20)//inner_rows,88)
                for i in range(b):
                    ball(draw,x+(cw-8-inner_cols*size)//2+(i%inner_cols)*size,y+(ch-8-inner_rows*size)//2+(i//inner_cols)*size,size)
        else:
            cols=min(7,a*b)
            rows=(a*b+cols-1)//cols
            size=min(82,608//cols-3,(bottom-top)//rows-3)
            for i in range(a*b):
                ball(draw,56+(i%cols)*(608//cols),top+(i//cols)*((bottom-top)//rows),size)
    else:
        topic_panel(draw,(56,350,664,846),heading)
    draw.rounded_rectangle((44,865,676,1174),22,fill="#fff0fa",outline="#ffcc22",width=2)
    for size in (36,34,32,30,28,26,24):
        f=face(size)
        ls=lines(narration,f,580)
        step=round(size*1.48)
        if len(ls)*step<=270: break
    if len(ls)*step>270: raise RuntimeError("Portrait subtitle exceeds safe area")
    for i,line in enumerate(ls):
        draw_mixed(draw,(64,884+i*step),line,f,"#233753")
    draw.rectangle((44,1210,44+round(632*number/count),1218),fill="#e92760")
    image.save(path)

def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, args)],
                   check=True, timeout=240)


def render(scenes, folder, portrait=False, reuse_audio=None):
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    for index, scene in enumerate(scenes, 1):
        image = folder / f"scene-{index}.png"
        audio = folder / f"voice-{index}.mp3"
        clip = folder / f"lesson-{index}.mp4"
        (portrait_frame if portrait else frame)(image, scene, index, len(scenes))
        for attempt in range(3):
            try:
                if reuse_audio is not None:
                    import shutil
                    shutil.copyfile(reuse_audio / audio.name, audio)
                else:
                    gTTS(text=expand_currency(scene[1]), lang="si", slow=False, timeout=(8, 30)).save(str(audio))
                break
            except gTTSError:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        duration = audio_length(audio) + scene[-1]
        if len(scenes) == 13 and index < len(scenes):
            duration = max(25, duration)
        ffmpeg("-loop", 1, "-framerate", 24, "-i", image, "-i", audio,
               "-af", "apad", "-t", f"{duration:.3f}", "-c:v", "libx264",
               "-preset", "veryfast", "-tune", "stillimage", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-ar", 44100, "-ac", 1, clip)
        files.append(clip)
    manifest = folder / "lesson-clips.txt"
    manifest.write_text("".join(f"file '{clip.name}'\n" for clip in files), encoding="utf-8")
    result = folder / "teaching-video.mp4"
    ffmpeg("-f", "concat", "-safe", 0, "-i", manifest, "-c", "copy",
           "-movflags", "+faststart", result)
    if portrait:
        import json
        meta = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(result)]))
        video = next(s for s in meta['streams'] if s['codec_type']=='video')
        if (video['width'],video['height']) != (720,1280): raise RuntimeError('Portrait dimensions incorrect')
        if not any(s['codec_type']=='audio' for s in meta['streams']): raise RuntimeError('Missing audio')
        duration = float(meta['format']['duration'])
    else:
        _, _, _, duration = probe_video(result, landscape_lesson=True)
    if not 300 <= duration <= 600:
        raise RuntimeError(f"Lesson duration is {duration:.1f}s. Required range is 300–600s.")
    ffmpeg("-xerror", "-i", result, "-f", "null", "-")
    print(f"Teaching video decoded with Sinhala audio and subtitles, {duration:.1f} seconds")
    return result
