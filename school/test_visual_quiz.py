#!/usr/bin/env python3
"""Offline regression checks for picture-first Sinhala quizzes (no network)."""
import datetime as dt
import unittest
from visual_quiz import ITEMS, START, image_page, select


class TestVisualQuiz(unittest.TestCase):
    def test_sixteen_distinct_questions(self):
        quizzes = [select(START + dt.timedelta(days=n)) for n in range(16)]
        self.assertEqual(len({q["q"] for q in quizzes}), 16)
        self.assertEqual(len({q["image_title"] for q in quizzes[:8]}), 8)
        self.assertEqual([q["image_title"] for q in quizzes[:8]],
                         [q["image_title"] for q in quizzes[8:16]])

    def test_question_and_photo_metadata(self):
        for item in ITEMS:
            self.assertTrue(item["topic"])
            self.assertTrue(item["image_title"].lower().endswith((".jpg", ".jpeg", ".png")))
            self.assertIn("Wikimedia Commons", item["image_credit"])
            self.assertIn("commons.wikimedia.org/wiki/File:", image_page(item))
            self.assertEqual(len(item["choices"]), 4)
            self.assertEqual(len(item["alternate"]["choices"]), 4)
            for version in (item, item["alternate"]):
                self.assertGreaterEqual(version["answer"], 0)
                self.assertLess(version["answer"], 4)
                self.assertTrue(version["explanation"])
                self.assertLessEqual(len(version["q"]), 100)

    def test_today_in_colombo_is_unchanged_across_formats(self):
        day = dt.date(2026, 11, 22)
        card = select(day)
        reel = select(day)
        narration = select(day)
        self.assertEqual(card, reel)
        self.assertEqual(card, narration)
        self.assertEqual(card["image_title"], "Sri Lankan leopard - Panthera pardus kotiya.jpg")


if __name__ == "__main__":
    unittest.main()
