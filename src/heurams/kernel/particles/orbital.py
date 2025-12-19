from typing import TypedDict

from heurams.services.logger import get_logger

logger = get_logger(__name__)
logger.debug("Orbital 类型定义模块已加载")


class OrbitalSchedule(TypedDict):
    quick_review: list
    recognition: list
    final_review: list


class Orbital(TypedDict):
    schedule: OrbitalSchedule
    puzzles: dict


"""一份示例
["__metadata__.orbital.puzzles"] # 谜题定义
"Recognition" = { __origin__ = "recognition", __hint__ = "", primary = "eval:nucleon['content']", secondery = ["eval:nucleon['keyword_note']", "eval:nucleon['note']"], top_dim = ["eval:nucleon['translation']"] }
"SelectMeaning" = { __origin__ = "mcq", __hint__ = "eval:nucleon['content']", jammer = "eval:nucleon['keyword_note']", max_riddles_num = "eval:default['mcq']['max_riddles_num']", prefix = "选择正确项: " }
"FillBlank" = { __origin__ = "cloze", __hint__ = "", text = "eval:nucleon['content']", delimiter = "eval:metadata['formation']['delimiter']", min_denominator = "eval:default['cloze']['min_denominator']"}

["__metadata__.orbital.schedule"] # 内置的推荐学习方案
quick_review = [["FillBlank", "1.0"], ["SelectMeaning", "0.5"], ["recognition", "1.0"]]
recognition = [["recognition", "1.0"]]
final_review = [["FillBlank", "0.7"], ["SelectMeaning", "0.7"], ["recognition", "1.0"]]
"""
