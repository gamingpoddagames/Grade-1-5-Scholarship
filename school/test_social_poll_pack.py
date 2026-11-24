#!/usr/bin/env python3
"""No-network regression tests for attractive, accurate Facebook/Blogger poll packs."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import social_poll_pack as polls


class PollPackTests(unittest.TestCase):
    def test_text_poll_comes_from_same_reviewed_quiz_bank(self):
        from quiz_topics import select
        day=dt.date(2026,11,25)
        q=polls.select_poll(day,"text")
        self.assertEqual(q["q"],select(day,offset=0)["q"])
        self.assertEqual(len(q["choices"]),4)
        self.assertEqual(len(set(q["choices"])),4)
        self.assertIn("punchinanamaga.blogspot.com",polls.caption_for(q,"text"))

    def test_image_poll_uses_distinct_rights_cleared_question(self):
        from visual_quiz import select
        day=dt.date(2026,11,25)
        q=polls.select_poll(day,"image")
        self.assertNotEqual(q["q"],select(day)["q"])
        caption=polls.caption_for(q,"image")
        self.assertIn("ඡායාරූපය:",caption)
        self.assertIn("punchinanamaga.blogspot.com",caption)

    def test_bad_input_is_rejected_before_publish(self):
        with self.assertRaises(ValueError):
            polls.select_poll("2026-11-25","fake")
        with patch("social_poll_pack.select_text",return_value={
            "grade":5,"q":"Bad?","choices":["2","2","3","4"],"answer":0
        }):
            with self.assertRaisesRegex(RuntimeError,"distinct"):
                polls.select_poll("2026-11-25","text")

    def test_preview_saves_complete_publishable_pack_without_posting(self):
        q={"grade":5,"topic":"ගණිතය","q":"2 + 2 = කීයද?",
           "choices":["3","4","5","6"],"answer":1,
           "explanation":"2 + 2 = 4."}
        with tempfile.TemporaryDirectory() as folder, \
             patch("social_poll_pack.select_poll",return_value=q), \
             patch("social_poll_pack.create_card") as create_card, \
             patch("social_poll_pack.validate_card") as validate, \
             patch("social_poll_pack.publish") as pub:
            art=polls.build_pack("2026-11-25","text",folder)
            self.assertTrue((Path(folder)/"youtube-community-draft.txt").is_file())
            self.assertTrue((Path(folder)/"facebook-caption.txt").is_file())
            self.assertTrue((Path(folder)/"question.json").is_file())
            self.assertIn("4", (Path(folder)/"status.json").read_text(encoding="utf-8"))
            create_card.assert_called_once()
            validate.assert_called_once()
            pub.assert_not_called()
            self.assertIn("punchinanamaga.blogspot.com",art[2])

    def test_community_post_is_draft_not_false_api_claim(self):
        q=polls.select_poll("2026-11-25","text")
        text=polls.community_draft(q,"text")
        self.assertIn("Text Poll",text)
        self.assertIn(q["q"],text)
        self.assertIn(polls.BLOG,text)


if __name__=="__main__":
    unittest.main()
