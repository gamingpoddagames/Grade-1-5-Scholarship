#!/usr/bin/env python3
"""Additive daily education polls: Facebook + Blogger + YouTube draft pack.

Does not change the existing Facebook video renderer or workflows.
'Poll' on Facebook means an A/B/C/D answer-in-caption prompt or photo card,
not a native platform tally. Blogger uses answer-reveal in existing
Crossposter. YouTube Community polls cannot be sent by this standard uploader:
produce complete owner-reviewable text and image draft files.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

from blogger_link_safety import FACEBOOK_LANDING_URL, validate_blogger_links
from facebook_card import create_card, validate_card
from font_safety import check_caption
from quiz_topics import select as select_text
from visual_quiz import select as select_image, image_credit
from youtube_shorts import today_sri_lanka, OWNER_CHANNEL_ID
from social_text import clean_caption

BLOG = "https://punchinanamaga.blogspot.com/"
CHANNEL = "https://www.youtube.com/channel/" + OWNER_CHANNEL_ID


def select_poll(day, kind, *, text_offset=0):
    if isinstance(day, str):
        day = dt.date.fromisoformat(day)
    if kind not in ("text", "image"):
        raise ValueError("Poll type must be text or image")
    if kind == "text":
        question = select_text(day, offset=text_offset)
        question = dict(question)
    else:
        # The daily Facebook photo post already uses select_image(day).
        # Select a *different* licensed photograph/quiz for this bonus poll.
        question = dict(select_image(day + dt.timedelta(days=3)))
        today_photo = select_image(day)
        if question["q"] == today_photo["q"]:
            raise RuntimeError("Image poll would repeat today's Facebook image quiz")
    choices=question.get("choices", [])
    answer=question.get("answer")
    if (len(choices)!=4 or len(set(str(x) for x in choices))!=4
            or not isinstance(answer,int) or answer not in range(4)):
        raise RuntimeError("Poll must have 4 distinct answers and one checked key")
    if not 1 <= int(question.get("grade",0)) <= 5:
        raise RuntimeError("Poll grade is not primary school 1–5")
    return question


def caption_for(question, kind):
    source="පින්තූරය සමඟ" if kind=="image" else "පෙළ ප්‍රශ්නය"
    lines=[
        f"පුංචි නැණ මඟ | {question['grade']} ශ්‍රේණිය",
        f"අද {source} - දැනුම පරීක්ෂා කරමු.",
        "",
        question["q"],
        "",
        *[f"{chr(65+i)}) {ch}" for i,ch in enumerate(question["choices"])],
        "",
        "පළමුව ඔබේ පිළිතුර තෝරාගන්න. නිවැරදි පිළිතුර සහ පැහැදිලි කිරීම නොමිලේ Blogger ලිපියෙන් බලන්න.",
    ]
    if kind=="image":
        lines.extend(["","ඡායාරූපය: " + image_credit(question)])
    lines.extend(["",FACEBOOK_LANDING_URL,
                  "#PunchiNenaMaga #SinhalaEducation #Quiz"])
    result=clean_caption("\n".join(lines))
    check_caption(result)
    validate_blogger_links(result)
    return result


def community_draft(question, kind):
    lines=[
        f"පුංචි නැණ මඟ | {question['grade']} ශ්‍රේණිය",
        "Image Poll" if kind=="image" else "Text Poll",
        "",
        question["q"],
        "",
        *[f"{chr(65+i)}) {choice}" for i,choice in enumerate(question["choices"])],
        "",
        "දරුවන් සමඟ පිළිතුර සිතා බලන්න.",
        "තවත් නොමිලේ පාඩම්: " + BLOG,
    ]
    if kind=="image":
        lines.extend(["", "රූපයේ මූලාශ්‍රය: " + image_credit(question)])
    return "\n".join(lines)


def build_pack(day, kind, outdir, *, text_offset=0):
    if isinstance(day,str):
        day=dt.date.fromisoformat(day)
    q=select_poll(day,kind,text_offset=text_offset)
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    art=outdir/("image-poll.png" if kind=="image" else "text-quiz.png")
    create_card(q,art)
    validate_card(art)
    caption=caption_for(q,kind)
    (outdir/"facebook-caption.txt").write_text(caption,encoding="utf-8")
    (outdir/"youtube-community-draft.txt").write_text(
        community_draft(q,kind),encoding="utf-8")
    (outdir/"question.json").write_text(
        json.dumps(q,ensure_ascii=False,indent=2),encoding="utf-8")
    safe_info={"date":day.isoformat(),"kind":kind,"grade":q["grade"],
               "question":q["q"],"answer":str(q["choices"][q["answer"]]),
               "facebook_poll_type":"educational text/image question; no native vote tally",
               "youtube_community":"prepared only; requires eligible channel and supported post action",
               "blogger_landing":BLOG,"owner_youtube_channel":CHANNEL}
    (outdir/"status.json").write_text(
        json.dumps(safe_info,ensure_ascii=False,indent=2),encoding="utf-8")
    return q,art,caption


def publish(q, art, caption, day, kind, *, slot=None):
    from crosspost import Crossposter
    if kind not in ("text","image"):
        raise ValueError("Not an approved poll kind")
    title=f"පුංචි නැණ මඟ | {day.isoformat()} | "+(
        "පින්තූර දැනුම විමසුම" if kind=="image" else "අද පෙළ දැනුම විමසුම")
    if slot:
        title += f" | {slot}"
    url, fb_id=Crossposter().publish(
        question=q,title=title,
        media_kind=("photo" if kind=="image" else "text"),
        media_path=(art if kind=="image" else None),
        caption=caption,
        image_info=(q if kind=="image" else None))
    print("Blogger quiz and Facebook poll-style post:",url,fb_id)
    return url,fb_id


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--date",help="Asia/Colombo YYYY-MM-DD")
    p.add_argument("--kind",choices=["image","text","rotate"],default="rotate")
    p.add_argument("--morning",action="store_true",
                   help="Use the separate morning text quiz for this date")
    p.add_argument("--output",default="school/output/social-poll-pack")
    p.add_argument("--publish",action="store_true",
                   help="Post to authorized Blogger+Facebook page only")
    args=p.parse_args()
    day=dt.date.fromisoformat(args.date) if args.date else today_sri_lanka()
    kind=("text" if day.toordinal()%2==0 else "image") if args.kind=="rotate" else args.kind
    if args.morning:
        kind="text"
    out=Path(args.output)/day.isoformat()/("morning" if args.morning else kind)
    q,art,caption=build_pack(day,kind,out,text_offset=2 if args.morning else 0)
    print("Prepared checked",kind,"poll artwork + Facebook/Blogger/YouTube pack",art)
    if args.publish:
        publish(q,art,caption,day,kind,slot="උදෑසන" if args.morning else None)
    else:
        print("PREVIEW ONLY: nothing sent to Blogger, Facebook or YouTube.")


if __name__=="__main__":
    main()
