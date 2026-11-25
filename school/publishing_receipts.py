"""Shared Blogger/Facebook receipt validation with no rendering dependencies."""
import datetime as dt
import re
import urllib.parse

from blogger_publisher import EXPECTED_BLOG_HOST

STATE = re.compile(r"<!-- PNM_FACEBOOK_STATE:(READY|PENDING|PUBLISHED:[A-Za-z0-9_]+) -->")


def today_in_sri_lanka():
    return (dt.datetime.now(dt.timezone.utc) +
            dt.timedelta(hours=5, minutes=30)).date()


def validate_blog_url(raw):
    value = urllib.parse.urlsplit(raw or "")
    if (value.scheme != "https" or value.hostname != EXPECTED_BLOG_HOST
            or value.username or value.password or not value.path):
        raise RuntimeError("Blogger returned an unexpected article URL; no Facebook post sent")
    return raw
