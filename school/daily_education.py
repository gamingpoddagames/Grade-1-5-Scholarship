"""Run one daily curriculum slot with the existing publication safeguards."""
import argparse
import html
import json
import os
import urllib.request
from datetime import date
from pathlib import Path

from crosspost import Crossposter, today_in_sri_lanka, verified_facebook_permalink
from curriculum_bank import SUBJECTS, get_questions
from curriculum_pages import SITE, heading
from puzzle_posts import generate, facebook_caption
from video_cta import append_outro
from youtube_shorts import build_metadata, upload


def paper(day, *, folder=None, publish=False):
    courses = [(grade, subject) for grade in range(1, 6) for subject in SUBJECTS]
    grade, subject = courses[day.toordinal() % len(courses)]
    bank = [q for q in get_questions() if q["grade"] == grade and q["subject"] == subject]
    question = bank[(day.toordinal() // len(courses)) % len(bank)]
    title = heading(grade, subject)
    base = f"{SITE}downloads/grade-{grade}-{subject}"
    urls = [f"{base}-{kind}.pdf" for kind in ("paper", "answers")]
    if folder is not None:
        from daily_papers import publish_pdfs, render_pdfs
        paths = render_pdfs(folder, day, grade, subject, title)
        if publish:
            urls = publish_pdfs(day, paths)
        else:
            print("Rendered dated PDFs:", *(str(path) for path in paths))
    body = f"""<section lang="si"><h2>{title}</h2>
<p>{day.year} දෛනික පුහුණුව. පුංචි නැණ මඟ මුල් නිර්මාණ අභ්‍යාස පත්‍රය සහ වෙනම පිළිතුරු පත්‍රය.</p>
<p><a href="{urls[0]}" download>ප්‍රශ්න පත්‍රය බාගන්න (PDF)</a></p>
<p><a href="{urls[1]}" download>පිළිතුරු පත්‍රය බාගන්න (PDF)</a></p>
<h3>අද අමතර ප්‍රශ්නය</h3><p>{html.escape(question["q"])}</p>
<details><summary>පිළිතුර බලන්න</summary><p>{html.escape(question["choices"][question["answer"]])}</p>
<p>{html.escape(question["explanation"])}</p></details>
<h3>නිල 5 ශ්‍රේණි ශිෂ්‍යත්ව සම්පත්</h3>
<ul><li><a href="https://www.doenets.lk/downloads">විභාග දෙපාර්තමේන්තුවේ නිල බාගැනීම්</a></li>
<li><a href="https://www.doenets.lk/evaluationreports">නිල ලකුණු දීමේ පටිපාටි සහ ඇගයීම් වාර්තා</a></li></ul></section>"""
    return title, body, urls, [f"Grade {grade}", SUBJECTS[subject], "Practice papers", str(day.year)]


def verify_pdf(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        if response.read(5) != b"%PDF-":
            raise RuntimeError(f"Download did not return a PDF: {url}")
    print("Verified PDF:", url)


def publish_youtube(slot, day, title, question, original, folder, blog):
    if os.getenv("YOUTUBE_UPLOAD_ENABLED", "").lower() != "true":
        print("YouTube upload disabled by repository configuration")
        return None
    privacy = os.getenv("YOUTUBE_PRIVACY", "private").strip() or "private"
    if privacy not in {"private", "unlisted", "public"}:
        raise RuntimeError("Invalid YouTube privacy setting")
    if privacy != "private" and os.getenv("YOUTUBE_PUBLICATION_REVIEWED", "").lower() != "true":
        raise RuntimeError("YouTube publication review required for non-private visibility")
    if slot == "short":
        meta = build_metadata(question, day, privacy=privacy, offset=3)
        meta["snippet"]["description"] += "\n\n" + blog
        movie = append_outro(original, "youtube", "school")
    else:
        marker = f"PNM-LESSON-{day:%Y%m%d}"
        meta = {
            "_marker": marker,
            "snippet": {"title": title, "description": f"පුංචි නැණ මඟ ගණිත පාඩම\n{blog}\n{marker}",
                        "categoryId": "27", "defaultLanguage": "si", "defaultAudioLanguage": "si"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": True},
        }
        movie = original
    return upload(movie, meta, folder)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slot", choices=("image", "short", "paper", "quiz", "lesson"))
    parser.add_argument("--date", type=date.fromisoformat, default=today_in_sri_lanka())
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    day, slot = args.date, args.slot
    folder = Path("school/output/daily") / slot
    folder.mkdir(parents=True, exist_ok=True)
    receipt_path = folder / "receipt.json"
    receipt = {"date": day.isoformat(), "slot": slot, "publish_requested": args.publish}
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    body = labels = image_info = question = media = original = None
    kind = "text"
    if slot == "image":
        from visual_quiz import select, draw_card
        question = image_info = select(day)
        media = folder / "educational-image.png"
        draw_card(question, media)
        title, caption, kind = "අද පින්තූර ප්‍රශ්නය", question["q"], "photo"
    elif slot == "quiz":
        question, media = generate(day, folder)
        title = f"බුද්ධි පරීක්ෂණ ගැටලුව {question['question_number']}"
        caption, kind = facebook_caption(question), "photo"
    elif slot == "short":
        from quiz_topics import select
        from quiz_reel_renderer import render_quiz_video
        question = select(day, offset=3)
        original = render_quiz_video(question, folder)
        media = append_outro(original, "facebook", "school")
        title, caption, kind = "සිංහල කෙටි වීඩියෝ ප්‍රශ්නය", question["q"], "video"
    elif slot == "paper":
        title, body, urls, labels = paper(day, folder=folder, publish=args.publish)
        for url in urls:
            verify_pdf(url)
        receipt["pdfs"] = urls
        caption = title + " ප්‍රශ්න පත්‍රය සහ පිළිතුරු PDF දෙකම නොමිලේ ලබාගන්න."
    else:
        from teaching_video import lesson, render
        topic, scenes = lesson(day)
        title, kind = f"{topic} සිංහල ගණිත පාඩම", "video"
        caption = f"{topic} රූප සටහන් සහ පුහුණු ප්‍රශ්න සමඟ ඉගෙන ගනිමු."
        body = "<h2>" + html.escape(title) + "</h2>" + "".join(
            f"<h3>{html.escape(scene[0])}</h3><p>{html.escape(scene[1])}</p>" for scene in scenes
        )
        labels = ["ගණිතය", "සිංහල පාඩම්", "Teaching video"]
        original = media = render(scenes, folder / "render")
    if body:
        (folder / "blogger-preview.html").write_text(body, encoding="utf-8")
    if not args.publish:
        receipt["rendered"] = True
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        print("Preview complete. No social publishing was requested.")
        return
    for name in ("FB_PAGE_ID", "FB_PAGE_ACCESS_TOKEN"):
        os.environ[name] = os.getenv(name, "").strip()
    version = os.getenv("FB_GRAPH_VERSION", "v27.0")
    title = f"පුංචි නැණ මඟ | {day} | {title}"
    blog, fb_id = Crossposter().publish(
        question=question, title=title, media_kind=kind, media_path=media,
        caption=caption, image_info=image_info, version=version, body=body, labels=labels)
    receipt.update(blogger=blog, facebook_id=fb_id)
    receipt["facebook_url"] = verified_facebook_permalink(
        fb_id, os.environ["FB_PAGE_ACCESS_TOKEN"].strip(), version, kind)
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    if original:
        receipt["youtube"] = publish_youtube(slot, day, title, question, original, folder, blog)
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
