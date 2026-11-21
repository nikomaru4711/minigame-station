import pyxel
from audio import Audio
from game_select import GameSelectScene, GAME_IDS
from game01 import Game01
from game02 import Game02
from game03 import Game03
from result import ResultScene
from score import ScoreScene
from score_hud import ScoreHUD
from setting import Settings
from settings_scene import SettingsScene
from title import TitleScene
from ui import Button


class App:
    def __init__(self):
        self.fps = 60
        pyxel.init(440, 250, title="Minigame Station", fps=self.fps)
        self.settings = Settings()
        self.audio = Audio(self.settings)
        # ランキングへのユーザー名付き記録登録は未実装。
        self.rankings = {key: [] for key in ("Attack", *GAME_IDS)}
        self.play_mode = "single"
        self.active_game_id = None
        self.game_cleared = False
        self.score_hud = ScoreHUD()
        self.attack_finished = False
        self.next_button = None
        self.change_scene("Title")
        pyxel.run(self.update, self.draw)

    def change_scene(self, next_scene_id):
        if next_scene_id == "Attack":
            self.play_mode = "attack"
            self.score_hud.reset()
            next_scene_id = GAME_IDS[0]
        elif next_scene_id == "Retry":
            next_scene_id = self.active_game_id
        elif next_scene_id == "NextGame":
            next_scene_id = GAME_IDS[GAME_IDS.index(self.active_game_id) + 1]
        elif next_scene_id in ("Title", "GameSelect"):
            self.play_mode = "single"

        scenes = {
            "Title": TitleScene, "GameSelect": GameSelectScene,
            "Score": ScoreScene, "Settings": SettingsScene, "Result": ResultScene,
            "Game01": Game01, "Game02": Game02, "Game03": Game03,
        }
        self.current_scene_id = next_scene_id
        if next_scene_id in GAME_IDS:
            if self.play_mode == "single":
                self.score_hud.reset()
            self.active_game_id = next_scene_id
            self.game_cleared = False
        self.attack_finished = False
        self.next_button = None
        pyxel.stop()
        self.scene = scenes[next_scene_id](self)

    def finish_game(self, cleared):
        self.game_cleared = cleared
        if self.play_mode == "attack":
            # シーンもゲームのオブジェクトも維持し、更新だけを停止する。
            self.attack_finished = True
            last_game = self.active_game_id == GAME_IDS[-1]
            label = "リザルトへ" if last_game else "次のミニゲームへ"
            self.next_button = Button(label, (100, 210, 240, 28))
            pyxel.mouse(True)
            return None
        return "Result"

    def add_score(self, amount):
        """各ゲームから加点を受け取り、順番に演出する。"""
        self.score_hud.add(amount)

    def update(self):
        if self.current_scene_id in GAME_IDS or self.current_scene_id == "Result":
            self.score_hud.update()
        if self.attack_finished:
            if not self.score_hud.animating and self.next_button.clicked():
                target = "Result" if self.active_game_id == GAME_IDS[-1] else "NextGame"
                self.change_scene(target)
            return
        next_scene = self.scene.update()
        if next_scene is not None:
            self.change_scene(next_scene)

    def draw(self):
        self.scene.draw()
        if self.current_scene_id in GAME_IDS or self.current_scene_id == "Result":
            # ヲツベーダーでは画面上部のボスHPバーより下に置く。
            y = 24 if self.current_scene_id == "Game03" else 4
            self.score_hud.draw(y)
        if self.attack_finished and not self.score_hud.animating:
            self.next_button.draw(self.scene.font10)


if __name__ == "__main__":
    App()
