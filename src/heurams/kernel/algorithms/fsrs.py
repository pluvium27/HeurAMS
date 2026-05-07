"""
FSRS 算法模块 — 基于 py-fsrs 的现代间隔重复调度器

基于: https://github.com/open-spaced-repetition/py-fsrs
"""
import json
import os
import pathlib
from datetime import datetime, timezone, timedelta
from typing import TypedDict

from fsrs import Scheduler, Card, Rating

from heurams.context import config_var
from heurams.services.logger import get_logger
from heurams.services.timer import get_daystamp, get_timestamp

from .base import BaseAlgorithm

logger = get_logger(__name__)

# 全局 Scheduler 状态文件路径
_SCHEDULER_STATE_FILE = pathlib.Path(
    config_var.get()["global"]["paths"]["misc"]
) / "fsrs_scheduler_state.json"


def _get_global_scheduler():
    """获取全局 FSRS Scheduler 实例, 从文件加载或创建新的"""
    if os.path.exists(_SCHEDULER_STATE_FILE):
        try:
            with open(_SCHEDULER_STATE_FILE, "r", encoding="utf-8") as f:
                return Scheduler.from_json(f.read())
        except Exception:
            logger.warning("FSRS Scheduler 状态文件加载失败, 创建新实例")
    return Scheduler()


def _save_global_scheduler(scheduler):
    """保存全局 FSRS Scheduler 实例到文件"""
    try:
        _SCHEDULER_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = scheduler.to_json()
        with open(_SCHEDULER_STATE_FILE, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception:
        logger.exception("FSRS Scheduler 状态保存失败")


def _feedback_to_rating(feedback: int) -> Rating:
    """将 SM-2 风格 feedback (0-5) 映射为 FSRS Rating (1-4)"""
    if feedback <= 2:
        return Rating.Again
    elif feedback == 3:
        return Rating.Hard
    elif feedback == 4:
        return Rating.Good
    else:
        return Rating.Easy


def _datetime_to_daystamp(dt: datetime) -> int:
    """将 datetime 转换为天数戳（从 1970-01-01）"""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = dt - epoch
    return delta.days


def _daystamp_to_datetime(daystamp: int) -> datetime:
    """将天数戳转换为 UTC datetime"""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return epoch + timedelta(days=daystamp)


class FSRSAlgorithm(BaseAlgorithm):
    algo_name = "FSRS"
    desc = "基于 py-fsrs 的现代间隔重复调度器"

    class AlgodataDict(TypedDict):
        # FSRS 特有字段
        fsrs_state: int        # State 枚举值: 1=Learning, 2=Review, 3=Relearning
        fsrs_step: int         # 当前学习步进索引, -1 表示 None (Review 状态)
        fsrs_stability: float  # 稳定性（秒）, 0.0 表示尚未计算
        fsrs_difficulty: float # 难度 [1.0, 10.0], 0.0 表示尚未计算
        # 标准 BaseAlgorithm 兼容字段
        real_rept: int
        rept: int
        interval: int
        last_date: int
        next_date: int
        is_activated: int
        last_modify: float

    defaults = {
        "fsrs_state": 1,          # State.Learning
        "fsrs_step": 0,
        "fsrs_stability": 0.0,
        "fsrs_difficulty": 0.0,
        "real_rept": 0,
        "rept": 0,
        "interval": 0,
        "last_date": 0,
        "next_date": 0,
        "is_activated": 0,
        "last_modify": get_timestamp(),
    }

    @classmethod
    def _algodata_to_card(cls, algodata):
        """从 algodata 恢复 Card 实例"""
        data = algodata.get(cls.algo_name, cls.defaults.copy())

        card = Card()

        # State: int → IntEnum
        card.state = data.get("fsrs_state", 1)

        # Step: -1 表示 None（Review 状态下的 card.step 为 None）
        step = data.get("fsrs_step", -1)
        card.step = None if step == -1 else step

        # Stability: 0.0 表示尚未计算（新卡片）
        stability = data.get("fsrs_stability", 0.0)
        card.stability = None if stability == 0.0 else stability

        # Difficulty: 0.0 表示尚未计算
        difficulty = data.get("fsrs_difficulty", 0.0)
        card.difficulty = None if difficulty == 0.0 else difficulty

        # due: 新卡片(next_date ≤ 0)设为当前时间
        next_date = data.get("next_date", 0)
        if next_date <= 0:
            card.due = datetime.now(timezone.utc)
        else:
            card.due = _daystamp_to_datetime(next_date)

        # last_review
        last_date = data.get("last_date", 0)
        card.last_review = (
            _daystamp_to_datetime(last_date) if last_date > 0 else None
        )

        return card

    @classmethod
    def _card_to_algodata(cls, card, algodata):
        """将 Card 实例状态写回 algodata"""
        if cls.algo_name not in algodata:
            algodata[cls.algo_name] = cls.defaults.copy()

        data = algodata[cls.algo_name]
        data["fsrs_state"] = int(card.state)
        data["fsrs_step"] = card.step if card.step is not None else -1
        data["fsrs_stability"] = card.stability if card.stability is not None else 0.0
        data["fsrs_difficulty"] = (
            card.difficulty if card.difficulty is not None else 0.0
        )
        data["last_date"] = (
            _datetime_to_daystamp(card.last_review)
            if card.last_review
            else data.get("last_date", 0)
        )
        data["next_date"] = (
            _datetime_to_daystamp(card.due) if card.due else 0
        )
        data["interval"] = max(0, data["next_date"] - data["last_date"])
        data["last_modify"] = get_timestamp()
        return algodata

    @classmethod
    def revisor(
        cls, algodata: dict, feedback: int = 5, is_new_activation: bool = False
    ):
        """FSRS 算法迭代决策机制实现

        将 feedback (0-5) 映射为 FSRS Rating 后交由 py-fsrs 调度器处理。

        Args:
            feedback (int): 0-5 的记忆保留率量化参数
            is_new_activation: 是否为全新激活（重置为初始状态）
        """
        logger.debug(
            "FSRS.revisor 开始, feedback: %d, is_new_activation: %s",
            feedback,
            is_new_activation,
        )

        if feedback == -1:
            logger.debug("feedback 为 -1, 跳过更新")
            return

        scheduler = _get_global_scheduler()
        rating = _feedback_to_rating(feedback)

        if is_new_activation:
            card = Card()
            logger.debug("新激活, 创建新 Card")
        else:
            card = cls._algodata_to_card(algodata)

        card, review_log = scheduler.review_card(card, rating)
        _save_global_scheduler(scheduler)

        cls._card_to_algodata(card, algodata)
        # real_rept: 总复习次数
        algodata[cls.algo_name]["real_rept"] += 1
        # rept: 成功回忆次数（feedback ≥ 3 视为成功）
        if feedback >= 3:
            algodata[cls.algo_name]["rept"] += 1

        logger.debug(
            "FSRS.revisor 完成: stability=%s, difficulty=%s, state=%s, "
            "next_date=%d",
            card.stability,
            card.difficulty,
            card.state,
            algodata[cls.algo_name]["next_date"],
        )

    @classmethod
    def is_due(cls, algodata):
        data = algodata.get(cls.algo_name, cls.defaults.copy())
        next_date = data.get("next_date", 0)
        current = get_daystamp()
        result = next_date <= current
        logger.debug(
            "FSRS.is_due: next_date=%d, current=%d, result=%s",
            next_date,
            current,
            result,
        )
        return result

    @classmethod
    def get_rating(cls, algodata):
        data = algodata.get(cls.algo_name, cls.defaults.copy())
        difficulty = data.get("fsrs_difficulty", 0.0)
        logger.debug("FSRS.get_rating: difficulty=%f", difficulty)
        return str(difficulty)

    @classmethod
    def nextdate(cls, algodata) -> int:
        data = algodata.get(cls.algo_name, cls.defaults.copy())
        next_date = data.get("next_date", 0)
        logger.debug("FSRS.nextdate: %d", next_date)
        return next_date
