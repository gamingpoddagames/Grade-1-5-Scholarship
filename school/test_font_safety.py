#!/usr/bin/env python3
"""Offline publishing gate tests: no real Facebook API or credentials."""
import datetime as dt
import pathlib
import tempfile
import unicodedata
import unittest

from PIL import Image, ImageDraw
from font_safety import check_caption, draw_mixed, mixed_width, script_runs, test_image_glyphs
from brand_assets import font
from website_promo import TOPICS, card, caption, slide
from build_resources import all_questions, video
from facebook_card import create_card
from daily_publisher import make_content

class FacebookGlyphGateTests(unittest.TestCase):
    def test_real_fonts_support_separate_sinhala_latin_runs(self):
        self.assertTrue(test_image_glyphs(None))
        face=font(45,True)
        chunks=script_runs("5 ශ්‍රේණිය • PDF සහ Quiz",face)
        self.assertTrue(any(x[0]=="si" for x in chunks))
        self.assertTrue(any(x[0]=="latin" for x in chunks))
        im=Image.new("RGB",(1200,200),"white"); d=ImageDraw.Draw(im)
        self.assertGreater(mixed_width(d,"5 ශ්‍රේණිය • PDF",face),0)
        self.assertGreater(draw_mixed(d,(20,20),"5 ශ්‍රේණිය • PDF",face,"black"),20)
    def test_reject_boxes_replacement_emoji_controls(self):
        for bad in ("සිංහල □","සිංහල �","පාඩම 📝","පාඩම 📚","පාඩම 📄","පාඩම\x00"):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError):check_caption(unicodedata.normalize("NFC",bad))
        with self.assertRaises(ValueError):
            check_caption("සිංහල \u25a1")
    def test_all_promotion_creatives_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            for number,topic in enumerate(TOPICS):
                with self.subTest(number=number):
                    self.assertTrue(check_caption(caption(topic)))
                    card(topic,root/f"card-{number}.png")
                    self.assertGreater((root/f"card-{number}.png").stat().st_size,10000)
                    for i in range(3):
                        rendered=slide(topic,i)
                        self.assertEqual(rendered.size,(1080,1920))
    def test_daily_question_card_captions_and_all_bank_glyphs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            message=make_content(dt.date(2026,11,20),root)
            self.assertTrue(check_caption(message))
            questions=all_questions()
            # Every possible daily question must have glyphs supported by the fonts,
            # even if this day's random selection is short.
            face=font(43)
            for q in questions:
                for val in [q["q"],*q["choices"],q["explanation"],q["topic"]]:
                    with self.subTest(sample=str(val)[:30]):
                        script_runs(str(val),face)
            create_card(questions[0],root/"question.png")
            self.assertGreater((root/"question.png").stat().st_size,10000)
    def test_no_invisible_formatting_in_captions(self):
        for raw in ["normal test","පුංචි නැණ මඟ - පාඩම්", "https://punchinanamaga.blogspot.com/?utm_source=facebook"]:
            self.assertTrue(check_caption(raw))

if __name__=="__main__":unittest.main()
