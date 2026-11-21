import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from firestore_client import FirestoreClient
from player import PlayerProfile, valid_name
from ranking_service import RankingService


class FirestoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "player.json"
        self.player = PlayerProfile(self.path)
        self.client = FirestoreClient(self.player, "test-project", "test-key")
        self.client.token = "fake-token"
        self.client.expires_at = float("inf")
        self.client.uid = "anonymous-user"

    def submit(self, score=300):
        return self.client.submit("Game01", self.player.player_id, "テスト", score)

    def previous(self, score):
        return {"fields": {"score": {"integerValue": str(score)}}, "updateTime": "2026-11-21T00:00:00Z"}

    def test_uuid_name_and_auth_survive_restart(self):
        self.player.set_name("  プレイヤー　")
        self.player.set_auth("project", "uid", "refresh")
        reloaded = PlayerProfile(self.path)
        self.assertEqual(reloaded.player_id, self.player.player_id)
        self.assertEqual(reloaded.name, "プレイヤー")
        self.assertEqual(reloaded.auth["refresh_token"], "refresh")

    def test_empty_and_whitespace_names_rejected(self):
        for name in ("", " ", "　", "\t\n", "a" * 17, "name\nvalue"):
            self.assertFalse(valid_name(name))
            with self.assertRaises(ValueError):
                self.player.set_name(name)

    def test_corrupt_profile_is_not_overwritten_with_new_identity(self):
        self.path.write_text("broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            PlayerProfile(self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "broken")

    def test_create_saves_exactly_three_fields_with_uuid(self):
        missing = HTTPError("url", 404, "not found", {}, None)
        with patch.object(self.client, "_firestore", side_effect=[missing, {}]) as request:
            self.assertTrue(self.submit())
        method, url, body = request.call_args.args
        self.assertEqual(method, "PATCH")
        self.assertIn("/rankings_game01/anonymous-user?currentDocument.exists=false", url)
        self.assertEqual(body["fields"], {
            "player_id": {"stringValue": self.player.player_id},
            "player_name": {"stringValue": "テスト"},
            "score": {"integerValue": "300"},
        })

    def test_equal_or_lower_scores_do_not_overwrite_best(self):
        for score in (200, 300):
            with patch.object(self.client, "_firestore", return_value=self.previous(300)) as request:
                self.assertFalse(self.submit(score))
                self.assertEqual(request.call_count, 1)

    def test_higher_score_uses_update_time_precondition(self):
        with patch.object(self.client, "_firestore", side_effect=[self.previous(100), {}]) as request:
            self.assertTrue(self.submit())
        self.assertIn("currentDocument.updateTime=", request.call_args.args[1])

    def test_concurrent_higher_score_is_not_overwritten(self):
        conflict = HTTPError("url", 412, "conflict", {}, None)
        with patch.object(self.client, "_firestore", side_effect=[self.previous(100), conflict,
                                                                 self.previous(400)]) as request:
            self.assertFalse(self.submit())
        self.assertEqual([call.args[0] for call in request.call_args_list], ["GET", "PATCH", "GET"])

    def test_fetch_uses_separate_collection_and_top_five_query(self):
        fields = {"player_id": {"stringValue": self.player.player_id},
                  "player_name": {"stringValue": "名前"}, "score": {"integerValue": "628"}}
        with patch.object(self.client, "_firestore", return_value=[{}, {"document": {"fields": fields}}]) as request:
            entries = self.client.fetch("Attack")
        query = request.call_args.args[2]["structuredQuery"]
        self.assertEqual(query["limit"], 5)
        self.assertEqual(query["from"], [{"collectionId": "rankings_attack"}])
        self.assertEqual(entries, [{"player_id": self.player.player_id, "name": "名前", "score": 628}])

    def test_anonymous_login_and_refresh_reuse_same_uid(self):
        self.client.token = None
        with patch.object(self.client, "_request", return_value={
            "idToken": "first", "localId": "uid", "refreshToken": "refresh", "expiresIn": "3600",
        }) as request:
            self.client._authenticate()
        self.assertIn("accounts:signUp", request.call_args.args[1])
        client = FirestoreClient(PlayerProfile(self.path), "test-project", "test-key")
        with patch.object(client, "_request", return_value={
            "id_token": "next", "user_id": "uid", "refresh_token": "refresh2", "expires_in": "3600",
        }) as request:
            client._authenticate()
        self.assertIn("securetoken.googleapis.com", request.call_args.args[1])
        self.assertEqual(client.uid, "uid")

    def test_http_request_sends_bearer_and_json(self):
        response = io.BytesIO(b'{"ok": true}')
        with patch("firestore_client.urlopen", return_value=response) as urlopen:
            self.assertTrue(self.client._request("PATCH", "https://example.invalid", {"score": 200}, token="token")["ok"])
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "PATCH")
        self.assertEqual(request.get_header("Authorization"), "Bearer token")
        self.assertEqual(json.loads(request.data), {"score": 200})
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 8)

    def test_unconfigured_service_does_not_start_network(self):
        client = FirestoreClient(self.player, "", "")
        service = RankingService(client)
        with patch.object(client, "_request") as request:
            service.submit("Attack", self.player.player_id, "名前", 200)
            service.refresh("Attack")
            service.poll()
        request.assert_not_called()
        self.assertIsNone(service.worker)
        self.assertEqual(service.status["Attack"], "Firebase未設定")

    def test_service_updates_main_thread_data_and_retries_failures(self):
        service = RankingService(self.client)
        entries = [{"player_id": self.player.player_id, "name": "名前", "score": 200}]
        with patch.object(self.client, "submit", side_effect=[OSError("offline"), True]) as submit, \
                patch.object(self.client, "fetch", return_value=entries):
            service.submit("Game02", self.player.player_id, "名前", 200)
            service.jobs.join()
            service.poll()
            self.assertIn("通信失敗", service.status["Game02"])
            self.assertIn("Game02", service.pending)
            service.retry_pending()
            service.jobs.join()
            service.poll()
        self.assertEqual(submit.call_count, 2)
        self.assertEqual(service.rankings["Game02"], entries)
        self.assertNotIn("Game02", service.pending)


if __name__ == "__main__":
    unittest.main()
