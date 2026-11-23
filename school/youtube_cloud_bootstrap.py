#!/usr/bin/env python3
"""One-time owner-run gcloud bootstrap for the Punchi Nena Maga upload project.

Only Google login and desktop OAuth consent require browser interaction.
Creates/reuses a Made-for-Kids-upload project, enables YouTube Data API v3,
and then hands the correct Desktop OAuth JSON to the existing secure GitHub
secrets wizard. Never uses a service account for YouTube channel uploads.
"""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import webbrowser

PROJECT_PREFIX = "mfk110"
DISPLAY_NAME = "Punchi Nena Maga YouTube"
API_SERVICE = "youtube.googleapis.com"
OWNER_CHANNEL_ID = "UCQ2EM8DjUfg3WgzB8r6hYDQ"


def state_file():
    # Not inside the Git repository. Stores only the *public project ID*.
    base = os.environ.get("LOCALAPPDATA")
    return (Path(base) if base else Path.home() / ".config") / "PunchiNenaMaga" / "youtube-project.json"


def validate_project_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"mfk110[a-z0-9-]{3,23}", value):
        raise ValueError("Project ID must begin with mfk110, use lower-case ASCII/numbers/hyphens and fit 6–30 chars")
    if value.endswith("-"):
        raise ValueError("Project ID cannot end with a hyphen")
    return value


def choose_project_id(custom=None, *, path=None):
    """Reuse previous ID instead of creating a different Cloud project on reruns."""
    file = path or state_file()
    if custom:
        return validate_project_id(custom)
    if file.exists():
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            return validate_project_id(data["project_id"])
        except (KeyError, ValueError, TypeError, UnicodeError) as exc:
            raise RuntimeError(
                "Saved local project ID is malformed. Pass --project-id explicitly; "
                "do not create another project automatically.") from exc
    return validate_project_id("mfk110-pnm-" + secrets.token_hex(3))


def remember_project(project_id, *, path=None):
    target = path or state_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    # Contains no OAuth token or password; useful after closing the terminal.
    target.write_text(json.dumps({"project_id": project_id,
                                  "channel_id": OWNER_CHANNEL_ID}, indent=2),
                      encoding="utf-8")
    return target


def gcloud_command():
    executable = shutil.which("gcloud") or shutil.which("gcloud.cmd")
    if not executable:
        raise RuntimeError(
            "Google Cloud CLI not installed. Use Windows: "
            "winget install --id Google.CloudSDK -e; reopen Command Prompt.")
    return executable


def run_gcloud(executable, *args, can_fail=False):
    cmd = [executable, *args]
    result = subprocess.run(cmd, text=True, capture_output=True,
                            check=False, timeout=300)
    if result.returncode and not can_fail:
        # Avoid dumping token-bearing CLI messages. Show just the operation
        # and a generic error; the owner can run the command manually.
        raise RuntimeError(
            "Google Cloud CLI command failed: " + " ".join(args[:2]) +
            ". Check your Google login, project quota and permissions.")
    return result


def ensure_google_login(executable):
    active = run_gcloud(
        executable, "auth", "list", "--filter=status:ACTIVE",
        "--format=value(account)", can_fail=True
    )
    if active.returncode == 0 and active.stdout.strip():
        print("An active Google Cloud CLI login exists.")
        return
    print("Opening Google's sign-in page to authorize gcloud...")
    run_gcloud(executable, "auth", "login", "--brief")
    after = run_gcloud(
        executable, "auth", "list", "--filter=status:ACTIVE",
        "--format=value(account)")
    if not after.stdout.strip():
        raise RuntimeError("Google login did not complete")


def ensure_project(executable, project_id):
    validate_project_id(project_id)
    # A permission error in describe can also mean "not accessible".
    # A failed create will stop safely; never use a different project.
    existing = run_gcloud(
        executable, "projects", "describe", project_id,
        "--format=value(projectId)", can_fail=True
    )
    if existing.returncode == 0:
        if existing.stdout.strip() != project_id:
            raise RuntimeError("Returned project ID differs from requested ID")
        print("Reusing existing Google Cloud project:", project_id)
    else:
        print("Creating new Google Upload Project:", project_id)
        run_gcloud(executable, "projects", "create", project_id,
                   "--name=" + DISPLAY_NAME)
    confirmed = run_gcloud(
        executable, "projects", "describe", project_id,
        "--format=value(projectId)")
    if confirmed.stdout.strip() != project_id:
        raise RuntimeError("Created project could not be verified")
    return project_id


def ensure_youtube_api(executable, project_id):
    print("Enabling YouTube Data API v3 on project:", project_id)
    run_gcloud(executable, "services", "enable", API_SERVICE,
               "--project=" + project_id)
    confirmed = run_gcloud(
        executable, "services", "list", "--enabled",
        "--project=" + project_id,
        "--filter=config.name:" + API_SERVICE,
        "--format=value(config.name)")
    if API_SERVICE not in confirmed.stdout.split():
        raise RuntimeError("YouTube API enablement was not confirmed")
    print("Verified enabled API:", API_SERVICE)


def desktop_client_page(project_id):
    validate_project_id(project_id)
    return "https://console.cloud.google.com/auth/clients?project=" + project_id


def continue_oauth(json_path, project_id):
    target = Path(json_path).expanduser()
    if not target.is_file():
        raise RuntimeError("Desktop OAuth JSON file is missing; do not paste its contents")
    wizard = Path(__file__).resolve().parent / "youtube_oauth_setup.py"
    # No OAuth secret or JSON file contents are logged or sent via CLI args:
    # only the local file path is passed to the existing owner-side script.
    return subprocess.run(
        [sys.executable, str(wizard), "--client-secrets", str(target),
         "--expected-project", project_id, "--enable-private-test"],
        check=False
    ).returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description="Secure YouTube Google Cloud Setup")
    parser.add_argument("--project-id", help="Reuse an existing mfk110-prefixed project")
    parser.add_argument("--oauth-json", type=Path,
                        help="Existing Desktop OAuth client JSON file path")
    parser.add_argument("--skip-browser", action="store_true",
                        help="Do not open the Google Auth console automatically")
    args = parser.parse_args(argv)

    project_id = choose_project_id(args.project_id)
    print("Target YouTube channel:", OWNER_CHANNEL_ID)
    print("Google Upload Project:", project_id)
    executable = gcloud_command()
    ensure_google_login(executable)
    ensure_project(executable, project_id)
    ensure_youtube_api(executable, project_id)
    config = remember_project(project_id)
    print("Saved project ID locally:", config)
    url = desktop_client_page(project_id)
    print("\nGoogle Auth Platform Desktop OAuth client:", url)
    if not args.skip_browser and not args.oauth_json:
        webbrowser.open(url)

    if args.oauth_json:
        return continue_oauth(args.oauth_json, project_id)

    print(
        "\nGoogle Auth Platform still requires owner approval:\n"
        "  1. Complete the Google Auth Platform setup for personal use or\n"
        "     an appropriate external audience (include your own test user).\n"
        "  2. Create an OAuth Client of type Desktop app.\n"
        "  3. Download the client JSON file to your PC (never send it to ChatGPT).\n"
        "  4. Paste only the LOCAL FILE PATH below to finish authorization.\n"
        "Press Enter without a path to finish the Google Cloud stage now."
    )
    try:
        raw = input("Downloaded OAuth JSON file path (or Enter to skip): ").strip().strip('"')
    except EOFError:
        raw = ""
    if raw:
        return continue_oauth(raw, project_id)
    print("Google Cloud project + YouTube API ready; OAuth upload remains disabled.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print("SETUP STOPPED:", exc, file=sys.stderr)
        raise SystemExit(1)
