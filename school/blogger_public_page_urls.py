#!/usr/bin/env python3
"""Inspect own Blogger page links without printing credentials or editing the blog."""
import sys
from blogger_publisher import API, EXPECTED_BLOG_ID, EXPECTED_BLOG_HOST, access_token_from_env, authenticate_blog, request_json

def main():
    token=access_token_from_env()
    authenticate_blog(token)
    params=""
    wanted={"පෞද්ගලිකත්ව ප්‍රතිපත්තිය", "භාවිත නියමයන්", "අප ගැන", "සම්බන්ධතා"}
    seen=set()
    while True:
        suffix=("?"+params) if params else "?maxResults=100"
        response=request_json(f"{API}/blogs/{EXPECTED_BLOG_ID}/pages{suffix}", access_token=token)
        for item in response.get("items",[]):
            title=item.get("title","")
            url=item.get("url","")
            if title in wanted and url.startswith(f"https://{EXPECTED_BLOG_HOST}/"):
                print(f"PUBLIC BLOGGER PAGE: {title}: {url}")
                seen.add(title)
        nxt=response.get("nextPageToken")
        if not nxt:break
        import urllib.parse
        params=urllib.parse.urlencode({"maxResults":100,"pageToken":nxt})
    missing=wanted-seen
    if missing:
        print("Not returned as public pages:", ", ".join(sorted(missing)))
    if "පෞද්ගලිකත්ව ප්‍රතිපත්තිය" not in seen or "භාවිත නියමයන්" not in seen:
        raise SystemExit("Cannot verify required legal-page public URLs")
if __name__=="__main__":
    main()
