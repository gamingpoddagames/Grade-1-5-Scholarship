#!/usr/bin/env python3
"""Curated, picture-first Sinhala quiz bank and shared photo rendering.

One topic/photo is selected for BOTH the Facebook image card and the video.
Only named, verified Wikimedia Commons files are used, never random search results.
A failed download must block a visual post instead of publishing unrelated art.
"""
from datetime import date
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import json

START = date(2026, 11, 22)
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "PunchiNenaMagaVisualQuiz/1.0 (educational; https://punchinanamaga.blogspot.com/)"

# Real photographs with stable Wikimedia Commons file titles; rights and credit
# are kept with each image. Original exam PDFs remain on their existing bank.
ITEMS = [
    {
        "topic": "ශ්‍රී ලංකාවේ සතුන්",
        "image_title": "Sri Lankan leopard - Panthera pardus kotiya.jpg",
        "image_credit": "Senthi Aathavan Senthilverl / Wikimedia Commons / CC BY-SA 4.0",
        "image_license": "CC BY-SA 4.0",
        "q": "පින්තූරයේ දැක්වෙන වන සත්වයා කුමක්ද?",
        "choices": ["ශ්‍රී ලංකා කොටියා", "ව්‍යාඝ්‍රයා", "සිංහයා", "හිවලා"],
        "answer": 0,
        "explanation": "මෙය ශ්‍රී ලංකාවට ආවේණික කොටි උපවිශේෂයකි.",
        "alternate": {
            "q": "මෙම සත්වයාගේ සිරුරේ ඇති රටාව කුමක්ද?",
            "choices": ["වටකුරු කළු ලප", "දිගු සුදු ඉරි", "නිල් තිත්", "රතු ඉරි"],
            "answer": 0,
            "explanation": "කොටියාගේ සම මත කළු ලපවලින් සෑදුණු රටාවක් ඇත."
        },
    },
    {
        "topic": "සත්ව ලෝකය",
        "image_title": "ElephantSriLanka.jpg",
        "image_credit": "Kvenkat07 / Wikimedia Commons / CC0",
        "image_license": "CC0",
        "q": "මෙම සත්වයාගේ හොඬය භාවිතා කළ හැක්කේ කුමකටද?",
        "choices": ["ගඳ දැනීමට", "පියාසර කිරීමට", "බිත්තර දැමීමට", "කූඩු තැනීමට"],
        "answer": 0,
        "explanation": "අලියාගේ හොඬය ගඳ දැනීමටත් දේවල් අල්ලාගැනීමටත් උපකාරී වේ.",
        "alternate": {
            "q": "මෙම සත්වයා අයත් කාණ්ඩය කුමක්ද?",
            "choices": ["ක්ෂීරපායින්", "පක්ෂීන්", "උරගයින්", "මත්ස්‍යයින්"],
            "answer": 0,
            "explanation": "අලියා ක්ෂීරපායී සත්වයෙකි."
        },
    },
    {
        "topic": "අභ්‍යවකාශය",
        "image_title": "Full Disk of Saturn.jpg",
        "image_credit": "NASA / Voyager 1 / Wikimedia Commons / Public Domain",
        "image_license": "Public Domain",
        "q": "රූපයේ දැක්වෙන වළලු සහිත ග්‍රහලෝකය කුමක්ද?",
        "choices": ["සෙනසුරු", "සිකුරු", "අඟහරු", "බුධ"],
        "answer": 0,
        "explanation": "මෙම රූපයේ දැක්වෙන්නේ සෙනසුරු ග්‍රහලෝකයයි.",
        "alternate": {
            "q": "සෙනසුරුගේ වළලු ප්‍රධාන වශයෙන් සෑදී ඇත්තේ කුමකින්ද?",
            "choices": ["හිම හා පාෂාණ කැබලි", "ගස් හා කොළ", "දියර ජලය", "වැලි කඳු"],
            "answer": 0,
            "explanation": "සෙනසුරුගේ වළලු අයිස් කැබලි හා පාෂාණ අංශුවලින් සෑදී ඇත."
        },
    },
    {
        "topic": "අපේ පෘථිවිය",
        "image_title": "The Earth seen from Apollo 17 (Original Orientation).jpg",
        "image_credit": "NASA / Apollo 17 / Wikimedia Commons / Public Domain",
        "image_license": "Public Domain",
        "q": "පින්තූරයේ පෙනෙන ග්‍රහලෝකය කුමක්ද?",
        "choices": ["පෘථිවිය", "නෙප්චූන්", "යුරේනස්", "අඟහරු"],
        "answer": 0,
        "explanation": "මෙය අභ්‍යවකාශයෙන් ඡායාරූපගත කළ පෘථිවියයි.",
        "alternate": {
            "q": "පෘථිවි මතුපිට වැඩි ප්‍රමාණයක් වැසී ඇත්තේ කුමකින්ද?",
            "choices": ["ජලයෙන්", "වැලිවලින්", "අයිස්වලින්", "වනාන්තරයෙන්"],
            "answer": 0,
            "explanation": "පෘථිවි මතුපිටින් සියයට හැත්තෑවකට ආසන්න ප්‍රමාණයක් ජලයෙන් වැසී ඇත."
        },
    },
    {
        "topic": "කෘමීන් හඳුනාගමු",
        "image_title": "Blue morpho.jpg",
        "image_credit": "Elsendor / Wikimedia Commons / Public Domain",
        "image_license": "Public Domain",
        "q": "නිල් පැහැති පියාපත් සහිත මෙම සත්වයා කුමක්ද?",
        "choices": ["සමනලයා", "බත්කූරා", "මී මැස්සා", "කූඹියා"],
        "answer": 0,
        "explanation": "මෙය නිල් මෝර්ෆෝ සමනල විශේෂයකි.",
        "alternate": {
            "q": "සමනලයාගේ ජීවන චක්‍රයේ බිත්තරයෙන් පසුව එන්නේ කුමක්ද?",
            "choices": ["දළඹුවා", "පියාපත්", "කෝෂය", "මල් පැණි"],
            "answer": 0,
            "explanation": "සමනල බිත්තරයෙන් මුලින්ම දළඹුවා බිහි වේ."
        },
    },
    {
        "topic": "සාගර ජීවීන්",
        "image_title": "Green Sea Turtle swimming.jpg",
        "image_credit": "RobertoCostaPinto / Wikimedia Commons / CC BY-SA 4.0",
        "image_license": "CC BY-SA 4.0",
        "q": "මුහුදේ පිහිනන මෙම සත්වයා කුමක්ද?",
        "choices": ["මුහුදු කැස්බෑවා", "ඩොල්ෆින්", "මුහුදු අශ්වයා", "මෝරා"],
        "answer": 0,
        "explanation": "මෙය මුහුදු කැස්බෑවෙකි. කැස්බෑවන් උරග සතුන් වේ.",
        "alternate": {
            "q": "මුහුදු කැස්බෑවා අයත් සත්ව කාණ්ඩය කුමක්ද?",
            "choices": ["උරගයින්", "මත්ස්‍යයින්", "පක්ෂීන්", "උභයජීවීන්"],
            "answer": 0,
            "explanation": "මුහුදු කැස්බෑවා මසුන් අතරට නොව උරගයින් අතරට අයත් වේ."
        },
    },
    {
        "topic": "ශ්‍රී ලංකාවේ පක්ෂීන්",
        "image_title": "Feeding Bee-eaters.jpg",
        "image_credit": "Chamara Ranathunga / Wikimedia Commons / CC BY-SA 4.0",
        "image_license": "CC BY-SA 4.0",
        "q": "රූපයේ දැක්වෙන මෙම පක්ෂීන් ආහාරයට ගන්නේ මොනවාද?",
        "choices": ["කෘමීන්", "කළුගල්", "ලුණු", "මැටි"],
        "answer": 0,
        "explanation": "මෙම බිඟුහර පක්ෂීන් මී මැස්සන් වැනි කෘමීන් ආහාරයට ගනී.",
        "alternate": {
            "q": "මෙවැනි පක්ෂීන්ගේ ශරීරය ආවරණය වී ඇත්තේ කුමකින්ද?",
            "choices": ["පිහාටුවලින්", "කොරපොතුවලින්", "ලොම්වලින්", "කටුවලින්"],
            "answer": 0,
            "explanation": "පක්ෂීන්ගේ සිරුර පිහාටුවලින් ආවරණය වී ඇත."
        },
    },
    {
        "topic": "ශ්‍රී ලංකාවේ උරුමය",
        "image_title": "Sri Lanka-Sigiriya-Rock.JPG",
        "image_credit": "Wikimedia Commons contributors / CC BY-SA 3.0",
        "image_license": "CC BY-SA 3.0",
        "q": "පින්තූරයේ දැක්වෙන ඓතිහාසික ස්ථානය කුමක්ද?",
        "choices": ["සීගිරිය", "මිහින්තලය", "යාපහුව", "රිටිගල"],
        "answer": 0,
        "explanation": "මෙම ගල් පර්වත බලකොටුව සීගිරියයි.",
        "alternate": {
            "q": "සීගිරිය පිහිටා ඇත්තේ ශ්‍රී ලංකාවේ කුමන දිස්ත්‍රික්කයේද?",
            "choices": ["මාතලේ", "යාපනය", "ගාල්ල", "මඩකලපුව"],
            "answer": 0,
            "explanation": "සීගිරිය පිහිටා ඇත්තේ මාතලේ දිස්ත්‍රික්කයේය."
        },
    },
]


def select(day):
    """16 distinct question-and-image combinations before the quiz text repeats."""
    if isinstance(day, str):
        day = date.fromisoformat(day)
    offset = (day - START).days
    item = dict(ITEMS[(offset // 1) % len(ITEMS)])
    # Use the alternate question on the second cycle of 8 photographs.
    if (offset // len(ITEMS)) % 2:
        item.update(item["alternate"])
    item.pop("alternate", None)
    item["grade"] = 5
    item["format"] = "visual"
    return item


def image_page(item):
    from urllib.parse import quote
    return "https://commons.wikimedia.org/wiki/File:" + quote(item["image_title"].replace(" ", "_"))


def image_credit(item):
    return item["image_credit"] + " (photo cropped for layout)"


def photo(item, size):
    """Get only the specifically curated photograph; reject unrelated/broken results."""
    from PIL import Image, ImageOps
    params = urlencode({
        "action": "query", "format": "json", "prop": "imageinfo",
        "iiprop": "url", "iiurlwidth": "1200",
        "titles": "File:" + item["image_title"],
    })
    req = Request(COMMONS_API + "?" + params, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=35) as response:
        payload = json.load(response)
    pages = payload.get("query", {}).get("pages", {})
    imageinfo = next((p.get("imageinfo", []) for p in pages.values() if "missing" not in p), [])
    if not imageinfo:
        raise RuntimeError("Approved Commons quiz image not available: " + item["image_title"])
    info = imageinfo[0]
    url = info.get("thumburl") or info.get("url")
    host = (urlsplit(url).hostname or "") if url else ""
    if host not in {"upload.wikimedia.org", "thumb.wikimedia.org"}:
        raise RuntimeError("Untrusted visual quiz image source")
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=50) as response:
        raw = response.read(12_000_001)
    if len(raw) < 10000 or len(raw) > 12_000_000:
        raise RuntimeError("Approved visual quiz photo invalid or too large")
    with Image.open(BytesIO(raw)) as source:
        source.load()
        if source.width < 300 or source.height < 220:
            raise RuntimeError("Visual quiz photo has insufficient resolution")
        return ImageOps.fit(source.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.45))


def _wrap(draw, text, face, width):
    from font_safety import mixed_width
    lines, current = [], ""
    for word in str(text).split():
        test = (current + " " + word).strip()
        if mixed_width(draw, test, face) <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _write(draw, text, x, y, face, fill, width, line_height):
    from font_safety import draw_mixed
    for s in _wrap(draw, text, face, width):
        draw_mixed(draw, (x, y), s, face, fill)
        y += line_height
    return y


def draw_card(item, target):
    """1080 x 1350 Facebook photo with the question and all answers legible."""
    from PIL import Image, ImageDraw
    from brand_assets import font, latin_font, logo
    from font_safety import draw_mixed
    if len(item["choices"]) != 4 or not 0 <= item["answer"] < 4:
        raise ValueError("A visual quiz needs four choices and one valid answer")
    artwork = photo(item, (932, 490))
    canvas = Image.new("RGB", (1080, 1350), "#eaf7fb")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((36, 35, 1044, 1320), 36, fill="#ffffff")
    d.rounded_rectangle((36, 35, 1044, 242), 36, fill="#083f70")
    canvas.paste(logo(140).resize((138, 138)), (73, 72))
    draw_mixed(d, (231, 83), "පුංචි නැණ මඟ", font(56, True), "#ffffff")
    d.text((236, 173), "SINHALA PICTURE QUIZ", font=latin_font(29), fill="#9be7e1")
    canvas.paste(artwork, (74, 264))
    d.rectangle((74, 730, 1006, 754), fill="#083f70")
    d.text((88, 732), "Photo: " + item["image_credit"][:90], font=latin_font(16), fill="#ffffff")
    draw_mixed(d, (101, 782), item["topic"], font(30, True), "#087b74")
    question_face = next((font(s, True) for s in (42, 37, 33, 30)
                          if len(_wrap(d, item["q"], font(s, True), 865)) <= 2), font(29, True))
    qlines = _wrap(d, item["q"], question_face, 865)
    if len(qlines) > 2:
        raise ValueError("Visual question too long for the photo card")
    _write(d, item["q"], 105, 829, question_face, "#123454", 865, 51)
    for i, choice in enumerate(item["choices"]):
        top = 951 + i * 72
        d.rounded_rectangle((94, top, 986, top+63), 15, fill="#f1f8ff", outline="#c4deee", width=2)
        line = f"{chr(65+i)}) {choice}"
        face = next((font(sz) for sz in (31, 28, 25)
                     if len(_wrap(d, line, font(sz), 830)) == 1), font(24))
        if len(_wrap(d, line, face, 830)) > 1:
            raise ValueError("Visual answer too wide for card")
        draw_mixed(d, (122, top+11), line, face, "#173c5c")
    d.rounded_rectangle((94, 1250, 986, 1300), 14, fill="#0d8079")
    draw_mixed(d, (138, 1257), "පිළිතුර සිතා බලන්න!", font(29, True), "#ffffff")
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, optimize=True)
    print("Original Sinhala visual quiz card:", target, item["image_title"])


def render_video(item, outdir):
    """Use the SAME photo and question as the daily image post for both frames."""
    from PIL import Image, ImageDraw
    from brand_assets import font, latin_font
    from font_safety import draw_mixed
    import subprocess
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    artwork = photo(item, (928, 603))
    for ix, reveal in enumerate((False, True)):
        im = Image.new("RGB", (1080, 1920), "#071e3a")
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((49, 72, 1031, 1850), 36, fill="#12375d")
        draw_mixed(d, (108, 125), "පුංචි නැණ මඟ", font(60, True), "#ffffff")
        draw_mixed(d, (110, 251), item["topic"], font(37, True), "#81ece0")
        im.paste(artwork, (76, 338))
        d.rectangle((76, 914, 1004, 941), fill="#083f70")
        d.text((91, 916), "Photo: " + item["image_credit"][:91], font=latin_font(16), fill="#ffffff")
        qface = next((font(s, True) for s in (49, 44, 40, 36)
                      if len(_wrap(d, item["q"], font(s, True), 840)) <= 2), font(34, True))
        if len(_wrap(d, item["q"], qface, 840)) > 2:
            raise ValueError("Question too long for visual Reel")
        _write(d, item["q"], 110, 981, qface, "#ffffff", 840, 67)
        for i, ch in enumerate(item["choices"]):
            top = 1185 + 116 * i
            fill = "#12866b" if reveal and i == item["answer"] else "#244f79"
            d.rounded_rectangle((93, top, 989, top+99), 17, fill=fill)
            line = f"{chr(65+i)}) {ch}"
            face = next((font(s) for s in (40, 36, 32)
                         if len(_wrap(d, line, font(s), 815)) == 1), font(30))
            if len(_wrap(d, line, face, 815)) > 1:
                raise ValueError("Answer does not fit in visual Reel")
            draw_mixed(d, (133, top+22), line, face, "#ffffff")
        footer = ("නිවැරදි පිළිතුර: " + chr(65+item["answer"])) if reveal else "පිළිතුර සිතන්න..."
        draw_mixed(d, (112, 1710), footer, font(42, True), "#91f3c2" if reveal else "#ffd778")
        d.text((110, 1830), "Punchi Nena Maga | Free Sinhala Learning", font=latin_font(26), fill="#e0eafb")
        im.save(outdir / f"frame-{ix}.png")
    manifest = outdir / "frames.txt"
    manifest.write_text(
        "file 'frame-0.png'\nduration 6\nfile 'frame-1.png'\nduration 5\nfile 'frame-1.png'\n", encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
        "-safe", "0", "-i", manifest.name, "-vf", "fps=24,format=yuv420p",
        "-movflags", "+faststart", "-c:v", "libx264", "-preset", "veryfast",
        "grade5-quiz.mp4"
    ], cwd=outdir, check=True, timeout=180)
    print("Photo-led visual quiz frames and video generated:", item["image_title"])
