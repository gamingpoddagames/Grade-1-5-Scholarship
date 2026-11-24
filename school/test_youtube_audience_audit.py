#!/usr/bin/env python3
"""No-network check of read-only, per-video YouTube audience diagnostic."""
import unittest
from unittest.mock import MagicMock
from youtube_audience_audit import check, summarize


class AudienceTests(unittest.TestCase):
    def test_channel_report_never_changes_settings(self):
        service=MagicMock()
        service.channels.return_value.list.return_value.execute.return_value={
            "items":[{"id":"UCQ2EM8DjUfg3WgzB8r6hYDQ",
                      "status":{"selfDeclaredMadeForKids":False,"madeForKids":False}}]
        }
        service.videos.return_value.list.return_value.execute.return_value={
            "items":[{"id":"3m3lRvYFS9A",
                      "status":{"privacyStatus":"private",
                                "selfDeclaredMadeForKids":True}}]
        }
        result=check(service)
        self.assertFalse(result["channel_self_declared_made_for_kids"])
        self.assertTrue(result["videos"][0]["self_declared_made_for_kids"])
        self.assertIn("review this setting for every video",result["recommendation"])
        service.channels.return_value.update.assert_not_called()
        service.videos.return_value.update.assert_not_called()

    def test_wrong_channel_fails_closed(self):
        service=MagicMock()
        service.channels.return_value.list.return_value.execute.return_value={
            "items":[{"id":"UCWRONG","status":{}}]}
        with self.assertRaisesRegex(RuntimeError,"mismatch"):
            check(service)
        service.videos.return_value.list.assert_not_called()

    def test_not_in_api_means_unknown_not_false(self):
        report=summarize({},[])
        self.assertIsNone(report["channel_self_declared_made_for_kids"])
        self.assertIsNone(report["channel_reported_made_for_kids"])


if __name__=="__main__":
    unittest.main()
