"""Kernel 操作辅助函数库"""

import heurams.interface.widgets as pzw
import heurams.kernel.evaluators as pz

puzzle2widget = {
    pz.RecognitionPuzzle: pzw.Recognition,
    pz.ClozePuzzle: pzw.ClozePuzzle,
    pz.MCQPuzzle: pzw.MCQPuzzle,
    pz.BaseEvaluator: pzw.BasePuzzleWidget,
}
