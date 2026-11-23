#!/usr/bin/env python3
"""Offline QA: educational discussion prompts and optional sponsor transparency."""
import os
import unittest
from unittest.mock import patch

from engagement_monetization import (
    comment_invitation, improve_facebook_caption, get_approved_sponsor_url,
    optional_sponsored_block,
)
from crosspost import article_content
from blogger_link_safety import validate_blogger_links

Q = {
    "q": "පේළිවල එකතුව 27 නම් මැද කොටුවට එන අංකය කුමක්ද?",
    "choices": ["9", "11", "7"],
    "option_labels": ["1", "2", "3"],
    "answer": 0,
    "puzzle_kind": "magic_grid",
    "puzzle_display": ["12 5 10", "7 ? 11", "8 13 6"],
    "explanation": "7 + 9 + 11 = 27.",
}
BLOG = "https://punchinanamaga.blogspot.com/2026/11/quiz-32.html"


class EngagementMonetizationTests(unittest.TestCase):
    def test_specific_comment_invitation_asks_for_reason_not_random_bait(self):
        prompt = comment_invitation(Q)
        self.assertIn("(1)", prompt)
        self.assertIn("පේළියකටත්", prompt)
        self.assertIn("පැහැදිලි කරන්න", prompt)
        self.assertNotIn("කමෙන්ට් දැම්මොත් පිළිතුර", prompt)

    def test_every_real_facebook_caption_keeps_owned_lesson_link(self):
        original = "ශිෂ්‍යත්ව ප්‍රශ්නය\n(1) 9\n(2) 11\n(3) 7\n" + BLOG
        improved = improve_facebook_caption(original, Q)
        self.assertIn(BLOG, improved)
        self.assertEqual(improved.count(BLOG), 1)
        self.assertIn("ඔබ තෝරාගත් අංකය", improved)
        self.assertTrue(validate_blogger_links(improved))
        self.assertEqual(improve_facebook_caption(improved, Q), improved)

    def test_older_four_answer_quiz_also_gets_a_reason_prompt(self):
        q = {"q": "රතු ග්‍රහලෝකය කුමක්ද?",
             "choices": ["සිකුරු","බ්‍රහස්පති","අඟහරු","සෙනසුරු"],
             "answer": 2}
        prompt = comment_invitation(q)
        self.assertIn("A, B, C, D", prompt)
        self.assertIn("හේතුවක්", prompt)

    def test_no_ad_without_explicit_link_approval(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(get_approved_sponsor_url())
            self.assertEqual(optional_sponsored_block(), "")
            page = article_content(Q, media_kind="photo")
            self.assertNotIn("punchi-sponsored", page)

    def test_javascript_source_is_not_a_direct_link(self):
        javascript_src = "https://bicea.org/14/3777aa5b8fbe2c3a7513a1e6dc0637c5"
        with patch.dict(os.environ, {
            "ADSTERRA_SPONSORED_LINK_ENABLED": "true",
            "ADSTERRA_AGE_APPROPRIATE_REVIEWED": "true",
            "ADSTERRA_DIRECT_LINK": javascript_src,
        }, clear=True):
            with self.assertRaisesRegex(ValueError, "Direct Link"):
                optional_sponsored_block()

    def test_approved_labelled_sponsor_stays_outside_answer_gate(self):
        safe_link = "https://example.org/verified-adsterra-direct-link"
        with patch.dict(os.environ, {
            "ADSTERRA_SPONSORED_LINK_ENABLED": "true",
            "ADSTERRA_AGE_APPROPRIATE_REVIEWED": "true",
            "ADSTERRA_DIRECT_LINK": safe_link,
        }, clear=True):
            article = article_content(Q, media_kind="photo")
            self.assertIn("දැන්වීම / Sponsored", article)
            self.assertIn('rel="sponsored nofollow noopener noreferrer"', article)
            self.assertIn(safe_link, article)
            self.assertIn("<details>", article)
            self.assertLess(article.index("</details>"), article.index("punchi-sponsored"))
            # The Facebook caption remains linked directly to Blogger, not an ad.
            caption = improve_facebook_caption("ප්‍රශ්නය\n" + BLOG, Q)
            self.assertNotIn(safe_link, caption)

    def test_ad_link_requires_age_appropriate_review_and_valid_https(self):
        for url in ["http://ad.example/abc", "javascript:alert(1)",
                    "https://user:pass@ad.example/link",
                    "https://ad.example/code.js"]:
            with patch.dict(os.environ, {
                "ADSTERRA_SPONSORED_LINK_ENABLED": "true",
                "ADSTERRA_AGE_APPROPRIATE_REVIEWED": "true",
                "ADSTERRA_DIRECT_LINK": url,
            }, clear=True):
                with self.assertRaises(ValueError):
                    optional_sponsored_block()
        with patch.dict(os.environ, {
            "ADSTERRA_SPONSORED_LINK_ENABLED": "true",
            "ADSTERRA_DIRECT_LINK": "https://example.org/valid",
        }, clear=True):
            with self.assertRaisesRegex(ValueError, "reviewed"):
                optional_sponsored_block()


if __name__ == "__main__":
    unittest.main()
