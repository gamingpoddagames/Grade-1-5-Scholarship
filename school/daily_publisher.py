#!/usr/bin/env python3
"""Deterministic school-content publisher. No AI and no third-party Python packages."""
import argparse
import datetime as dt
import html
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
from build_resources import all_questions

BASE = pathlib.Path(__file__).resolve().parent
BANK = BASE / "questions.json"
SITE = "https://gamingpoddagames.github.io/Grade-1-5-Scholarship/"
BLOG = "https://punchinanamaga.blogspot.com/?utm_source=facebook&utm_medium=social&utm_campaign=school_daily_quiz"

def make_content(day, output_dir):
    questions = all_questions()
    if not questions:
        raise ValueError("Question bank empty")
    index = (day - dt.date(2026, 11, 18)).days % len(questions)
    item = questions[index]
    # Keep Sinhala text in standard Unicode NFC form.
    item = {key: (unicodedata.normalize("NFC", value) if isinstance(value, str) else [unicodedata.normalize("NFC", v) for v in value] if isinstance(value, list) else value) for key, value in item.items()}
    correct = item["choices"][item["answer"]]
    # Plain Sinhala Facebook copy: avoid emoji/font fallback at the start of a line.
    title = f"පුංචි නැණ මඟ - {item['grade']} ශ්‍රේණිය - {item['topic']}"
    message = "\n".join([
        title,
        "",
        "අද පුහුණු ප්‍රශ්නය",
        item["q"],
        "",
        *[f"{chr(65 + i)}) {choice}" for i, choice in enumerate(item["choices"])],
        "",
        "දරුවාට මුලින් පිළිතුර තෝරාගැනීමට අවස්ථාව දෙන්න.",
        "",
        f"නිවැරදි පිළිතුර: {chr(65 + item['answer'])}) {correct}",
        f"පැහැදිලි කිරීම: {item['explanation']}",
        "",
        f"නොමිලේ සිංහල පාඩම් සහ අලුත් ලිපි: {BLOG}",
        f"ප්‍රශ්න පත්‍ර සහ Online Quiz: {SITE}",
        "",
        "#Grade5Scholarship #SinhalaEducation"
    ])
    message = unicodedata.normalize("NFC", message)
    if "\ufffd" in message:
        raise ValueError("Invalid replacement character in Sinhala content")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "facebook_post.txt").write_text(message, encoding="utf-8")
    (output_dir / "question.json").write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    paper = (f"<!doctype html><html lang='si'><meta charset='utf-8'>"
             f"<title>{html.escape(title)}</title>"
             "<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@400;700&display=swap'>"
             "<style>body{font-family:'Noto Sans Sinhala','Iskoola Pota','Nirmala UI',sans-serif;max-width:760px;margin:40px auto;line-height:2}h1{font-size:24px}.answer{break-before:page}</style>"
             f"<h1>{html.escape(title)}</h1><p>දිනය: {day.isoformat()}</p>"
             f"<h2>{html.escape(item['q'])}</h2>"
             + "".join(f"<p>{chr(65+i)}. {html.escape(c)}</p>" for i,c in enumerate(item["choices"]))
             + f"<div class='answer'><h2>පිළිතුර</h2><p>{html.escape(correct)}</p><p>{html.escape(item['explanation'])}</p></div>"
             + "<p>මුල් නිර්මාණ පුහුණු ප්‍රශ්නයකි; නිල විභාග පත්‍රයක් නොවේ.</p></html>")
    (output_dir / "printable.html").write_text(paper, encoding="utf-8")
    return message

def publish(message, page_id, token, version="v27.0"):
    payload = urllib.parse.urlencode({"message":message,"access_token":token}).encode("utf-8")
    request = urllib.request.Request(f"https://graph.facebook.com/{version}/{page_id}/feed",data=payload,method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        # Never echo tokens or query params to logs.
        raise RuntimeError(f"Facebook API rejected post: HTTP {exc.code}; inspect Meta permissions") from None
    if not result.get("id"):
        raise RuntimeError("Facebook did not return a post ID")
    print("Facebook post published:", result["id"])
    # Compare the text returned by Graph API with the original UTF-8 payload.
    # Read-back may be unavailable for some Page tokens; posting must not fail for that reason.
    try:
        query = urllib.parse.urlencode({"fields": "message", "access_token": token})
        url = f"https://graph.facebook.com/{version}/{result['id']}?{query}"
        with urllib.request.urlopen(url, timeout=20) as response:
            saved = json.load(response).get("message")
        if saved is None:
            print("Facebook text verification: message field unavailable.")
        elif unicodedata.normalize("NFC", saved) == unicodedata.normalize("NFC", message):
            print("Facebook text verification: Unicode text matches exactly.")
        else:
            print("Facebook text verification: returned text differs from sent message.")
    except (urllib.error.URLError, ValueError, KeyError):
        print("Facebook text verification: not available with this Page token.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Asia/Colombo calendar date YYYY-MM-DD; default today's Sri Lanka date")
    parser.add_argument("--output", default="school/output")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    today = dt.date.fromisoformat(args.date) if args.date else (dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=5,minutes=30)).date()
    message = make_content(today, pathlib.Path(args.output))
    print("Content generated for", today.isoformat())
    if args.publish:
        page_id = os.getenv("FB_PAGE_ID", "")
        token = os.getenv("FB_PAGE_ACCESS_TOKEN", "")
        if not (page_id and token):
            print("Facebook disabled: missing FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN. Files generated only.")
            return
        publish(message, page_id, token, os.getenv("FB_GRAPH_VERSION", "v27.0"))
if __name__ == "__main__":
    main()
