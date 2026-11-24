#!/usr/bin/env python3
"""A distinct adult/general-audience practical-learning series.

This never changes or relabels child-directed Grade 1–5 videos. YouTube
audience is classified from the ACTUAL content, not the brand/channel name.
The content here is everyday household/workplace financial arithmetic
explicitly aimed at adult learners, parents and small-business owners.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path

from build_resources import video
from blogger_link_safety import FACEBOOK_LANDING_URL
from social_text import clean_caption
from youtube_shorts import OWNER_CHANNEL_ID, BLOG, upload, today_sri_lanka

START=dt.date(2026,11,24)
TARGET_AUDIENCE="general"
TOPICS=("ගෘහස්ථ අයවැය","කුඩා ව්‍යාපාර ගණනය","මිල සහ වට්ටම්","වැඩිහිටි මුදල් සැලසුම්")
GENERAL_MARKER="PNM-GENERAL-"


def select(day):
    if isinstance(day,str):
        day=dt.date.fromisoformat(day)
    serial=(day-START).days
    if serial<0:
        raise ValueError("Adult learning series starts on 2026-11-24")
    variant=serial%len(TOPICS)
    if variant==0:
        monthly=68000+serial*120
        expenses=49500+serial*35
        result=monthly-expenses
        question=f"මාසික ආදායම රු. {monthly:,}ක් සහ වියදම රු. {expenses:,}ක් නම් ඉතිරිය කීයද?"
        explanation=f"ආදායමෙන් වියදම අඩු කළ විට රු. {result:,}ක් ඉතිරි වේ."
        diffs=[0,-2000,1500,3000]
    elif variant==1:
        buy=4500+serial*60
        sell=buy+1200+serial*10
        extra=300+serial*2
        result=sell-buy-extra
        question=f"භාණ්ඩයක මිලදී ගැනීම රු. {buy:,}, විකිණීම රු. {sell:,} සහ අමතර වියදම රු. {extra:,} නම් ලාභය කීයද?"
        explanation=f"ලාභය = {sell:,} - {buy:,} - {extra:,} = රු. {result:,}."
        diffs=[-400,0,250,700]
    elif variant==2:
        price=10000+serial*100
        discount=20
        result=price*(100-discount)//100
        question=f"රු. {price:,}ක භාණ්ඩයකට 20% වට්ටමක් ලැබුණොත් ගෙවිය යුතු මිල කීයද?"
        explanation=f"20% වට්ටම රු. {price*discount//100:,}යි. ඉතිරි මිල රු. {result:,}යි."
        diffs=[-500,1000,0,2000]
    else:
        target=15000+serial*100
        months=3
        result=target//months
        question=f"මාස තුනකින් රු. {target:,}ක් ඉතිරි කිරීමට මාසයකට කොපමණක් වෙන් කළ යුතුද?"
        explanation=f"රු. {target:,} ÷ {months} = රු. {result:,}."
        diffs=[2000,-1000,1000,0]
    options=[result+x for x in diffs]
    if min(options)<0 or len(set(options))!=4:
        raise RuntimeError("Adult quiz generator produced invalid answers")
    question_data={
        "audience":"general",
        "audience_basis":"Practical finances, household budgeting and workplace arithmetic explicitly aimed at adult learners and parents; no grade-school labels or child-directed characters.",
        "topic":TOPICS[variant],
        "q":question,
        "choices":[f"රු. {n:,}" for n in options],
        "answer":diffs.index(0),
        "explanation":explanation,
        "content_date":day.isoformat()
    }
    return question_data


def metadata_for(question,day,privacy="private"):
    if isinstance(day,str):
        day=dt.date.fromisoformat(day)
    if privacy not in {"private","unlisted","public"}:
        raise ValueError("Invalid YouTube privacy")
    # Explicit independent review of target audience and substance is required.
    if (question.get("audience")!="general"
            or question.get("topic") not in TOPICS
            or not question.get("audience_basis")
            or "grade" in question
            or "ශ්‍රේණිය" in question.get("q","")):
        raise RuntimeError("Adult/general audience classification not justified; stop")
    choices=question.get("choices",[])
    if len(choices)!=4 or len(set(choices))!=4 or question.get("answer") not in range(4):
        raise RuntimeError("Four unique choices and verified answer required")
    marker=GENERAL_MARKER+day.strftime("%Y%m%d")
    title=f"වැඩිහිටියන්ට ප්‍රයෝජනවත් ගණිතය | {question['topic']} #Shorts"
    description=(
        "පුංචි නැණ මඟ | වැඩිහිටියන්, දෙමාපියන් සහ කුඩා ව්‍යාපාරිකයන් සඳහා ප්‍රායෝගික දැනුම.\n\n"
        + question["q"] + "\n"
        + "\n".join(f"{chr(65+i)}) {ch}" for i,ch in enumerate(choices))
        + "\n\nපිළිතුර සහ පැහැදිලි කිරීම වීඩියෝව අවසානයේ.\n"
        + "වැඩිදුර සිංහල ඉගෙනුම් සහ ලිපි: " + BLOG
        + "\n\nමෙය අධ්‍යාපනික ගණනය කිරීමක් පමණි; පුද්ගලික මූල්‍ය උපදෙසක් නොවේ.\n"
        + "#AdultLearning #SinhalaSkills #MoneyMath #Shorts\n" + marker
    )
    return {
        "snippet":{
            "title":title,"description":description,"categoryId":"27",
            "defaultLanguage":"si","defaultAudioLanguage":"si",
            "tags":["Sinhala Skills","Adults and Parents","Money Math",
                    "Personal Budgeting","Practical Education"]
        },
        "status":{
            "privacyStatus":privacy,
            # This ORIGINAL adult-relevant series is directed at a general audience.
            # This is NOT a global channel-wide setting and must never be copied to
            # the original Grade 1-5 school video pipeline.
            "selfDeclaredMadeForKids":False
        },
        "_marker":marker
    }


def facebook_caption(q):
    return clean_caption("\n".join([
        "පුංචි නැණ මඟ | වැඩිහිටියන්ට ප්‍රයෝජනවත් දැනුම",
        q["topic"],"",q["q"],"",
        *[f"{chr(65+i)}) {v}" for i,v in enumerate(q["choices"])],
        "","නිවැරදි පිළිතුර සහ ගණනය වීඩියෝව අවසානයේ බලන්න.",
        "ගණනය ඔබ කළේ කෙසේද? හේතුව සමඟ අදහසක් දක්වන්න.",
        "",FACEBOOK_LANDING_URL,
        "#SinhalaEducation #PracticalMath #AdultLearning"
    ]))


def prepare(day,outdir):
    if isinstance(day,str):
        day=dt.date.fromisoformat(day)
    question=select(day)
    folder=Path(outdir)
    folder.mkdir(parents=True,exist_ok=True)
    movie=video(folder,[question],day)
    info=metadata_for(question,day)
    (folder/"youtube-metadata.json").write_text(
        json.dumps({"snippet":info["snippet"],"status":info["status"],
                    "unique_marker":info["_marker"]},ensure_ascii=False,indent=2),
        encoding="utf-8")
    (folder/"facebook-caption.txt").write_text(facebook_caption(question),encoding="utf-8")
    (folder/"editorial-question.json").write_text(
        json.dumps(question,ensure_ascii=False,indent=2),encoding="utf-8")
    return question,movie,info


def run(day,outdir,*,publish_social=False,upload_youtube=False):
    if isinstance(day,str):
        day=dt.date.fromisoformat(day)
    q,movie,info=prepare(day,outdir)
    if publish_social:
        from crosspost import Crossposter
        if os.getenv("BLOGGER_ALLOW_PUBLICATION","").lower()=="false":
            raise RuntimeError("Blogger publishing explicitly disabled")
        article,fbid=Crossposter().publish(
            question=q,
            title=f"පුංචි නැණ මඟ | {day.isoformat()} | වැඩිහිටි දැනුම: {q['topic']}",
            media_kind="video",media_path=movie,caption=facebook_caption(q))
        print("Adult/general Blogger article:",article,"Facebook:",fbid)
    if upload_youtube:
        if os.getenv("YOUTUBE_UPLOAD_ENABLED","").lower()!="true":
            raise RuntimeError("YouTube uploads not authorized")
        privacy=os.getenv("YOUTUBE_GENERAL_PRIVACY", "private").strip() or "private"
        if privacy!="private" and os.getenv("YOUTUBE_GENERAL_PUBLIC_REVIEWED","").lower()!="true":
            raise RuntimeError("Public adult content requires YOUTUBE_GENERAL_PUBLIC_REVIEWED=true after owner review")
        metadata=metadata_for(q,day,privacy=privacy)
        try:
            receipt=upload(movie,metadata,Path(outdir))
        except RuntimeError as exc:
            if "already uploaded" not in str(exc):
                raise
            print("Adult general-audience video already uploaded; no duplicate.")
        else:
            print("General audience YouTube upload:",receipt["video_url"],receipt["privacy"])
    else:
        print("YouTube PREVIEW ONLY: no new video uploaded")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--date",help="Asia/Colombo YYYY-MM-DD")
    p.add_argument("--output",default="school/output/adult-general-learning")
    p.add_argument("--publish-social",action="store_true",
                   help="Publish separate adult-relevant video to FB+Blogger")
    p.add_argument("--upload-youtube",action="store_true")
    args=p.parse_args()
    day=dt.date.fromisoformat(args.date) if args.date else today_sri_lanka()
    run(day,args.output,publish_social=args.publish_social,
        upload_youtube=args.upload_youtube)


if __name__=="__main__":
    main()
