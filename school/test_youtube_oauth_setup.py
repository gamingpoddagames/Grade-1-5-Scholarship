#!/usr/bin/env python3
"""Unit checks for safe local Google OAuth/GitHub secret bootstrap."""
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch, Mock
from pathlib import Path

from youtube_oauth_setup import (
    DEFAULT_REPO, verify_channel, validate_google_client_file,
    run_gh, set_secret, set_variable
)
from youtube_shorts import OWNER_CHANNEL_ID


class YoutubeOauthBootstrapTests(unittest.TestCase):
    def test_google_cloud_project_is_child_content_upload_project(self):
        required = {
            "client_id": "example.apps.googleusercontent.com",
            "client_secret": "test-secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "oauth.json"
            compliant = {"installed": {**required, "project_id": "mfk110-punchi-nana"}}
            path.write_text(json.dumps(compliant), encoding="utf-8")
            self.assertEqual(validate_google_client_file(path), "mfk110-punchi-nana")
            noncompliant = {"installed": {**required, "project_id": "other-project"}}
            path.write_text(json.dumps(noncompliant), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "mfk110"):
                validate_google_client_file(path)
            path.write_text(json.dumps({"web": compliant["installed"]}), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Desktop"):
                validate_google_client_file(path)

    def test_only_exact_owner_channel_may_authorize(self):
        expected = {"id": OWNER_CHANNEL_ID, "snippet": {"title": "පුංචි නැණ මඟ"}}
        self.assertEqual(verify_channel([expected]), expected)
        with self.assertRaisesRegex(RuntimeError, "No GitHub secrets"):
            verify_channel([])
        with self.assertRaisesRegex(RuntimeError, "No GitHub secrets"):
            verify_channel([{"id": "UC0000000000000000000000"}])
        with self.assertRaisesRegex(RuntimeError, "No GitHub secrets"):
            verify_channel([expected, expected])

    def test_secrets_go_through_stdin_not_argument_list(self):
        fake = Mock(returncode=0, stdout="done", stderr="")
        secret = "TOP-SECRET-NEVER-IN-ARGUMENTS"
        with patch("youtube_oauth_setup.shutil.which", return_value="/bin/gh"), \
             patch("youtube_oauth_setup.subprocess.run", return_value=fake) as call:
            set_secret(DEFAULT_REPO, "YOUTUBE_REFRESH_TOKEN", secret)
        self.assertEqual(call.call_args.args[0][:3],
                         ["gh", "secret", "set"])
        self.assertNotIn(secret, repr(call.call_args.args[0]))
        self.assertEqual(call.call_args.kwargs["input"], secret + "\n")
        self.assertFalse(call.call_args.kwargs.get("shell", False))
        self.assertTrue(call.call_args.kwargs["capture_output"])

    def test_invalid_publishing_variables_rejected(self):
        for value in ("yes", "any", "PUBLIC", "https://evil.example"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    set_variable(DEFAULT_REPO, "YOUTUBE_UPLOAD_ENABLED", value)

    def test_supported_variables_set_without_secrets(self):
        fake = Mock(returncode=0, stdout="", stderr="")
        with patch("youtube_oauth_setup.shutil.which", return_value="/bin/gh"), \
             patch("youtube_oauth_setup.subprocess.run", return_value=fake) as call:
            set_variable(DEFAULT_REPO, "YOUTUBE_PRIVACY", "private")
        self.assertIn("private", call.call_args.args[0])
        self.assertNotIn("secret", call.call_args.args[0])

    def test_missing_gh_cli_fails_closed(self):
        with patch("youtube_oauth_setup.shutil.which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "GitHub CLI"):
                run_gh(["auth", "status"])

    def test_cli_errors_never_dump_secret_value(self):
        fake = Mock(returncode=1, stdout="", stderr="sensitive error")
        with patch("youtube_oauth_setup.shutil.which", return_value="/bin/gh"), \
             patch("youtube_oauth_setup.subprocess.run", return_value=fake):
            with self.assertRaises(RuntimeError) as err:
                set_secret(DEFAULT_REPO, "YOUTUBE_REFRESH_TOKEN", "ultra-private")
        self.assertNotIn("ultra-private", str(err.exception))
        self.assertNotIn("sensitive error", str(err.exception))


if __name__ == "__main__":
    unittest.main()
