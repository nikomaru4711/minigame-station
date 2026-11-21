import pyxel


class Audio:
    """SEは0・1、BGMは2・3チャンネルを使用する。音源は作成しない。"""

    def __init__(self, settings):
        self.settings = settings
        self.base_gains = [pyxel.channels[i].gain for i in range(4)]
        self.apply_volumes()

    def apply_volumes(self):
        for i, gain in enumerate(self.base_gains):
            volume = self.settings.se_volume if i < 2 else self.settings.bgm_volume
            pyxel.channels[i].gain = gain * volume

    def play_se(self, channel, sound):
        if channel not in (0, 1):
            raise ValueError("SE channel must be 0 or 1")
        pyxel.play(channel, sound)

    def play_bgm(self, sound, channel=2, loop=True):
        if channel not in (2, 3):
            raise ValueError("BGM channel must be 2 or 3")
        pyxel.play(channel, sound, loop=loop)
