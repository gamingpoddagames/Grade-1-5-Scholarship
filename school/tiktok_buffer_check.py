"""Read-only Buffer connection check for the education project."""
import os
import re
from urllib.parse import urlparse
import requests
GRAPH = "https://api.buffer.com"
TARGET = "punchinanamaga"

def gql(key, query, variables=None):
    try:
        reply = requests.post(GRAPH, headers={"Authorization": "Bearer " + key, "User-Agent": "Punchi Nena Maga-Buffer-Publisher/1.0"},
                              json={"query": query, "variables": variables or {}}, timeout=45)
        result = reply.json()
    except (requests.RequestException, ValueError):
        raise RuntimeError("Buffer API connection or response failed") from None
    if not reply.ok or not isinstance(result, dict) or result.get("errors"):
        # Never print GraphQL messages, headers, or response bodies.
        raise RuntimeError(f"Buffer API rejected the request (HTTP {reply.status_code}); check key, scope and schema")
    if not isinstance(result.get("data"), dict):
        raise RuntimeError("Buffer API returned no data")
    return result["data"]


def choose_channel(channels):
    matches = []
    for channel in channels:
        if str(channel.get("service", "")).lower() != "tiktok":
            continue
        handle = str(channel.get("name", "")).lstrip("@").lower()
        link = urlparse(str(channel.get("externalLink") or ""))
        linked_handle = link.path.strip("/").lstrip("@").lower()
        verified_link = link.scheme == "https" and link.hostname in ("www.tiktok.com", "tiktok.com") and linked_handle == TARGET
        # A display name alone is never account identity evidence.
        if handle != TARGET and not verified_link:
            continue
        if handle == TARGET and link.hostname and not verified_link:
            raise RuntimeError("Buffer username and TikTok profile link disagree")
        if channel.get("isDisconnected") or channel.get("isLocked"):
            raise RuntimeError("Punchi Nena Maga TikTok channel needs reconnecting or is locked")
        if (channel.get("metadata") or {}).get("defaultToReminders") is True:
            raise RuntimeError("Punchi Nena Maga TikTok channel is set to reminders; select Automatic in Buffer")
        matches.append(channel)
    if len(matches) != 1:
        raise RuntimeError("Exactly one connected @punchinanamaga TikTok channel is required; unrelated accounts are never selected")
    return matches[0]


def connected_channel(key):
    orgs = gql(key, "query { account { organizations { id } } }")["account"]["organizations"]
    channels = []
    for org in orgs:
        result = gql(key, """query($org: OrganizationId!) {
          channels(input:{organizationId:$org}) {
            id name displayName service externalLink organizationId isDisconnected isLocked
            metadata { ... on TiktokMetadata { defaultToReminders } }
          }
        }""", {"org": org["id"]})
        channels.extend(result["channels"])
    # Report only public TikTok handles, never IDs, keys or organization data.
    for candidate in channels:
        if str(candidate.get("service", "")).lower() != "tiktok":
            continue
        link = urlparse(str(candidate.get("externalLink") or ""))
        handle = link.path.strip("/").lstrip("@") if link.scheme == "https" and link.hostname in ("www.tiktok.com", "tiktok.com") else str(candidate.get("name", "")).lstrip("@")
        if re.fullmatch(r"[A-Za-z0-9_.]{1,24}", handle):
            print("Connected TikTok public handle: @" + handle)
    channel = choose_channel(channels)
    print("PASS: Buffer connection matches @punchinanamaga and supports Automatic publishing")
    return channel



if __name__ == "__main__":
    key = os.getenv("PUNCHI_BUFFER_API_KEY", "").strip()
    if not key:
        raise SystemExit("Missing PUNCHI_BUFFER_API_KEY; configure the repository secret.")
    connected_channel(key)
