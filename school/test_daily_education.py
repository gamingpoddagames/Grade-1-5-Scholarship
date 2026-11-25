"""Regression tests for the scheduled curriculum slots."""
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from daily_education import paper
from teaching_video import frame, lesson


class DailyEducationTests(unittest.TestCase):
    def test_papers_have_distinct_answer_and_question_downloads(self):
        first = date(2026, 11, 25)
        urls = set()
        for offset in range(15):
            _, body, (questions, answers), labels = paper(first + timedelta(days=offset))
            self.assertIn("මුල් නිර්මාණ", body)
            self.assertIn("නිල 5 ශ්‍රේණි", body)
            self.assertTrue(questions.endswith("-paper.pdf"))
            self.assertTrue(answers.endswith("-answers.pdf"))
            self.assertIn("2026", labels)
            urls.add(questions)
        self.assertEqual(len(urls), 15)

    def test_lesson_equations_and_subtitle_layout(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / "frame.png"
            for day in (date(2026, 11, 25), date(2026, 11, 26)):
                _, scenes = lesson(day)
                self.assertEqual(len(scenes), 23)
                for index, scene in enumerate(scenes, 1):
                    frame(target, scene, index, len(scenes))
                    if scene[2] and index % 2:
                        a, b = scene[2]
                        self.assertIn(scene[0], (f"{a} × {b} = {a*b}", f"{a*b} ÷ {a} = {b}"))
