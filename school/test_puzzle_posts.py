#!/usr/bin/env python3
"""Test six different original scholarship visual questions and older post safety."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path
from PIL import Image

from puzzle_posts import make_puzzle, generate, facebook_caption, poster, compute, START
from diverse_puzzles import KINDS, make_diverse, validate_puzzle
from crosspost import article_content


class ScholarshipPuzzleTests(unittest.TestCase):
    def test_existing_2026_11_23_puzzles_stay_unchanged(self):
        original = make_puzzle(dt.date(2026, 11, 23))
        self.assertEqual(original["question_number"], 29)
        self.assertEqual([w[3] for w in original["puzzle_circles"]],
                         ["40","36","30","?"])
        self.assertEqual(original["choices"], ["60","80","100"])
        self.assertEqual(original["answer"], 1)
        self.assertIn("5 × 4 × (3 + 1) = 80", original["explanation"])
        self.assertNotIn("80 යි", facebook_caption(original))
        old_bonus = make_puzzle("2026-11-23", variant=1)
        self.assertEqual(old_bonus["question_number"], 30)
        self.assertIn("puzzle_circles", old_bonus)

    def assert_correct_math(self, question):
        kind = question["puzzle_kind"]
        v = question["visual"]
        answer = question["choices"][question["answer"]]
        self.assertEqual(len(question["choices"]), 3)
        self.assertEqual(len(set(question["choices"])), 3)
        self.assertEqual(question["correct_value"], answer)
        self.assertIn(answer, question["choices"])
        self.assertTrue(question["explanation"])
        if kind == "sequence":
            seq=v["values"]
            increments=[seq[i]-seq[i-1] for i in range(1,4)]
            self.assertEqual(increments[2]-increments[1], 3)
            self.assertEqual(increments[1]-increments[0], 3)
            self.assertEqual(int(answer),seq[3]+increments[2]+3)
            self.assertEqual(seq[-1],"?")
        elif kind == "magic_grid":
            g=v["grid"]
            self.assertEqual(g[1][1],"?")
            total=v["target"]
            for row in (g[0],g[2]):
                self.assertEqual(sum(map(int,row)),total)
            for col in (0,2):
                self.assertEqual(sum(int(g[i][col]) for i in range(3)),total)
            self.assertEqual(int(answer),total-int(g[1][0])-int(g[1][2]))
        elif kind == "balance":
            self.assertEqual((2*v["first"]-v["second"])%3,0)
            self.assertEqual(int(answer),(2*v["first"]-v["second"])//3)
            self.assertEqual(v["first"],2*v["circle"]+v["square"])
        elif kind == "dot_pattern":
            counts=v["counts"]
            self.assertEqual(counts[-1],"?")
            for i,(rows,cols) in enumerate(v["sizes"][:3]):
                self.assertEqual(counts[i],rows*cols)
            rows,cols=v["sizes"][-1]
            self.assertEqual(int(answer),rows*cols)
        elif kind == "clocks":
            minutes=v["minutes"]
            self.assertIsNone(minutes[-1])
            jump=v["interval"]
            self.assertEqual(minutes[1],(minutes[0]+jump)%(12*60))
            self.assertEqual(minutes[2],(minutes[1]+jump)%(12*60))
            expected=(minutes[2]+jump)%(12*60)
            hour=expected//60%12 or 12
            self.assertEqual(answer,f"{hour}:{expected%60:02d}")
        elif kind == "pyramid":
            r=v["rows"]
            self.assertEqual(r[0],["?"])
            self.assertEqual([r[3][i]+r[3][i+1] for i in range(3)],r[2])
            self.assertEqual([r[2][i]+r[2][i+1] for i in range(2)],r[1])
            self.assertEqual(int(answer),sum(r[1]))
        else:
            self.fail("Unexpected new puzzle kind "+kind)

    def test_six_truly_different_categories_with_unique_daily_bonus(self):
        begin=dt.date(2026,11,24)
        self.assertEqual(len(set(KINDS)),6)
        daily=[]
        for i in range(90):
            day=begin+dt.timedelta(days=i)
            q=make_puzzle(day)
            extra=make_puzzle(day,variant=1)
            validate_puzzle(q)
            validate_puzzle(extra)
            self.assert_correct_math(q)
            self.assert_correct_math(extra)
            self.assertNotEqual(q["puzzle_kind"],extra["puzzle_kind"])
            self.assertNotEqual(q["question_number"],extra["question_number"])
            self.assertNotEqual(q["question_number"], 29)
            self.assertNotIn("puzzle_circles",q)
            self.assertNotIn("puzzle_circles",extra)
            self.assertIn("punchinanamaga.blogspot.com",facebook_caption(q))
            self.assertNotIn(q["explanation"],facebook_caption(q))
            daily.append(q["puzzle_kind"])
        self.assertEqual(set(daily),set(KINDS))
        for left,right in zip(daily,daily[1:]):
            self.assertNotEqual(left,right)

    def test_new_style_launch_is_not_a_wheel_or_next_days_design(self):
        launch=make_puzzle("2026-11-23",variant=2)
        next_day=make_puzzle("2026-11-24")
        self.assertEqual(launch["question_number"],31)
        self.assertEqual(launch["puzzle_kind"],"dot_pattern")
        self.assertEqual(next_day["puzzle_kind"],"sequence")
        self.assert_correct_math(launch)

    def test_new_grid_post_32_is_not_old_dot_or_number_wheel(self):
        q = make_puzzle("2026-11-23", variant=3)
        self.assertEqual(q["question_number"], 32)
        self.assertEqual(q["puzzle_kind"], "magic_grid")
        self.assertEqual(q["variant"], "fresh-grid")
        self.assert_correct_math(q)
        self.assertEqual(q["visual"]["target"], 27)
        self.assertEqual(q["choices"][q["answer"]], "9")
        self.assertEqual(q["visual"]["grid"], [
            ["12", "5", "10"],
            ["7", "?", "11"],
            ["8", "13", "6"]])
        self.assertNotIn("puzzle_circles", q)
        self.assertNotEqual(q["puzzle_kind"], make_puzzle("2026-11-23", variant=2)["puzzle_kind"])
        page = article_content(q, media_kind="photo")
        self.assertIn("<details>", page)
        self.assertIn("27", page)
        with tempfile.TemporaryDirectory() as root:
            _, image_path = generate("2026-11-23", root, variant=3)
            self.assertTrue(image_path.exists())
            with Image.open(image_path) as image:
                self.assertEqual(image.size, (1080, 1350))

    def test_fresh_clock_33_uses_a_new_question_and_real_time_calculations(self):
        q = make_puzzle("2026-11-23", variant=4)
        self.assertEqual(q["question_number"], 33)
        self.assertEqual(q["puzzle_kind"], "clocks")
        self.assertEqual(q["variant"], "fresh-clock")
        self.assert_correct_math(q)
        self.assertEqual(q["visual"]["minutes"], [255, 280, 305, None])
        self.assertEqual(q["visual"]["interval"], 25)
        self.assertEqual(q["choices"], ["5:55", "5:05", "5:30"])
        self.assertEqual(q["answer"], 2)
        self.assertNotIn("puzzle_circles", q)
        self.assertNotEqual(q["puzzle_kind"], make_puzzle("2026-11-23", variant=3)["puzzle_kind"])
        page = article_content(q, media_kind="photo")
        self.assertIn("5:30", page)
        self.assertIn("විනාඩි 25", page)
        with tempfile.TemporaryDirectory() as root:
            item, image_path = generate("2026-11-23", root, variant=4)
            self.assertEqual(item["puzzle_kind"], "clocks")
            self.assertTrue(image_path.exists())
            with Image.open(image_path) as img:
                self.assertEqual(img.size, (1080, 1350))

    def test_blogger_copies_puzzle_datasets_and_full_solution(self):
        for i in range(6):
            q=make_puzzle(dt.date(2026,11,24)+dt.timedelta(days=i))
            result=article_content(q,media_kind="photo")
            self.assertIn("<details>",result)
            self.assertIn("<ul>",result)
            self.assertIn("PNM_FACEBOOK_STATE:READY",result)
            self.assertIn("රූපයේ ගැටලුව",result)
            self.assertIn(q["explanation"].split(".")[0][:15],result)
            self.assertNotIn("PNM_FACEBOOK_EMBED",result)

    def test_all_six_poster_layouts_render_successfully(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(6):
                q=make_puzzle(dt.date(2026,11,24)+dt.timedelta(days=i))
                path=Path(tmp)/f"{q['puzzle_kind']}.png"
                poster(q,path)
                self.assertGreater(path.stat().st_size,20000)
                with Image.open(path) as image:
                    self.assertEqual(image.size,(1080,1350))
                    self.assertEqual(image.mode,"RGB")
            item,path=generate("2026-11-23",Path(tmp)/"fresh",variant=2)
            self.assertEqual(item["puzzle_kind"],"dot_pattern")
            self.assertTrue(path.exists())
            self.assertTrue((path.parent/"quiz.json").exists())
            self.assertTrue((path.parent/"caption.txt").exists())
            self.assertTrue((path.parent/"blogger-preview.html").exists())


if __name__=="__main__":
    unittest.main()
