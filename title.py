from ui import MenuScene
import pyxel
from player import MAX_NAME_LENGTH, valid_name
from text_input import ime_composing


class TitleScene(MenuScene):
    def __init__(self, app):
        super().__init__(app, "Minigame Station", [
            ("ミニゲームアタックをプレイ", "Attack"),
            ("ミニゲームをプレイ", "GameSelect"),
            ("スコア", "Score"),
            ("設定", "Settings"),
        ])
        self.name_text = app.player.name
        self.name_area = (80, 52, 280, 26)
        self.focused = True
        for i, (button, _) in enumerate(self.buttons):
            button.area = (80, 100 + i * 34, 280, 28)

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.focused = self.is_mouse_over_area(self.name_area)
        if self.focused:
            text = "".join(c for c in pyxel.input_text if c.isprintable())
            if text:
                self.name_text = (self.name_text + text)[:MAX_NAME_LENGTH]
                self.app.name_error = ""
            if not text and pyxel.btnp(pyxel.KEY_BACKSPACE, hold=15, repeat=4) and not ime_composing():
                self.name_text = self.name_text[:-1]
        for button, target in self.buttons:
            if button.clicked():
                if target in ("Attack", "GameSelect"):
                    if not self.app.set_player_name(self.name_text):
                        self.focused = True
                        return None
                elif valid_name(self.name_text):
                    if not self.app.set_player_name(self.name_text):
                        return None
                return target
        return None

    def draw(self):
        pyxel.cls(0)
        pyxel.text((440 - self.font20.text_width(self.heading)) // 2,
                   10, self.heading, 10, self.font20)
        pyxel.text(80, 38, "プレイヤーネーム（16文字まで）", 7, self.font10)
        x, y, w, h = self.name_area
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 10 if self.focused else 12)
        text = self.name_text or "名前を入力してください"
        pyxel.text(x + 8, y + 8, text, 7 if self.name_text else 5, self.font10)
        if self.focused and pyxel.frame_count % 60 < 30:
            cursor_x = x + 8 + self.font10.text_width(self.name_text)
            pyxel.line(cursor_x, y + 6, cursor_x, y + 19, 10)
        message = self.app.name_error
        if not message and not valid_name(self.name_text):
            message = "名前を入力してからプレイしてください"
        if message:
            pyxel.text(80, 83, message, 8, self.font10)
        for button, target in self.buttons:
            if target in ("Attack", "GameSelect") and not valid_name(self.name_text):
                bx, by, bw, bh = button.area
                pyxel.rect(bx, by, bw, bh, 1)
                pyxel.rectb(bx, by, bw, bh, 5)
                pyxel.text(bx + (bw - self.font10.text_width(button.label)) // 2,
                           by + 9, button.label, 5, self.font10)
            else:
                button.draw(self.font10)
