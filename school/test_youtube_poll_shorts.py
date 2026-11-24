#!/usr/bin/env python3
"""Check YouTube poll companion metadata, appearance and privacy without uploading."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from social_poll_pack import select_poll
from youtube_poll_shorts import frame,metadata_for_poll


class YoutubePollShortsTests(unittest.TestCase):
    def test_poll_markers_differ_from_existing_daily_and_three_reels(self):
        day=dt.date(2026,11,25)
        q=select_poll(day,"text")
        data=metadata_for_poll(q,day,"text")
        self.assertEqual(data["_marker"],"PNM-POLL-20261125-TEXT")
        self.assertIn(data["_marker"],data["snippet"]["description"])
        self.assertEqual(data["status"]["privacyStatus"],"private")
        self.assertIs(data["status"]["selfDeclaredMadeForKids"],True)
        self.assertIn("punchinanamaga.blogspot.com",data["snippet"]["description"])
        self.assertNotIn("PNM-SHORT-20261125-01",data["snippet"]["description"])

    def test_still_image_is_converted_into_mobile_readable_answer_reveal(self):
        q={"grade":4,"topic":"ගණිතය","q":"3 + 2 = කීයද?",
           "choices":["3","4","5","7"],"answer":2}
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"original.png"
            Image.new("RGB",(1080,1350),"#ffffff").save(source)
            open_img=Path(d)/"question.png"
            answer_img=Path(d)/"answer.png"
            frame(source,q,False,open_img)
            frame(source,q,True,answer_img)
            with Image.open(open_img) as a, Image.open(answer_img) as b:
                self.assertEqual(a.size,(1080,1920))
                self.assertEqual(b.size,(1080,1920))
                self.assertNotEqual(a.getpixel((60,1510)),
                                    b.getpixel((60,1510)))
            self.assertGreater(answer_img.stat().st_size,10_000)

    def test_invalid_artwork_dimensions_fail_closed(self):
        q={"grade":5,"q":"Math?","choices":["1","2","3","4"],"answer":1}
        with tempfile.TemporaryDirectory() as d:
            art=Path(d)/"wrong.png"
            Image.new("RGB",(500,500),"white").save(art)
            with self.assertRaisesRegex(ValueError,"1080x1350"):
                frame(art,q,False,Path(d)/"output.png")

if __name__=="__main__":
    unittest.main()
