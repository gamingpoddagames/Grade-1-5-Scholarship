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
    (dest/"post-index.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    readme="""# පුංචි නැණ මඟ — Blogger starter package (free)
    
This is a review-before-posting pack, NOT a completed Blogger blog or an AdSense-approved website.

1. Sign in at https://www.blogger.com/ with the SAME Google account you used for AdSense.
2. Create a blog titled පුංචි නැණ මඟ, using a free available *.blogspot.com address.
3. In Settings, add a clear original blog description; enable Search visibility; choose HTTPS.
4. Use Posts > New Post, switch to HTML view, paste the content from each grade-*-*.html file. Set the title from post-index.json.
5. Review Sinhala spelling and factual accuracy before publishing. Do not blindly mass-publish 15 near-identical posts: distribute and improve the articles.
6. Create public About, Contact, Privacy and Terms pages that correctly describe THIS Blogger site and its actual tracking/advertising state. Do not copy the GitHub privacy policy unchanged.
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
    print("Prepared",len(manifest),"Blogger article files in",dest)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="blogger_output")
    args=parser.parse_args()
    export(Path(args.output))
if __name__=="__main__":
    main()
