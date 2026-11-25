"""Render and distribute dated practice PDFs from the existing curriculum."""
import html
import json
import os
import random
import urllib.error
import urllib.parse
import urllib.request

from curriculum_bank import get_questions
from curriculum_pages import CSS
from supplementary_questions import SUPPLEMENTARY_SUBJECTS, questions

REPO = "gamingpoddagames/Grade-1-5-Scholarship"
API = f"https://api.github.com/repos/{REPO}"


def rows_for_day(day, grade, subject):
    rng = random.Random(day.toordinal())
    if subject in SUPPLEMENTARY_SUBJECTS:
        return questions(subject, rng)
    bank = [row for row in get_questions() if row["grade"] == grade and row["subject"] == subject]
    if subject != "math":
        return rng.sample(bank, min(10, len(bank)))
    choices = []
    for index in range(10):
        left = rng.randint(2, 6 + grade * 4)
        right = rng.randint(1, left)
        if index % 3 == 0 and grade >= 3:
            left = rng.randint(2, 10)
            right = rng.randint(2, 10)
            op, answer = "×", left * right
        elif index % 2:
            op, answer = "−", left - right
        else:
            op, answer = "+", left + right
        options = [answer, answer + 1, answer + 3, answer + 5]
        rng.shuffle(options)
        choices.append({
            "q": f"{left} {op} {right} = කීයද?",
            "choices": options,
            "answer": options.index(answer),
            "explanation": f"{left} {op} {right} = {answer}",
        })
    return choices


def render_pdfs(folder, day, grade, subject, title):
    from weasyprint import HTML
    rows = rows_for_day(day, grade, subject)
    paths = []
    for answers in (False, True):
        label = "පිළිතුරු" if answers else "ප්‍රශ්න පත්‍රය"
        parts = [f'<div class="header"><h1>{html.escape(title)} · {label}</h1>'
                 f'<p>පුංචි නැණ මඟ · {day} · මුල් නිර්මාණ පුහුණු පත්‍රය</p></div>']
        for index, row in enumerate(rows, 1):
            question = html.escape(row["q"])
            options = "".join(f"<span>{chr(65+i)}) {html.escape(str(value))}</span>"
                              for i, value in enumerate(row["choices"]))
            correct = row["answer"]
            answer = html.escape(str(row["choices"][correct]))
            explanation = html.escape(row["explanation"])
            solution = f'<p class="answer">{chr(65+correct)}) {answer} · {explanation}</p>' if answers else ""
            parts.append(f'<section class="question"><h2>{index}. {question}</h2>'
                         f'<div class="options">{options}</div>{solution}</section>')
        suffix = "answers" if answers else "paper"
        path = folder / f"{day}-grade-{grade}-{subject}-{suffix}.pdf"
        HTML(string=f'<!doctype html><html lang="si"><meta charset="utf-8">'
                    f'<style>{CSS}</style><body>{"".join(parts)}</body></html>').write_pdf(path)
        if path.stat().st_size < 1200 or not path.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError(f"PDF quality check failed for {path.name}")
        paths.append(path)
    return paths


def request(url, token, *, payload=None, content_type="application/json"):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
               "Content-Type": content_type, "User-Agent": "PunchiNenaMagaDailyPapers"}
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and payload is None:
            return None
        raise RuntimeError(f"GitHub paper archive request failed (HTTP {exc.code})") from None


def publish_pdfs(day, paths):
    token = os.environ.get("PAPER_ARCHIVE_TOKEN", "").strip()
    if not token or os.getenv("GITHUB_REPOSITORY") != REPO:
        raise RuntimeError("Authorized repository release credentials are required for paper downloads")
    tag = f"practice-papers-{day:%Y-%m}"
    release = request(f"{API}/releases/tags/{tag}", token)
    if release is None:
        payload = {"tag_name": tag, "target_commitish": "main",
                   "name": f"Punchi Nena Maga practice papers · {day:%Y-%m}",
                   "body": "Original Sinhala educational practice papers and separate answers.",
                   "make_latest": "false"}
        release = request(f"{API}/releases", token, payload=json.dumps(payload).encode())
    release_id = int(release["id"])
    assets = {asset["name"]: asset for asset in release["assets"]}
    urls = []
    for path in paths:
        asset = assets.get(path.name)
        if asset is None:
            upload = f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets"
            upload += "?" + urllib.parse.urlencode({"name": path.name})
            asset = request(upload, token, payload=path.read_bytes(), content_type="application/pdf")
        expected = f"https://github.com/{REPO}/releases/download/{tag}/{path.name}"
        if asset.get("state") != "uploaded" or asset.get("browser_download_url") != expected:
            raise RuntimeError(f"Paper asset is missing or incomplete: {path.name}")
        urls.append(expected)
    return urls
