import pyxel
from module import GameModule
from ui import Button


class SettingsScene(GameModule):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.error = ""
        pyxel.mouse(True)
        self.controls = []
        for key, y in (("bgm_volume", 80), ("se_volume", 135)):
            self.controls.append((key, Button("－", (250, y, 35, 28)),
                                  Button("＋", (350, y, 35, 28))))
        self.back = Button("保存してタイトルに戻る", (100, 210, 240, 28))

    def update(self):
        for key, minus, plus in self.controls:
            step = -1 if minus.clicked() else (1 if plus.clicked() else 0)
            if step:
                value = round(getattr(self.app.settings, key) * 10) + step
                setattr(self.app.settings, key, max(0, min(10, value)) / 10)
                self.app.audio.apply_volumes()
                self.save()
        if self.back.clicked() and self.save():
            return "Title"
        return None

    def save(self):
        try:
            self.app.settings.save()
        except OSError:
            self.error = "設定を保存できませんでした。再度お試しください。"
            return False
        self.error = ""
        return True

    def draw(self):
        pyxel.cls(0)
        pyxel.text(200, 20, "設定", 10, self.font20)
        for label, (key, minus, plus) in zip(("BGM 音量", "SE 音量"), self.controls):
            y = minus.area[1]
            pyxel.text(60, y + 9, label, 7, self.font10)
            value = round(getattr(self.app.settings, key) * 100)
            pyxel.text(298, y + 9, f"{value}%", 7, self.font10)
            minus.draw(self.font10)
            plus.draw(self.font10)
        if self.error:
            pyxel.text(15, 184, self.error, 8, self.font10)
        self.back.draw(self.font10)
