"""Kernel 操作辅助函数库"""

import random
import heurams.kernel.particles as pt
import heurams.kernel.puzzles as pz
import heurams.interface.widgets as pzw
from typing import TypedDict

staging = {}  # 细粒度缓存区, 是 ident -> quality 的封装


def report_to_staging(atom: pt.Atom, quality):
    staging[atom.ident] = min(quality, staging[atom.ident])


def clear():
    staging = dict()


def deploy_to_electron():
    for atom_ident, quality in staging.items():
        if pt.atom_registry[atom_ident].registry["electron"].is_activated:
            pt.atom_registry[atom_ident].registry["electron"].revisor(quality=quality)
        else:
            pt.atom_registry[atom_ident].registry["electron"].revisor(
                quality=quality, is_new_activation=True
            )
    clear()


puzzle2widget = {
    pz.RecognitionPuzzle: pzw.Recognition,
    pz.ClozePuzzle: pzw.ClozePuzzle,
    pz.MCQPuzzle: pzw.MCQPuzzle,
    pz.BasePuzzle: pzw.BasePuzzleWidget,
}
