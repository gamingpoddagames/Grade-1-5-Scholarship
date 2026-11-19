#!/usr/bin/env python3
"""Create transparent monetization-readiness/help pages without collecting children's data.
Advertising is intentionally OFF pending valid site/account approval and child-directed compliance.
"""
from pathlib import Path
import html
import os
import re

BASE="https://gamingpoddagames.github.io/Grade-1-5-Scholarship/"
FB="https://www.facebook.com/profile.php?id=61596326146776"
CSS="""body{font-family:'Noto Sans Sinhala','Nirmala UI',sans-serif;max-width:890px;line-height:1.85;margin:auto;padding:22px;background:#f2f8fc;color:#183654}header,article{background:#fff;border-radius:18px;padding:24px;margin-bottom:18px;box-shadow:0 4px 18px #10385015}h1{color:#115e98}h2{color:#087a76}a{color:#086ca5}nav a{margin-right:15px}.notice{border-left:4px solid #087a76;background:#eff8f4;padding:12px 18px}"""
PAGES=[
("contact","සම්බන්ධ වන්න",[
("දෙමාපියන් සහ ගුරුවරුන් සඳහා","ප්‍රශ්න පත්‍රයක දෝෂයක්, පිළිතුරක ගැටලුවක් හෝ අන්තර්ගතය පිළිබඳ යෝජනාවක් දැනුම් දීමට අපගේ නිල Facebook Page වෙත පුද්ගලික පණිවිඩයක් යවන්න."),
("සම්බන්ධතා මාර්ගය",f'<a href="{FB}" rel="noopener noreferrer">පුංචි නැණ මඟ — නිල Facebook Page</a>'),
("දරුවන්ගේ පෞද්ගලිකත්වය","දරුවෙකුගේ නම, පාසල, උපන්දිනය, දුරකථන අංකය, ලිපිනය, ඡායාරූප හෝ වෙනත් පෞද්ගලික තොරතුරු පණිවිඩවල එවන්න එපා. දෝෂය වචන මඟින් හෝ ප්‍රශ්න අංකයෙන් පමණක් පෙන්වන්න."),
("පිළිතුරු කාලය","මෙය නොමිලේ අධ්‍යාපනික ව්‍යාපෘතියකි. ප්‍රතිචාර ලබාදෙන කාලය ස්ථාවර නැත.")]),
("support","ව්‍යාපෘතියට සහය වීම සහ මුදල් උපයන ආකාරය",[
("දැනට නොමිලේ","1–5 ශ්‍රේණි පුහුණු ප්‍රශ්න, පිළිතුරු PDF සහ Quiz නොමිලේ පවතී. ප්‍රශ්න බලන්න හෝ බාගන්න ගෙවීමක් අවශ්‍ය නැත."),
("වෙළඳ දැන්වීම් තත්ත්වය","දැනට වෙබ් අඩවියේ AdSense හෝ තෙවන පාර්ශ්ව advertising code ක්‍රියාත්මක කර නැත. අනාගතයේ දැන්වීම් පෙන්වීම සඳහා Google අනුමැතිය, පැහැදිලි privacy disclosure සහ දරුවන්ට අදාළ අමතර ආරක්ෂණ අවශ්‍ය වේ."),
("වෙබ් අඩවියට සහය විය හැක්කේ","දෙමාපියන් සහ ගුරුවරුන්ට මෙම නොමිලේ අධ්‍යාපනික සම්පත් අදාළ පුද්ගලයන් සමඟ බෙදාගැනීමෙන් සහ අන්තර්ගත දෝෂ දැනුම් දීමෙන් සහය විය හැකියි. මිලදී ගැනීම් හෝ මුදල් ගෙවීම් ඉල්ලන්නේ නැත."),
("වැඩිදුර සම්බන්ධතා",f'<a href="{BASE}contact/">අප හා සම්බන්ධ වන්න</a>')])
]
def build_page(slug,title,sections):
    text=[]
    for heading,body in sections:
        if "<a " in body:
            body_display=body
        else:
            body_display=html.escape(body)
        text.append(f"<section><h2>{html.escape(heading)}</h2><p>{body_display}</p></section>")
    desc=html.escape(sections[0][1][:150],quote=True)
    return (f'<!doctype html><html lang="si"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)} | පුංචි නැණ මඟ</title><meta name="description" content="{desc}"><meta name="robots" content="index,follow">'
            f'<link rel="canonical" href="{BASE}{slug}/">'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@400;700&display=swap">'
            f'<style>{CSS}</style></head><body><header><nav><a href="../">මුල් පිටුව</a><a href="../about/">අප ගැන</a><a href="../privacy/">Privacy</a></nav>'
            f'<h1>{html.escape(title)}</h1></header><article>{"".join(text)}</article>'
            '<footer><a href="../terms/">භාවිත නියමයන්</a> · <a href="../contact/">සම්බන්ධතා</a> · <a href="../support/">ව්‍යාපෘතියට සහය</a></footer></body></html>')
def main():
    import sys
    root=Path(sys.argv[1])
    for slug,title,sections in PAGES:
        dest=root/slug
        dest.mkdir(parents=True,exist_ok=True)
        (dest/"index.html").write_text(build_page(slug,title,sections),encoding="utf-8")
        print("Monetization readiness page generated:",slug)
    publisher=os.environ.get("ADSENSE_PUBLISHER_ID","").strip()
    # Verification-only: No ad loader or tags are ever activated by this build.
    # Only add ads.txt with actual approved publisher ID after operator sets variable.
    if publisher:
        if not re.fullmatch(r"pub-[0-9]{16}",publisher):
            raise ValueError("ADSENSE_PUBLISHER_ID must be pub- followed by 16 digits")
        (root/"ads.txt").write_text(f"google.com, {publisher}, DIRECT, f08c47fec0942fa0\n",encoding="utf-8")
        print("ads.txt created for configured real publisher ID; ad serving remains disabled")
    else:
        print("No publisher ID configured: no ads.txt or advertising scripts emitted.")
if __name__=="__main__":
    main()
