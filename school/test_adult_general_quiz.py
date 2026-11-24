#!/usr/bin/env python3
"""Validate honest audience categorization and mathematical adult quiz answers."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adult_general_quiz import TOPICS, facebook_caption, metadata_for, select
from quiz_topics import select as school_select


class AdultGeneralAudienceTests(unittest.TestCase):
    def test_each_daily_adult_question_has_exact_arithmetic_and_unique_options(self):
        for i in range(90):
            date=dt.date(2026,11,24)+dt.timedelta(days=i)
            q=select(date)
            self.assertEqual(q["audience"],"general")
            self.assertIn(q["topic"],TOPICS)
            self.assertNotIn("grade",q)
            self.assertEqual(len(q["choices"]),4)
            self.assertEqual(len(set(q["choices"])),4)
            self.assertTrue(0 <= q["answer"] < 4)
            self.assertIn(q["choices"][q["answer"]][4:].strip(),q["explanation"])

    def test_actual_adult_series_is_classified_as_general_audience_only_per_video(self):
        q=select("2026-11-25")
        metadata=metadata_for(q,"2026-11-25")
        self.assertEqual(metadata["status"]["privacyStatus"],"private")
        self.assertIs(metadata["status"]["selfDeclaredMadeForKids"],False)
        self.assertIn("PNM-GENERAL-20261125",metadata["snippet"]["description"])
        self.assertNotIn("5 ශ්‍රේණිය",metadata["snippet"]["title"])
        self.assertIn("වැඩිහිටියන්",metadata["snippet"]["description"])
        self.assertIn("punchinanamaga.blogspot.com",metadata["snippet"]["description"])
        self.assertIn("punchinanamaga.blogspot.com",facebook_caption(q))

    def test_child_directed_source_is_not_relabeled_general(self):
        child=school_select("2026-11-25")
        with self.assertRaisesRegex(RuntimeError,"classification"):
            metadata_for(child,"2026-11-25")
        adult=select("2026-11-25")
        with self.assertRaisesRegex(RuntimeError,"classification"):
            metadata_for({**adult,"grade":5},"2026-11-25")
        with self.assertRaisesRegex(RuntimeError,"classification"):
            metadata_for({**adult,"audience":"children"},"2026-11-25")
        with self.assertRaisesRegex(RuntimeError,"classification"):
            metadata_for({**adult,"audience_basis":""},"2026-11-25")

    def test_unique_daily_marker_and_no_implicit_public_upload(self):
        first=metadata_for(select("2026-11-25"),"2026-11-25")
        second=metadata_for(select("2026-11-26"),"2026-11-26")
        self.assertNotEqual(first["_marker"],second["_marker"])
        self.assertEqual(first["status"]["privacyStatus"],"private")

    def test_original_facebook_grade_video_appearance_remains_unchanged(self):
        from quiz_reel_renderer import make_frame
        from PIL import Image
        q=school_select("2026-11-25",offset=0)
        with tempfile.TemporaryDirectory() as d:
            school_path=Path(d)/"school.png"
            adult_path=Path(d)/"adult.png"
            make_frame(q,school_path,False)
            make_frame(select("2026-11-25"),adult_path,False)
            with Image.open(school_path) as s, Image.open(adult_path) as a:
                self.assertEqual(s.size,(1080,1920))
                self.assertEqual(a.size,(1080,1920))
                self.assertNotEqual(s.getpixel((110,1800)),a.getpixel((110,1800)))

if __name__=="__main__":
    unittest.main()
