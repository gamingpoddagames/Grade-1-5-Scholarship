#!/usr/bin/env python3
"""Offline layout/branding tests; live FFmpeg encoding is smoke-tested in Actions."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops
from video_cta import CHANNEL, append_outro, image_card, profile, probe_video


class CTATests(unittest.TestCase):
    def test_both_social_platforms_have_exact_actions(self):
        fb=profile("facebook","general")
        yt=profile("youtube","general")
        kids=profile("youtube","school")
        self.assertEqual(CHANNEL,"පුංචි නැණ මඟ")
        self.assertEqual(fb["primary"],"FOLLOW")
        self.assertEqual(yt["primary"],"SUBSCRIBE")
        self.assertIn("COMMENT",fb["secondary"])
        self.assertIn("COMMENT",yt["secondary"])
        self.assertNotIn("COMMENT",kids["secondary"])
        self.assertIn(CHANNEL,fb["voice"])
        self.assertIn(CHANNEL,yt["voice"])
        self.assertIn("SHARE",kids["secondary"])

    def test_vertical_mobile_artwork_is_readable_and_platform_specific(self):
        for size in ((1080,1920),(720,1280)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as td:
                fb=Path(td)/"fb.png";yt=Path(td)/"yt.png"
                image_card(fb,"facebook","general",size)
                image_card(yt,"youtube","school",size)
                with Image.open(fb) as a, Image.open(yt) as b:
                    self.assertEqual(a.size,size)
                    self.assertEqual(b.size,size)
                    self.assertNotEqual(ImageChops.difference(a,b).getbbox(),None)
                    self.assertEqual(a.mode,"RGB")
                    self.assertGreater(fb.stat().st_size,10000)
                    self.assertGreater(yt.stat().st_size,10000)

    def test_bad_dimensions_and_action_types_fail(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"resolution"):
                image_card(Path(td)/"bad.png","youtube","general",(600,900))
        with self.assertRaisesRegex(ValueError,"school/general"):
            profile("instagram","school")

    def test_prevent_double_cta_or_overwriting_source(self):
        with self.assertRaisesRegex(ValueError,"twice"):
            append_outro("grade5-youtube-cta.mp4","youtube")
        with self.assertRaisesRegex(ValueError,"overwrite"):
            append_outro("source.mp4","facebook",output="source.mp4")

if __name__=="__main__":
    unittest.main()
