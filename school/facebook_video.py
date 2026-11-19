#!/usr/bin/env python3
"""Post an original quiz MP4 to an authorized Facebook Page via Graph API."""
import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import uuid
from font_safety import check_caption

def upload(path, page_id, access_token, version, *, title=None, description=None):
    path=Path(path)
    if not path.is_file() or path.stat().st_size==0:
        raise ValueError("Quiz video file is absent or empty")
    boundary="SchoolUpload"+uuid.uuid4().hex
    fields={
        "access_token":access_token,
        "title":title or "පුංචි නැණ මඟ - 5 ශ්‍රේණිය ශිෂ්‍යත්ව ප්‍රශ්නය",
        "description":description or ("5 ශ්‍රේණිය ශිෂ්‍යත්ව පුහුණුව: ප්‍රශ්නයට පිළිතුර සිතා බලන්න. "
                       "නොමිලේ පත්‍ර හා පිළිතුරු: "
                       "https://gamingpoddagames.github.io/Grade-1-5-Scholarship/ "
                       "#Grade5Scholarship #SinhalaEducation")
    }
    check_caption(fields["title"])
    check_caption(fields["description"])
    body=bytearray()
    for key,value in fields.items():
        body.extend((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n").encode("utf-8"))
    body.extend((f"--{boundary}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"grade5-quiz.mp4\"\r\nContent-Type: video/mp4\r\n\r\n").encode("utf-8"))
    body.extend(path.read_bytes())
    body.extend((f"\r\n--{boundary}--\r\n").encode("utf-8"))
    url=f"https://graph-video.facebook.com/{version}/{page_id}/videos"
    req=urllib.request.Request(url,method="POST",data=bytes(body),headers={"Content-Type":f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req,timeout=120) as response:
            answer=json.load(response)
    except urllib.error.HTTPError as exc:
        # Important: don't log the response body, which might contain credentials.
        raise RuntimeError(f"Facebook video upload failed (HTTP {exc.code}); check Page permissions and API compatibility") from None
    except urllib.error.URLError:
        raise RuntimeError("Facebook video upload network error") from None
    if not answer.get("id"):
        raise RuntimeError("Meta video endpoint did not confirm a video ID")
    print("Facebook video published:",answer["id"])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--video",required=True)
    args=parser.parse_args()
    page_id=os.environ.get("FB_PAGE_ID","")
    token=os.environ.get("FB_PAGE_ACCESS_TOKEN","")
    if not page_id or not token:
        print("Video upload skipped: missing Facebook Page secrets.")
        return
    upload(args.video,page_id,token,os.getenv("FB_GRAPH_VERSION","v27.0"))

if __name__=="__main__":
    main()
