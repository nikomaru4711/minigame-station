import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyxel
from main import App
from setting import Settings


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyxel.init(440, 250, title="Navigation tests", fps=60)

    def setUp(self):
        for i in range(4):
            pyxel.channels[i].gain = 0.125
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.settings = Settings(Path(self.temporary.name) / "settings.json")
        with patch("main.Settings", return_value=self.settings), \
                patch.object(pyxel, "init"), patch.object(pyxel, "run"):
            self.app = App()

    def click(self, button):
        x, y, _, _ = button.area
        with patch.object(pyxel, "mouse_x", x + 1), \
                patch.object(pyxel, "mouse_y", y + 1), \
                patch.object(pyxel, "btnp", return_value=True):
            self.app.update()

    def finish(self, success):
        target = self.app.finish_game(success)
        if target is not None:
            self.app.change_scene(target)

    def test_title_buttons_and_individual_game(self):
        self.assertEqual(len(self.app.scene.buttons), 4)
        self.click(self.app.scene.buttons[1][0])
        self.assertEqual(self.app.current_scene_id, "GameSelect")
        self.click(self.app.scene.buttons[2][0])
        self.assertEqual(self.app.current_scene_id, "Game03")
        self.assertEqual(self.app.play_mode, "single")
        self.finish(True)
        self.assertEqual([target for _, target in self.app.scene.buttons], ["Title"])
        self.click(self.app.scene.buttons[0][0])
        self.assertEqual(self.app.current_scene_id, "Title")

    def test_attack_advances_after_failure_or_success(self):
        for success in (False, True):
            with self.subTest(success=success):
                self.click(self.app.scene.buttons[0][0])
                for game_id in ("Game01", "Game02", "Game03"):
                    self.assertEqual(self.app.current_scene_id, game_id)
                    self.assertEqual(self.app.play_mode, "attack")
                    game = self.app.scene
                    self.finish(success)
                    self.assertIs(self.app.scene, game)
                    self.assertEqual(self.app.current_scene_id, game_id)
                    self.assertTrue(self.app.attack_finished)
                    with patch.object(game, "update") as update:
                        self.app.update()
                        update.assert_not_called()
                    self.assertEqual(self.app.next_button.area[1], 210)
                    if game_id == "Game03":
                        self.assertEqual(self.app.next_button.label, "リザルトへ")
                    self.click(self.app.next_button)
                self.assertEqual(self.app.current_scene_id, "Result")
                self.assertEqual(self.app.play_mode, "attack")
                self.assertEqual(self.app.scene.heading, "リザルト")
                self.assertEqual([target for _, target in self.app.scene.buttons], ["Title"])
                self.app.draw()
                self.click(self.app.scene.buttons[0][0])
                self.assertEqual(self.app.current_scene_id, "Title")
                self.assertEqual(self.app.play_mode, "single")

    def test_attack_terminal_states_keep_game_scene_and_enable_button(self):
        self.app.change_scene("Attack")
        for game_id in ("Game01", "Game03"):
            for state in ("GAMEOVER", "CLEAR"):
                self.app.change_scene(game_id)
                game = self.app.scene
                game.state = state
                self.app.update()
                self.assertIs(self.app.scene, game)
                self.assertEqual(self.app.current_scene_id, game_id)
                self.assertTrue(self.app.attack_finished)
                self.assertEqual(self.app.game_cleared, state == "CLEAR")
                with patch.object(pyxel, "text") as text:
                    self.app.draw()
                labels = [call.args[2] for call in text.call_args_list]
                self.assertNotIn("GAME OVER", labels)
                self.assertNotIn("CLEAR!", labels)

    def test_attack_game02_keeps_completed_answer_on_screen(self):
        self.app.change_scene("Attack")
        self.app.change_scene("Game02")
        game = self.app.scene
        game.state = "RESULT"
        game.current_house_pos = (220, -84)
        game.answer_count = 0
        game.user_answer = 1
        game.time = 180
        self.app.update()
        self.assertIs(self.app.scene, game)
        self.assertTrue(self.app.attack_finished)
        time = game.time
        for _ in range(5):
            self.app.update()
            self.app.draw()
        self.assertEqual(game.time, time)
        self.click(self.app.next_button)
        self.assertEqual(self.app.current_scene_id, "Game03")

    def test_attack_waits_for_score_animation_and_carries_total(self):
        self.app.change_scene("Attack")
        self.app.add_score(120)
        self.finish(False)
        self.click(self.app.next_button)
        self.assertEqual(self.app.current_scene_id, "Game01")
        while self.app.score_hud.animating:
            self.app.update()
        self.assertEqual(self.app.score_hud.value, 120)
        self.click(self.app.next_button)
        self.assertEqual(self.app.current_scene_id, "Game02")
        self.assertEqual(self.app.score_hud.value, 120)
        self.finish(True)
        self.click(self.app.next_button)
        self.assertEqual(self.app.current_scene_id, "Game03")
        self.finish(False)
        self.click(self.app.next_button)
        self.assertEqual(self.app.current_scene_id, "Result")
        self.assertEqual(self.app.score_hud.value, 120)
        self.assertFalse(self.app.attack_finished)
        self.click(self.app.scene.buttons[0][0])
        self.app.change_scene("Attack")
        self.assertIsNone(self.app.score_hud.value)

    def test_score_fades_in_then_merges_then_counts_up_in_order(self):
        hud = self.app.score_hud
        self.assertIsNone(hud.display_value)
        self.app.add_score(100)
        self.app.add_score(25)
        self.assertEqual(hud.display_value, 0)
        for _ in range(hud.ENTER_FRAMES // 2):
            hud.update()
        dx, dy, opacity = hud.bonus_pose()
        self.assertGreater(dx, 0)
        self.assertGreater(dy, 0)
        self.assertGreater(opacity, 0)
        self.assertLess(opacity, 1)
        for _ in range(hud.ENTER_FRAMES // 2):
            hud.update()
        self.assertEqual(hud.bonus_pose(), (0, 14, 1))
        for _ in range(hud.MERGE_FRAMES):
            hud.update()
        self.assertEqual(hud.bonus_pose(), (0, 0, 1))
        self.assertEqual(hud.display_value, 0)
        hud.update()
        self.assertGreater(hud.display_value, 0)
        self.assertLess(hud.display_value, 100)
        previous = hud.display_value
        while hud.animating:
            hud.update()
            self.assertGreaterEqual(hud.display_value, previous)
            previous = hud.display_value
        self.assertEqual(hud.value, 125)
        self.assertEqual(hud.display_value, 125)

    def test_score_drawing_is_static_and_under_boss_bar(self):
        self.app.change_scene("Game03")
        self.app.add_score(10)
        self.app.score_hud.update()
        frame = self.app.score_hud.frame
        with patch.object(pyxel, "text") as text:
            self.app.draw()
            self.app.draw()
        scores = [call for call in text.call_args_list if call.args[2].startswith("スコア ")]
        self.assertEqual(len(scores), 2)
        self.assertTrue(all(call.args[1] == 24 for call in scores))
        self.assertEqual(self.app.score_hud.frame, frame)
        self.app.change_scene("Game01")
        self.assertIsNone(self.app.score_hud.value)

    def test_single_game_can_retry_after_failure(self):
        for game_id in ("Game01", "Game02", "Game03"):
            with self.subTest(game_id=game_id):
                self.app.change_scene(game_id)
                old_game = self.app.scene
                self.finish(False)
                self.assertEqual([target for _, target in self.app.scene.buttons], ["Retry", "Title"])
                self.click(self.app.scene.buttons[0][0])
                self.assertEqual(self.app.current_scene_id, game_id)
                self.assertIsNot(self.app.scene, old_game)
                self.assertEqual(self.app.play_mode, "single")

    def test_game01_and_game03_report_clear_and_failure(self):
        for game_id in ("Game01", "Game03"):
            for state in ("CLEAR", "GAMEOVER"):
                self.app.change_scene(game_id)
                self.app.scene.state = state
                self.app.update()
                self.assertEqual(self.app.current_scene_id, "Result")
                self.assertEqual(self.app.game_cleared, state == "CLEAR")

    def test_game02_waits_for_answer_animation_including_zero(self):
        for correct in (False, True):
            self.app.change_scene("Game02")
            game = self.app.scene
            game.state = "RESULT"
            game.current_house_pos = (220, -84)
            game.answer_count = 0
            game.user_answer = 0 if correct else 1
            game.time = 0
            for _ in range(180):
                self.app.update()
            self.assertEqual(self.app.current_scene_id, "Game02")
            self.app.update()
            self.assertEqual(self.app.current_scene_id, "Result")
            self.assertEqual(self.app.game_cleared, correct)

    def test_game02_waits_until_last_character_and_drawing_does_not_advance_timer(self):
        self.app.change_scene("Game02")
        game = self.app.scene
        game.state = "RESULT"
        game.current_house_pos = (220, -84)
        game.answer_count = game.user_answer = 1
        game.wotu_list = [{"timer": 0, "delay": 4, "duration": 20,
                           "sx": 200, "sy": 120, "tx": 40, "ty": 140,
                           "x": 200, "y": 120}]
        for _ in range(4):
            self.app.update()
        self.assertEqual(game.time, 0)
        for _ in range(180):
            self.app.update()
            self.app.draw()
            self.app.draw()
        self.assertEqual(game.time, 180)
        self.assertEqual(self.app.current_scene_id, "Game02")
        self.app.update()
        self.assertEqual(self.app.current_scene_id, "Result")
        self.assertTrue(self.app.game_cleared)

    def test_rankings_top_five_and_placeholders(self):
        self.app.change_scene("Score")
        with patch.object(pyxel, "text") as text:
            self.app.draw()
        self.assertEqual(sum(call.args[2] == "---" for call in text.call_args_list), 10)
        self.app.rankings["Attack"] = [
            {"name": f"User{i}", "score": i * 10} for i in range(7)
        ]
        with patch.object(pyxel, "text") as text:
            self.app.draw()
        names = [call.args[2] for call in text.call_args_list if call.args[0] == 105]
        self.assertEqual(names, ["User6", "User5", "User4", "User3", "User2"])
        self.app.rankings["Attack"] = self.app.rankings["Attack"][:2]
        with patch.object(pyxel, "text") as text:
            self.app.draw()
        self.assertEqual(sum(call.args[2] == "---" for call in text.call_args_list), 6)
        for expected in (1, 2, 3, 0):
            self.click(self.app.scene.next)
            self.assertEqual(self.app.scene.category, expected)

    def test_settings_save_reload_and_independent_channel_gains(self):
        self.app.change_scene("Settings")
        bgm_minus = self.app.scene.controls[0][1]
        se_minus = self.app.scene.controls[1][1]
        for _ in range(15):
            self.click(bgm_minus)
        self.assertEqual(self.settings.bgm_volume, 0)
        self.assertEqual(self.settings.se_volume, 1)
        self.assertEqual(pyxel.channels[2].gain, 0)
        self.assertGreater(pyxel.channels[0].gain, 0)
        self.click(se_minus)
        reloaded = Settings(self.settings.path)
        self.assertEqual(reloaded.bgm_volume, 0)
        self.assertEqual(reloaded.se_volume, 0.9)
        self.click(self.app.scene.back)
        self.assertEqual(self.app.current_scene_id, "Title")

    def test_bad_settings_fall_back_to_defaults(self):
        for contents in ("{", "[]", json.dumps({"bgm_volume": -1, "se_volume": "bad"})):
            self.settings.path.write_text(contents, encoding="utf-8")
            settings = Settings(self.settings.path)
            self.assertEqual((settings.bgm_volume, settings.se_volume), (1, 1))

    def test_settings_save_error_keeps_screen_open(self):
        self.app.change_scene("Settings")
        with patch.object(self.settings, "save", side_effect=OSError("read only")):
            self.click(self.app.scene.back)
        self.assertEqual(self.app.current_scene_id, "Settings")
        self.assertTrue(self.app.scene.error)


if __name__ == "__main__":
    unittest.main()
