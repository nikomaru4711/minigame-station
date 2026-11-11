import pyxel

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pyxel UI Button Example")
        
        # ボタンの位置・サイズを設定
        self.btn_x = 40
        self.btn_y = 50
        self.btn_w = 80
        self.btn_h = 20
        
        # マウスカーソルを有効化
        pyxel.mouse(True)
        
        # 状態変数
        self.is_hovered = False
        self.click_count = 0

        pyxel.run(self.update, self.draw)

    def is_mouse_over(self, x, y, w, h):
        """マウスカーソルが指定された矩形領域内にあるか判定"""
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        return x <= mx <= x + w and y <= my <= y + h

    def update(self):
        # ホバー状態のチェック
        self.is_hovered = self.is_mouse_over(self.btn_x, self.btn_y, self.btn_w, self.btn_h)

        # クリック処理 (左クリックが押された瞬間)
        if self.is_hovered and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.click_count += 1

    def draw(self):
        pyxel.cls(0)

        # 1. ボタンの色を変更 (ホバー時: 白, 通常時: 濃いグレー)
        bg_color = 7 if self.is_hovered else 13
        text_color = 0 if self.is_hovered else 7

        # 2. ボタン枠と背景の描画
        pyxel.rect(self.btn_x, self.btn_y, self.btn_w, self.btn_h, bg_color)
        pyxel.rectb(self.btn_x, self.btn_y, self.btn_w, self.btn_h, 7) # 外枠

        # 3. ボタンテキストの描画 (中央揃えの計算)
        label = "CLICK ME"
        text_x = self.btn_x + (self.btn_w - len(label) * 4) // 2
        text_y = self.btn_y + (self.btn_h - 6) // 2
        pyxel.text(text_x, text_y, label, text_color)

        # 情報の表示
        pyxel.text(10, 10, f"Clicks: {self.click_count}", 10)

App()