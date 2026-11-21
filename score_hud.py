from collections import deque

import pyxel
from module import GameModule


class ScoreHUD(GameModule):
    """点数の計算はゲーム側で行い、app.add_score(加点値)から演出を予約する。"""

    ENTER_FRAMES = 24
    MERGE_FRAMES = 18
    COUNT_FRAMES = 30

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        self.value = 0
        self.display_value = 0
        self.count_from = 0
        self.pending = deque()
        self.amount = None
        self.frame = 0

    @property
    def animating(self):
        return self.amount is not None or bool(self.pending)

    def add(self, amount):
        if type(amount) is not int or amount < 0:
            raise ValueError("Score addition must be a non-negative integer")
        if amount:
            # 確定スコアは即時反映し、表示の進行とは独立させる。
            self.value += amount
            self.pending.append(amount)

    def update(self):
        if self.amount is None:
            if not self.pending:
                return
            self.amount = self.pending.popleft()
            self.count_from = self.display_value
            self.frame = 0
        self.frame += 1
        count_start = self.ENTER_FRAMES + self.MERGE_FRAMES
        if self.frame > count_start:
            t = min((self.frame - count_start) / self.COUNT_FRAMES, 1)
            # 合流後だけ本体の数値をカウントアップする。
            self.display_value = self.count_from + round(self.amount * (1 - (1 - t) ** 3))
            if t == 1:
                self.display_value = self.count_from + self.amount
                self.amount = None

    def bonus_pose(self):
        """加点文字の右方向オフセット・下方向オフセット・不透明度。"""
        if self.frame <= self.ENTER_FRAMES:
            t = self.frame / self.ENTER_FRAMES
            return 24 * (1 - t) ** 3, 14, t
        t = min((self.frame - self.ENTER_FRAMES) / self.MERGE_FRAMES, 1)
        return 0, 14 * (1 - t * t), 1

    def draw(self, y=110):
        center = pyxel.width // 2
        value = str(self.display_value)
        label = "スコア"
        pyxel.text(center - self.font20.text_width(label) // 2, y - 24, label, 7, self.font20)
        value_width = self.font20.text_width(value)
        pyxel.text(center - value_width // 2, y, value, 10, self.font20)
        if self.amount is not None and self.frame <= self.ENTER_FRAMES + self.MERGE_FRAMES:
            dx, dy, opacity = self.bonus_pose()
            text = f"+{self.amount}"
            x = center + value_width // 2 - self.font10.text_width(text) + dx
            pyxel.dither(opacity)
            pyxel.text(x, y + dy * 2, text, 10, self.font10)
            pyxel.dither(1)
