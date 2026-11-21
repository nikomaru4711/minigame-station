import json
from pathlib import Path
from threading import RLock
import uuid


PROFILE_PATH = Path(__file__).resolve().parent / "data" / "player.json"
MAX_NAME_LENGTH = 16


def valid_name(name):
    return (isinstance(name, str) and 0 < len(name.strip()) <= MAX_NAME_LENGTH
            and all(c.isprintable() for c in name.strip()))


class PlayerProfile:
    def __init__(self, path=PROFILE_PATH):
        self.path = Path(path)
        self.lock = RLock()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            data = {}
        # 壊れた既存ファイルを新しいUUIDで上書きしない。
        if not isinstance(data, dict):
            raise ValueError("Invalid player profile")
        self.player_id = str(uuid.UUID(data["player_id"])) if "player_id" in data else str(uuid.uuid4())
        self.name = data.get("name", "")
        if not isinstance(self.name, str):
            self.name = ""
        self.auth = data.get("auth", {})
        if not isinstance(self.auth, dict):
            raise ValueError("Invalid authentication profile")
        self.save()

    def save(self):
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps({
                "player_id": self.player_id, "name": self.name, "auth": self.auth,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(self.path)

    def set_name(self, name):
        if not valid_name(name):
            raise ValueError("A player name of 1 to 16 characters is required")
        with self.lock:
            previous = self.name
            self.name = name.strip()
            try:
                self.save()
            except OSError:
                self.name = previous
                raise

    def set_auth(self, project_id, uid, refresh_token):
        with self.lock:
            self.auth = {"project_id": project_id, "uid": uid, "refresh_token": refresh_token}
            self.save()
