#!/usr/bin/env python3
"""Owner-only Google OAuth bootstrap for scheduled Sinhala YouTube Shorts.

Run once on the owner's own Windows PC. Opens Google sign-in locally,
verifies the exact authorized channel, and writes credentials directly to
GitHub Actions secrets using the official gh CLI. No passwords/tokens are
pasted into ChatGPT, uploaded to git, or written to a local secrets file.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from youtube_shorts import OWNER_CHANNEL_ID, OWNER_CHANNEL_URL, SCOPES

DEFAULT_REPO = "gamingpoddagames/Grade-1-5-Scholarship"


def verify_channel(items, expected_id=OWNER_CHANNEL_ID):
    if len(items) != 1 or items[0].get("id") != expected_id:
        raise RuntimeError(
            "The Google account did not authorize the requested channel "
            + OWNER_CHANNEL_URL + ". No GitHub secrets were changed.")
    return items[0]


def validate_google_client_file(path):
    """Require Google's Desktop OAuth credentials for the kids-video upload project."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise RuntimeError("OAuth client JSON file is invalid") from exc
    info = data.get("installed")
    if not isinstance(info, dict):
        raise RuntimeError("Google OAuth client must be a Desktop application")
    project_id = str(info.get("project_id", ""))
    if not project_id.startswith("mfk110"):
        raise RuntimeError(
            "Made for Kids uploads require a dedicated Google Upload Project "
            "whose project ID begins with mfk110. No credentials were saved.")
    for required in ("client_id", "client_secret", "auth_uri", "token_uri"):
        if not info.get(required):
            raise RuntimeError("Incomplete Desktop OAuth credentials: " + required)
    return project_id


def run_gh(args, *, secret_value=None):
    if not shutil.which("gh"):
        raise RuntimeError(
            "GitHub CLI is missing. Install from https://cli.github.com/ "
            "and sign in with: gh auth login")
    command = ["gh", *args]
    result = subprocess.run(
        command, input=(str(secret_value) + "\n") if secret_value is not None else None,
        text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"GitHub CLI command failed (exit {result.returncode}): "
            + " ".join(command[:2]) + ". Check gh auth status locally.")
    return result.stdout.strip()


def set_secret(repo, key, value):
    if not value:
        raise RuntimeError(f"Cannot save an empty GitHub secret: {key}")
    # Sends through stdin, not command-line arguments or environment logs.
    run_gh(["secret", "set", key, "--repo", repo], secret_value=value)
    print(f"Saved encrypted GitHub Actions secret: {key}")


def set_variable(repo, key, value):
    if value not in ("true", "false", "private", "unlisted", "public"):
        raise ValueError("Invalid YouTube workflow variable")
    run_gh(["variable", "set", key, "--repo", repo, "--body", value])
    print(f"Set GitHub Actions variable: {key}={value}")


def main():
    parser = argparse.ArgumentParser(
        description="Authorize the exact Punchi Nena Maga YouTube channel for GitHub Actions")
    parser.add_argument(
        "--client-secrets", required=True, type=Path,
        help="Google Cloud Desktop OAuth JSON downloaded to your PC")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument(
        "--enable-private-test", action="store_true",
        help="Enable private test uploads to verified YouTube channel")
    args = parser.parse_args()

    if args.repo != DEFAULT_REPO:
        raise RuntimeError("Unexpected repository. Stop rather than sending tokens elsewhere.")
    path = args.client_secrets.expanduser()
    if not path.is_file():
        raise RuntimeError("Google OAuth JSON file not found: " + str(path))
    validate_google_client_file(path)
    if not shutil.which("gh"):
        raise RuntimeError(
            "Install GitHub CLI from https://cli.github.com/ then run gh auth login.")
    run_gh(["auth", "status"])
    # Validate GitHub authorization before opening Google OAuth consent.
    run_gh(["repo", "view", args.repo, "--json", "nameWithOwner"])

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Missing Python libraries. Run: "
            "python -m pip install google-auth-oauthlib google-api-python-client") from exc

    print("Opening Google sign-in for the owner's YouTube channel...")
    print("Required target:", OWNER_CHANNEL_URL)
    flow = InstalledAppFlow.from_client_secrets_file(str(path), scopes=SCOPES)
    credentials = flow.run_local_server(
        host="127.0.0.1", port=0, open_browser=True,
        access_type="offline", prompt="consent",
        authorization_prompt_message="Complete the Google authorization in your browser.",
        success_message="Google authorization completed. Return to your terminal."
    )
    client_id = credentials.client_id
    client_secret = credentials.client_secret
    refresh_token = credentials.refresh_token
    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError(
            "Google did not return a refresh token; check OAuth consent settings "
            "and retry. Nothing was saved.")

    service = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    actual = service.channels().list(part="snippet", mine=True).execute().get("items", [])
    verified = verify_channel(actual)
    print("Verified exact YouTube channel:", verified["id"])
    print("Channel name:", verified.get("snippet", {}).get("title", ""))

    set_secret(args.repo, "YOUTUBE_CLIENT_ID", client_id)
    set_secret(args.repo, "YOUTUBE_CLIENT_SECRET", client_secret)
    set_secret(args.repo, "YOUTUBE_REFRESH_TOKEN", refresh_token)
    set_variable(args.repo, "YOUTUBE_PRIVACY", "private")
    set_variable(args.repo, "YOUTUBE_PUBLICATION_REVIEWED", "false")
    set_variable(
        args.repo, "YOUTUBE_UPLOAD_ENABLED",
        "true" if args.enable_private_test else "false"
    )

    print("\nSetup successful. Secrets never appeared in the console.")
    print("YouTube channel:", OWNER_CHANNEL_URL)
    if args.enable_private_test:
        print("Private test uploads enabled; public uploads still blocked.")
    else:
        print("Uploads remain disabled until enabled in GitHub Actions variables.")
    print("Next: https://github.com/" + args.repo +
          "/actions/workflows/youtube-shorts.yml")
    print("Review the private Short in YouTube Studio before permitting public uploads.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError) as exc:
        print("Setup stopped:", str(exc), file=sys.stderr)
        raise SystemExit(1)
