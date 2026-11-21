import pyxel
from module import GameModule


class Button:
    def __init__(self, label, area):
        self.label = label
        self.area = area

    def hovered(self):
        x, y, w, h = self.area
        return x <= pyxel.mouse_x < x + w and y <= pyxel.mouse_y < y + h

    def clicked(self):
        return self.hovered() and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

    def draw(self, font):
        x, y, w, h = self.area
        pyxel.rect(x, y, w, h, 6 if self.hovered() else 1)
        pyxel.rectb(x, y, w, h, 12)
        pyxel.text(x + (w - font.text_width(self.label)) // 2,
                   y + (h - 10) // 2, self.label, 7, font)


class MenuScene(GameModule):
    def __init__(self, app, heading, choices):
        super().__init__()
        self.app = app
        self.heading = heading
        pyxel.mouse(True)
        self.buttons = [
            (Button(label, (80, 65 + i * 36, 280, 28)), target)
            for i, (label, target) in enumerate(choices)
        ]

    def update(self):
        for button, target in self.buttons:
            if button.clicked():
                return target
        return None

    def draw(self):
        pyxel.cls(0)
        pyxel.text((440 - self.font20.text_width(self.heading)) // 2,
                   20, self.heading, 10, self.font20)
        for button, _ in self.buttons:
            button.draw(self.font10)
