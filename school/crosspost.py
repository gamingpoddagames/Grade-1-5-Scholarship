#!/usr/bin/env python3
"""Idempotent Blogger-first publishing for original Sinhala Facebook quizzes.

Creates the matching public Blogger article before Facebook publishing so the
Facebook caption links to the *actual* article. Blogger is also the durable
delivery ledger. PENDING remote sends are never blindly retried.
"""
import datetime as dt
import html
import os
import re
import urllib.parse
import urllib.request
import json
from pathlib import Path

from blogger_publisher import (
    API, EXPECTED_BLOG_ID, EXPECTED_BLOG_HOST, access_token_from_env,
    authenticate_blog, list_existing, request_json,
)
from blogger_link_safety import FACEBOOK_LANDING_URL
from font_safety import check_caption

STATE = re.compile(r"<!-- PNM_FACEBOOK_STATE:(READY|PENDING|PUBLISHED:[A-Za-z0-9_]+) -->")
EMBED_MARKER = "<!-- PNM_FACEBOOK_EMBED -->"
TRUSTED_FACEBOOK_HOSTS = {"www.facebook.com", "web.facebook.com", "facebook.com"}


def today_in_sri_lanka():
    return (dt.datetime.now(dt.timezone.utc) +
            dt.timedelta(hours=5, minutes=30)).date()


def validate_blog_url(raw):
    value = urllib.parse.urlsplit(raw or "")
    if (value.scheme != "https" or value.hostname != EXPECTED_BLOG_HOST
            or value.username or value.password or not value.path):
        raise RuntimeError("Blogger returned an unexpected article URL; no Facebook post sent")
    return raw


def article_content(question, *, media_kind, image_info=None):
    if not question.get("q") or len(question.get("choices", [])) != 4:
        raise ValueError("Cannot create an incomplete Blogger quiz post")
    answer = question.get("answer")
    if not isinstance(answer, int) or not 0 <= answer < 4:
        raise ValueError("Invalid answer index")
    q = html.escape(str(question["q"]))
    options = "".join(
        "<li>" + chr(65 + i) + ") " + html.escape(str(choice)) + "</li>"
        for i, choice in enumerate(question["choices"]))
    correct = html.escape(str(question["choices"][answer]))
    explanation = html.escape(str(question.get("explanation", "") or ""))
    parts = [
        '<section lang="si" class="punchi-quiz">',
        "<h2>" + q + "</h2>",
        "<p>ඔබේ පිළිතුර තෝරාගෙන දැනුම පරීක්ෂා කරන්න.</p>",
        '<ol style="list-style:none;padding-left:0;line-height:2.2;">' + options + "</ol>",
        "<p>පිළිතුර සිතා බලන්න.</p>",
        "<details><summary>නිවැරදි පිළිතුර බලන්න</summary>",
        "<p><strong>" + chr(65 + answer) + ") " + correct + "</strong></p>",
        "<p>" + explanation + "</p></details>",
    ]
    if image_info and image_info.get("image_title"):
        # Keep exact rights-cleared photograph and mandatory attribution visible.
        image_name = urllib.parse.quote(str(image_info["image_title"]).replace(" ", "_"), safe="")
        source = "https://commons.wikimedia.org/wiki/Special:FilePath/" + image_name
        credit = html.escape(str(image_info.get("image_credit", "Wikimedia Commons")))
        parts.append(
            '<figure><img loading="lazy" alt="' + q + '" '
            'style="max-width:100%;height:auto;" src="' + html.escape(source, quote=True) + '"/>'
            "<figcaption>ඡායාරූපය: " + credit +
            " (Wikimedia Commons, මුල් රූපය)</figcaption></figure>")
    parts.extend([
        "<p>මෙය ළමුන්ගේ අධ්‍යාපනික පුහුණුව සඳහා නිර්මාණය කළ ප්‍රශ්නයකි.</p>",
        "<p>තවත් නොමිලේ ප්‍රශ්න සහ පිළිතුරු: "
        '<a href="https://punchinanamaga.blogspot.com/p/learning-welcome.html">'
        "පුංචි නැණ මඟ</a></p>",
        "</section>",
        "<!-- PNM_FACEBOOK_STATE:READY -->"
    ])
    return "\n".join(parts)


def safe_facebook_url(url):
    parsed = urllib.parse.urlsplit(url or "")
    if (parsed.scheme != "https" or parsed.hostname not in TRUSTED_FACEBOOK_HOSTS
            or parsed.username or parsed.password or not parsed.path):
        return None
    return url


def verified_facebook_permalink(object_id, page_token, version, kind):
    """Resolve true Meta permalink; never infer a URL from an ID."""
    if not re.fullmatch(r"[0-9_]+", str(object_id)):
        return None
    fields = "permalink_url,link" if kind == "photo" else "permalink_url"
    params = urllib.parse.urlencode({"fields": fields, "access_token": page_token})
    url = f"https://graph.facebook.com/{version}/{object_id}?{params}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=22) as response:
            payload = json.load(response)
    except Exception:
        print("Facebook permalink unavailable; preserving Blogger article without an unverified embed")
        return None
    for key in ("permalink_url", "link"):
        value = safe_facebook_url(payload.get(key))
        if value:
            return value
    return None


def facebook_embed(permalink, media_kind):
    link = html.escape(permalink, quote=True)
    widget = ("video" if media_kind == "video" else "post")
    plugin = "https://www.facebook.com/plugins/" + widget + ".php?href=" + (
        urllib.parse.quote(permalink, safe=""))
    return (
        "\n" + EMBED_MARKER + "\n"
        "<h3>අදාළ Facebook " + ("වීඩියෝව" if media_kind == "video" else "පළ කිරීම") + "</h3>"
        '<p><a href="' + link + '" rel="noopener noreferrer">Facebook හි බලන්න</a></p>'
        '<iframe title="Facebook quiz" loading="lazy" allowfullscreen '
        'style="max-width:100%;width:560px;border:0;min-height:360px;" '
        'src="' + html.escape(plugin, quote=True) + '"></iframe>'
    )


class Crossposter:
    """One session per workflow: publish article, then Facebook, then embed."""

    def __init__(self):
        if os.getenv("BLOGGER_ALLOW_PUBLICATION", "").lower() != "true":
            raise RuntimeError(
                "Crossposting requires repository variable BLOGGER_ALLOW_PUBLICATION=true; "
                "no unmatched Facebook post was sent")
        if not os.getenv("FB_PAGE_ID") or not os.getenv("FB_PAGE_ACCESS_TOKEN"):
            raise RuntimeError("Facebook Page credentials missing; no Blogger-only post was created")
        self.token = access_token_from_env()
        authenticate_blog(self.token)
        self.existing = list_existing("posts", self.token)

    def get(self, item_id):
        return request_json(
            f"{API}/blogs/{EXPECTED_BLOG_ID}/posts/{item_id}?view=ADMIN",
            access_token=self.token)

    def update(self, item_id, content):
        updated = request_json(
            f"{API}/blogs/{EXPECTED_BLOG_ID}/posts/{item_id}",
            access_token=self.token, method="PATCH", payload={"content": content})
        if not updated.get("id"):
            raise RuntimeError("Blogger did not confirm article update")
        return updated

    def article(self, question, title, media_kind, image_info=None):
        previous = self.existing.get(title)
        if previous:
            if previous["status"] != "live" or not previous["id"]:
                raise RuntimeError("Blogger title exists as draft/scheduled; review it before publishing")
            article = self.get(previous["id"])
            validate_blog_url(article.get("url"))
            return article, False
        payload = {
            "kind": "blogger#post",
            "blog": {"id": EXPECTED_BLOG_ID},
            "title": title,
            "content": article_content(question, media_kind=media_kind, image_info=image_info),
            "labels": ["සිංහල ප්‍රශ්න", "Grade 1-5", "Facebook Quiz"]
        }
        article = request_json(
            f"{API}/blogs/{EXPECTED_BLOG_ID}/posts?isDraft=false",
            access_token=self.token, method="POST", payload=payload)
        if not article.get("id"):
            raise RuntimeError("Blogger did not confirm new article creation")
        validate_blog_url(article.get("url"))
        self.existing[title] = {"id": str(article["id"]), "status": "live"}
        print("Matching Blogger article published:", article["url"])
        return article, True

    def publish(self, *, question, title, media_kind, media_path, caption,
                image_info=None, version="v27.0"):
        """Return Blogger URL and optional Meta ID; abort on uncertain retry."""
        if media_kind not in {"video", "photo"}:
            raise ValueError("Media kind must be video or photo")
        if not Path(media_path).is_file():
            raise RuntimeError("Media is missing; nothing published")
        article, created = self.article(question, title, media_kind, image_info)
        article_url = validate_blog_url(article.get("url"))
        state = STATE.search(article.get("content", ""))
        if not state:
            # A preexisting unmanaged post may already have a corresponding FB post.
            raise RuntimeError(
                "Matching legacy Blogger article found without delivery receipt; "
                "Facebook was not reposted to avoid duplicates")
        value = state.group(1)
        if value.startswith("PUBLISHED:"):
            print("SKIPPED duplicate Facebook post for existing Blogger article:", article_url)
            return article_url, value.partition(":")[2]
        if value == "PENDING":
            raise RuntimeError(
                "Facebook delivery previously attempted with uncertain result. "
                "Review Page and Blogger before attempting a retry.")
        if value != "READY":
            raise RuntimeError("Unexpected Blogger delivery state")

        full_caption = caption.replace(FACEBOOK_LANDING_URL, article_url)
        if article_url not in full_caption:
            full_caption += "\n\n" + article_url
        check_caption(full_caption)

        # Reserve the single remote attempt in durable Blogger state *first*.
        pending_content = STATE.sub("<!-- PNM_FACEBOOK_STATE:PENDING -->",
                                    article["content"], count=1)
        self.update(article["id"], pending_content)
        if media_kind == "video":
            from facebook_video import upload
            object_id = upload(
                media_path, os.environ["FB_PAGE_ID"], os.environ["FB_PAGE_ACCESS_TOKEN"],
                version, title=title, description=full_caption)
        else:
            from facebook_card import publish
            object_id = publish(media_path, full_caption)
        if not object_id:
            raise RuntimeError("Facebook did not return a confirmed object ID")
        print("Facebook delivery confirmed:", object_id)

        permalink = verified_facebook_permalink(
            str(object_id), os.environ["FB_PAGE_ACCESS_TOKEN"], version, media_kind)
        latest = self.get(article["id"])
        content = latest.get("content", pending_content)
        if permalink and EMBED_MARKER not in content:
            content += facebook_embed(permalink, media_kind)
        content = STATE.sub(
            "<!-- PNM_FACEBOOK_STATE:PUBLISHED:" + str(object_id) + " -->",
            content, count=1)
        self.update(article["id"], content)
        print("Blogger + Facebook matched successfully:", article_url)
        return article_url, str(object_id)
