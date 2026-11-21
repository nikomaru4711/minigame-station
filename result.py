import pyxel
from ui import MenuScene
from game_select import GAME_IDS


class ResultScene(MenuScene):
    """加点演出中も操作できる終了メニュー。"""

    def __init__(self, app):
        attack = app.play_mode == "attack"
        has_next = attack and app.active_game_id != GAME_IDS[-1]
        if attack:
            if has_next:
                heading = "クリア！" if app.game_cleared else "ゲーム終了"
                choices = [("次のミニゲームへ", "NextGame")]
            else:
                heading = "リザルト"
                choices = [("タイトルに戻る", "Title")]
        elif not app.game_cleared:
            heading = "もう一度挑戦！"
            choices = [("もう一度プレイ", "Retry"), ("タイトルに戻る", "Title")]
        else:
            heading = "クリア！"
            choices = [("タイトルに戻る", "Title")]
        super().__init__(app, heading, choices)
        for i, (button, _) in enumerate(self.buttons):
            button.area = (100, 210 - (len(self.buttons) - 1 - i) * 36, 240, 28)

    def draw(self):
        super().draw()
        if self.app.play_mode == "attack":
            index = GAME_IDS.index(self.app.active_game_id) + 1
            pyxel.text(170, 85, f"ミニゲーム {index} / 3", 7, self.font10)
