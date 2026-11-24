#!/usr/bin/env python3
"""Read-only YouTube audience audit for the verified owner channel.

Never changes channel or video settings. This helps the owner choose a per-video
audience in Studio rather than blanket-marking the whole learning channel as
child-directed or blanket-marking school lessons as adult-targeted.
"""
import json
from pathlib import Path
from youtube_shorts import OWNER_CHANNEL_ID, youtube_service_from_env


def summarize(channel_status, video_statuses):
    self_declared=channel_status.get("selfDeclaredMadeForKids")
    detected=channel_status.get("madeForKids")
    return {
        "channel_id":OWNER_CHANNEL_ID,
        "channel_self_declared_made_for_kids":self_declared,
        "channel_reported_made_for_kids":detected,
        "recommendation":(
            "Review channel audience in YouTube Studio: Settings > Channel > Advanced settings > Audience. "
            "Use 'review this setting for every video' for mixed general-audience and "
            "genuinely child-directed videos. Do not misclassify the latter."),
        "videos":video_statuses,
    }


def check(service=None):
    if service is None:
        service, _=youtube_service_from_env()
    response=service.channels().list(part="status",mine=True).execute()
    items=response.get("items",[])
    if len(items)!=1 or items[0].get("id")!=OWNER_CHANNEL_ID:
        raise RuntimeError("Owner channel mismatch; audience audit blocked")
    # Only inspect videos whose owner-specific URLs were verified in previous
    # upload receipts; do not modify their audience flags.
    ids=["3m3lRvYFS9A","fWKUmHpr74E","aLKKLApwkeA","fDnsXHmhlg4",
         "zh_dzcbQlqY"]
    response=service.videos().list(part="status",id=",".join(ids)).execute()
    videos=[]
    for item in response.get("items",[]):
        status=item.get("status",{})
        videos.append({
            "video_id":item.get("id"),
            "privacy":status.get("privacyStatus","unknown"),
            "self_declared_made_for_kids":status.get("selfDeclaredMadeForKids"),
            "reported_made_for_kids":status.get("madeForKids"),
        })
    return summarize(items[0].get("status",{}),videos)


def main():
    result=check()
    target=Path("school/output/youtube-audience-audit.json")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Read-only owner channel audit:",result["channel_id"])
    print("Channel self-declared Made for Kids:",result["channel_self_declared_made_for_kids"])
    print("Channel reported Made for Kids:",result["channel_reported_made_for_kids"])
    for v in result["videos"]:
        print("Video",v["video_id"],v["privacy"],"selfDeclaredMFK",v["self_declared_made_for_kids"],
              "reportedMFK",v["reported_made_for_kids"])
    print("No YouTube channel/video audience settings were changed.")


if __name__=="__main__":
    main()
