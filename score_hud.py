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
            self.pending.append(amount)

    def update(self):
        if self.amount is None:
            if not self.pending:
                return
            self.amount = self.pending.popleft()
            self.frame = 0
        self.frame += 1
        count_start = self.ENTER_FRAMES + self.MERGE_FRAMES
        if self.frame > count_start:
            t = min((self.frame - count_start) / self.COUNT_FRAMES, 1)
            # 合流後だけ本体の数値をカウントアップする。
            self.display_value = self.value + round(self.amount * (1 - (1 - t) ** 3))
            if t == 1:
                self.value += self.amount
                self.display_value = self.value
                self.amount = None

    def bonus_pose(self):
        """加点文字の右方向オフセット・下方向オフセット・不透明度。"""
        if self.frame <= self.ENTER_FRAMES:
            t = self.frame / self.ENTER_FRAMES
            return 24 * (1 - t) ** 3, 14, t
        t = min((self.frame - self.ENTER_FRAMES) / self.MERGE_FRAMES, 1)
        return 0, 14 * (1 - t * t), 1

    def draw(self, y=4):
        right = pyxel.width - 8
        value_right = right - 24
        value = str(self.display_value)
        label = "スコア " + value
        width = max(130, self.font10.text_width(label) + 32)
        pyxel.rect(right - width, y - 2, width + 4, 30, 0)
        pyxel.text(value_right - self.font10.text_width(label), y, label, 7, self.font10)
        if self.amount is not None and self.frame <= self.ENTER_FRAMES + self.MERGE_FRAMES:
            dx, dy, opacity = self.bonus_pose()
            text = f"+{self.amount}"
            # 右からの移動中も文字全体を画面内に収める。
            x = value_right - self.font10.text_width(text) + dx
            pyxel.dither(opacity)
            pyxel.text(x, y + dy, text, 10, self.font10)
            pyxel.dither(1)
