from ui import MenuScene


class TitleScene(MenuScene):
    def __init__(self, app):
        super().__init__(app, "Minigame Station", [
            ("ミニゲームアタックをプレイ", "Attack"),
            ("ミニゲームをプレイ", "GameSelect"),
            ("スコア", "Score"),
            ("設定", "Settings"),
        ])
