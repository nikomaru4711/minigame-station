from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from attack_breakdown import AttackBreakdown


class AttackBreakdownTests(unittest.TestCase):
    def setUp(self):
        self.scores = {"Game01": {"base": 200, "bonus": 428},
                       "Game02": {"base": 150, "bonus": 0},
                       "Game03": {"base": 200, "bonus": 25}}
        self.view = AttackBreakdown(self.scores)

    def advance(self, frames):
        for _ in range(frames):
            self.view.update()

    def test_base_and_bonus_animate_separately_in_game_order(self):
        self.assertEqual(self.view.display_total, 0)
        self.advance(15)
        self.assertGreater(self.view.shown(0, 0), 0)
        self.assertLess(self.view.shown(0, 0), 200)
        self.assertEqual(self.view.shown(0, 1), 0)
        self.advance(15)
        self.assertEqual(self.view.shown(0, 0), 200)
        self.assertEqual(self.view.shown(0, 1), 0)
        self.advance(15)
        self.assertGreater(self.view.shown(0, 1), 0)
        self.assertEqual(self.view.shown(1, 0), 0)
        self.advance(15)
        self.assertEqual(self.view.display_total, 628)
        self.advance(60)
        self.assertEqual(self.view.display_total, 778)
        self.advance(60)
        self.assertEqual(self.view.display_total, 1003)

    def test_total_is_monotonic_and_final_values_do_not_change(self):
        previous = 0
        for _ in range(220):
            self.view.update()
            self.assertGreaterEqual(self.view.display_total, previous)
            self.assertLessEqual(self.view.display_total, 1003)
            previous = self.view.display_total
        self.assertEqual(self.view.frame, 180)
        self.assertEqual(self.view.display_total, 1003)

    def test_score_snapshot_and_replay_are_independent_from_confirmed_scores(self):
        self.advance(180)
        replay = AttackBreakdown(self.scores)
        self.assertEqual(replay.display_total, 0)
        self.scores["Game01"]["base"] = 0
        self.assertEqual(self.view.display_total, 1003)
        self.assertEqual(replay.scores[0], (200, 428))

    def test_all_zero_results_finish_without_negative_values(self):
        view = AttackBreakdown({key: {"base": 0, "bonus": 0} for key in self.scores})
        for _ in range(180):
            view.update()
            self.assertEqual(view.display_total, 0)


if __name__ == "__main__":
    unittest.main()
