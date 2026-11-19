#!/usr/bin/env python3
"""Offline tests: never contact Blogger or publish anything."""
import datetime as dt
import pathlib
import tempfile
import unittest
from unittest import mock

from blogger_export import export
import blogger_publisher as pub

class PublisherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        export(self.root)
        self.day = dt.date(2026,11,19)
    def tearDown(self):
        self.tmp.cleanup()
    def test_preview_has_no_network_or_credentials(self):
        with mock.patch.object(pub, "access_token_from_env", side_effect=AssertionError("OAuth was invoked")), mock.patch.object(pub, "request_json", side_effect=AssertionError("Network invoked")):
            result=pub.execute(mode="preview",kind="posts",export_dir=self.root,day=self.day,limit=1)
        self.assertEqual(result["prepared"],21)
        self.assertEqual(result["created"],0)
    def test_reject_unapproved_publication(self):
        with mock.patch.dict("os.environ", {"BLOGGER_ALLOW_PUBLICATION": "false"}):
            with self.assertRaisesRegex(RuntimeError,"Public posting disabled"):
                pub.execute(mode="publish",kind="posts",export_dir=self.root,day=self.day)
    def test_reject_page_draft(self):
        with self.assertRaisesRegex(RuntimeError,"page drafting"):
            pub.execute(mode="draft",kind="pages",export_dir=self.root,day=self.day)
    def test_safe_id_and_hostname(self):
        with mock.patch.object(pub, "request_json", return_value={"id": pub.EXPECTED_BLOG_ID, "url":"https://evil.example/"}):
            with self.assertRaisesRegex(RuntimeError,"Blog identity mismatch"):
                pub.authenticate_blog("opaque_access_token")
        with mock.patch.object(pub, "request_json", return_value={"id": pub.EXPECTED_BLOG_ID, "url":"https://punchinanamaga.blogspot.com/"}):
            self.assertEqual(pub.authenticate_blog("opaque_access_token")["id"],pub.EXPECTED_BLOG_ID)
    def test_duplicate_skips_and_draft_insert(self):
        candidates=pub.planned_items(self.root,"posts",self.day)
        old_title=candidates[0][0]
        requests=[]
        def fake_request(url,*,access_token=None,method="GET",payload=None):
            requests.append((url,method,payload))
            if url.endswith("/blogs/"+pub.EXPECTED_BLOG_ID):
                return {"id":pub.EXPECTED_BLOG_ID,"url":"https://punchinanamaga.blogspot.com/"}
            if method=="GET":
                if "status=live" in url:
                    return {"items":[{"title":old_title,"id":"999"}]}
                return {"items":[]}
            return {"id":"12345"}
        with mock.patch.object(pub,"request_json", side_effect=fake_request):
            result=pub.execute(mode="draft",kind="posts",export_dir=self.root,day=self.day,limit=1,token_factory=lambda:"test-access")
        self.assertEqual(result["created"],1)
        self.assertGreaterEqual(result["skipped"],1)
        writes=[r for r in requests if r[1]=="POST"]
        self.assertEqual(len(writes),1)
        self.assertIn("isDraft=true",writes[0][0])
        self.assertNotEqual(writes[0][2]["title"],old_title)
        self.assertTrue(writes[0][2]["content"].startswith("<h2>"))
    def test_page_drafts_and_public_requires_opt_in(self):
        with mock.patch.dict("os.environ",{"BLOGGER_ALLOW_PUBLICATION":"true"}):
            calls=[]
            def fake(url,*,access_token=None,method="GET",payload=None):
                calls.append((url,method,payload))
                if url.endswith("/blogs/"+pub.EXPECTED_BLOG_ID):
                    return {"id":pub.EXPECTED_BLOG_ID,"url":"https://punchinanamaga.blogspot.com/"}
                if method=="GET":
                    return {"items":[]}
                return {"id":"page987"}
            with mock.patch.object(pub,"request_json",side_effect=fake):
                result=pub.execute(mode="publish",kind="pages",export_dir=self.root,day=self.day,limit=1,token_factory=lambda:"test-access")
            self.assertEqual(result["created"],1)
            self.assertEqual(len([a for a in calls if a[1]=="POST"]),1)
            self.assertNotIn("isDraft", [a for a in calls if a[1]=="POST"][0][0])
    def test_only_exact_match_draft_is_published(self):
        candidates=pub.planned_items(self.root,"posts",self.day)
        original_title, original_body, _=candidates[0]
        seen=[]
        def fake(url,*,access_token=None,method="GET",payload=None):
            seen.append((url,method))
            if url.endswith("/blogs/"+pub.EXPECTED_BLOG_ID):
                return {"id":pub.EXPECTED_BLOG_ID,"url":"https://punchinanamaga.blogspot.com/"}
            if "/posts/existing1/publish" in url:
                return {"id":"existing1"}
            if "/posts/existing1?view=ADMIN" in url:
                return {"id":"existing1","content":original_body}
            if method=="GET" and "status=draft" in url:
                return {"items":[{"id":"existing1","title":original_title}]}
            return {"items":[]}
        with mock.patch.dict("os.environ",{"BLOGGER_ALLOW_PUBLICATION":"true"}):
            with mock.patch.object(pub,"request_json",side_effect=fake):
                result=pub.execute(mode="publish",kind="posts",export_dir=self.root,day=self.day,limit=1,token_factory=lambda:"fake")
        self.assertEqual(result["created"],1)
        self.assertTrue(any("/posts/existing1/publish" in x[0] for x in seen))
        self.assertFalse(any("isDraft=false" in x[0] for x in seen))
    def test_inaccessible_draft_does_not_stop_other_posts(self):
        first=pub.planned_items(self.root,"posts",self.day)[0][0]
        sent=[]
        def fake(url,*,access_token=None,method="GET",payload=None):
            if url.endswith("/blogs/"+pub.EXPECTED_BLOG_ID):
                return {"id":pub.EXPECTED_BLOG_ID,"url":"https://punchinanamaga.blogspot.com/"}
            if "/posts/existing404" in url:
                raise RuntimeError("Blogger/Google request failed (HTTP 404)")
            if method=="GET" and "status=draft" in url:
                return {"items":[{"id":"existing404","title":first}]}
            if method=="GET":
                return {"items":[]}
            sent.append(payload["title"])
            return {"id":"new123"}
        with mock.patch.dict("os.environ",{"BLOGGER_ALLOW_PUBLICATION":"true"}):
            with mock.patch.object(pub,"request_json",side_effect=fake):
                result=pub.execute(mode="publish",kind="posts",export_dir=self.root,day=self.day,limit=1,token_factory=lambda:"fake")
        self.assertEqual(result["created"],1)
        self.assertEqual(result["skipped"],1)
        self.assertNotIn(first,sent)
    def test_missing_secrets_do_not_access_network(self):
        with mock.patch.dict("os.environ",{},clear=True):
            with self.assertRaisesRegex(RuntimeError,"Required GitHub Actions secrets"):
                pub.access_token_from_env()

if __name__=="__main__":
    unittest.main()
