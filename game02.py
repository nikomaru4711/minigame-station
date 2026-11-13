# ヲツ数え
import pyxel
import math
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
        pyxel.mouse(True)
        pyxel.images[0].load(0, 0, "assets/images/wotu_icon_40px.png")
        pyxel.images[0].load(40, 0, "assets/images/wotu_icon_rotate_40px.png")
        # ユーザー設定 #####
        self.s_button_area = (70, 100, 30, 11) #(x,y,w,h)
        self.confirm_ans_button_area = (300, 100, 100, 100) 
        ###################
        self.current_house_pos = (220, 0) # 家の位置
        self.active_events = []  # 発生中のイベントを管理するリスト
        self.max_events = 5  # 同時発生の上限数
        # bool ########################
        self.is_hover_start = False
        self.is_hover_confirm_answer = False
        # 状態 #####################
        self.state = "INTRODUCTION"
        self.input_text = ""
        self.user_answer = None  # 確定した回答（int）
        self.max_digits = 3  # 最大桁数
        # タイマー #####################
        self.time_limit = 1200
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

    def try_spawn_event(self):
        r = rand.random()
        housex, housey = self.current_house_pos
        if r < 0.25: # ヲツが部屋に入っていく
            ra = rand.randint(1,3)
            self.active_events.append({
                "type": "entry",
                "amount": ra,
                "x": -20,
                "y": housey+20,
                "timer": 0,
                "state": "none",
                "is_finished": False
            })
            self.anser_count += ra
        elif r < 0.5: # ヲツが部屋から出ていく
            ra = rand.randint(1,3)
            self.active_events.append({
                "type": "exit",
                "amount": ra,
                "x": housex,
                "y": housey+20,
                "timer": 0,
                "state": "none",
                "is_finished": False
            })
            self.anser_count -= ra
        elif r < 0.75: # ヲツが部屋に入ろうとして入らない
            ra = rand.randint(1,3)
            self.active_events.append({
                "type": "feint",
                "amount": 3,
                "x": -30,
                "y": housey+20,
                "y_origin": housey+20,
                "timer": 0,
                "state": "walking_straight",
                "is_finished": False
            })
        elif r < 1.0: # ヲツが煙突から入っていく
            ra = rand.randint(1,3)
            self.active_events.append({
                "type": "entry_from_chimney",
                "amount": ra,
                "x": housex+17,
                "y": -30,
                "timer": 0,
                "state": "none",
                "is_finished": False
            })
            self.anser_count +=ra
    
    def update(self):
        # 状態ごとの動作 
        if self.state == "INTRODUCTION":
            self.is_hover_start = self.is_mouse_over_area(self.s_button_area)
            if self.is_hover_start and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                pyxel.mouse(False)
                self.start_game()
        elif self.state == "PLAY":
            housex, housey = self.current_house_pos
            self.time_limit -=1
            # イベント抽選 ###############################################################
            if len(self.active_events) < self.max_events and self.time_limit > 240:
                self.try_spawn_event()

            # イベントごとの更新 ##########################################################
            for ev in self.active_events:
                if ev["type"] == "entry":
                    ev["x"] += 2
                    if ev["x"] > housex:
                        ev["is_finished"] = True
                elif ev["type"] == "exit":
                    ev["x"] += 2
                    if ev["x"] > pyxel.width + 50:
                        ev["is_finished"] = True
                elif ev["type"] == "feint":
                    if ev["state"] == "walking_straight":
                        if ev["x"] < housex - 140:
                            ev["x"] += 2
                        else:
                            ev["state"] = "waiting"
                            ev["timer"]  = 0
                    elif ev["state"] == "waiting":
                        ev["timer"] += 1
                        if ev["timer"] > 40:
                            ev["state"] = "jumping"
                            ev["timer"] = 0
                    elif ev["state"] == "jumping":
                        ev["y"] =  ev["y_origin"] - (40 * abs(math.sin(ev["timer"]/10)))
                        ev["timer"] += 1
                        if ev["timer"] > 62:
                            ev["state"] = "back"
                            ev["timer"] = 0
                    elif ev["state"] == "back":
                        ev["x"] -= 2
                        if ev["x"] < -30:
                            ev["is_finished"] = True
                elif ev["type"] == "entry_from_chimney":
                    ev["y"] += 2
                    if ev["y"] > housey:
                        ev["is_finished"] = True
            
            # 完了したイベントの削除 #######################################################
            self.active_events = [
                ev for ev in self.active_events if not ev["is_finished"]
            ]
            if self.time_limit > 0:
                self.state = "ANSWER"
                pyxel.mouse(True)
        elif self.state == "ANSWER":
            if len(self.input_text) < self.max_digits:
                for num in range(10):
                    if pyxel.btnp(getattr(pyxel, f"KEY_{num}")) or pyxel.btnp(
                        getattr(pyxel, f"KEY_KP_{num}")
                    ):
                        if self.input_text == "0":
                            self.input_text = str(num)  # "05" のように先頭に0が残るのを防ぐ
                        else:
                            self.input_text += str(num)

                # 2. Backspace で1文字削除（長押し連続削除対応）
                if pyxel.btnp(pyxel.KEY_BACKSPACE, hold=15, repeat=4):
                    self.input_text = self.input_text[:-1]

                # 3. Enter で確定して self.user_answer に保存
                if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_KP_ENTER):
                    if self.input_text != "":
                        self.user_answer = int(self.input_text)
                        # ここで結果判定フェーズへ遷移させる（例: self.phase = "result"）
                self.is_hover_confirm_answer = self.is_mouse_over_area(self.confirm_ans_button_area)
                if self.is_hover_confirm_answer and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    pyxel.mouse(False)
                    self.state = "RESULT"
        elif self.state == "RESULT":
            a=1



    def draw(self):
        pyxel.cls(0)
        if self.state == "INTRODUCTION":
            # 半透明な図形を描画 ########################
            # pyxel.dither(0.5)
            # pyxel.rect(0, 0, pyxel.width, pyxel.height, 1)
            # pyxel.dither(1.0)
            ############################################
            button_bg_color = 6 if self.is_hover_start else 12
            button_text_color = 13 if self.is_hover_start else 7
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
            for ev in self.active_events:
                for index in range(ev["amount"]):
                    if ev["type"] == "entry_from_chimney":
                        pyxel.blt(
                                    ev["x"],
                                    ev["y"] + (60 * index * index - 100 * index),
                                    0, 40, 0, 40, 40, 0
                                )
                    else:
                        pyxel.blt(
                            ev["x"] + (30 * index * index - 50 * index),
                            ev["y"] + (-13 * index * index + 39 * index - 13),
                            0, 0, 0, 40, 40, 0
                        )
            # 常に描画されるもの
            self.draw_house(self.current_house_pos)
            pyxel.text(216, 20, str(int(self.time_limit / 60)), 7, self.font12)  
        elif self.state == "ANSWER":
            pyxel.text(200, 20, "家の中にいるヲツは何人？(数字を入力)", 7, self.font12)
            self.draw_house(self.current_house_pos)

                

            

