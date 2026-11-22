"""Validate public lesson destinations before any Facebook API call."""
import re
from urllib.parse import parse_qsl, urlsplit

BLOG_HOST = 'punchinanamaga.blogspot.com'
FACEBOOK_LANDING_URL = f'https://{BLOG_HOST}/p/learning-welcome.html'
URL_RE = re.compile(r'(?:https?://|//|www\.)[^\s<>\"\']+', re.IGNORECASE)
REDIRECT_KEYS = {'url', 'target', 'redirect', 'redirect_url', 'redirect_uri', 'next', 'destination'}


def validate_blogger_links(caption):
    urls = URL_RE.findall(caption)
    if not urls:
        raise ValueError('Facebook caption must include a direct Blogger lesson link')
    for raw in urls:
        url = urlsplit(raw.rstrip('.,);]'))
        if (url.scheme != 'https' or url.netloc.lower() != BLOG_HOST
                or url.username or url.password):
            raise ValueError('Facebook lesson links must point directly to the owned HTTPS Blogger site')
        for key, value in parse_qsl(url.query):
            if key.lower() in REDIRECT_KEYS or '://' in value or value.startswith('//'):
                raise ValueError('Redirect destinations are not permitted in Blogger promotion links')
    return True
