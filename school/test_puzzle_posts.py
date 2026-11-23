#!/usr/bin/env python3
"""Offline math, Sinhala layout and Blogger-content checks for logic puzzle posts."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from puzzle_posts import START, compute, make_puzzle, facebook_caption, generate, poster
from crosspost import article_content


class ScholarshipPuzzleTests(unittest.TestCase):
    def test_launch_puzzle_verified_solution(self):
        q = make_puzzle(dt.date(2026, 11, 23))
        self.assertEqual(q["question_number"], 29)
        self.assertEqual([w[3] for w in q["puzzle_circles"]], ["40", "36", "30", "?"])
        self.assertEqual(q["choices"], ["60", "80", "100"])
        self.assertEqual(q["answer"], 1)
        self.assertIn("5 × 4 × (3 + 1) = 80", q["explanation"])
        self.assertNotIn("80 යි", facebook_caption(q))

    def test_many_days_have_computed_answers_and_unique_choices(self):
        seen = set()
        for day in range(120):
            q = make_puzzle(START + dt.timedelta(days=day))
            wheels = q["puzzle_circles"]
            self.assertEqual(len(wheels), 4)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertTrue(all(int(value) > 0 for value in q["choices"]))
            self.assertEqual(len(set(tuple(v[:3]) for v in wheels)), 4)
            for l, top, r, bottom in wheels[:3]:
                self.assertEqual(int(bottom), compute(l, top, r, rule=q["rule_index"]))
            l, top, r, hidden = wheels[-1]
            self.assertEqual(hidden, "?")
            self.assertEqual(int(q["choices"][q["answer"]]), compute(l, top, r, rule=q["rule_index"]))
            self.assertIn("comment", facebook_caption(q))
            seen.add((q["question_number"], tuple(tuple(w) for w in wheels)))
        self.assertEqual(len(seen), 120)

    def test_bonus_is_new_and_distinct_from_daily_post(self):
        day = dt.date(2026, 11, 23)
        standard = make_puzzle(day)
        bonus = make_puzzle(day, variant=1)
        self.assertEqual(bonus["date"], day.isoformat())
        self.assertEqual(bonus["question_number"], 30)
        self.assertEqual(bonus["variant"], "bonus")
        self.assertNotEqual(bonus["puzzle_circles"], standard["puzzle_circles"])
        self.assertEqual(len(bonus["choices"]), 3)
        self.assertEqual(len(set(bonus["choices"])), 3)
        for left, top, right, bottom in bonus["puzzle_circles"][:3]:
            self.assertEqual(int(bottom), compute(left, top, right, rule=bonus["rule_index"]))
        left, top, right, unknown = bonus["puzzle_circles"][-1]
        self.assertEqual(unknown, "?")
        correct = compute(left, top, right, rule=bonus["rule_index"])
        self.assertEqual(int(bonus["choices"][bonus["answer"]]), correct)

    def test_blog_contains_hidden_worked_solution(self):
        q = make_puzzle("2026-11-23")
        html = article_content(q, media_kind="photo")
        self.assertIn("<details>", html)
        self.assertIn("(2) 80", html)
        self.assertIn("5 × 4 × (3 + 1) = 80", html)
        self.assertIn("<table", html)
        self.assertNotIn("PNM_FACEBOOK_EMBED", html)

    def test_original_poster_is_mobile_readable(self):
        q = make_puzzle("2026-11-23")
        with tempfile.TemporaryDirectory() as tmp:
            item, output = generate("2026-11-23", tmp)
            self.assertTrue(output.exists())
            with Image.open(output) as im:
                self.assertEqual(im.size, (1080, 1350))
                self.assertEqual(im.mode, "RGB")
                self.assertNotEqual(im.getpixel((5, 5)), im.getpixel((5, 1330)))
            self.assertTrue((Path(tmp) / "blogger-preview.html").exists())
            self.assertTrue((Path(tmp) / "quiz.json").exists())
            self.assertTrue((Path(tmp) / "caption.txt").exists())


if __name__ == "__main__":
    unittest.main()
