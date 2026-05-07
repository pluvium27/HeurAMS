"""Kernel 操作辅助函数库"""

import heurams.interface.widgets as pzw
import heurams.kernel.puzzles as pz
import platform
import os
from heurams.context import config_var

puzzle2widget = {
    pz.RecognitionPuzzle: pzw.Recognition,
    pz.ClozePuzzle: pzw.ClozePuzzle,
    pz.MCQPuzzle: pzw.MCQPuzzle,
    pz.BasePuzzle: pzw.BasePuzzleWidget,
}


def set_term_title(title):
    if not config_var.get()["interface"]["global"]["change_window_title"]:
        return
    system = platform.system()
    if system == "Windows":
        os.system(f"title {title}")
    else:  # Linux, Mac, etc.
        os.write(2, f"\033]2;{title}\007".encode("utf-8"))
