"""Publish one original adult/general Sinhala quiz per Colombo date via Buffer.
Public GitHub release assets host only the generated, intended-public MP4.
Durable create-attempt marker prevents blind retries after uncertain outcomes.
"""
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse
from zoneinfo import ZoneInfo
import requests
from tiktok_buffer_check import connected_channel, gql, TARGET
from adult_general_quiz import select, metadata_for
from quiz_reel_renderer import render_quiz_video

REPO = "gamingpoddagames/Grade-1-5-Scholarship"
API = "https://api.github.com/repos/" + REPO
FIELDS = "id text channelId status externalLink sentAt schedulingType shareMode createdAt"

def github(method, path, **kwargs):
    token = os.environ["GH_TOKEN"]
    r = requests.request(method, API + path, headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"}, timeout=60, **kwargs)
    if r.status_code == 404 and method == "GET":
        return None
    if not r.ok:
        raise RuntimeError("GitHub release operation failed: HTTP " + str(r.status_code))
    return r.json()

def asset(release, name, data, mime):
    release_id = int(release["id"])
    url = "https://uploads.github.com/repos/" + REPO + "/releases/" + str(release_id) + "/assets?" + urlencode({"name": name})
    headers = {"Authorization": "Bearer " + os.environ["GH_TOKEN"], "Content-Type": mime, "Accept": "application/vnd.github+json"}
    for attempt in range(5):
        # Check server state before retrying a POST: a failed HTTP response can
        # still leave either a completed asset or a zero-byte starter asset.
        current = github("GET", "/releases/" + str(release_id))
        if not current:
            raise RuntimeError("Release disappeared")
        for existing in current.get("assets", []):
            if existing["name"] != name:
                continue
            if existing["state"] == "uploaded" and existing["size"] == len(data):
                if hashlib.sha256(public_bytes(existing["browser_download_url"])).digest() != hashlib.sha256(data).digest():
                    raise RuntimeError("Existing release asset differs from intended data")
                return existing
            if existing["state"] == "starter" and existing["size"] == 0:
                # GitHub documents empty starter assets after HTTP 502.
                response = requests.delete(API + "/releases/assets/" + str(existing["id"]), headers=headers, timeout=60)
                if response.status_code not in (204, 404):
                    raise RuntimeError("Could not clear empty starter asset")
            else:
                raise RuntimeError("Existing asset is incomplete or inconsistent")
        try:
            r = requests.post(url, headers=headers, data=data, timeout=180)
            if r.ok:
                return r.json()
            if r.status_code not in (408, 429, 500, 502, 503, 504):
                raise RuntimeError("GitHub asset upload failed: HTTP " + str(r.status_code))
            print("Transient media upload HTTP", r.status_code, "attempt", attempt + 1)
        except (requests.Timeout, requests.ConnectionError):
            print("Transient media connection failure, attempt", attempt + 1)
        time.sleep(min(60, 5 * 2**attempt))
    raise RuntimeError("GitHub asset upload retries exhausted; no new Buffer post attempted here")

def public_bytes(url):
    if urlparse(url).hostname != "github.com":
        raise RuntimeError("Unexpected media URL")
    r = requests.get(url, timeout=90)
    r.raise_for_status()
    return r.content

def verify_post(key, channel, post_id, caption):
    for attempt in range(25):
        post = gql(key, "query($id:PostId!){post(input:{id:$id}){"+FIELDS+"}}", {"id":post_id})["post"]
        if post.get("channelId") != channel["id"] or post.get("text") != caption:
            raise RuntimeError("Post destination or caption mismatch")
        link = urlparse(post.get("externalLink") or "")
        if post.get("status") == "sent" and link.scheme == "https" and link.hostname in ("www.tiktok.com", "tiktok.com") and link.path.startswith("/@" + TARGET + "/video/"):
            print("PUBLISHED: " + post["externalLink"])
            return post["externalLink"]
        if post.get("status") in ("error", "draft", "pendingApproval"):
            break
        if attempt < 24:
            time.sleep(10)
    raise RuntimeError("Buffer post is not yet verified sent; reconcile rather than recreate")

def publish_movie(movie, caption, day, slot, folder):
    key = os.environ["PUNCHI_BUFFER_API_KEY"].strip()
    channel = connected_channel(key)
    if slot not in {"adult", "image", "short", "paper", "quiz", "quiz-bonus", "lesson", "lesson-bonus", "lesson-portrait"}:
        raise ValueError("Unknown TikTok slot")
    marker = "PNM-TIKTOK-" + day.isoformat() + ("" if slot == "adult" else "-" + slot)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    tag = "tiktok-media-" + day.strftime("%Y-%m")
    release = github("GET", "/releases/tags/" + tag)
    attempt_name = marker + "-attempt.json"
    receipt_name = marker + "-receipt.json"
    if release:
        assets = {a["name"]: a for a in release["assets"]}
        if receipt_name in assets:
            receipt = json.loads(public_bytes(assets[receipt_name]["browser_download_url"]))
            return verify_post(key, channel, receipt["id"], receipt["caption"])
        if attempt_name in assets:
            raise RuntimeError("Prior create attempt has unknown outcome; inspect Buffer before retrying")
    if slot.startswith("lesson"):
        dims = subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0",str(movie)],text=True).strip()
        if dims != "720,1280": raise RuntimeError("TikTok lessons require native portrait 720x1280, not padded landscape")
    optimized = folder / "tiktok.mp4"
    subprocess.run(["ffmpeg","-y","-i",str(movie),"-vf","scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1","-c:v","libx264","-b:v","350k","-maxrate","500k","-bufsize","1000k","-preset","fast","-c:a","aac","-b:a","64k","-movflags","+faststart",str(optimized)],check=True,timeout=600)
    data = optimized.read_bytes()
    if not 10000 < len(data) <= 100*1024*1024 or data[4:8] != b"ftyp":
        raise RuntimeError("Invalid or oversized MP4")
    digest = hashlib.sha256(data).hexdigest()
    name = marker + "-" + digest[:16] + ".mp4"
    caption = caption.strip() + "\n" + marker
    if not release:
        release = github("POST", "/releases", json={"tag_name":tag,"target_commitish":"main","name":"Punchi original TikTok media "+day.strftime("%Y-%m"),"body":"Original public educational MP4s and delivery records.","make_latest":"false"})
    media = asset(release, name, data, "video/mp4")
    url = "https://github.com/"+REPO+"/releases/download/"+tag+"/"+name
    if media.get("browser_download_url") != url or hashlib.sha256(public_bytes(url)).hexdigest()!=digest:
        raise RuntimeError("Public MP4 integrity check failed")
    asset(release, attempt_name, json.dumps({"date":str(day),"target":TARGET,"sha256":digest}).encode(), "application/json")
    result = gql(key, """mutation($input:CreatePostInput!){createPost(input:$input){
      __typename ... on PostActionSuccess {post {id text channelId status externalLink sentAt schedulingType shareMode createdAt}}
      ... on MutationError {message}
    }}""", {"input":{"text":caption,"channelId":channel["id"],"schedulingType":"automatic","mode":"shareNow","assets":[{"video":{"url":url,"metadata":{"thumbnailOffset":1000}}}],"metadata":{"tiktok":{"isAiGenerated":True}}}})["createPost"]
    post = result.get("post") or {}
    if not post.get("id") or post.get("channelId") != channel["id"]:
        raise RuntimeError("Buffer create not verified; do not retry blindly")
    asset(release, receipt_name, json.dumps({"id":post["id"],"caption":caption,"target":TARGET},ensure_ascii=False).encode(),"application/json")
    return verify_post(key, channel, post["id"], caption)

def main():
    day = datetime.now(ZoneInfo("Asia/Colombo")).date()
    folder = Path("school/output/tiktok")
    question = select(day)
    metadata_for(question, day)
    movie = render_quiz_video(question, folder)
    caption = "පුංචි නැණ මඟ | " + question["topic"] + "\n" + question["q"] + "\nතවත් දැනුමට අප හා එක්වන්න. #Sinhala #Education"
    publish_movie(movie, caption, day, "adult", folder)

if __name__ == "__main__":
    main()
