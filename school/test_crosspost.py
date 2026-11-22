#!/usr/bin/env python3
"""Offline safety checks for Blogger-first Facebook crossposting."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from crosspost import (
    Crossposter, STATE, article_content, validate_blog_url, safe_facebook_url,
    facebook_embed
)

Q = {
    "grade": 5, "topic": "අභ්‍යවකාශය",
    "q": "රතු ග්‍රහලෝකය ලෙස හඳුන්වන්නේ කුමන ග්‍රහලෝකයද?",
    "choices": ["සිකුරු", "බ්‍රහස්පති", "අඟහරු", "සෙනසුරු"],
    "answer": 2, "explanation": "අඟහරු රතු ග්‍රහලෝකයයි.",
}
BLOG_URL = "https://punchinanamaga.blogspot.com/2026/11/sinhala-quiz.html"
FB_URL = "https://www.facebook.com/example/videos/123456789/"


class CrosspostingTests(unittest.TestCase):
    def test_blogger_article_contains_full_question_answers_and_receipt(self):
        page = article_content(Q, media_kind="video")
        self.assertIn(Q["q"], page)
        self.assertIn("C) අඟහරු", page)
        self.assertIn("නිවැරදි පිළිතුර", page)
        self.assertIn("PNM_FACEBOOK_STATE:READY", page)
        self.assertNotIn("<iframe", page)

    def test_urls_are_not_redirects_to_unowned_websites(self):
        self.assertEqual(validate_blog_url(BLOG_URL), BLOG_URL)
        for bad in (
            "http://punchinanamaga.blogspot.com/2026/11/post.html",
            "https://attacker.com/post.html",
            "https://punchinanamaga.blogspot.com.evil.com/post",
            "https://punchinanamaga.blogspot.com@evil.com/post",
        ):
            with self.assertRaises(RuntimeError):
                validate_blog_url(bad)
        self.assertEqual(safe_facebook_url(FB_URL), FB_URL)
        self.assertIsNone(safe_facebook_url("https://evil.example/viral-video"))

    def test_public_embed_uses_verified_url(self):
        result = facebook_embed(FB_URL, "video")
        self.assertIn("plugins/video.php", result)
        self.assertIn("facebook.com", result)
        self.assertIn("PNM_FACEBOOK_EMBED", result)

    def fake_poster(self, state="READY"):
        poster = Crossposter.__new__(Crossposter)
        contents = ['<h2>Quiz</h2>\n<!-- PNM_FACEBOOK_STATE:' + state + ' -->']
        def article(*args, **kwargs):
            return {"id": "77", "url": BLOG_URL, "content": contents[-1]}, False
        def update(_id, content):
            contents.append(content)
            return {"id": _id}
        def get(_id):
            return {"id": _id, "url": BLOG_URL, "content": contents[-1]}
        poster.article = article
        poster.update = update
        poster.get = get
        return poster, contents

    def test_real_blogger_link_sent_to_facebook_and_embedded(self):
        poster, contents = self.fake_poster()
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp) / "video.mp4"
            media.write_bytes(b"fake-media-for-mocked-upload")
            with patch.dict(os.environ, {"FB_PAGE_ID": "123",
                                         "FB_PAGE_ACCESS_TOKEN": "private"}, clear=False), \
                 patch("facebook_video.upload", return_value="9876") as upload, \
                 patch("crosspost.verified_facebook_permalink", return_value=FB_URL):
                blog, fb_id = poster.publish(
                    question=Q, title="Unique daily quiz", media_kind="video",
                    media_path=media, caption="ප්‍රශ්නය\nhttps://punchinanamaga.blogspot.com/p/learning-welcome.html")
        self.assertEqual(blog, BLOG_URL)
        self.assertEqual(fb_id, "9876")
        self.assertIn(BLOG_URL, upload.call_args.kwargs["description"])
        self.assertNotIn("/p/learning-welcome.html", upload.call_args.kwargs["description"])
        self.assertTrue(any("STATE:PENDING" in x for x in contents))
        self.assertIn("STATE:PUBLISHED:9876", contents[-1])
        self.assertIn("plugins/video.php", contents[-1])

    def test_uncertain_remote_send_is_never_repeated(self):
        poster, contents = self.fake_poster("PENDING")
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "video.mp4"
            file.write_bytes(b"fake")
            with patch("facebook_video.upload") as upload:
                with self.assertRaisesRegex(RuntimeError, "uncertain"):
                    poster.publish(question=Q, title="Same title", media_kind="video",
                                   media_path=file, caption="test")
                upload.assert_not_called()

    def test_confirmed_delivery_is_not_repeated(self):
        poster, contents = self.fake_poster("PUBLISHED:9876")
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "video.mp4"
            file.write_bytes(b"fake")
            with patch("facebook_video.upload") as upload:
                blog, fb_id = poster.publish(
                    question=Q, title="Same title", media_kind="video",
                    media_path=file, caption="test")
                self.assertEqual((blog, fb_id), (BLOG_URL, "9876"))
                upload.assert_not_called()


if __name__ == "__main__":
    unittest.main()
