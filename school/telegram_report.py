#!/usr/bin/env python3
"""Private Telegram status summary for Punchi Nena Maga.

Only sends to explicitly configured TELEGRAM_CHAT_ID, never a public channel
by default. Does not infer live AdSense earnings or Google Search rankings.
"""
import argparse
import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

REPO="gamingpoddagames/Grade-1-5-Scholarship"
BLOG="https://punchinanamaga.blogspot.com/"
WORKFLOWS=(
    "Punchi Nena Maga Daily Education",
    "Blogger Auto Publisher (Google OAuth)",
    "School Daily Content (No AI)",
    "Test Sinhala Voiceover (No Paid AI)",
    "School Website Visitor Promotion (FB Photo and Sinhala Video)",
    "Publish Scholarship Website",
    "Weekly Blogger Growth Health Check",
    "Build Blogger Starter Kit",
)
REPORT_LINK="https://github.com/"+REPO+"/actions"

def get_json(url, token=""):
    headers={"Accept":"application/vnd.github+json","User-Agent":"PunchiNenaMaga-TelegramReporting/1.0"}
    if token:headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=30) as reply:
        return json.load(reply)

def workflow_summary(api_response, now):
    cutoff=now-dt.timedelta(days=7)
    counts={x:Counter() for x in WORKFLOWS}
    recent=[]
    for row in api_response.get("workflow_runs",[]):
        name=row.get("name","")
        if name not in counts:continue
        created=row.get("created_at","")
        try:created_at=dt.datetime.fromisoformat(created.replace("Z","+00:00"))
        except (ValueError,TypeError):continue
        if created_at<cutoff:continue
        outcome=row.get("conclusion") or row.get("status") or "unknown"
        counts[name][outcome]+=1
        recent.append((created_at,name,outcome))
    return counts,sorted(recent,reverse=True)

def format_report(now, runs, blogger=None):
    counts,recent=workflow_summary(runs,now)
    sri=now+dt.timedelta(hours=5,minutes=30)
    lines=[
        "📚 පුංචි නැණ මඟ — Daily Operations Report",
        "📅 "+sri.strftime("%Y-%m-%d %H:%M")+" (Sri Lanka)",
        "",
        "📰 Blogger website: "+BLOG,
        "🔗 GitHub resources: https://gamingpoddagames.github.io/Grade-1-5-Scholarship/",
        "",
        "⚙️ GitHub Actions: last 7 days",
    ]
    for name in WORKFLOWS:
        c=counts[name]
        ok=c["success"]
        failed=c["failure"]+c["timed_out"]+c["action_required"]
        pending=sum(c[s] for s in ("in_progress","queued","pending","waiting","requested"))
        lines.append(f"• {name}: ✅{ok} ❌{failed} ⏳{pending}")
    failures=[item for item in recent if item[2] in ("failure","timed_out","action_required")]
    if failures:
        lines.extend(("","⚠️ Recent failed runs: "+str(len(failures))))
        for date,name,state in failures[:3]:
            lines.append("• "+date.strftime("%m-%d")+" "+name+" ("+state+")")
    if blogger is not None:
        lines.append("")
        lines.append("📝 Blogger API (verified account)")
        lines.append("• Public post titles: "+str(blogger["live"]))
        lines.append("• Private draft titles: "+str(blogger["draft"]))
        lines.append("• Original articles remaining in queue: "+str(blogger["remaining"]))
        if "daily_delivery" in blogger:
            lines.append("• Today's paired Blogger and Facebook delivery:")
            for title, url, status in blogger["daily_delivery"][:12]:
                lines.append(f"  {title} — {status} {url}")
        if blogger["remaining"]<=4:
            lines.append("⚠️ New original content needed before publishing queue runs out.")
    else:
        lines.extend(("","📝 Blogger API: unavailable or not configured; no content count inferred."))
    lines.extend((
        "",
        "💰 AdSense: approval and income are NOT verified by this bot.",
        "   Check: https://www.google.com/adsense/",
        "🔎 Search Console: indexing/click metrics NOT verified by this bot.",
        "   Check: https://search.google.com/search-console",
        "📈 UTM links added to Facebook campaigns (analytics connection needed for real clicks).",
        "🔍 Workflow details: "+REPORT_LINK
    ))
    return "\n".join(lines)

def telegram_send(message, bot_token, chat_id):
    if not bot_token or not chat_id:
        print("Telegram report preview only: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.")
        return False
    # send to the exact chat configured by owner; never print tokens/chat id
    url="https://api.telegram.org/bot"+bot_token+"/sendMessage"
    encoded=urllib.parse.urlencode({
        "chat_id":chat_id,"text":message[:3800],
        "disable_web_page_preview":"true"
    }).encode()
    req=urllib.request.Request(url,data=encoded,method="POST",
        headers={"Content-Type":"application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req,timeout=35) as resp:
            result=json.load(resp)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Telegram delivery failed, HTTP "+str(exc.code)+". Confirm bot and chat permissions.") from None
    except urllib.error.URLError:
        raise RuntimeError("Telegram network connection failed") from None
    if not result.get("ok"):
        raise RuntimeError("Telegram did not confirm message delivery")
    print("Telegram report delivery confirmed by Telegram API (message ID received).")
    return True

def read_blogger_inventory():
    # Keep the private OAuth credentials scoped to this optional read-only step.
    needed=("BLOGGER_CLIENT_ID","BLOGGER_CLIENT_SECRET","BLOGGER_REFRESH_TOKEN")
    if any(not os.getenv(x) for x in needed):return None
    from blogger_publisher import (API, EXPECTED_BLOG_ID, access_token_from_env,
                                   authenticate_blog, list_existing, request_json)
    from crosspost import STATE, today_in_sri_lanka, validate_blog_url
    from blogger_export import export
    import pathlib
    import tempfile
    token=access_token_from_env()
    authenticate_blog(token)
    existing=list_existing("posts",token)
    with tempfile.TemporaryDirectory() as folder:
        output=pathlib.Path(folder)
        export(output)
        items=json.loads((output/"post-index.json").read_text(encoding="utf-8"))
    day = today_in_sri_lanka()
    markers = ("අද පින්තූර ප්‍රශ්නය", "සිංහල කෙටි වීඩියෝ ප්‍රශ්නය", "බුද්ධි පරීක්ෂණ ගැටලුව",
               "ශ්‍රේණිය", "සිංහල ගණිත පාඩම")
    delivery = []
    for title, item in existing.items():
        if not title.startswith(f"පුංචි නැණ මඟ - {day} - ") or item["status"] != "live":
            continue
        if not any(marker in title for marker in markers):
            continue
        article = request_json(f"{API}/blogs/{EXPECTED_BLOG_ID}/posts/{item['id']}?view=ADMIN",
                               access_token=token)
        state = STATE.search(article.get("content", ""))
        if state:
            delivery.append((title.split(" - ", 2)[-1], validate_blog_url(article.get("url")), state.group(1)))
    return {"daily_delivery":delivery,
            "live":sum(x["status"]=="live" for x in existing.values()),
            "draft":sum(x["status"]=="draft" for x in existing.values()),
            "remaining":sum(row["title"] not in existing for row in items)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--send",action="store_true",help="Send report to configured private Telegram chat")
    args=parser.parse_args()
    now=dt.datetime.now(dt.timezone.utc)
    runs=get_json("https://api.github.com/repos/"+REPO+"/actions/runs?per_page=100",
                  os.getenv("GITHUB_TOKEN",""))
    try:blogger=read_blogger_inventory()
    except (RuntimeError,urllib.error.URLError,ValueError) as exc:
        blogger=None
        print("Blogger API inventory unavailable; reporting verified GitHub runs only.")
    report=format_report(now,runs,blogger)
    import pathlib
    out=pathlib.Path("reports")/"daily-telegram-report.txt"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(report,encoding="utf-8")
    print("Report generated for preview (no credentials exposed).")
    if args.send:
        telegram_send(report,os.getenv("TELEGRAM_BOT_TOKEN",""),os.getenv("TELEGRAM_CHAT_ID",""))

if __name__=="__main__":main()
