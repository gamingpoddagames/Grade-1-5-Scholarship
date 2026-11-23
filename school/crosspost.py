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
import unicodedata
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
from social_text import clean_caption, clean_title

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
    choices = question.get("choices", [])
    if not question.get("q") or len(choices) not in (3, 4):
        raise ValueError("Cannot create an incomplete Blogger quiz post")
    answer = question.get("answer")
    if not isinstance(answer, int) or not 0 <= answer < len(choices):
        raise ValueError("Invalid answer index")
    labels = question.get("option_labels") or [chr(65 + i) for i in range(len(choices))]
    if len(labels) != len(choices) or len(set(labels)) != len(labels):
        raise ValueError("Option labels are invalid")
    q = html.escape(str(question["q"]))
    def display_label(value):
        label = html.escape(str(value))
        return "(" + label + ")" if str(value).isdigit() else label + ")"
    options = "".join(
        "<li>" + display_label(labels[i]) + " " + html.escape(str(choice)) + "</li>"
        for i, choice in enumerate(choices))
    correct = html.escape(str(choices[answer]))
    answer_label = display_label(labels[answer])
    explanation = html.escape(str(question.get("explanation", "") or "")).replace("\n", "<br>")
    parts = [
        '<section lang="si" class="punchi-quiz">',
        "<h2>" + q + "</h2>",
        "<p>ඔබේ පිළිතුර තෝරාගෙන දැනුම පරීක්ෂා කරන්න.</p>",
        '<ol style="list-style:none;padding-left:0;line-height:2.2;">' + options + "</ol>",
        "<p>පිළිතුර සිතා බලන්න.</p>",
        "<details><summary>නිවැරදි පිළිතුර බලන්න</summary>",
        "<p><strong>" + answer_label + " " + correct + "</strong></p>",
        "<p>" + explanation + "</p></details>",
    ]
    if question.get("learning_notes"):
        notes = question["learning_notes"]
        if not isinstance(notes, list) or not all(isinstance(n, str) for n in notes):
            raise ValueError("Invalid educational learning notes")
        parts.append("<h3>මෙම ගැටලුවෙන් ඉගෙනගන්න දේ</h3>")
        for paragraph in notes:
            parts.append("<p>" + html.escape(paragraph) + "</p>")
    if question.get("puzzle_circles"):
        # Show the identical four-circle data on Blogger without revealing
        # the missing number before the user opens the solution.
        table_rows = []
        for index, wheel in enumerate(question["puzzle_circles"], 1):
            if len(wheel) != 4:
                raise ValueError("Invalid puzzle circle")
            left, top, right, bottom = wheel
            safe_values = [html.escape(str(v)) for v in (left, top, right, bottom)]
            table_rows.append(
                "<tr><td>" + str(index) + "</td>" +
                "".join("<td>" + v + "</td>" for v in safe_values) +
                "</tr>")
        parts.insert(4, (
            "<h3>රූපයේ සංඛ්‍යා</h3>"
            '<table style="border-collapse:collapse;width:100%;text-align:center;" border="1">'
            "<thead><tr><th>වටය</th><th>වම</th><th>ඉහළ</th><th>දකුණ</th><th>පහළ</th></tr></thead>"
            "<tbody>" + "".join(table_rows) + "</tbody></table>"))
    if image_info and image_info.get("image_title"):
        # Keep exact rights-cleared photograph and mandatory attribution visible.
        image_name = urllib.parse.quote(str(image_info["image_title"]).replace(" ", "_"), safe="")
        source = "https://commons.wikimedia.org/wiki/Special:FilePath/" + image_name
        credit = html.escape(str(image_info.get("image_credit", "Wikimedia Commons")))
        source_page = ("https://commons.wikimedia.org/wiki/File:" + image_name)
        license_name = str(image_info.get("image_license", "")).strip()
        license_links = {
            "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
            "CC BY-SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
            "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
            "Public Domain": "https://creativecommons.org/publicdomain/mark/1.0/",
        }
        license_link = license_links.get(license_name)
        attribution = ('<a href="' + html.escape(source_page, quote=True) +
                       '" rel="noopener">Wikimedia Commons මුල් රූපය</a> — ' + credit)
        if license_link:
            attribution += (' | <a href="' + html.escape(license_link, quote=True) +
                            '" rel="noopener">' + html.escape(license_name) + '</a>')
        parts.append(
            '<figure><img loading="lazy" alt="' + q + '" '
            'style="max-width:100%;height:auto;" src="' + html.escape(source, quote=True) + '"/>'
            "<figcaption>ඡායාරූපය: " + attribution +
            " (Facebook quiz card හි රූපය අනුගත කර ඇත)</figcaption></figure>")
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
    fields = "link" if kind == "photo" else "permalink_url"
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
        permission = os.getenv("BLOGGER_ALLOW_PUBLICATION", "").lower()
        if permission not in ("", "true"):
            raise RuntimeError(
                "Blogger publication explicitly disabled or invalid in GitHub variables; "
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
        if media_kind not in {"video", "photo", "text"}:
            raise ValueError("Media kind must be video, photo or text")
        if media_kind != "text" and not Path(media_path).is_file():
            raise RuntimeError("Media is missing; nothing published")
        # Preserve the exact title of an existing post created before the
        # desktop-caption update. Renaming the title key would accidentally
        # create a second Blogger article and a duplicate Facebook post.
        old_title = title
        normalized_title = clean_title(title)
        if old_title in getattr(self, "existing", {}):
            title = old_title
        else:
            title = normalized_title
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
            fb_id = value.partition(":")[2]
            # A verified permalink can become available later; repair an embed
            # without ever reposting the already-published Facebook video.
            if EMBED_MARKER not in article.get("content", ""):
                permalink = verified_facebook_permalink(
                    fb_id, os.environ["FB_PAGE_ACCESS_TOKEN"], version, media_kind)
                if permalink:
                    self.update(
                        article["id"],
                        article["content"] + facebook_embed(permalink, media_kind))
                    print("Recovered missing Facebook embed on existing Blogger article")
            print("SKIPPED duplicate Facebook post for existing Blogger article:", article_url)
            return article_url, fb_id
        if value == "PENDING":
            raise RuntimeError(
                "Facebook delivery previously attempted with uncertain result. "
                "Review Page and Blogger before attempting a retry.")
        if value != "READY":
            raise RuntimeError("Unexpected Blogger delivery state")

        full_caption = caption.replace(FACEBOOK_LANDING_URL, article_url)
        if article_url not in full_caption:
            full_caption += "\n\n" + article_url
        full_caption = clean_caption(full_caption)
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
        elif media_kind == "photo":
            from facebook_card import publish
            object_id = publish(media_path, full_caption)
        else:
            from daily_publisher import publish
            object_id = publish(
                full_caption, os.environ["FB_PAGE_ID"],
                os.environ["FB_PAGE_ACCESS_TOKEN"], version)
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
