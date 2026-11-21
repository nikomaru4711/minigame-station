import json
from pathlib import Path


SETTINGS_PATH = Path(__file__).resolve().parent / "data" / "settings.json"
BGM_VOLUME = 1.0
SE_VOLUME = 1.0


class Settings:
    def __init__(self, path=SETTINGS_PATH):
        self.path = Path(path)
        self.bgm_volume = BGM_VOLUME
        self.se_volume = SE_VOLUME
        self.load()

    def load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if not isinstance(data, dict):
            return
        for key in ("bgm_volume", "se_volume"):
            value = data.get(key)
            if type(value) in (int, float) and 0 <= value <= 1:
                setattr(self, key, float(value))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps({
            "bgm_volume": self.bgm_volume,
            "se_volume": self.se_volume,
        }, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)
