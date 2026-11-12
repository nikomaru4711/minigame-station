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
        self.current_house_pos = (220, 0)
        # bool ########################
        self.is_hover = False
        self.is_event1_running = False
        self.is_event2_running = False
        # タイマー #####################
        ###############################
        

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
        self.fill_polygon([
            (posx, posy - 75),
            (posx + 63, posy - 12),
            (posx + 63, posy + 75),
            (posx - 63, posy + 75),
            (posx - 63, posy - 12)
        ], house_color)
        
        # 窓（4つ・2.5倍スケール）
        pyxel.rect(posx + 15, posy, 15, 15, window_color)
        pyxel.rect(posx + 35, posy, 15, 15, window_color)
        pyxel.rect(posx + 15, posy + 20, 15, 15, window_color)
        pyxel.rect(posx + 35, posy + 20, 15, 15, window_color)
        
        # 煙突（2.5倍スケール）
        pyxel.rect(posx + 25, posy - 62, 25, 50, house_color)
        self.fill_polygon([
            (posx + 22, posy - 65),
            (posx + 50, posy - 65),
            (posx + 55, posy - 72),
            (posx + 17, posy - 72)
        ], house_color)

    def start_game(self):
        # ランダム要素の設定 ##########
        self.initial_count = rand.randint(0, 6)
        self.entry_count = rand.randint(5,15)
        self.exit_count = rand.randint(5, self.initial_count + self.entry_count)
        ##############################
        self.anser_count = self.initial_count + self.entry_count - self.exit_count
        self.state = "SETUP"

    def is_mouse_over_area(self, area):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        x, y, w, h = area
        return x <= mx <= x + w and y <= my <= y + h

    def wotu_in(self, event):
        event = True

    def wotu_out(self, event):
        event = True
    
    def wotu_in_chimney(self, event):
        event = True

    def wotu_feint(self, event):
        event = True
    
    def update(self):
        self.is_hover = self.is_mouse_over_area(self.s_button_area)
        if self.is_hover and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            pyxel.mouse(False)
            self.start_game()
        # 状態ごとの動作
        if self.state == "PLAY":
            event1 = rand.random()
            event2 = rand.random()
            # ヲツが入ってくる
            # ヲツが出てくる
            # ヲツが入ろうとして入らない
            # 煙突からヲツが入っていく
            # 発生するイベントを管理
            if not(self.is_event1_running):
                if event1 > 0.9:
                    event1=0
                elif event1 > 0.8:
                    event1=0
                elif event1 > 0.7:
                    event1=0

            if not(self.is_event2_running):
                if event2 > 0.9:
                    event2=0
                elif event2 > 0.8:
                    event2=0
                elif event2 > 0.7:
                    event2=0
                        

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
        elif self.state == "SETUP":
            # summary:家の中にいるヲツの表示と家の配置
            housex, housey = self.current_house_pos
            # ヲツの配置(160~240, 120~146でw=h=40)
            if self.initial_count > 0:
                for count in range(1, self.initial_count + 1):
                    posx = 160 + 40 * ((count - 1) % 3)
                    posy = 120 + 26 * ((count - 1) // 3)
                    pyxel.blt(posx, posy, 0, 0, 0, 40, 40, 0)
            # 家の位置を更新し続ける
            self.draw_house(self.current_house_pos)
            if housey < 120:
                self.current_house_pos = (housex, housey+2)
            else :
                self.state = "PLAY"
        elif self.state == "PLAY":
                self.draw_house(self.current_house_pos)
                pyxel.text(200, 140, "READY", 7, self.font12)

            

