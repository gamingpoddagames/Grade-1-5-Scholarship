#!/usr/bin/env python3
"""Offline checks for safely targeting the owner's Sinhala YouTube channel."""
import datetime as dt
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from youtube_shorts import (
    BLOG, OWNER_CHANNEL_ID, OWNER_CHANNEL_URL,
    SCOPES, assert_not_duplicate, build_metadata,
    upload, youtube_service_from_env
)

QUESTION = {
    "grade": 5,
    "q": "රතු ග්‍රහලෝකය ලෙස හඳුන්වන්නේ කුමන ග්‍රහලෝකයද?",
    "choices": ["සිකුරු", "බ්‍රහස්පති", "අඟහරු", "සෙනසුරු"],
    "answer": 2,
}


class YoutubeShortsTests(unittest.TestCase):
    def test_exact_channel_matches_supplied_link(self):
        self.assertEqual(OWNER_CHANNEL_ID, "UCQ2EM8DjUfg3WgzB8r6hYDQ")
        self.assertEqual(len(OWNER_CHANNEL_ID), 24)
        self.assertEqual(OWNER_CHANNEL_URL,
                         "https://www.youtube.com/channel/UCQ2EM8DjUfg3WgzB8r6hYDQ")
        self.assertIn("https://www.googleapis.com/auth/youtube.upload", SCOPES)
        self.assertIn("https://www.googleapis.com/auth/youtube.readonly", SCOPES)

    def test_short_metadata_child_education_defaults_private(self):
        day = dt.date(2026, 11, 24)
        data = build_metadata(QUESTION, day)
        self.assertLessEqual(len(data["snippet"]["title"]), 100)
        self.assertTrue(data["snippet"]["title"].endswith("#Shorts"))
        self.assertIn(QUESTION["q"], data["snippet"]["description"])
        self.assertIn(BLOG, data["snippet"]["description"])
        self.assertIn("PNM-SHORT-20261124-01", data["snippet"]["description"])
        self.assertEqual(data["status"]["privacyStatus"], "private")
        self.assertIs(data["status"]["selfDeclaredMadeForKids"], True)
        self.assertEqual(data["snippet"]["categoryId"], "27")
        self.assertEqual(data["snippet"]["defaultAudioLanguage"], "si")

    def test_different_dates_have_distinct_delivery_ids(self):
        first = build_metadata(QUESTION, dt.date(2026, 11, 24))
        second = build_metadata(QUESTION, dt.date(2026, 11, 25))
        self.assertNotEqual(first["_marker"], second["_marker"])

    def test_bad_metadata_and_privacy_are_rejected(self):
        with self.assertRaises(ValueError):
            build_metadata(QUESTION, dt.date(2026, 11, 24), privacy="unknown")
        bad = {**QUESTION, "answer": 10}
        with self.assertRaises(ValueError):
            build_metadata(bad, dt.date(2026, 11, 24))
        with self.assertRaises(ValueError):
            build_metadata({"q": "No options", "choices": []}, dt.date(2026, 11, 24))

    def test_only_the_supplied_channel_id_is_accepted(self):
        env = {"YOUTUBE_CLIENT_ID": "test", "YOUTUBE_CLIENT_SECRET": "test",
               "YOUTUBE_REFRESH_TOKEN": "test",
               "YOUTUBE_CHANNEL_ID": "UC0000000000000000000000"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(RuntimeError, "differs from"):
                youtube_service_from_env()

    def test_no_credentials_means_no_oauth_or_upload(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "Missing YOUTUBE_CLIENT_ID"):
                youtube_service_from_env()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "short.mp4"
            path.write_bytes(b"0" * 15000)
            data = build_metadata(QUESTION, dt.date(2026, 11, 24))
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "UPLOAD_ENABLED"):
                    upload(path, data, Path(td))

    def test_duplicate_video_title_and_marker_are_rejected(self):
        service = MagicMock()
        channel = {"contentDetails": {"relatedPlaylists": {"uploads": "UU-exact"}}}
        today = dt.date(2026, 11, 24)
        data = build_metadata(QUESTION, today)
        service.playlistItems.return_value.list.return_value.execute.return_value = {
            "items": [{"snippet": {"title": "other",
                                    "description": "description " + data["_marker"]}}],
        }
        with self.assertRaisesRegex(RuntimeError, "already uploaded"):
            assert_not_duplicate(service, channel, data["_marker"], data["snippet"]["title"])
        service.playlistItems.return_value.list.return_value.execute.return_value = {
            "items": [{"snippet": {"title": data["snippet"]["title"],
                                    "description": "no marker"}}],
        }
        with self.assertRaisesRegex(RuntimeError, "already uploaded"):
            assert_not_duplicate(service, channel, data["_marker"], data["snippet"]["title"])

    def test_no_playlist_blocks_duplicate_risk(self):
        service = MagicMock()
        with self.assertRaisesRegex(RuntimeError, "Cannot verify prior uploads"):
            assert_not_duplicate(service, {}, "PNM-SHORT-EXAMPLE", "test")


if __name__ == "__main__":
    unittest.main()
