import pyxel
from game_select import GAME_NAMES
from module import GameModule
from ui import Button


class ScoreScene(GameModule):
    CATEGORIES = ("Attack", "Game01", "Game02", "Game03")
    NAMES = ("ミニゲームアタック", *GAME_NAMES)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.category = 0
        pyxel.mouse(True)
        self.previous = Button("前へ", (20, 48, 60, 24))
        self.next = Button("次へ", (360, 48, 60, 24))
        self.back = Button("タイトルに戻る", (120, 214, 200, 26))

    def update(self):
        if self.previous.clicked():
            self.category = (self.category - 1) % len(self.CATEGORIES)
        elif self.next.clicked():
            self.category = (self.category + 1) % len(self.CATEGORIES)
        elif self.back.clicked():
            return "Title"
        return None

    def draw(self):
        pyxel.cls(0)
        pyxel.text(150, 12, "スコアランキング", 10, self.font20)
        label = self.NAMES[self.category]
        pyxel.text((440 - self.font10.text_width(label)) // 2, 55, label, 7, self.font10)
        entries = sorted(self.app.rankings[self.CATEGORIES[self.category]],
                         key=lambda entry: entry["score"], reverse=True)[:5]
        for i in range(5):
            name = entries[i]["name"] if i < len(entries) else "---"
            score = str(entries[i]["score"]) if i < len(entries) else "---"
            y = 88 + i * 23
            pyxel.text(65, y, str(i + 1), 10, self.font10)
            while self.font10.text_width(name) > 170:
                name = name[:-1]
            pyxel.text(105, y, name, 7, self.font10)
            pyxel.text(310, y, score, 7, self.font10)
        for button in (self.previous, self.next, self.back):
            button.draw(self.font10)
