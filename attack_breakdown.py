import pyxel
from game_select import GAME_IDS, GAME_NAMES


class AttackBreakdown:
    """最終リザルト専用の表示。確定点には触れず、毎回０から内訳を演出する。"""

    PART_FRAMES = 30

    def __init__(self, scores):
        self.scores = tuple((scores[game_id]["base"], scores[game_id]["bonus"])
                            for game_id in GAME_IDS)
        self.frame = 0

    def update(self):
        self.frame = min(self.frame + 1, len(self.scores) * 2 * self.PART_FRAMES)

    def progress(self, row, part):
        start = (row * 2 + part) * self.PART_FRAMES
        return max(0, min(1, (self.frame - start) / self.PART_FRAMES))

    def shown(self, row, part):
        t = self.progress(row, part)
        return round(self.scores[row][part] * (1 - (1 - t) ** 3))

    @property
    def display_total(self):
        return sum(self.shown(row, part) for row in range(len(self.scores)) for part in (0, 1))

    def draw(self, font10, font20):
        pyxel.text(30, 46, "ミニゲーム", 6, font10)
        pyxel.text(200, 46, "基礎点（＋ボーナス点）", 6, font10)
        for row, name in enumerate(GAME_NAMES):
            y = 64 + row * 32
            pyxel.text(30, y + 5, name, 7, font10)
            for part, x in ((0, 200), (1, 254)):
                t = self.progress(row, part)
                if part == 1 and t == 0:
                    continue
                number = self.shown(row, part)
                text = str(number) if part == 0 else f"（+{number}）"
                color = (7 if part == 0 else 10) if t > 0 else 5
                offset = round(16 * (1 - t) ** 3) if t > 0 else 0
                pyxel.dither(min(1, t * 3) if t > 0 else 1)
                pyxel.text(x + offset, y, text, color, font20)
                pyxel.dither(1)
            pyxel.line(30, y + 25, 410, y + 25, 1)
        total = f"合計スコア {self.display_total}"
        pyxel.text((pyxel.width - font20.text_width(total)) // 2, 166, total, 10, font20)
