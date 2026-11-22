#!/usr/bin/env python3
"""Regression checks: no repeated questions, exact screenshot-style frames."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from quiz_topics import select
from quiz_reel_renderer import make_frame, validate


class QuizReelTests(unittest.TestCase):
    def test_four_unique_reels_per_day_for_35_days(self):
        seen = set()
        start = dt.date(2026, 11, 22)
        for day_index in range(35):
            day = start + dt.timedelta(days=day_index)
            for offset in range(4):
                q = validate(select(day, offset))
                self.assertNotIn(q["q"], seen)
                seen.add(q["q"])
                self.assertEqual(len(q["choices"]), 4)
                self.assertTrue(0 <= q["answer"] < 4)
        self.assertEqual(len(seen), 140)

    def test_mars_question_is_correct(self):
        q = select(dt.date(2026, 11, 22), offset=0)
        self.assertNotIn("රතු ග්‍රහලෝකය", q["q"])
        from quiz_topics import QUIZZES
        self.assertEqual(QUIZZES[0][2], 2)
        self.assertEqual(QUIZZES[0][1][2], "අඟහරු")

    def test_card_frames_render_without_offtopic_images(self):
        from PIL import Image
        q = select(dt.date(2026, 11, 22), offset=0)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "question.png"
            make_frame(q, path, False)
            self.assertTrue(path.exists())
            with Image.open(path) as picture:
                self.assertEqual(picture.size, (1080, 1920))
                self.assertEqual(picture.getpixel((10, 10)), (11, 36, 68))
            answer = Path(folder) / "answer.png"
            make_frame(q, answer, True)
            self.assertGreater(answer.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
