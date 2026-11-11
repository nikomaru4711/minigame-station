# ヲツ数え
import pyxel
import random as rand
# 家の座標元データ ########################################################
# self.house_area = [(80, 20), (105, 45), (105, 80), (55, 80), (55, 45)]
# self.house_window_area1 = [(86, 50), (92, 50), (92, 56), (86, 56)]
# self.house_window_area2 = [(94, 50), (100, 50), (100, 56), (94, 56)]
# self.house_window_area3 = [(86, 58), (92, 58), (92, 64), (86, 64)]
# self.house_window_area4 = [(94, 58), (100, 58), (100, 64), (94, 64)]
# self.house_chimney1 = [(90, 25), (90, 45), (100, 45), (100, 25)]
# self.house_chimney2 = [(89, 24), (101, 24), (103, 21), (87, 21)]
##########################################################################

class Game02:
    def __init__(self, app):
        self.app = app
        self.font12 = app.font12
        self.state = "INTRODUCTION"
        pyxel.mouse(True)
        pyxel.images[0].load(0, 0, "assets/images/wotu_icon_40px.png")
        # ユーザー設定 #####
        self.s_button_area = (70, 100, 30, 11) #(x,y,w,h)
        ###################
        self.is_hover = False
        # ランダム要素の設定 ##########
        initial_count = rand.randint(0, 3)
        entry_count = rand.randint(5,15)
        exit_count = rand.randint(5, initial_count + entry_count)
        ##############################
        anser_wotu_count = initial_count + entry_count - exit_count

    def fill_polygon(self, pts, col):
    # 凸多角形を三角形に分割して塗りつぶして描画
        x0, y0 = pts[0]
        for i in range(1, len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            pyxel.tri(x0, y0, x1, y1, x2, y2, col)

    def draw_house (self, center_pos):
        posx, posy = center_pos
        house_color = 13
        window_color = 10
        self.fill_polygon([(posx, posy-30), (posx+25, posy-5),
                           (posx+25, posy+30), (posx-25, posy+30),
                           (posx-25, posy-5)]
                           , house_color)
        pyxel.rect(posx+6, posy, 6, 6, window_color)
        pyxel.rect(posx+14, posy, 6, 6, window_color)
        pyxel.rect(posx+6, posy+8, 6, 6, window_color)
        pyxel.rect(posx+14, posy+8, 6, 6, window_color)
        pyxel.rect(posx+10, posy-25, 10, 20, house_color)
        self.fill_polygon([(posx+9, posy-26), (posx+20, posy-26),
                           (posx+22, posy-29), (posx+7, posy-29)
                           ], house_color)

    def onClick_s():
        pyxel.mouse(False)

    def is_mouse_over_area(self, area):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        x, y, w, h = area
        return x <= mx <= x + w and y <= my <= y + h
    
    def update(self):
        self.is_hover = self.is_mouse_over_area(self.s_button_area)
        if self.is_hover and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.state = "PLAY"

    def draw(self):
        pyxel.cls(0)
        if self.state == "INTRODUCTION":
            # 半透明な図形を描画 ########################
            # pyxel.dither(0.5)
            # pyxel.rect(0, 0, pyxel.width, pyxel.height, 1)
            # pyxel.dither(1.0)
            ############################################
            button_bg_color = 6 if self.is_hover else 12
            button_text_color = 13 if self.is_hover else 7
            pyxel.text(2, 2, "ヲツかぞえ", 7, self.font12)
            pyxel.text(5, 17, "家の中にいるヲツの数を計算して、\n最後に答えよう", 7, self.font12)

            pyxel.text(85, 50, "←ヲツ", 7, self.font12)            
            pyxel.blt(40, 45, 0, 0, 0, 40, 40, 0)
            
            sx, sy, sw, sh = self.s_button_area
            pyxel.rect(sx, sy, sw, sh, button_bg_color)
            pyxel.rectb(sx, sy, sw, sh, 5)
            pyxel.text(sx+2, sy, "START", button_text_color, self.font12)
        elif self.state == "PLAY":
            pyxel.blt(20, 50, 0, 0, 0, 40, 40, 0)
            self.draw_house((80, 30))

            

