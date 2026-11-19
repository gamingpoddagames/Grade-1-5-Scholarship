#!/usr/bin/env python3
"""Weekly read-only school Blogger growth health report.

No Search Console or AdSense performance is inferred. Never prints credentials.
"""
import datetime as dt
import json
import os
import pathlib
import urllib.error
import urllib.request
import urllib.parse

from blogger_publisher import (API, EXPECTED_BLOG_ID, EXPECTED_BLOG_HOST,
    access_token_from_env, authenticate_blog, list_existing)

BLOG="https://punchinanamaga.blogspot.com/"

def check_public(url):
    req=urllib.request.Request(url,headers={"User-Agent":"PunchiNenaMaga-SiteMonitor/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=25) as resp:
            return {"http_status":resp.status,"final_host":urllib.parse.urlparse(resp.url).hostname}
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
        return {"error":type(exc).__name__}

def main():
    token=access_token_from_env()
    blog=authenticate_blog(token)
    existing=list_existing("posts",token)
    output=pathlib.Path("health_output")
    manifest_path=pathlib.Path("blogger_output/post-index.json")
    planned=json.loads(manifest_path.read_text(encoding="utf-8"))
    remaining=[row["title"] for row in planned if row["title"] not in existing]
    drafts=sum(1 for x in existing.values() if x["status"]=="draft")
    live=sum(1 for x in existing.values() if x["status"]=="live")
    home=check_public(BLOG)
    posts_sitemap=check_public(BLOG+"sitemap.xml")
    pages_sitemap=check_public(BLOG+"sitemap-pages.xml")
    status={
        "checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "blog":EXPECTED_BLOG_HOST,
        "verified_owner_blog":str(blog.get("id"))==EXPECTED_BLOG_ID,
        "known_live_titles":live,"known_draft_titles":drafts,
        "editorial_queue_total":len(planned),"editorial_queue_remaining":len(remaining),
        "public_homepage":home,"blogger_posts_sitemap":posts_sitemap,
        "blogger_pages_sitemap":pages_sitemap,
        "note":"Read-only Blogger API and public URL checks, NOT Google indexing or Ads approval."
    }
    output.mkdir(exist_ok=True)
    (output/"weekly-health.json").write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")
    print("WEEKLY BLOGGER HEALTH:",json.dumps(status,ensure_ascii=False))
    if len(remaining)<=4:
        print("::warning::Blogger original article queue has 4 or fewer unique posts remaining; prepare reviewed additions.")
    if not remaining:
        print("::warning::The finite article queue is exhausted; scheduled publishing will create no new posts.")
    if home.get("http_status")!=200:
        raise RuntimeError("Public Blogger homepage did not return HTTP 200")
    if posts_sitemap.get("http_status")!=200:
        raise RuntimeError("Blogger post sitemap did not return HTTP 200")
    if pages_sitemap.get("http_status")!=200:
        raise RuntimeError("Blogger page sitemap did not return HTTP 200")
    print("HEALTH CHECK PASSED. Does not establish Google rankings, visitors, or AdSense eligibility.")

if __name__=="__main__":
    main()
