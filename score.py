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
        self.tabs = []
        x = 14
        for label, width in zip(self.NAMES, (130, 90, 90, 90)):
            self.tabs.append(Button(label, (x, 46, width, 28)))
            x += width + 4
        self.back = Button("タイトルに戻る", (120, 214, 200, 26))
        self.refresh = Button("更新", (350, 214, 76, 26))
        self.reload()

    def reload(self):
        self.app.ranking_service.retry_pending()
        for category in self.CATEGORIES:
            self.app.ranking_service.refresh(category)

    def update(self):
        for index, tab in enumerate(self.tabs):
            if tab.clicked():
                self.category = index
                return None
        if self.back.clicked():
            return "Title"
        if self.refresh.clicked():
            self.reload()
        return None

    def draw(self):
        pyxel.cls(0)
        pyxel.text(150, 12, "スコアランキング", 10, self.font20)
        for index, tab in enumerate(self.tabs):
            x, y, width, height = tab.area
            selected = index == self.category
            pyxel.rect(x, y, width, height, 1 if selected else 6 if tab.hovered() else 0)
            pyxel.rectb(x, y, width, height, 12 if selected else 5)
            pyxel.text(x + (width - self.font10.text_width(tab.label)) // 2,
                       y + 9, tab.label, 10 if selected else 7, self.font10)
            if selected:
                pyxel.rect(x, y + height - 3, width, 3, 10)
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
        self.back.draw(self.font10)
        self.refresh.draw(self.font10)
        status = self.app.ranking_service.status[self.CATEGORIES[self.category]]
        if status:
            pyxel.text(20, 200, status, 6, self.font10)
