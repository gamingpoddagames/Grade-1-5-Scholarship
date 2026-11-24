#!/usr/bin/env python3
"""Mirror the THREE existing Facebook/Blogger Reels to the owner's YouTube channel.

The exact source content and renderer are reused from school/three_reels.py:
quiz_topics.select(day, offsets 1,2,3) + build_resources.video().
This is an additive pipeline: no Facebook code, voice, layout, posts or Blogger
article are modified. For YouTube, individual copies have metadata/receipts.

Does not create YouTube Community poll posts (not available to this API client).
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path

from build_resources import video
from quiz_topics import select
from youtube_shorts import build_metadata, upload, today_sri_lanka, redact_metadata
from video_cta import append_outro


def checked_reels(day):
    """Precisely the same three reviewed questions as three_reels.run()."""
    questions = [select(day, offset=offset) for offset in (1, 2, 3)]
    if len({q["q"] for q in questions}) != 3:
        raise RuntimeError("Cannot mirror repeated daily Reel questions")
    for q in questions:
        answers = q.get("choices", [])
        if len(answers) != 4 or len(set(str(c) for c in answers)) != 4:
            raise RuntimeError("Quiz must have four DISTINCT choices")
        if q.get("answer") not in range(4):
            raise RuntimeError("Incorrect answer key")
    return questions


def mirror(day, output, *, publish=False, privacy="private"):
    if isinstance(day, str):
        day = dt.date.fromisoformat(day)
    if privacy not in ("private", "public", "unlisted"):
        raise ValueError("Invalid YouTube visibility")
    if publish and os.environ.get("YOUTUBE_UPLOAD_ENABLED", "").lower() != "true":
        raise RuntimeError("Owner has not enabled YouTube uploading")
    if publish and privacy != "private" and os.environ.get("YOUTUBE_PUBLICATION_REVIEWED", "").lower() != "true":
        raise RuntimeError("Non-private mirroring requires explicit owner review")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    results=[]
    for index, q in enumerate(checked_reels(day), 1):
        folder = output / ("fb-blogger-reel-" + str(index))
        folder.mkdir(parents=True, exist_ok=True)
        # Exact source used by Facebook/Blogger three_reels.py, unmodified.
        original=video(folder,[q],day)
        movie=append_outro(original, "youtube", "school")
        metadata=build_metadata(q,day,privacy=privacy,offset=index)
        (folder / "youtube-metadata.json").write_text(
            json.dumps(redact_metadata(metadata), ensure_ascii=False, indent=2),
            encoding="utf-8")
        if not Path(movie).is_file() or Path(movie).stat().st_size < 10_000:
            raise RuntimeError("Missing rendered original MP4; upload blocked")
        if not publish:
            status="preview"
            url=None
        else:
            try:
                receipt=upload(movie,metadata,folder)
                status="uploaded"
                url=receipt["video_url"]
            except RuntimeError as exc:
                # Only a positively identified existing daily marker/title is
                # a safe skip. Any credential, quota or network failure stops.
                if "already uploaded" not in str(exc):
                    raise
                status="already_uploaded"
                url=None
                print("Already on YouTube; skipping without repost:", metadata["_marker"])
        results.append({
            "source":"Facebook + Blogger three-reels",
            "day":day.isoformat(), "slot":index,
            "question":q["q"], "marker":metadata["_marker"],
            "status":status, "privacy":privacy, "video_url":url
        })
    (output/"mirror-report.json").write_text(
        json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    return results


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--date", help="Sri Lanka YYYY-MM-DD")
    p.add_argument("--output",default="school/output/youtube-facebook-mirror")
    p.add_argument("--upload",action="store_true")
    p.add_argument("--privacy",choices=["private","unlisted","public"],default="private")
    args=p.parse_args()
    day=dt.date.fromisoformat(args.date) if args.date else today_sri_lanka()
    for row in mirror(day,args.output,publish=args.upload,privacy=args.privacy):
        print("YouTube mirrored:",row["slot"],row["status"],row["marker"],row["video_url"])


if __name__=="__main__":
    main()
