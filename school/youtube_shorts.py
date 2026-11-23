#!/usr/bin/env python3
"""Prepared Grade 1–5 Sinhala YouTube Shorts uploader.

A valid YouTube OAuth refresh token and the exact expected channel ID are
required; no uploads happen by default. This uses the same reviewed daily
question and original Sinhala narrator as the school Blogger/Facebook Reels.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path

BLOG = "https://punchinanamaga.blogspot.com/"
MARKER_PREFIX = "PNM-SHORT-"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
DEFAULT_PRIVACY = "private"
# Channel supplied by the owner. It is a public permanent YouTube ID.
OWNER_CHANNEL_ID = "UCQ2EM8DjUfg3WgzB8r6hYDQ"
OWNER_CHANNEL_URL = "https://www.youtube.com/channel/" + OWNER_CHANNEL_ID


def today_sri_lanka():
    return (dt.datetime.now(dt.timezone.utc) +
            dt.timedelta(hours=5, minutes=30)).date()


def build_metadata(question, day, *, privacy="private"):
    if privacy not in {"private", "unlisted", "public"}:
        raise ValueError("Privacy must be private, unlisted or public")
    if not question.get("q") or len(question.get("choices", [])) != 4:
        raise ValueError("YouTube Short needs a genuine complete quiz")
    answer = question.get("answer")
    if not isinstance(answer, int) or answer not in range(4):
        raise ValueError("Invalid correct answer")
    grade = question.get("grade", 5)
    if not isinstance(grade, int) or not 1 <= grade <= 5:
        raise ValueError("Quiz grade must be an integer between 1 and 5")
    grade_label = f"{grade} ශ්‍රේණිය"
    marker = MARKER_PREFIX + day.strftime("%Y%m%d") + "-01"
    title = f"{grade_label} | {question['q']} #Shorts"
    # Metadata title may be at most 100 Unicode code points.
    if len(title) > 100:
        title = f"{grade_label} | අලුත් අධ්‍යාපනික ප්‍රශ්නය #Shorts"
    labels = "\n".join(f"{chr(65+i)}) {c}" for i, c in enumerate(question["choices"]))
    desc = (
        "පුංචි නැණ මඟ | Grade 1–5 Sinhala Education\n\n"
        + question["q"] + "\n" + labels + "\n\n"
        "පිළිතුර සිතා බලන්න. වීඩියෝව අවසානයේ පිළිතුර පෙන්වයි.\n"
        "තවත් නොමිලේ ප්‍රශ්න සහ පැහැදිලි කිරීම්:\n"
        + BLOG
        + "\n\nස්වාධීන අධ්‍යාපනික අභ්‍යාසයකි; නිල විභාග ප්‍රශ්නයක් නොවේ.\n"
        + f"#SinhalaQuiz #Grade{grade} #Shorts\n"
        + "\n" + marker
    )
    return {
        "snippet": {
            "title": title,
            "description": desc,
            "categoryId": "27",  # Education
            "defaultLanguage": "si",
            "defaultAudioLanguage": "si",
            "tags": ["පුංචි නැණ මඟ", grade_label,
                     "Sinhala Quiz", f"Grade {grade}", "Sri Lanka Education"],
        },
        "status": {
            "privacyStatus": privacy,
            # This quiz stream is explicitly directed to primary-school children.
            "selfDeclaredMadeForKids": True,
        },
        "_marker": marker,
    }


def redact_metadata(metadata):
    # A local, reviewable representation. This contains no OAuth secrets.
    return {"snippet": metadata["snippet"], "status": metadata["status"],
            "unique_marker": metadata["_marker"]}


def youtube_service_from_env():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()
    expected_id = os.environ.get("YOUTUBE_CHANNEL_ID", OWNER_CHANNEL_ID).strip()
    if expected_id != OWNER_CHANNEL_ID:
        raise RuntimeError("Configured channel ID differs from the owner's supplied channel; upload blocked")
    if not all((client_id, client_secret, refresh_token, expected_id)):
        raise RuntimeError(
            "Missing YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / "
            "YOUTUBE_REFRESH_TOKEN / YOUTUBE_CHANNEL_ID; no upload attempted")
    if not expected_id.startswith("UC") or len(expected_id) != 24:
        raise RuntimeError("Expected exact 24-character YouTube channel ID")
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    credentials = Credentials(
        token=None, refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id, client_secret=client_secret,
        scopes=SCOPES
    )
    credentials.refresh(Request())
    service = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    channels = service.channels().list(part="snippet,contentDetails", mine=True).execute()
    found = channels.get("items", [])
    if len(found) != 1 or found[0].get("id") != expected_id:
        raise RuntimeError(
            "OAuth account does not match YOUTUBE_CHANNEL_ID; upload blocked")
    print("YouTube destination verified:", found[0]["id"],
          found[0].get("snippet", {}).get("title", ""))
    return service, found[0]


def assert_not_duplicate(service, channel, marker, title):
    # Read the recent uploads playlist of the verified authorized channel.
    playlist = channel.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    if not playlist:
        raise RuntimeError("Cannot verify prior uploads; refusing duplicate risk")
    token = None
    # Scan up to 1,000 recent uploads for a repeat marker.
    for _ in range(20):
        response = service.playlistItems().list(
            part="snippet", playlistId=playlist, maxResults=50,
            **({"pageToken": token} if token else {})).execute()
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            if marker in snippet.get("description", "") or snippet.get("title") == title:
                raise RuntimeError("This daily YouTube Short is already uploaded: " + marker)
        token = response.get("nextPageToken")
        if not token:
            break
    if token:
        raise RuntimeError("Recent upload listing exceeded 1,000; stop before possible duplicate upload")


def upload(mp4, metadata, folder):
    mp4 = Path(mp4)
    if not mp4.is_file() or mp4.stat().st_size < 10_000:
        raise RuntimeError("Valid rendered MP4 required before YouTube upload")
    if os.getenv("YOUTUBE_UPLOAD_ENABLED", "").lower() != "true":
        raise RuntimeError("Explicit YOUTUBE_UPLOAD_ENABLED=true required for upload")
    service, channel = youtube_service_from_env()
    assert_not_duplicate(service, channel, metadata["_marker"], metadata["snippet"]["title"])
    from googleapiclient.http import MediaFileUpload
    request = service.videos().insert(
        part="snippet,status",
        body={"snippet": metadata["snippet"], "status": metadata["status"]},
        media_body=MediaFileUpload(str(mp4), mimetype="video/mp4",
                                   chunksize=8*1024*1024, resumable=True)
    )
    result = None
    # Google handles the resumable upload; do not accidentally re-send video.
    while result is None:
        _, result = request.next_chunk()
    video_id = result.get("id")
    if not video_id:
        raise RuntimeError("YouTube API upload response contained no video ID")
    # Confirm the created resource belongs to the exact authorized channel.
    check = service.videos().list(part="snippet,status", id=video_id).execute()
    items = check.get("items", [])
    if len(items) != 1 or items[0].get("snippet", {}).get("channelId") != channel["id"]:
        raise RuntimeError("Video returned but ownership verification failed; review before retrying")
    actual_privacy = items[0].get("status", {}).get("privacyStatus", "unknown")
    report = {
        "youtube_id": video_id,
        "video_url": "https://www.youtube.com/watch?v=" + video_id,
        "channel_id": channel["id"],
        "privacy": actual_privacy,
        "marker": metadata["_marker"],
        "verified_utc": dt.datetime.now(dt.timezone.utc).isoformat()
    }
    (folder / "youtube-upload-receipt.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("YouTube upload confirmed:", report["video_url"], "privacy:", actual_privacy)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Asia/Colombo date YYYY-MM-DD")
    parser.add_argument("--output", default="school/output/youtube-shorts")
    parser.add_argument("--render", action="store_true", help="Render new original MP4")
    parser.add_argument("--upload", action="store_true",
                        help="Render and upload after explicit authorization and channel verification")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"],
                        default=DEFAULT_PRIVACY)
    args = parser.parse_args()
    if args.upload and args.privacy != "private":
        if os.getenv("YOUTUBE_PUBLICATION_REVIEWED", "").lower() != "true":
            raise RuntimeError(
                "Non-private uploads require YOUTUBE_PUBLICATION_REVIEWED=true")
    day = dt.date.fromisoformat(args.date) if args.date else today_sri_lanka()
    from quiz_topics import select
    question = select(day, offset=0)
    metadata = build_metadata(question, day, privacy=args.privacy)
    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "youtube-metadata.json").write_text(
        json.dumps(redact_metadata(metadata), ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("Prepared YouTube Short metadata:", metadata["snippet"]["title"])
    print("Privacy:", args.privacy, "madeForKids: true", "date:", day.isoformat())
    if not args.render and not args.upload:
        print("PREVIEW ONLY: no video rendered or uploaded")
        return
    from build_resources import video
    path = video(outdir, [question], day)
    if args.upload:
        upload(path, metadata, outdir)
    else:
        print("RENDERED ONLY: YouTube upload not requested", path)


if __name__ == "__main__":
    main()
