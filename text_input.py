"""IMEの確定文字を共通で扱う。キー押下と文字入力を重ねて数えない。"""

import os
import sys
from functools import lru_cache


def configure_ime():
    # Pyxelは未確定文字(SDL_TEXTEDITING)を公開しないため、変換中の表示は
    # OSのIMEに任せる。SDL初期化より前に指定する必要がある。
    os.environ["SDL_IME_SHOW_UI"] = "1"
    os.environ["SDL_IME_INTERNAL_EDITING"] = "1"


def append_digits(current, committed, max_digits):
    translation = str.maketrans("０１２３４５６７８９", "0123456789")
    for character in committed.translate(translation):
        if character not in "0123456789":
            continue
        if current == "0":
            current = character
        elif len(current) < max_digits:
            current += character
    return current


@lru_cache(maxsize=1)
def _windows_ime():
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32")
    imm32 = ctypes.WinDLL("imm32")
    user32.GetFocus.restype = wintypes.HWND
    imm32.ImmGetContext.argtypes = [wintypes.HWND]
    imm32.ImmGetContext.restype = wintypes.HANDLE
    imm32.ImmGetCompositionStringW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                              ctypes.c_void_p, wintypes.DWORD]
    imm32.ImmGetCompositionStringW.restype = wintypes.LONG
    imm32.ImmReleaseContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
    return user32, imm32


def ime_composing():
    """変換中のBackspaceで、既に確定済みの入力を消さないための判定。"""
    if sys.platform != "win32":
        return False
    user32, imm32 = _windows_ime()
    window = user32.GetFocus()
    if not window:
        return False
    context = imm32.ImmGetContext(window)
    if not context:
        return False
    try:
        return imm32.ImmGetCompositionStringW(context, 8, None, 0) > 0  # GCS_COMPSTR
    finally:
        imm32.ImmReleaseContext(window, context)
