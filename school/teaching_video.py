"""Generate narrated Sinhala teaching videos."""
import random
import subprocess
import time
from datetime import date

from gtts import gTTS
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
    scenes = [(title, f"අද පුංචි නැණ මඟ පාඩම {title} ගැනයි. {rule} රූපයේ තිත් ගණන් කරමින් අපි උදාහරණ බලමු.", None, False, 3)]
    for index, (a, b) in enumerate(pairs):
        total = a * b
        if division:
            question = f"තිත් {total} ක් කණ්ඩායම් {a} කට සමානව බෙදමු. එක් කණ්ඩායමකට තිත් කීයක් ලැබෙනවා ද?"
            solution = f"හැම කණ්ඩායමකටම එක බැගින් තිත් දෙන්න. තිත් අවසන් වන තුරු එහෙම බෙදාගෙන යන්න. දැන් එක් කණ්ඩායමක තිත් {NUMBERS[b]} ක් තියෙනවා. කණ්ඩායම් {a} ටම එකම ගණන ලැබිලා."
            formula = f"{total} ÷ {a} = {b}"
        else:
            question = f"එක් කණ්ඩායමක තිත් {b} ක් තියෙනවා. ඒ වගේ කණ්ඩායම් {a} ක තිත් කීයක් තියෙනවා ද?"
            solution = f"එක් එක් කණ්ඩායමේ තිත් {NUMBERS[b]} බැගින් තියෙනවා. ඒ නිසා {b} කියන ගණන {a} වතාවක් එකතු කරන්න. එකතුව {total} යි. රූපයේ තිත් එකින් එක ගණන් කර පිළිතුර පරීක්ෂා කරන්න."
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


def frame(path, scene, number, count):
    heading, narration, groups, reveal, _ = scene
    image = Image.new("RGB", (1280, 720), "#101827")
    draw = ImageDraw.Draw(image)
    faces = [ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
             for path, size in ((BOLD, 30), (BOLD, 56), (FONT, 32))]
    draw.rounded_rectangle((44, 36, 1236, 475), 25, fill="#1c2e45")
    draw_mixed(draw, (72, 56), "පුංචි නැණ මඟ", faces[0], "#8ee1cb")
    draw_mixed(draw, (72, 118), heading, faces[1], "#ffcf79")
    if not groups:
        for index in range(count):
            x = 72 + index * min(85, 1100 // count)
            color = "#ffcf79" if index == number - 1 else "#36546c"
            draw.rounded_rectangle((x, 340, x + 36, 352), 5, fill=color)
    if groups:
        a, b = groups
        if reveal:
            for group in range(a):
                x = 72 + group * 155
                draw.rounded_rectangle((x, 225, x + 135, 412), 18, outline="#8ee1cb", width=3)
                for index in range(b):
                    dx, dy = x + 23 + (index % 2) * 55, 244 + (index // 2) * 39
                    draw.ellipse((dx, dy, dx + 24, dy + 24), fill="#ffcf79")
        else:
            for index in range(a * b):
                x, y = 84 + (index % 16) * 65, 224 + (index // 16) * 49
                draw.ellipse((x, y, x + 26, y + 26), fill="#ffcf79")
    y = 496
    for line in wrap(draw, narration, faces[2]):
        draw_mixed(draw, (72, y), line, faces[2], "#fff4df")
        y += 44
    if y > 708:
        raise RuntimeError("Lesson subtitle exceeds its safe area")
    draw.rectangle((44, 704, 44 + round(1192 * number / count), 709), fill="#8ee1cb")
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
                gTTS(text=scene[1], lang="si", slow=False, timeout=(8, 30)).save(str(audio))
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
