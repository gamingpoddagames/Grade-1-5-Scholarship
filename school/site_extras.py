#!/usr/bin/env python3
"""Generate original Sinhala parent guides and transparent site policies, no AI or paid services."""
import pathlib
import html
import sys

BASE="https://gamingpoddagames.github.io/Grade-1-5-Scholarship/"
ARTICLES=[
 ("grade-5-study-plan","5 ශ්‍රේණිය ශිෂ්‍යත්වයට දිනපතා අධ්‍යයන සැලැස්ම",
  [("දිනපතා අඩු කාලයකින් පටන් ගන්න","දරුවාට දිනකට විනාඩි 20ක ගණිත පුහුණුවක් සහ කෙටි විවේකයක් තබන්න. වැඩිපුර ප්‍රශ්න කරනවාට වඩා ඉගෙන ගත් දේ තේරුම් ගත්තාදැයි සොයා බැලීම වැදගත්ය."),
   ("වැරදි පිළිතුරු විමසා බලන්න","පිළිතුර වැරදුණා නම් නිවැරදි පිළිතුර පමණක් කියා නොදෙන්න. ගැටලුව විසඳූ පියවර දරුවාට පැහැදිලි කරවන්න. ඉන්පසු සමාන ප්‍රශ්නයක් නැවත කරන්න."),
   ("සතිපතා පුනරීක්ෂණය","සඳුදා සිට සිකුරාදා දක්වා එක් එක් දිනට කෙටි අභ්‍යාසයකි. සෙනසුරාදා සතියේ දුෂ්කර වූ ප්‍රශ්න නැවත කරන්න. ඉරිදා සැහැල්ලු ක්‍රීඩාමය පුහුණුවක් ලබා දෙන්න."),
   ("වෙනස මැනීම","දිනපතා ලකුණු තරගයක් ලෙස නොව, නිවැරදි පිළිතුරු ප්‍රතිශතය සහ වැරදි ගැටලු අවබෝධ වූ ආකාරය දෙමාපියන් සටහන් කර තබන්න.")]),
 ("how-to-use-papers","ප්‍රශ්න පත්‍ර නිවසේදී ප්‍රයෝජනවත් ලෙස භාවිත කරන්නේ කොහොමද?",
  [("ශ්‍රේණියට ගැළපෙන පත්‍රය තෝරන්න","දරුවා ඉගෙන ගන්නා ශ්‍රේණියට අදාළ ප්‍රශ්න පත්‍රය බාගන්න. මුලින් පිළිතුරු පත්‍රය නොපෙන්වා දරුවාට තනිව පිළිතුරු සෙවීමට ඉඩ දෙන්න."),
   ("අදහස පැහැදිලි කරවන්න","නිවැරදි පිළිතුරක් දුන්නත් එයට පැමිණි ආකාරය අසන්න. මෙය අහඹු පිළිතුරු තෝරාගැනීමෙන් වැළකීමට උපකාරී වේ."),
   ("බලහත්කාරයෙන් පාඩම් නොකරවන්න","දරුවාගේ වයස සහ අවධානය අනුව පුහුණු කාලය සකස් කරන්න. අවශ්‍ය විට විවේක දෙන්න."),
   ("PDF ගොනු භාවිතය","Paper PDF සහ Answers PDF වෙනම ගොනු ලෙස ලබා දේ. මුද්‍රණය කිරීමට හෝ දුරකථනයෙන් කියවීමට සුදුසුයි.")]),
 ("grade-1-4-maths-basics","1–4 ශ්‍රේණි ගණිතයේ මූලික හැකියා ගොඩනගමු",
  [("1 ශ්‍රේණිය","ගණන් කිරීම, අංක හඳුනාගැනීම සහ කුඩා සංඛ්‍යා එකතු කිරීම සඳහා සෙල්ලම් බඩු හෝ දෛනික වස්තු භාවිත කරන්න."),
   ("2 ශ්‍රේණිය","දෙකින් දෙකට හා පහෙන් පහට ගණන් කිරීම, අඩු කිරීම සහ කාලය කියවීම කෙටි අභ්‍යාස ලෙස කරන්න."),
   ("3 ශ්‍රේණිය","ගුණ කිරීමේ වගු, සරල බෙදීම සහ මිනුම් සම්බන්ධ ක්‍රියාකාරකම්වලට අවධානය දෙන්න."),
   ("4 ශ්‍රේණිය","ගුණ කිරීම සහ බෙදීම යෙදෙන වචන ගැටලු විසඳීමට පුහුණු කරන්න. පිළිතුර පමණක් නොව ක්‍රමය ද ලියන්න.")])
]
PAGES=[
 ("about","අප ගැන",[
  ("අපේ අරමුණ","පුංචි නැණ මඟ යනු 1–5 ශ්‍රේණි සඳහා සිංහලෙන් ස්වාධීන අධ්‍යාපනික අභ්‍යාස ලබාදෙන නොමිලේ වෙබ් අඩවියකි. දෙමාපියන් හා ගුරුවරුන් සමඟ නිවසේ පුහුණු කිරීමට එය නිර්මාණය කර ඇත."),
  ("නිලභාවය","මෙම අඩවිය රජයේ නිල විභාග ප්‍රශ්න පත්‍ර නිකුත් කරන ආයතනයක් නොවේ. අභ්‍යාස අපගේම පුහුණු ප්‍රශ්න වේ.")]),
 ("privacy","පෞද්ගලිකත්ව ප්‍රතිපත්තිය",[
  ("අප ලබාගන්නා දත්ත","මෙම වෙබ් අඩවියේ quiz එක ක්‍රියාකරන්නේ ඔබේ browser එක තුළය. ගිණුම් විවෘත කිරීම හෝ දරුවන්ගේ නම, වයස, දුරකථන අංක, ලකුණු අප වෙත යැවීම අවශ්‍ය නැත."),
  ("තෙවන පාර්ශ්ව","අකුරු පෙන්වීමට Google Fonts භාවිත කෙරේ. වෙබ් අඩවිය GitHub Pages මත පවතින නිසා hosting provider විසින් ඔවුන්ගේ ප්‍රතිපත්ති අනුව තාක්ෂණික logs සකස් කළ හැක. වත්මන් අනුවාදයේ Google AdSense සහ analytics tracking code එකක් ඇතුළත් නැත."),
  ("දැන්වීම් සහ වෙනස්කම්","අනාගතයේ දැන්වීම් හෝ analytics එක් කළහොත්, ඒවා සක්‍රිය කිරීමට පෙර මෙම ප්‍රතිපත්තිය යාවත්කාලීන කර දරුවන් සම්බන්ධ ආරක්ෂක සහ නීතිමය අවශ්‍යතා පරීක්ෂා කරනු ඇත.")]),
 ("terms","භාවිත නියමයන්",[
  ("අධ්‍යාපනික භාවිතය","මෙහි ප්‍රශ්න පත්‍ර පෞද්ගලික හා පන්තිකාමර පුහුණුව සඳහා නොමිලේ මුද්‍රණය කළ හැක. නිල විභාග ප්‍රශ්න පත්‍ර ලෙස හඳුන්වා නොදෙන්න."),
  ("නිවැරදිභාවය","අංක ගණිත ප්‍රශ්නවල පිළිතුරු ගණනය කරන ලද නමුත් වචන භාවිතය හා ශ්‍රේණි යෝග්‍යතාව පිළිබඳ අඛණ්ඩ සංස්කරණ අවශ්‍ය විය හැක. ගුරුවරයෙකු හෝ දෙමාපියෙකු විසින් දරුවන්ට ලබාදීමට පෙර පරීක්ෂා කිරීම සුදුසුය."),
  ("සම්බන්ධතා","ප්‍රසිද්ධ සහාය ඊමේල් ලිපිනයක් තවම සකසා නැත. නිල Facebook Page එක හරහා පණිවිඩ යැවිය හැක.")])
]
def generate(root):
 root=pathlib.Path(root)
 style="body{font-family:'Noto Sans Sinhala','Nirmala UI',sans-serif;line-height:1.9;max-width:850px;margin:0 auto;padding:28px;background:#f2f7fb;color:#173352}article,header{background:white;padding:24px;border-radius:15px;margin-bottom:18px}h1{line-height:1.45}a{color:#14669c}"
 for slug,title,sections in ARTICLES+PAGES:
  desc=sections[0][1][:145]
  content="".join(f"<section><h2>{html.escape(k)}</h2><p>{html.escape(v)}</p></section>" for k,v in sections)
  page=(f"<!doctype html><html lang='si'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>{html.escape(title)} | පුංචි නැණ මඟ</title><meta name='description' content='{html.escape(desc,quote=True)}'>"
        f"<link rel='canonical' href='{BASE}{slug}/'>"
        "<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@400;700&display=swap'>"
        f"<style>{style}</style></head><body><header><a href='../'>මුල් පිටුව</a><h1>{html.escape(title)}</h1></header>"
        f"<article>{content}</article><footer><a href='../privacy/'>Privacy</a> · <a href='../terms/'>Terms</a> · <a href='../about/'>About</a></footer></body></html>")
  out=root/slug
  out.mkdir(parents=True,exist_ok=True)
  (out/"index.html").write_text(page,encoding="utf-8")
  print("Generated",slug)
if __name__=="__main__":
 if len(sys.argv)!=2: raise SystemExit("Usage: python school/site_extras.py _site")
 generate(sys.argv[1])
