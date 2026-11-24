#!/usr/bin/env python3
"""Publish only approved original website-invitation media to authorized school Facebook Page."""
import argparse
from blogger_link_safety import validate_blogger_links
import os
from pathlib import Path
from facebook_card import publish as publish_photo
from facebook_video import upload as upload_video
from video_cta import append_outro

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--kind",choices=("photo","video"),required=True)
    p.add_argument("--output",default="promo_output")
    a=p.parse_args()
    folder=Path(a.output)
    caption=(folder/"facebook-caption.txt").read_text(encoding="utf-8")
    validate_blogger_links(caption)
    if not (os.environ.get("FB_PAGE_ID") and os.environ.get("FB_PAGE_ACCESS_TOKEN")):
        raise RuntimeError("No authorized Facebook Page token: leaving media as artifact only")
    if a.kind=="photo":
        image=folder/"school-website-invite.png"
        if not image.is_file():raise RuntimeError("Photo file missing")
        publish_photo(image,caption)
    else:
        video=folder/"school-promo.mp4"
        if not video.is_file():raise RuntimeError("Video missing")
        branded=append_outro(video,"facebook","general")
        upload_video(branded,os.environ["FB_PAGE_ID"],os.environ["FB_PAGE_ACCESS_TOKEN"],
                     os.getenv("FB_GRAPH_VERSION","v27.0"),title="පුංචි නැණ මඟ — නොමිලේ සිංහල පාඩම්",
                     description=caption)

if __name__=="__main__":main()
