#!/usr/bin/env python3
"""Regression checks for clean Sinhala Facebook desktop/mobile presentation."""
import datetime as dt
import pathlib
import tempfile
import unittest

from social_text import clean_caption, clean_title, clean_quiz_lines
from font_safety import check_caption


class FacebookSinhalaDesktopTests(unittest.TestCase):
    def test_pipes_become_readable_newlines(self):
        original = "5 ශ්‍රේණිය | බුද්ධි පරීක්ෂණ ගැටලුව\nප්‍රශ්න අංක 29"
        fixed = clean_caption(original)
        self.assertEqual(
            fixed,
            "5 ශ්‍රේණිය\nබුද්ධි පරීක්ෂණ ගැටලුව\nප්‍රශ්න අංක 29")
        self.assertNotIn("|", fixed)
        self.assertTrue(check_caption(fixed))

    def test_remove_hidden_copy_artifacts_without_damaging_sinhala(self):
        raw = "\ufeff\u200bශ්‍රී\u200d ලංකාව\u2060\r\nප්‍රශ්න\xa0 අංක 29"
        fixed = clean_caption(raw)
        self.assertNotIn("\ufeff", fixed)
        self.assertNotIn("\u200b", fixed)
        self.assertNotIn("\u2060", fixed)
        self.assertIn("\u200d", fixed)
        self.assertIn("ශ්‍රී", fixed)
        self.assertTrue(check_caption(fixed))

    def test_owned_blogger_url_not_changed(self):
        url = "https://punchinanamaga.blogspot.com/2026/11/math.html"
        self.assertIn(url, clean_caption("පිළිතුරු:\n" + url))
        self.assertEqual(
            clean_title("පුංචි නැණ මඟ | 2026-11-23 | අලුත් ප්‍රශ්නය"),
            "පුංචි නැණ මඟ - 2026-11-23 - අලුත් ප්‍රශ්නය")

    def test_daily_question_headline_short_and_simple(self):
        headline = clean_quiz_lines(5, "බුද්ධි පරීක්ෂණ ගැටලුව", 29)
        self.assertEqual(
            headline, "5 ශ්‍රේණිය\nබුද්ධි පරීක්ෂණ ගැටලුව\nප්‍රශ්න අංක 29")
        self.assertNotIn("|", headline)

    def test_existing_school_card_caption_and_credit_survive(self):
        from daily_publisher import make_content
        with tempfile.TemporaryDirectory() as folder:
            caption = make_content(
                dt.date(2026, 11, 23), pathlib.Path(folder))
            self.assertTrue(check_caption(caption))
            self.assertIn("ඡායාරූපය:", caption)
            self.assertIn("punchinanamaga.blogspot.com", caption)
            self.assertNotIn(" | ", caption)


if __name__ == "__main__":
    unittest.main()
