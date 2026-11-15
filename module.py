import pyxel

class GameModule:
    def __init__(self):
      self.font10 = pyxel.Font("assets/fonts/PixelMplus10-Regular.ttf", 10)
      self.font20 = pyxel.Font("assets/fonts/PixelMplus10-Regular.ttf", 20)
    
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