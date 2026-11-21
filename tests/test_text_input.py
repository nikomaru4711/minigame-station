import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from text_input import append_digits, configure_ime, ime_composing


class TextInputTests(unittest.TestCase):
    def test_sdl_renders_ime_composition_and_candidates(self):
        with patch.dict(os.environ, {}, clear=True):
            configure_ime()
            self.assertEqual(os.environ["SDL_IME_SHOW_UI"], "1")
            self.assertEqual(os.environ["SDL_IME_INTERNAL_EDITING"], "1")

    def test_fullwidth_and_halfwidth_digits_can_alternate(self):
        text = ""
        for committed in ("1", "２", "", "3"):
            text = append_digits(text, committed, 3)
        self.assertEqual(text, "123")

    def test_committed_batch_respects_limit_and_ignores_non_digits(self):
        self.assertEqual(append_digits("", "１２あ３４５", 3), "123")
        self.assertEqual(append_digits("12", "３４", 3), "123")
        self.assertEqual(append_digits("", "〇一二", 3), "")

    def test_leading_zero_behavior_is_preserved(self):
        self.assertEqual(append_digits("", "００５", 3), "5")
        self.assertEqual(append_digits("0", "１２", 3), "12")
        self.assertEqual(append_digits("", "０", 3), "0")

    def test_windows_composition_guard_releases_context(self):
        user32, imm32 = Mock(), Mock()
        user32.GetFocus.return_value = 10
        imm32.ImmGetContext.return_value = 20
        with patch("text_input.sys.platform", "win32"), \
                patch("text_input._windows_ime", return_value=(user32, imm32)):
            for size in (8, 0, -1):
                imm32.ImmGetCompositionStringW.return_value = size
                self.assertEqual(ime_composing(), size > 0)
        self.assertEqual(imm32.ImmReleaseContext.call_count, 3)

    def test_other_platforms_use_normal_committed_input(self):
        with patch("text_input.sys.platform", "linux"):
            self.assertFalse(ime_composing())


if __name__ == "__main__":
    unittest.main()
