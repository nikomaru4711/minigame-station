"""標準ライブラリだけでFirebase認証・Firestore REST APIを使用する。"""

import json
import time
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import firebase_config as config
from player import valid_name


class FirestoreClient:
    def __init__(self, profile, project_id=None, api_key=None):
        self.profile = profile
        self.project_id = config.PROJECT_ID if project_id is None else project_id
        self.api_key = config.API_KEY if api_key is None else api_key
        self.document_root = (f"https://firestore.googleapis.com/v1/projects/{quote(self.project_id, safe='')}"
                              f"/databases/{quote(config.DATABASE_ID, safe='()')}/documents")
        self.token = None
        self.expires_at = 0
        self.uid = None

    @property
    def enabled(self):
        return bool(self.project_id.strip() and self.api_key.strip())

    def _request(self, method, url, body=None, token=None, form=False):
        headers = {}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
            data = (urlencode(body) if form else json.dumps(body)).encode("utf-8")
        if token:
            headers["Authorization"] = "Bearer " + token
        request = Request(url, data=data, headers=headers, method=method)
        with urlopen(request, timeout=8) as response:
            return json.load(response)

    def _authenticate(self):
        if self.token and time.monotonic() < self.expires_at:
            return
        with self.profile.lock:
            auth = dict(self.profile.auth)
        key = urlencode({"key": self.api_key})
        if auth.get("project_id") == self.project_id and auth.get("refresh_token"):
            # 認証エラー時に別アカウントを作り直さず、同じUIDの復旧を求める。
            result = self._request("POST", "https://securetoken.googleapis.com/v1/token?" + key,
                                   {"grant_type": "refresh_token", "refresh_token": auth["refresh_token"]},
                                   form=True)
            token, uid = result["id_token"], result["user_id"]
            refresh, expires = result["refresh_token"], result["expires_in"]
        else:
            result = self._request("POST", "https://identitytoolkit.googleapis.com/v1/accounts:signUp?" + key,
                                   {"returnSecureToken": True})
            token, uid = result["idToken"], result["localId"]
            refresh, expires = result["refreshToken"], result["expiresIn"]
        self.profile.set_auth(self.project_id, uid, refresh)
        self.token, self.uid = token, uid
        self.expires_at = time.monotonic() + max(0, int(expires) - 60)

    def _firestore(self, method, url, body=None):
        self._authenticate()
        try:
            return self._request(method, url, body, token=self.token)
        except HTTPError as error:
            if error.code != 401:
                raise
        self.token = None
        self._authenticate()
        return self._request(method, url, body, token=self.token)

    def submit(self, category, player_id, name, score):
        if not self.enabled:
            raise ValueError("Firebase is not configured")
        if not valid_name(name) or type(score) is not int or score < 0:
            raise ValueError("Invalid ranking entry")
        collection = config.COLLECTIONS[category]
        self._authenticate()
        # 認証UIDをドキュメントIDにして、１ユーザー１件をルールでも保証する。
        url = self.document_root + "/" + collection + "/" + quote(self.uid, safe="")
        body = {"fields": {
            "player_id": {"stringValue": player_id},
            "player_name": {"stringValue": name.strip()},
            "score": {"integerValue": str(score)},
        }}
        for _ in range(4):
            try:
                previous = self._firestore("GET", url)
            except HTTPError as error:
                if error.code != 404:
                    raise
                condition = {"currentDocument.exists": "false"}
            else:
                if int(previous["fields"]["score"]["integerValue"]) >= score:
                    return False
                condition = {"currentDocument.updateTime": previous["updateTime"]}
            try:
                self._firestore("PATCH", url + "?" + urlencode(condition), body)
                return True
            except HTTPError as error:
                if error.code not in (409, 412):
                    raise
                # 別端末・別プロセスが更新した場合は再比較し、ベストを下げない。
        raise RuntimeError("Concurrent score update; retry required")

    def fetch(self, category):
        if not self.enabled:
            raise ValueError("Firebase is not configured")
        result = self._firestore("POST", self.document_root + ":runQuery", {
            "structuredQuery": {
                "from": [{"collectionId": config.COLLECTIONS[category]}],
                "orderBy": [{"field": {"fieldPath": "score"}, "direction": "DESCENDING"}],
                "limit": 5,
            },
        })
        entries = []
        for row in result:
            if "document" not in row:
                continue
            fields = row["document"]["fields"]
            entries.append({"player_id": fields["player_id"]["stringValue"],
                            "name": fields["player_name"]["stringValue"],
                            "score": int(fields["score"]["integerValue"])})
        return entries
