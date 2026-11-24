"""Render a Sinhala quiz and optionally upload it to the authorized school Page."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont, ImageOps, features

from blogger_link_safety import FACEBOOK_LANDING_URL
from facebook_video import upload

FONT = Path('/usr/share/fonts/truetype/noto')
EARTH = ('The_Earth_seen_from_Apollo_17.jpg', 'NASA / Apollo 17')
MARS = ('Mars_Valles_Marineris.jpeg', 'NASA / JPL-Caltech')
SHUTTLE = ('STS120LaunchHiRes-edit1.jpg', 'NASA / STS-120')
GALAXY = ('Hubble2005-01-barred-spiral-galaxy-NGC1300.jpg', 'NGC 1300 | NASA / ESA / Hubble')
QUESTIONS = [
    (EARTH, 'ලෝකයේ විශාලම සාගරය මොකක් ද?', 'පැසිෆික් සාගරය',
     'ලෝකයේ විශාලම සාගරය පැසිෆික් සාගරයයි.'),
    (MARS, 'රතු ග්‍රහලෝකය කියන්නේ මොන ග්‍රහලෝකයට ද?', 'අඟහරු',
     'එහි මතුපිට යකඩ ඔක්සයිඩ් නිසා රතු පාටින් පේනවා.'),
    (GALAXY, 'අපේ සූර්යයා තියෙන්නේ මොන මන්දාකිණියේ ද?', 'ක්ෂීරපථයේ',
     'අපේ සූර්යයාත් ඒ මන්දාකිණියේ තරුවක්.'),
    (SHUTTLE, 'රොකට්ටුවක් ගුවන්ගත වෙන්නේ කොහොම ද?', 'වායුව පහළට වේගයෙන් පිට කරලා',
     'වායුව පහළට යද්දී රොකට්ටුව ඉහළට තල්ලු වෙනවා.'),
    (EARTH, 'ලෝකයේ විශාලම මහද්වීපය මොකක් ද?', 'ආසියාව',
     'ශ්‍රී ලංකාවත් ආසියාවට අයිතියි.'),
    (MARS, 'අඟහරු වටා සඳවල් කීයක් යනවා ද?', 'දෙකයි',
     'අඟහරු වටා සඳවල් දෙකක් ගමන් කරනවා.'),
    (EARTH, 'පෘථිවියේ දවල් සහ රෑ මාරු වෙන්නේ ඇයි?', 'පෘථිවිය කැරකෙන නිසා',
     'සූර්යයාට මුහුණ දෙන පැත්තට දවල්. අනෙක් පැත්තට රෑ.'),
    (EARTH, 'පෘථිවිය වටා යන අපට රෑට පෙනෙන වස්තුව මොකක් ද?', 'සඳ',
     'සඳ පෘථිවිය වටා ගමන් කරනවා.'),
    (GALAXY, 'මන්දාකිණියක් කියන්නේ මොකක් ද?', 'තරු විශාල සමූහයක්',
     'තරු සමඟ වායු සහ දූවිලිත් එහි තියෙනවා.'),
    (EARTH, 'පෘථිවියේ දකුණු ධ්‍රැවය තියෙන්නේ මොන මහද්වීපයේ ද?', 'ඇන්ටාක්ටිකාවේ',
     'එය පෘථිවියේ දකුණු කෙළවරේ තියෙනවා.'),
    (MARS, 'පෘථිවියට පස්සේ සූර්යයාගෙන් ඈතට හමුවන ග්‍රහලෝකය මොකක් ද?', 'අඟහරු',
     'පෘථිවිය තුන්වැනියි. අඟහරු හතරවැනියි.'),
    (EARTH, 'පෘථිවියේ කාල හතර වෙනස් වෙන්නේ ඇයි?', 'පෘථිවියේ කැරකෙන අක්ෂය ඇල නිසා',
     'පෘථිවිය සූර්යයා වටා යද්දී ඒ ඇලය නිසා ලැබෙන හිරු එළිය වෙනස් වෙනවා.'),
]


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True, timeout=90)


def photo(filename):
    digest = hashlib.md5(filename.encode()).hexdigest()
    url = f'https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{urllib.parse.quote(filename)}'
    request = urllib.request.Request(url, headers={'User-Agent': 'PunchiNenaMagaEducationalQuiz/1.0 (https://punchinanamaga.blogspot.com/)'})
    with urllib.request.urlopen(request, timeout=35) as response:
        return ImageOps.contain(Image.open(response_bytes(response)).convert('RGB'), (480, 335))


def response_bytes(response):
    from io import BytesIO
    return BytesIO(response.read())


def frame(path, stage, picture, credit, question, answer, reason):
    canvas = Image.new('RGB', (720, 1280), '#101827')
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((55, 100, 665, 770), 34, fill='#1c2e45')
    def label(y, message, size, color='#fff4df', latin=False):
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf' if latin else str(FONT/'NotoSansSinhala-Bold.ttf'), size)
        lines = ['']
        for word in message.split():
            candidate = (lines[-1] + ' ' + word).strip()
            if lines[-1] and draw.textlength(candidate, font=font, language='si') > 540:
                lines.append(word)
            else:
                lines[-1] = candidate
        for line in lines:
            draw.text((360,y), line, font=font, anchor='mt', fill=color, language='si')
            y += int(size * 1.4)
    label(135, 'පුංචි නැණ මඟ   ලෝක දැනුම', 28, '#8ee1cb')
    label(220, question, 38)
    canvas.paste(picture, ((720-picture.width)//2, 390+(335-picture.height)//2))
    label(735, credit, 17, '#d5e7ed', latin=True)
    if stage == 'answer':
        label(811, 'නිවැරදි පිළිතුර', 29, '#8ee1cb')
        label(870, answer, 40, '#ffcf79')
        label(990, reason, 30)
    else:
        label(820, 'පිළිතුර හිතන්න', 30)
        draw.ellipse((293,880,427,1014), outline='#8ee1cb', width=7)
        label(900, stage if stage.isdigit() else '?', 72, '#ffcf79', latin=True)
    canvas.save(path)


def narration(question, answer, reason):
    # Match the news bulletin's complete sentences without quiz-specific comma cues.
    return f'{question} පිළිතුර හිතන්න.', f'{answer}. {reason}'


def render(row, output):
    (filename, credit), question, answer, reason = row
    picture = photo(filename)
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        clips = []
        spoken_question, spoken_answer = narration(question, answer, reason)
        stages = [('question', spoken_question)]
        stages += [(str(i), '') for i in range(5, 0, -1)]
        stages += [('answer', spoken_answer)]
        for stage, speech in stages:
            image = folder / f'{stage}.png'
            frame(image, stage, picture, credit, question, answer, reason)
            audio = folder / f'{stage}.mp3'
            if speech:
                gTTS(text=' '.join(speech.split()), lang='si', slow=False, timeout=(5, 30)).save(str(audio))
                duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration',
                                                         '-of','csv=p=0',str(audio)])) + .45
                source = ['-i', audio]
            else:
                duration = 1
                source = ['-f','lavfi','-i','anullsrc=r=48000:cl=mono']
            clip = folder / f'{stage}.mp4'
            ffmpeg('-loop',1,'-framerate',30,'-i',image,*source,'-t',f'{duration:.3f}','-af','apad',
                   '-c:v','libx264','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-ar',48000,'-ac',1,clip)
            clips.append(clip)
        manifest = folder/'clips.txt'
        manifest.write_text(''.join(f"file '{clip.name}'\n" for clip in clips))
        ffmpeg('-f','concat','-safe',0,'-i',manifest,'-c','copy','-movflags','+faststart',output)
        ffmpeg('-i',output,'-f','null','-')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--slot', required=True, type=int, choices=(0, 1, 2))
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    if not features.check('raqm'):
        raise RuntimeError('Sinhala shaping requires Pillow RAQM')
    today = datetime.now(ZoneInfo('Asia/Colombo')).date()
    row = QUESTIONS[((today - date(2026,11,22)).days * 3 + args.slot) % len(QUESTIONS)]
    output = Path('daily_reels') / f'sinhala-quiz-{today}-{args.slot+1}.mp4'
    output.parent.mkdir(exist_ok=True)
    render(row, output)
    # Original Facebook video remains intact; only an outro is appended to a copy.
    from video_cta import append_outro
    publish_movie = append_outro(output, "facebook", "school")
    if args.publish:
        page_id = os.getenv('FB_PAGE_ID', '').strip()
        token = os.getenv('FB_PAGE_ACCESS_TOKEN', '').strip()
        version = os.getenv('FB_GRAPH_VERSION', 'v27.0')
        if not page_id.isdecimal() or not token:
            raise RuntimeError('Facebook Page ID or Page token is missing or invalid')
        request = urllib.request.Request(
            f'https://graph.facebook.com/{version}/{page_id}?fields=id,name',
            headers={'Authorization': f'Bearer {token}'},
        )
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                page = json.load(response)
        except urllib.error.URLError:
            raise RuntimeError('Could not verify the configured Facebook Page') from None
        if 'පුංචි නැණ මඟ' not in page.get('name', ''):
            raise RuntimeError('Facebook Page does not match Punchi Nena Maga')
        print('Verified Facebook Page:', page['name'])
        upload(publish_movie, page_id, token, version,
               title='පුංචි නැණ මඟ – සාමාන්‍ය දැනුම',
               description=f'{row[1]} තත්පර පහක් ඇතුළත හිතලා බලන්න.\n\nතවත් සිංහල පාඩම්\n{FACEBOOK_LANDING_URL}')


if __name__ == '__main__':
    main()
