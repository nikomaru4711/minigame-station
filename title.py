import pyxel
from module import GameModule

class TitleScene(GameModule):
    def __init__(self, app):
        self.app = app
        
    def update(self):
        if pyxel.btnp(pyxel.KEY_1):
            self.app.change_scene("Game01")
            return "Game01"
        if pyxel.btnp(pyxel.KEY_2):
            self.app.change_scene("Game02")
            return "Game02"
        if pyxel.btnp(pyxel.KEY_3):
                    self.app.change_scene("Game03")
                    return "Game03"
        return None

    def draw(self):
        pyxel.cls(0)
        
