import pyxel
from ui import MenuScene
from game_select import GAME_IDS
from attack_breakdown import AttackBreakdown


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
        self.breakdown = AttackBreakdown(app.game_scores) if attack else None
        for i, (button, _) in enumerate(self.buttons):
            button.area = (100, 210 - (len(self.buttons) - 1 - i) * 36, 240, 28)

    def update(self):
        if self.breakdown is not None:
            self.breakdown.update()
        return super().update()

    def draw(self):
        super().draw()
        if self.breakdown is not None:
            self.breakdown.draw(self.font10, self.font20)
        else:
            self.app.score_hud.draw()
        category = "Attack" if self.app.play_mode == "attack" else self.app.active_game_id
        status = self.app.ranking_service.status.get(category, "")
        if status:
            pyxel.text(30, 192 if self.breakdown is not None else 151, status, 6, self.font10)
