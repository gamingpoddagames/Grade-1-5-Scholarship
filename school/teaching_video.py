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
    scenes = [(title, f"අද පුංචි නැණ මඟ පාඩම {title} ගැනයි. {rule} රූපයේ වලස් රූප ගණන් කරමින් අපි උදාහරණ බලමු.", None, False, 3)]
    for index, (a, b) in enumerate(pairs):
        total = a * b
        if division:
            question = f"වලස් රූප {total} ක් කණ්ඩායම් {a} කට සමානව බෙදමු. එක් කණ්ඩායමකට වලස් රූප කීයක් ලැබෙනවා ද?"
            solution = f"හැම කණ්ඩායමකටම එක බැගින් වලස් රූප දෙන්න. වලස් රූප අවසන් වන තුරු එහෙම බෙදාගෙන යන්න. දැන් එක් කණ්ඩායමක වලස් රූප {NUMBERS[b]} ක් තියෙනවා. කණ්ඩායම් {a} ටම එකම ගණන ලැබිලා."
            formula = f"{total} ÷ {a} = {b}"
        else:
            question = f"එක් කණ්ඩායමක වලස් රූප {b} ක් තියෙනවා. ඒ වගේ කණ්ඩායම් {a} ක වලස් රූප කීයක් තියෙනවා ද?"
            solution = f"එක් එක් කණ්ඩායමේ වලස් රූප {NUMBERS[b]} බැගින් තියෙනවා. ඒ නිසා {b} කියන ගණන {a} වතාවක් එකතු කරන්න. එකතුව {total} යි. රූපයේ වලස් රූප එකින් එක ගණන් කර පිළිතුර පරීක්ෂා කරන්න."
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


def bear(draw, x, y, size, color="#cb8859"):
    """Original vector teddy; one complete silhouette equals one counted item."""
    def ellipse(box, fill):
        draw.ellipse(tuple(round(v * size / 100 + (x if i % 2 == 0 else y)) for i, v in enumerate(box)), fill=fill)
    ellipse((8,4,34,31),color)
    ellipse((66,4,92,31),color)
    ellipse((16,12,84,68),color)
    ellipse((27,57,73,92),color)
    ellipse((9,59,33,81),color)
    ellipse((67,59,91,81),color)
    ellipse((22,79,46,99),color)
    ellipse((54,79,78,99),color)
    ellipse((34,39,66,59),"#fff0d7")
    ellipse((29,31,37,40),"#35253b")
    ellipse((63,31,71,40),"#35253b")
    ellipse((45,43,55,50),"#35253b")


def frame(path, scene, number, count):
    heading, narration, groups, reveal, _ = scene
    image = Image.new("RGB", (1280, 720), "#dff5ff")
    draw = ImageDraw.Draw(image)
    faces = [ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
             for path, size in ((BOLD, 30), (BOLD, 56), (FONT, 32))]
    draw.rounded_rectangle((24, 22, 1256, 478), 30, fill="#ffffff", outline="#76c9e8", width=3)
    draw.rounded_rectangle((44, 37, 1236, 104), 22, fill="#164b81")
    draw_mixed(draw, (72, 51), "පුංචි නැණ මඟ", faces[0], "#ffffff")
    heading_face = faces[1]
    while mixed_width(draw, heading, heading_face) > 1130 and heading_face.size > 30:
        heading_face = ImageFont.truetype(BOLD, heading_face.size - 2, layout_engine=ImageFont.Layout.RAQM)
    draw_mixed(draw, (72, 117), heading, heading_face, "#164b81")
    if groups:
        a, b = groups
        if reveal:
            colors = ("#fff0c7","#e4f7d7","#fce1ed","#e0edff")
            card_width = 1120 // a
            for group in range(a):
                x = 72 + group * card_width
                draw.rounded_rectangle((x, 213, x+card_width-8, 455), 18, fill=colors[group%4], outline="#6395c4", width=2)
                size = min(52, (card_width-22)//2)
                for index in range(b):
                    bear(draw, x+(card_width-8-2*size)//2+(index%2)*size, 224+(index//2)*55, size)
        else:
            # One bear per item; do not add any decorative animals to counting scenes.
            cols = min(14, a*b)
            rows = (a*b+cols-1)//cols
            size = min(76, 1120//cols-5, 230//rows-5)
            for index in range(a*b):
                bear(draw, 72+(index%cols)*(1120//cols), 214+(index//cols)*(230//rows), size)
    else:
        # Decorate only non-counting slides so extra mascots never confuse answers.
        draw.rounded_rectangle((72, 205, 1208, 451), 24, fill="#fff1ce")
        for x, color in ((220,"#d9915e"),(548,"#b783bb"),(876,"#79b4ae")):
            bear(draw, x, 229, 196, color)
    draw.rounded_rectangle((24, 488, 1256, 694), 24, fill="#fff9e8", outline="#f2c75c", width=2)
    y = 500
    for line in wrap(draw, narration, faces[2]):
        draw_mixed(draw, (72, y), line, faces[2], "#233753")
        y += 44
    if y > 720:
        raise RuntimeError("Lesson subtitle exceeds its safe area")
    draw.rectangle((44, 704, 44 + round(1192 * number / count), 709), fill="#278eae")
    image.save(path)

def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, args)],
                   check=True, timeout=240)


def render(scenes, folder):
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    for index, scene in enumerate(scenes, 1):
        image = folder / f"scene-{index}.png"
        audio = folder / f"voice-{index}.mp3"
        clip = folder / f"lesson-{index}.mp4"
        frame(image, scene, index, len(scenes))
        for attempt in range(3):
            try:
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
    _, _, _, duration = probe_video(result, landscape_lesson=True)
    if not 300 <= duration <= 600:
        raise RuntimeError(f"Lesson duration is {duration:.1f}s. Required range is 300–600s.")
    ffmpeg("-xerror", "-i", result, "-f", "null", "-")
    print(f"Teaching video decoded with Sinhala audio and subtitles, {duration:.1f} seconds")
    return result
