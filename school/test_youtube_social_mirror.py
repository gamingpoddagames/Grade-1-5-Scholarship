#!/usr/bin/env python3
"""No-network validation for Facebook/Blogger to YouTube mirroring."""
import datetime as dt
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import youtube_social_mirror as mirror


class MirrorTests(unittest.TestCase):
    def test_mirrors_exact_three_facebook_blog_reels(self):
        from quiz_topics import select
        day=dt.date(2026,11,25)
        actual=mirror.checked_reels(day)
        self.assertEqual([q["q"] for q in actual],
                         [select(day,offset=i)["q"] for i in (1,2,3)])
        self.assertEqual(len({q["q"] for q in actual}),3)

    def test_preview_never_uploads_and_does_not_modify_fb_renderer(self):
        day=dt.date(2026,11,25)
        with tempfile.TemporaryDirectory() as root, \
             patch("youtube_social_mirror.video") as vid, \
             patch("youtube_social_mirror.append_outro",side_effect=lambda path,*_: path) as outro, \
             patch("youtube_social_mirror.upload") as upload:
            def build(folder, questions, selected_day):
                target=Path(folder)/"grade5-quiz.mp4"
                target.write_bytes(b"0"*15000)
                return target
            vid.side_effect=build
            result=mirror.mirror(day,Path(root))
            self.assertEqual(vid.call_count,3)
            self.assertEqual(outro.call_count,3)
            upload.assert_not_called()
            self.assertEqual([r["status"] for r in result],["preview"]*3)
            self.assertEqual(
                [r["marker"] for r in result],
                ["PNM-SHORT-20261125-02","PNM-SHORT-20261125-03",
                 "PNM-SHORT-20261125-04"])
            self.assertEqual(len(json.loads(
                (Path(root)/"mirror-report.json").read_text(encoding="utf-8"))),3)

    def test_upload_blocks_if_owner_has_not_enabled(self):
        with tempfile.TemporaryDirectory() as root, \
             patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(RuntimeError,"not enabled"):
                mirror.mirror("2026-11-25",root,publish=True)

    def test_duplicate_marker_skips_but_other_errors_stop(self):
        with tempfile.TemporaryDirectory() as root, \
             patch("youtube_social_mirror.video") as vid, \
             patch("youtube_social_mirror.append_outro",side_effect=lambda path,*_: path), \
             patch("youtube_social_mirror.upload") as upload, \
             patch.dict(os.environ,{"YOUTUBE_UPLOAD_ENABLED":"true"},clear=True):
            def build(folder,questions,day):
                path=Path(folder)/"grade5-quiz.mp4"
                path.write_bytes(b"0"*15000)
                return path
            vid.side_effect=build
            upload.side_effect=[
                RuntimeError("This daily YouTube Short is already uploaded: PNM-SHORT-20261125-02"),
                {"video_url":"https://www.youtube.com/watch?v=test","privacy":"private"},
                {"video_url":"https://www.youtube.com/watch?v=test2","privacy":"private"},
            ]
            result=mirror.mirror("2026-11-25",root,publish=True)
            self.assertEqual([r["status"] for r in result],
                             ["already_uploaded","uploaded","uploaded"])
            self.assertEqual(upload.call_count,3)
        with tempfile.TemporaryDirectory() as root, \
             patch("youtube_social_mirror.video") as vid, \
             patch("youtube_social_mirror.append_outro",side_effect=lambda path,*_: path), \
             patch("youtube_social_mirror.upload",side_effect=RuntimeError("quota exceeded")), \
             patch.dict(os.environ,{"YOUTUBE_UPLOAD_ENABLED":"true"},clear=True):
            def build(folder,questions,day):
                path=Path(folder)/"grade5-quiz.mp4"
                path.write_bytes(b"0"*15000)
                return path
            vid.side_effect=build
            with self.assertRaisesRegex(RuntimeError,"quota"):
                mirror.mirror("2026-11-25",root,publish=True)


if __name__=="__main__":
    unittest.main()
