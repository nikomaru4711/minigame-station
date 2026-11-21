from ui import MenuScene


GAME_NAMES = ("イライラ棒", "ヲツかぞえ", "ヲツベーダー")
GAME_IDS = ("Game01", "Game02", "Game03")


class GameSelectScene(MenuScene):
    def __init__(self, app):
        super().__init__(app, "ミニゲームをプレイ", [
            *zip(GAME_NAMES, GAME_IDS),
            ("タイトルに戻る", "Title"),
        ])
