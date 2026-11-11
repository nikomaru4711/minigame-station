import pyxel
from title import TitleScene
from game01 import Game01
from game02 import Game02

class App:
    def __init__(self):
        pyxel.init(165, 125, title="Minigame Station")
        self.current_scene_id = "Title"
        self.font12 = pyxel.Font("assets/fonts/PixelMplus10-Regular.ttf", 10)
        self.scene = TitleScene(self)
        pyxel.run(self.update, self.draw)

    def change_scene(self, next_scene_id):
        self.current_scene_id = next_scene_id
        if next_scene_id == "Title":
            self.scene = TitleScene(self)
        elif next_scene_id == "Game01":
            self.scene = Game01(self)
        elif next_scene_id == "Game02":
            self.scene = Game02(self)

    def update(self):
        next_scene = self.scene.update()

        if next_scene is not None:
            self.change_scene(next_scene)

    def draw(self):
        self.scene.draw()
App()