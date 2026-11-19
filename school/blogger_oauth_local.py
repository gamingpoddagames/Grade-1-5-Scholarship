#!/usr/bin/env python3
"""Owner-only LOCAL OAuth authorization; NEVER run in GitHub Actions.

Use on your own computer. Requires pip install google-auth-oauthlib.
No credentials are written to the repository or any local file.
"""
import getpass
import os

SCOPE = ["https://www.googleapis.com/auth/blogger"]

def main():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        raise SystemExit("Install once: py -m pip install google-auth-oauthlib")
    print("Google Blogger OAuth setup (personal computer only).")
    print("Use an OAuth Desktop App client created at console.cloud.google.com/apis/credentials.")
    client_id = os.getenv("BLOGGER_CLIENT_ID") or input("OAuth Client ID: ").strip()
    client_secret = os.getenv("BLOGGER_CLIENT_SECRET") or getpass.getpass("OAuth Client Secret (not displayed): ").strip()
    if not client_id or not client_secret:
        raise SystemExit("Client ID and Client Secret are required.")
    config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }
    flow = InstalledAppFlow.from_client_config(config, scopes=SCOPE)
    credentials = flow.run_local_server(host="localhost", port=0, open_browser=True,
                                        access_type="offline", prompt="consent",
                                        authorization_prompt_message="Open this Google authorization URL: {url}")
    if not credentials.refresh_token:
        raise SystemExit("Google did not issue a refresh token. Ensure offline access and re-consent.")
    print("\nCopy the following three values into GitHub Actions repository Secrets (not Variables).")
    print("BLOGGER_CLIENT_ID:", client_id)
    print("BLOGGER_CLIENT_SECRET: [the same secret entered above; do not paste it in chat]")
    print("BLOGGER_REFRESH_TOKEN:", credentials.refresh_token)
    print("\nKeep credentials private. Close this terminal after storing the secrets.")
    print("If your OAuth app is External/Testing, refresh tokens may expire after 7 days.")

if __name__ == "__main__":
    main()
