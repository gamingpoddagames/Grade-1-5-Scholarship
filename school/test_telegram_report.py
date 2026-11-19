#!/usr/bin/env python3
"""Offline checks only; never send real Telegram messages."""
import datetime as dt
import unittest
from unittest import mock
import telegram_report as r

class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.now=dt.datetime(2026,11,20,0,0,tzinfo=dt.timezone.utc)
        self.runs={"workflow_runs":[
            {"name":"Blogger Auto Publisher (Google OAuth)","conclusion":"success","created_at":"2026-11-19T20:00:00Z"},
            {"name":"Publish Scholarship Website","conclusion":"failure","created_at":"2026-11-19T19:00:00Z"},
            {"name":"Publish Scholarship Website","conclusion":"success","created_at":"2026-11-02T19:00:00Z"},
            {"name":"Unknown other project","conclusion":"success","created_at":"2026-11-19T19:00:00Z"}
        ]}
    def test_summary_counts_only_recent_project_runs(self):
        c,rows=r.workflow_summary(self.runs,self.now)
        self.assertEqual(c["Blogger Auto Publisher (Google OAuth)"]["success"],1)
        self.assertEqual(c["Publish Scholarship Website"]["failure"],1)
        self.assertEqual(c["Publish Scholarship Website"]["success"],0)
        self.assertEqual(len(rows),2)
    def test_text_avoids_unverified_income_and_contains_own_blog(self):
        s=r.format_report(self.now,self.runs,{"live":2,"draft":1,"remaining":18})
        self.assertIn("https://punchinanamaga.blogspot.com/",s)
        self.assertIn("NOT verified",s)
        self.assertIn("18",s)
        self.assertIn("❌1",s)
        self.assertNotIn("earnings: $",s)
    def test_no_send_without_exact_private_credentials(self):
        with mock.patch.object(r.urllib.request,"urlopen",side_effect=AssertionError("Network called")):
            self.assertFalse(r.telegram_send("test","",""))
            self.assertFalse(r.telegram_send("test","secret",""))
    def test_delivery_confirmation_without_exposing_token(self):
        class Fake:
            def __enter__(self):return self
            def __exit__(self,*exc):pass
            def read(self,*args):return b'{"ok":true,"result":{"message_id":12}}'
        with mock.patch.object(r.urllib.request,"urlopen",return_value=Fake()) as call:
            self.assertTrue(r.telegram_send("hello","secret-bot","-100123"))
            req=call.call_args.args[0]
            self.assertIn("secret-bot",req.full_url)
            self.assertIn(b"chat_id=-100123",req.data)
    def test_unavailable_inventory_state(self):
        s=r.format_report(self.now,self.runs)
        self.assertIn("unavailable or not configured",s)
if __name__=="__main__":unittest.main()
