#!/usr/bin/env python3
"""Blogger v3 safe publisher for 'පුංචි නැණ මඟ'.

Defaults to local offline preview. Google credentials are ONLY read at runtime
from environment variables. No keys or refresh tokens are printed or saved.
Existing published titles are never overwritten; exact-match drafts may be published. No deletes.
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

from blogger_export import build_article, FB
from curriculum_bank import SUBJECTS, get_questions

EXPECTED_BLOG_ID = "1195814952260080161"
EXPECTED_BLOG_HOST = "punchinanamaga.blogspot.com"
API = "https://www.googleapis.com/blogger/v3"

PAGE_TITLES = {
    "about": "අප ගැන",
    "contact": "සම්බන්ධතා",
    "privacy": "පෞද්ගලිකත්ව ප්‍රතිපත්තිය",
    "terms": "භාවිත නියමයන්",
}

def request_json(url, *, access_token=None, method="GET", payload=None):
    headers = {"Accept": "application/json", "User-Agent": "PunchiNenaMaga-SchoolPublisher/1.0"}
    if access_token:
        headers["Authorization"] = "Bearer " + access_token
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Do not echo response bodies, headers, OAuth tokens or request internals.
        raise RuntimeError(f"Blogger/Google request failed (HTTP {exc.code})") from None
    except urllib.error.URLError:
        raise RuntimeError("Blogger/Google connection failed") from None

def access_token_from_env():
    variables = ("BLOGGER_CLIENT_ID", "BLOGGER_CLIENT_SECRET", "BLOGGER_REFRESH_TOKEN")
    absent = [name for name in variables if not os.getenv(name)]
    if absent:
        raise RuntimeError("Required GitHub Actions secrets are not configured: " + ", ".join(absent))
    body = urllib.parse.urlencode({
        "client_id": os.environ["BLOGGER_CLIENT_ID"],
        "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=body, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Google authorization failed (HTTP {exc.code}); recheck OAuth access") from None
    token = result.get("access_token")
    if not token:
        raise RuntimeError("Google authorization did not return an access token")
    return token

def authenticate_blog(token):
    result = request_json(f"{API}/blogs/{EXPECTED_BLOG_ID}", access_token=token)
    url = urllib.parse.urlparse(result.get("url", ""))
    if str(result.get("id")) != EXPECTED_BLOG_ID or url.hostname != EXPECTED_BLOG_HOST:
        raise RuntimeError("Blog identity mismatch. Publishing stopped to protect other blogs.")
    return result

def list_existing(kind, token):
    titles = {}
    endpoint = f"{API}/blogs/{EXPECTED_BLOG_ID}/{kind}"
    statuses = ("live", "draft") if kind == "pages" else ("live", "draft", "scheduled")
    # Official Blogger API v3 uses live/draft/scheduled for posts.
    for status in statuses:
        page_token = None
        while True:
            params = {"maxResults": 100, "status": status, "fetchBodies": "false"}
            if page_token:
                params["pageToken"] = page_token
            url = endpoint + "?" + urllib.parse.urlencode(params)
            data = request_json(url, access_token=token)
            for item in data.get("items", []):
                title = (item.get("title") or "").strip()
                if title and (title not in titles or status == "live"):
                    titles[title] = {"id": str(item.get("id", "")), "status": status}
            next_token = data.get("nextPageToken")
            if not next_token:
                break
            if next_token == page_token:
                raise RuntimeError("Unexpected Blogger pagination loop")
            page_token = next_token
    return titles

def planned_items(export_dir, kind, day):
    if kind == "pages":
        source = json.loads((export_dir / "pages-index.json").read_text(encoding="utf-8"))
        return [(PAGE_TITLES[row["slug"]], (export_dir / row["file"]).read_text(encoding="utf-8"), []) for row in source]
    if kind != "posts":
        raise ValueError("Unknown content kind")
    manifest = json.loads((export_dir / "post-index.json").read_text(encoding="utf-8"))
    # Same deterministic daily order, rotating among grades and subjects.
    offset = (day - dt.date(2026, 11, 19)).days % len(manifest)
    manifest = manifest[offset:] + manifest[:offset]
    return [(row["title"], (export_dir / row["file"]).read_text(encoding="utf-8"), row["labels"]) for row in manifest]

def execute(*, mode, kind, export_dir, day, limit=1, token_factory=access_token_from_env):
    assert mode in ("preview", "draft", "publish")
    assert kind in ("posts", "pages")
    if not 1 <= limit <= 4:
        raise ValueError("Maximum four items per run to protect content quality")
    items = planned_items(export_dir, kind, day)
    if mode == "preview":
        print(f"PREVIEW ONLY: {len(items)} candidate {kind}; no authorization or API writes")
        for title, _, _ in items[:limit]:
            print("Candidate title:", title)
        return {"prepared": len(items), "created": 0, "skipped": 0}
    if kind == "pages" and mode == "draft":
        raise RuntimeError("Blogger API page drafting is not reliably supported; review and explicitly publish pages instead")
    if mode == "publish" and os.getenv("BLOGGER_ALLOW_PUBLICATION", "").lower() != "true":
        raise RuntimeError("Public posting disabled: set BLOGGER_ALLOW_PUBLICATION=true in GitHub Actions Variables")
    token = token_factory()
    blog = authenticate_blog(token)
    print("Authorized blog:", blog.get("name", "Blogger blog"), "(" + EXPECTED_BLOG_HOST + ")")
    existing = list_existing(kind, token)
    created = 0
    skipped = 0
    for title, content, labels in items:
        previous = existing.get(title)
        if previous:
            if (mode == "publish" and kind == "posts" and previous["status"] == "draft"
                    and created < limit and previous["id"]):
                original = request_json(
                    f"{API}/blogs/{EXPECTED_BLOG_ID}/posts/{previous['id']}",
                    access_token=token)
                if original.get("content", "").strip() == content.strip():
                    result = request_json(
                        f"{API}/blogs/{EXPECTED_BLOG_ID}/posts/{previous['id']}/publish",
                        access_token=token, method="POST")
                    if not result.get("id"):
                        raise RuntimeError("Blogger did not confirm draft publication")
                    print("PUBLISHED MATCHING DRAFT:", title, "| ID", str(result["id"]))
                    created += 1
                else:
                    print("SKIPPED edited draft (not overwritten):", title)
                    skipped += 1
            else:
                skipped += 1
            continue
        if created >= limit:
            break
        if len(content) < (200 if kind == "pages" else 500) or "<h2>" not in content:
            raise ValueError("Article too short or malformed; publication stopped")
        payload = {"kind": "blogger#post" if kind == "posts" else "blogger#page",
                   "blog": {"id": EXPECTED_BLOG_ID}, "title": title, "content": content}
        if kind == "posts":
            payload["labels"] = labels
        params = urllib.parse.urlencode({"isDraft": "true" if mode == "draft" else "false"}) if kind == "posts" else ""
        suffix = "?" + params if params else ""
        result = request_json(f"{API}/blogs/{EXPECTED_BLOG_ID}/{kind}{suffix}",
                              access_token=token, method="POST", payload=payload)
        if not result.get("id"):
            raise RuntimeError("Blogger did not confirm an item ID")
        # Never print private credentials, nor claim publication during draft mode.
        print(("DRAFT CREATED" if mode == "draft" else "PUBLISHED") + ": " + title +
              " | ID " + str(result["id"]))
        created += 1
        existing[title] = {"id": str(result["id"]), "status": "draft" if mode == "draft" else "live"}
    print(f"COMPLETE: mode={mode} kind={kind} new={created} preexisting_titles_skipped={skipped}")
    return {"prepared": len(items), "created": created, "skipped": skipped}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preview", "draft", "publish"), default="preview")
    parser.add_argument("--kind", choices=("posts", "pages"), default="posts")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--date", help="YYYY-MM-DD date in Asia/Colombo (optional)")
    parser.add_argument("--export-dir", default="blogger_output")
    args = parser.parse_args()
    if args.date:
        today = dt.date.fromisoformat(args.date)
    else:
        today = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)).date()
    execute(mode=args.mode, kind=args.kind, export_dir=pathlib.Path(args.export_dir),
            day=today, limit=args.limit)

if __name__ == "__main__":
    main()
