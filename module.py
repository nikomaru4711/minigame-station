import pyxel
from pathlib import Path

class GameModule:
    def __init__(self):
      font_path = str(Path(__file__).resolve().parent / "assets/fonts/PixelMplus10-Regular.ttf")
      self.font10 = pyxel.Font(font_path, 10)
      self.font20 = pyxel.Font(font_path, 20)
      self._score_awarded = False

    def award_clear_score(self, bonus=0):
        self.award_score(200, bonus)

    def award_score(self, base, bonus=0):
        """基本点とボーナスを別々に予約し、二重加点を防ぐ。"""
        if self._score_awarded:
            return
        self._score_awarded = True
        self.app.add_score(base)
        if bonus > 0:
            self.app.add_score(bonus)
    
    def fill_polygon(self, pts, col):
        # 凸多角形を三角形に分割して塗りつぶして描画する
            x0, y0 = pts[0]
            for i in range(1, len(pts) - 1):
                x1, y1 = pts[i]
                x2, y2 = pts[i + 1]
                pyxel.tri(x0, y0, x1, y1, x2, y2, col)

    def is_mouse_over_area(self, area):
        # 選択したエリア上にマウスカーソルが存在するかを判定する
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        x, y, w, h = area
        return x <= mx <= x + w and y <= my <= y + h

    def update():
        pass

    def draw():
        pass
