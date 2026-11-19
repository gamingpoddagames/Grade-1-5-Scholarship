#!/usr/bin/env python3
"""Prepare copy/paste-ready original Sinhala Blogger educational articles.

No Blogger login or automated publishing is performed. The owner reviews each
article before posting. No ads, affiliate links, or children's data collection.
"""
import argparse
import html
import json
from pathlib import Path
from curriculum_bank import get_questions, SUBJECTS

SITE="https://gamingpoddagames.github.io/Grade-1-5-Scholarship/"
FB="https://www.facebook.com/profile.php?id=61596326146776"
INTRO={
"math": "ගණිතය ඉගෙනීමේදී අංක මතක තබාගැනීම පමණක් නොව, පිළිතුර සොයාගත් ආකාරය පැහැදිලි කිරීම ද වැදගත්ය. මුලින් වස්තු, කාසි හෝ කුඩා සටහන් යොදා ගැටලුව තේරුම් ගන්න.",
"sinhala": "සිංහල භාෂාව අධ්‍යයනයේදී අකුරු නිවැරදිව කියවීම, අලුත් වචනවල අර්ථය කතා කිරීම සහ සරල වාක්‍ය රචනා කිරීම එකට පුහුණු වීම ප්‍රයෝජනවත්ය.",
"environment": "පරිසරය ආශ්‍රිත ඉගෙනීම සඳහා නිවසේ සහ අවට පරිසරයේ දකින්නට ඇති දේ නිරීක්ෂණය කරන්න. ආරක්ෂිත සරල ක්‍රියාකාරකම් සහ කතාබහ මඟින් දරුවාගේ අවබෝධය වර්ධනය කරගත හැක."
}
GRADE_ADVICE={
1:"දරුවා සමඟ වචන හෝ අංක හඬින් කියවන්න. කෙටි කාලයක් තුළ ප්‍රශ්න දෙක තුනක් පමණක් කර විවේකයක් ලබාදෙන්න.",
2:"පිළිතුර තෝරාගැනීමට පෙර ප්‍රශ්නය දරුවාගේම වචනවලින් නැවත කියවන්න. අවශ්‍ය නම් රූපයක් හෝ වස්තු භාවිත කරන්න.",
3:"සෑම පිළිතුරකටම හේතුවක් කියන්න කියා ඉල්ලන්න. වැරදි පිළිතුරක් ලැබුණොත් තවත් සමාන කුඩා ප්‍රශ්නයක් සමඟ ආපසු උත්සාහ කරන්න.",
4:"පිළිතුරු සැසඳීමට සහ තමන් කළ වරද හඳුනාගැනීමට දරුවාට ඉඩ දෙන්න. සමහර ගැටලු සඳහා පියවර ලියා තැබීම උපකාරී වේ.",
5:"ශිෂ්‍යත්වය සඳහා කාලය මැනීමත් පුහුණු විය හැකි නමුත් නිවැරදිව තේරුම් ගැනීම මුල් තැනට දමන්න. ප්‍රශ්න වර්ග කිහිපයක් මාරුවෙන් මාරුවට කරන්න."
}
ACTIVITY={
"math":"අද දවසේ භාවිත කළ වස්තු 5–10ක් ගෙන ගණන් කර බලන්න. අංක හෝ ගණනය වචනවලින් පැහැදිලි කරවන්න.",
"sinhala":"ප්‍රශ්නවලින් අලුත් වචන තුනක් තෝරා ඒවා යොදා කෙටි වාක්‍ය සාදන්න.",
"environment":"නිවස ආසන්නයේ ඇති ආරක්ෂිත සරල දෙයක් නිරීක්ෂණය කර ඒ පිළිබඳ කුඩා සටහනක් ලියන්න හෝ කතා කරන්න."
}
def build_article(grade,subject,bank):
    rows=[q for q in bank if q["grade"]==grade and q["subject"]==subject][:6]
    assert len(rows)==6
    title=f"{grade} ශ්‍රේණිය {SUBJECTS[subject]} — නිවසේ පුහුණුව සහ පැහැදිලි කළ පිළිතුරු"
    chunks=[f"<h2>{html.escape(title)}</h2>",
            f"<p>{html.escape(INTRO[subject])}</p>",
            f"<p>{html.escape(GRADE_ADVICE[grade])}</p>",
            "<h3>නිවසේදී අත්හදා බලන ක්‍රමය</h3>",
            "<p>පහත ප්‍රශ්න හය මුලින් පිළිතුරු නොබලා කරන්න. ඉන්පසු නිවැරදි පිළිතුර සහ හේතුව කියවන්න. දරුවෙකුගේ ලකුණු හෝ පෞද්ගලික තොරතුරු එකතු කිරීම අවශ්‍ය නැත.</p>"]
    for i,q in enumerate(rows,1):
        options="".join(f"<li>{chr(65+j)}. {html.escape(choice)}</li>" for j,choice in enumerate(q["choices"]))
        ans=html.escape(q["choices"][q["answer"]])
        why=html.escape(q["explanation"])
        chunks.append(f'<section><h3>{i}. {html.escape(q["q"])}</h3><ol style="list-style:none;padding-left:12px">{options}</ol><details><summary><strong>නිවැරදි පිළිතුර සහ පැහැදිලි කිරීම</strong></summary><p><strong>{chr(65+q["answer"])}. {ans}</strong> — {why}</p></details></section>')
    chunks.append(f"<h3>අමතර ක්‍රියාකාරකම</h3><p>{html.escape(ACTIVITY[subject])}</p>")
    chunks.append(f'<p><strong>තවත් නොමිලේ පුහුණුව:</strong> <a href="{SITE}practice/grade-{grade}/{subject}/" rel="noopener">Online Quiz සහ බාගත කළ හැකි ප්‍රශ්න PDF / පිළිතුරු PDF</a></p>')
    chunks.append("<p><em>මෙම ප්‍රශ්න මුල් නිර්මාණ පුහුණු ද්‍රව්‍ය වේ. රජයේ නිල විභාග පත්‍ර හෝ නිල විෂය නිර්දේශ සහතිකයක් නොවේ. ගුරුවරයෙකුගේ මඟපෙන්වීම සමඟ භාවිත කරන්න.</em></p>")
    return title,"\n".join(chunks)
def export(dest):
    dest.mkdir(parents=True,exist_ok=True)
    bank=get_questions()
    manifest=[]
    for grade in range(1,6):
        for subject in SUBJECTS:
            title,body=build_article(grade,subject,bank)
            filename=f"grade-{grade}-{subject}.html"
            (dest/filename).write_text(body,encoding="utf-8")
            manifest.append({"title":title,"file":filename,"grade":grade,"subject":subject,"labels":[f"Grade {grade}","Sinhala education",SUBJECTS[subject]]})
    pages={
      "about":"<h2>අප ගැන</h2><p>පුංචි නැණ මඟ යනු ශ්‍රී ලංකාවේ 1–5 ශ්‍රේණි දරුවන් සඳහා නොමිලේ අධ්‍යාපනික මඟපෙන්වීම් ලබා දෙන ස්වාධීන බ්ලොග් අඩවියකි. මෙහි ගණිතය, සිංහල සහ පරිසරය ආශ්‍රිත පුහුණු අදහස් දෙමාපියන් සහ ගුරුවරුන් සඳහා ලියවෙයි.</p><p>මෙය රජයේ නිල අධ්‍යාපන අඩවියක් හෝ නිල ශිෂ්‍යත්ව විභාග පත්‍ර නිකුත් කරන සේවාවක් නොවේ. අන්තර්ගතය භාවිත කිරීමට පෙර පාඩම් මට්ටම පරීක්ෂා කරන්න.</p><p>වෙනත් නොමිලේ අභ්‍යාස: <a href='"+SITE+"'>පුංචි නැණ මඟ ප්‍රශ්න පත්‍ර අඩවිය</a>.</p>",
      "contact":"<h2>සම්බන්ධතා</h2><p>අන්තර්ගත දෝෂයක්, අලුත් අධ්‍යාපනික අදහසක් හෝ සාමාන්‍ය යෝජනාවක් තිබේ නම් දෙමාපියෙකු හෝ ගුරුවරයෙකු ලෙස අපගේ <a href='"+FB+"'>Facebook Page</a> හරහා පණිවිඩයක් යවන්න.</p><p>දරුවෙකුගේ නම, පාසල, උපන් දිනය, ලිපිනය, ඡායාරූප හෝ සම්බන්ධතා අංක වැනි පුද්ගලික දත්ත එවන්න එපා.</p>",
      "privacy":"<h2>පෞද්ගලිකත්ව ප්‍රතිපත්තිය</h2><p>මෙම බ්ලොග් අඩවියට පිවිසීමට දරුවන්ගෙන් නමක්, ගිණුමක් හෝ දුරකථන අංකයක් ඉල්ලා නොසිටිමු. Blogger සේවාව Google විසින් පවත්වාගෙන යන අතර cookies, hosting logs සහ වෙනත් තාක්ෂණික දත්ත එහි අදාළ ප්‍රතිපත්ති යටතේ සකස් විය හැක. Blogger භාවිත කරන widgets, embedded content හෝ comment functionality හරහා ද තෙවන පාර්ශ්ව සේවා සම්බන්ධ විය හැක.</p><p>Google AdSense සම්බන්ධතා ඉල්ලීමක්/සමාලෝචනයක් සිදුවිය හැකි නමුත් ads පෙන්වීමට අනුමැතිය ලැබී ඇතැයි මෙහි කියන්නේ නැත. අනාගතයේ වෙළඳ දැන්වීම් සක්‍රිය කරන විට cookies/ads disclosure, අවශ්‍ය consent සහ දරුවන් සඳහා අදාළ child-directed protections පිළිබඳ නිසි සැකසුම් පළමුව සකස් කළ යුතුය.</p><p>දරුවන්ගේ පුද්ගලික තොරතුරු comments හෝ messages තුළ පළ නොකරන්න. අවශ්‍ය විට අන්තර්ගත ගැටලු සඳහා <a href='"+FB+"'>අපගේ Facebook Page</a> හරහා වැඩිහිටියෙකුට සම්බන්ධ විය හැක.</p><p>Google privacy policy: <a href='https://policies.google.com/privacy'>https://policies.google.com/privacy</a>.</p>",
      "terms":"<h2>භාවිත නියමයන්</h2><p>මෙහි ලිපි අධ්‍යාපනික පුහුණුව සඳහා සපයන ස්වාධීන මූලාශ්‍ර වේ. නිල පාඨපොත්, පාසල් විභාග පත්‍ර හෝ රජයේ විෂය නිර්දේශ සහතිකය ලෙස භාවිත නොකරන්න.</p><p>දෙමාපියන්ට සහ ගුරුවරුන්ට දරුවාගේ මට්ටමට ගැළපෙන ලෙස ප්‍රශ්න තෝරාගැනීමට සහ වැරදි පිළිතුරු නැවත පරීක්ෂා කිරීමට අපි නිර්දේශ කරමු. නිවැරදිභාවයේ ගැටලුවක් දුටුවහොත් අපට දැනුම් දෙන්න.</p>"
    }
    for slug,body in pages.items():
        (dest/f"page-{slug}.html").write_text(body,encoding="utf-8")
    (dest/"pages-index.json").write_text(json.dumps([{"slug":slug,"file":f"page-{slug}.html"} for slug in pages],ensure_ascii=False,indent=2),encoding="utf-8")
    (dest/"post-index.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    readme="""# පුංචි නැණ මඟ — Blogger starter package (free)
    
This is a review-before-posting pack, NOT a completed Blogger blog or an AdSense-approved website.

1. Sign in at https://www.blogger.com/ with the SAME Google account you used for AdSense.
2. Create a blog titled පුංචි නැණ මඟ, using a free available *.blogspot.com address.
3. In Settings, add a clear original blog description; enable Search visibility; choose HTTPS.
4. Use Posts > New Post, switch to HTML view, paste the content from each grade-*-*.html file. Set the title from post-index.json.
5. Review Sinhala spelling and factual accuracy before publishing. Do not blindly mass-publish 15 near-identical posts: distribute and improve the articles.
6. Review and add About, Contact, Privacy and Terms in Blogger > Pages. Use the prepared page-*.html drafts. Confirm actual widgets, comments and cookie practices before publishing.
7. In Blogger, go to Earnings to check AdSense eligibility and connect the EXISTING AdSense account. Do NOT open a second AdSense account.
8. Ads remain OFF until Blogger/AdSense says approved and child-directed advertising and privacy requirements have been reviewed.

Blogger -> AdSense instructions:
https://support.google.com/blogger/answer/1269077
https://support.google.com/adsense/answer/7584263
https://support.google.com/adsense/answer/10502938

Free content library: https://gamingpoddagames.github.io/Grade-1-5-Scholarship/
Contact for parents/teachers: https://www.facebook.com/profile.php?id=61596326146776

No guarantee of AdSense approval, page views, ad impressions or earnings.
"""
    (dest/"README.md").write_text(readme,encoding="utf-8")
    print("Prepared",len(manifest),"Blogger article files and",len(pages),"policy page drafts in",dest)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="blogger_output")
    args=parser.parse_args()
    export(Path(args.output))
if __name__=="__main__":
    main()
