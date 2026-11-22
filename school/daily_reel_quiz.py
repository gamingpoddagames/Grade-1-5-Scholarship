"""Render a Sinhala quiz and optionally upload it to the authorized school Page."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont, ImageOps, features

from blogger_link_safety import FACEBOOK_LANDING_URL
from facebook_video import upload

FONT = Path('/usr/share/fonts/truetype/noto')
MANGO = ('Mango_(1).jpg', 'Renee Comet / NCI (public domain)')
EARTH = ('The_Earth_seen_from_Apollo_17.jpg', 'NASA / Apollo 17 (public domain)')
QUESTIONS = [
    (MANGO, 'අඹ අයිති මොන ඵල වර්ගයට ද?', 'ඩ්‍රූප්',
     'අඹ ගෙඩියේ බීජය වටා තද ආවරණයක් තියෙනවා.',
     'අඹ අයිති වෙන්නේ මොන ඵල වර්ගයට ද?',
     'නිවැරදි පිළිතුර, ඩ්‍රූප්. අඹ ගෙඩියේ බීජය වටා තද ආවරණයක් තියෙනවා.'),
    (EARTH, 'පෘථිවියට ස්වාභාවික චන්ද්‍රිකා කීයක් තියෙනවා ද?', 'එකයි',
     'ඒ අපේ සඳයි.', 'පෘථිවියට ස්වාභාවික චන්ද්‍රිකා කීයක් තියෙනවා ද?',
     'එකයි. ඒ අපේ සඳයි.'),
    (EARTH, 'පෘථිවියේ දවසක් ඇතිවන්නේ කොහොම ද?', 'පෘථිවිය කැරකෙන නිසා',
     'පෘථිවිය තමන්ගේ අක්ෂය වටා කැරකෙනවා.', 'පෘථිවියේ දවසක් ඇතිවන්නේ කොහොම ද?',
     'පෘථිවිය තමන්ගේ අක්ෂය වටා කැරකෙන නිසා දවල් සහ රෑ මාරුවෙන් මාරුවට එනවා.'),
    (MANGO, 'අඹ ගෙඩියක සාමාන්‍යයෙන් බීජ කීයක් තියෙනවා ද?', 'එකයි',
     'බීජය තියෙන්නේ තද ඇටය ඇතුළේ.', 'අඹ ගෙඩියක සාමාන්‍යයෙන් බීජ කීයක් තියෙනවා ද?',
     'එකයි. බීජය තියෙන්නේ තද ඇටය ඇතුළේ.'),
    (EARTH, 'සූර්යයාට ළඟින් පෘථිවිය කීවැනි ග්‍රහලෝකය ද?', 'තුන්වැනි ග්‍රහලෝකය',
     'බුධ සහ සිකුරු පෘථිවියට කලින් තියෙනවා.', 'සූර්යයාට ළඟින් පෘථිවිය කීවැනි ග්‍රහලෝකය ද?',
     'තුන්වැනි ග්‍රහලෝකය. මුලින් බුධ. ඊළඟට සිකුරු. ඉන් පස්සේ පෘථිවිය.'),
    (EARTH, 'පෘථිවියේ ඍතු වෙනස් වීමට ප්‍රධාන හේතුව මොකක් ද?', 'අක්ෂයේ ඇලය',
     'පෘථිවියේ අක්ෂය ඇල වී තිබෙනවා.', 'පෘථිවියේ ඍතු වෙනස් වීමට ප්‍රධාන හේතුව මොකක් ද?',
     'පෘථිවියේ අක්ෂය ඇල වෙලා තියෙනවා. පෘථිවිය සූර්යයා වටා යනකොට ඒ ඇලය නිසා උතුරු සහ දකුණු අර්ධ ගෝලවලට ලැබෙන හිරු එළිය වෙනස් වෙනවා.'),
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
    canvas = Image.new('RGB', (720, 1280), '#101f2d')
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((55, 100, 665, 770), 34, fill='#193347')
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
    label(135, 'පුංචි නැණ මඟ', 33, '#8ee1cb')
    label(215, question, 43)
    canvas.paste(picture, ((720-picture.width)//2, 390+(335-picture.height)//2))
    label(735, credit, 17, '#d5e7ed', latin=True)
    if stage == 'answer':
        label(811, 'නිවැරදි පිළිතුර', 29, '#8ee1cb')
        label(870, answer, 47, '#ffcf79')
        label(962, reason, 30)
    else:
        label(820, 'පිළිතුර හිතන්න', 30)
        draw.ellipse((293,880,427,1014), outline='#8ee1cb', width=7)
        label(900, stage if stage.isdigit() else '?', 72, '#ffcf79')
    canvas.save(path)


def render(row, output):
    (filename, credit), question, answer, reason, spoken_question, spoken_answer = row
    picture = photo(filename)
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        clips = []
        stages = [('question', spoken_question + ' ටිකක් හිතන්න.')]
        stages += [(str(i), '') for i in range(5, 0, -1)]
        stages += [('answer', spoken_answer)]
        for stage, speech in stages:
            image = folder / f'{stage}.png'
            frame(image, stage, picture, credit, question, answer, reason)
            audio = folder / f'{stage}.mp3'
            if speech:
                subprocess.run([sys.executable, '-m', 'edge_tts', '--voice', 'si-LK-ThiliniNeural',
                                '--rate=-10%', '--pitch=+6Hz', '--text', speech, '--write-media', str(audio)],
                               check=True, timeout=45)
                duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration',
                                                         '-of','csv=p=0',str(audio)])) + .45
                source = ['-i', audio]
            else:
                duration = 1
                source = ['-f','lavfi','-i','anullsrc=r=48000:cl=mono']
            clip = folder / f'{stage}.mp4'
            ffmpeg('-loop',1,'-framerate',30,'-i',image,*source,'-t',f'{duration:.3f}','-af','apad',
                   '-c:v','libx264','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-ar',48000,'-ac',1,clip)
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
        upload(output, page_id, token, version,
               title='පුංචි නැණ මඟ – සාමාන්‍ය දැනුම',
               description=f'{row[1]} තත්පර පහක් ඇතුළත හිතලා බලන්න.\n\nතවත් සිංහල පාඩම්\n{FACEBOOK_LANDING_URL}')


if __name__ == '__main__':
    main()
