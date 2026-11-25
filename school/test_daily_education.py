"""Regression tests for the scheduled curriculum slots."""
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from daily_education import paper
from daily_papers import render_pdfs, rows_for_day
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

    def test_dated_math_paper_answers_and_distinct_pdf_files(self):
        day = date(2026, 11, 25)
        operations = {"+": int.__add__, "−": int.__sub__, "×": int.__mul__}
        for row in rows_for_day(day, 5, "math"):
            left, operation, right, *_ = row["q"].split()
            self.assertEqual(row["choices"][row["answer"]], operations[operation](int(left), int(right)))
        with TemporaryDirectory() as directory:
            paper_path, answers_path = render_pdfs(Path(directory), day, 5, "math", "ගණිතය")
            self.assertNotEqual(paper_path.read_bytes(), answers_path.read_bytes())
            self.assertIn(day.isoformat(), paper_path.name)

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
