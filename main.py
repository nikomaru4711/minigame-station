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
from player import PlayerProfile, valid_name
from firestore_client import FirestoreClient
from ranking_service import RankingService
from text_input import configure_ime


class App:
    def __init__(self):
        self.fps = 60
        configure_ime()
        pyxel.init(440, 250, title="Minigame Station", fps=self.fps)
        self.settings = Settings()
        self.audio = Audio(self.settings)
        self.player = PlayerProfile()
        self.ranking_service = RankingService(FirestoreClient(self.player))
        self.rankings = self.ranking_service.rankings
        self.name_error = ""
        self.run_player_name = self.player.name
        self.game_score = 0
        self.game_scores = {game_id: {"base": 0, "bonus": 0} for game_id in GAME_IDS}
        self._game_submitted = False
        self.play_mode = "single"
        self.active_game_id = None
        self.game_cleared = False
        self.score_hud = ScoreHUD()
        self.attack_finished = False
        self.next_button = None
        self.change_scene("Title")
        pyxel.run(self.update, self.draw)

    def change_scene(self, next_scene_id):
        if next_scene_id in ("Attack", "GameSelect", "Retry", "NextGame", *GAME_IDS):
            if not valid_name(self.player.name):
                self.name_error = "名前を入力してからプレイしてください"
                return
        if next_scene_id == "Attack":
            self.play_mode = "attack"
            self.run_player_name = self.player.name
            self.score_hud.reset()
            self.game_scores = {game_id: {"base": 0, "bonus": 0} for game_id in GAME_IDS}
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
                self.run_player_name = self.player.name
                self.game_scores = {game_id: {"base": 0, "bonus": 0} for game_id in GAME_IDS}
            self.game_score = 0
            self.game_scores[next_scene_id] = {"base": 0, "bonus": 0}
            self._game_submitted = False
            self.active_game_id = next_scene_id
            self.game_cleared = False
        self.attack_finished = False
        self.next_button = None
        pyxel.stop()
        self.scene = scenes[next_scene_id](self)

    def finish_game(self, cleared):
        self.game_cleared = cleared
        if not self._game_submitted:
            self._game_submitted = True
            self.ranking_service.submit(self.active_game_id, self.player.player_id,
                                        self.run_player_name, self.game_score)
            if self.play_mode == "attack" and self.active_game_id == GAME_IDS[-1]:
                self.ranking_service.submit("Attack", self.player.player_id,
                                            self.run_player_name, self.score_hud.value)
        if self.play_mode == "attack":
            # シーンもゲームのオブジェクトも維持し、更新だけを停止する。
            self.attack_finished = True
            last_game = self.active_game_id == GAME_IDS[-1]
            label = "リザルトへ" if last_game else "次のミニゲームへ"
            self.next_button = Button(label, (100, 210, 240, 28))
            pyxel.mouse(True)
            return None
        return "Result"

    def add_score(self, amount, *, bonus=False):
        """点数は即時に確定し、表示の加算演出を順番に予約する。"""
        self.score_hud.add(amount)
        self.game_score += amount
        if self.active_game_id in self.game_scores:
            part = "bonus" if bonus else "base"
            self.game_scores[self.active_game_id][part] += amount

    def set_player_name(self, name):
        try:
            self.player.set_name(name)
        except ValueError:
            self.name_error = "名前を１〜16文字で入力してください"
            return False
        except OSError:
            self.name_error = "名前を保存できませんでした"
            return False
        self.name_error = ""
        return True

    def update(self):
        self.ranking_service.poll()
        self.score_hud.update()
        if self.attack_finished:
            if self.next_button.clicked():
                target = "Result" if self.active_game_id == GAME_IDS[-1] else "NextGame"
                self.change_scene(target)
            return
        next_scene = self.scene.update()
        if next_scene is not None:
            self.change_scene(next_scene)

    def draw(self):
        self.scene.draw()
        if self.attack_finished:
            self.next_button.draw(self.scene.font10)


if __name__ == "__main__":
    App()
