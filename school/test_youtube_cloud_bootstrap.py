#!/usr/bin/env python3
"""No-network regression checks for owner Google Cloud project wizard."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from youtube_cloud_bootstrap import (
    PROJECT_PREFIX, API_SERVICE, OWNER_CHANNEL_ID, validate_project_id,
    choose_project_id, remember_project, ensure_project, ensure_youtube_api,
    ensure_google_login, desktop_client_page, continue_oauth,
)
from youtube_oauth_setup import validate_google_client_file


class GoogleCloudBootstrapTests(unittest.TestCase):
    def test_mfk110_project_id_validation(self):
        self.assertEqual(validate_project_id("mfk110-pnm-123abc"),"mfk110-pnm-123abc")
        for bad in ("wrong-project", "mfk110-", "mfk110-A", "mfk110-pnm;",
                    "mfk110-"+"a"*40, "mfk110-pnm-", "", None):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                validate_project_id(bad)

    def test_project_id_persists_without_credentials(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "project.json"
            with patch("youtube_cloud_bootstrap.secrets.token_hex",
                       return_value="a1b2c3"):
                first=choose_project_id(path=state)
            self.assertEqual(first,"mfk110-pnm-a1b2c3")
            remember_project(first,path=state)
            second=choose_project_id(path=state)
            self.assertEqual(second,first)
            contents=state.read_text(encoding="utf-8")
            self.assertNotIn("refresh_token",contents)
            self.assertNotIn("client_secret",contents)
            self.assertEqual(json.loads(contents)["channel_id"],OWNER_CHANNEL_ID)

    def test_create_project_only_when_needed(self):
        missing=Mock(returncode=1, stdout="",stderr="")
        confirmed=Mock(returncode=0,stdout="mfk110-pnm-test1\n",stderr="")
        with patch("youtube_cloud_bootstrap.run_gcloud",
                   side_effect=[missing,Mock(returncode=0,stdout=""),confirmed]) as runner:
            output=ensure_project("gcloud","mfk110-pnm-test1")
            self.assertEqual(output,"mfk110-pnm-test1")
            self.assertEqual(runner.call_count,3)
            self.assertIn("create",runner.call_args_list[1].args)

    def test_existing_project_must_be_exact_id(self):
        ok=Mock(returncode=0,stdout="mfk110-pnm-test2\n",stderr="")
        with patch("youtube_cloud_bootstrap.run_gcloud",return_value=ok) as runner:
            ensure_project("gcloud","mfk110-pnm-test2")
            self.assertEqual(runner.call_count,2)
            self.assertNotIn("create",str(runner.call_args_list))

    def test_api_enablement_is_verified(self):
        success=Mock(returncode=0,stdout=API_SERVICE+"\n",stderr="")
        with patch("youtube_cloud_bootstrap.run_gcloud",return_value=success) as runner:
            ensure_youtube_api("gcloud","mfk110-pnm-test1")
            self.assertEqual(runner.call_count,2)
            self.assertIn(API_SERVICE,runner.call_args_list[0].args)
            self.assertIn("--project=mfk110-pnm-test1",runner.call_args_list[0].args)
        with patch("youtube_cloud_bootstrap.run_gcloud",
                   side_effect=[success,Mock(returncode=0,stdout="")]):
            with self.assertRaisesRegex(RuntimeError,"not confirmed"):
                ensure_youtube_api("gcloud","mfk110-pnm-test1")

    def test_login_only_if_no_active_account(self):
        active=Mock(returncode=0,stdout="owner@gmail.example\n",stderr="")
        with patch("youtube_cloud_bootstrap.run_gcloud",return_value=active) as runner:
            ensure_google_login("gcloud")
            self.assertEqual(runner.call_count,1)
        empty=Mock(returncode=0,stdout="",stderr="")
        with patch("youtube_cloud_bootstrap.run_gcloud",
                   side_effect=[empty,empty,active]) as runner:
            ensure_google_login("gcloud")
            self.assertIn("login",runner.call_args_list[1].args)

    def test_open_only_expected_google_auth_platform_url(self):
        url=desktop_client_page("mfk110-pnm-test3")
        self.assertEqual(url,"https://console.cloud.google.com/auth/clients?project=mfk110-pnm-test3")
        with self.assertRaises(ValueError):
            desktop_client_page("bad.example/?evil=true")

    def test_oauth_json_project_must_equal_the_gcloud_project(self):
        info={
            "project_id":"mfk110-pnm-project1",
            "client_id":"client.apps.googleusercontent.com",
            "client_secret":"SECRET",
            "auth_uri":"https://accounts.google.com/o/oauth2/auth",
            "token_uri":"https://oauth2.googleapis.com/token",
        }
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"client.json"
            path.write_text(json.dumps({"installed":info}),encoding="utf-8")
            self.assertEqual(validate_google_client_file(
                path,expected_project="mfk110-pnm-project1"),"mfk110-pnm-project1")
            with self.assertRaisesRegex(RuntimeError,"DIFFERENT"):
                validate_google_client_file(path,expected_project="mfk110-pnm-project2")
            with patch("youtube_cloud_bootstrap.subprocess.run",
                       return_value=Mock(returncode=0)) as runner:
                self.assertEqual(continue_oauth(path,"mfk110-pnm-project1"),0)
                cmd=runner.call_args.args[0]
                self.assertIn("--expected-project",cmd)
                self.assertIn("mfk110-pnm-project1",cmd)
                self.assertIn("--enable-private-test",cmd)


if __name__=="__main__":
    unittest.main()
