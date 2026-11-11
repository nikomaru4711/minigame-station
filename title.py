import pyxel

class TitleScene:
    def __init__(self, app):
        self.app = app
        self.font12 = app.font12
        
    def update(self):
        if pyxel.btnp(pyxel.KEY_1):
            self.app.change_scene("Game01")
            return "Game01"
        if pyxel.btnp(pyxel.KEY_2):
            self.app.change_scene("Game02")
            return "Game02"
        return None

    def draw(self):
        pyxel.cls(0)
        
