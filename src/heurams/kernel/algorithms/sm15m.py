"""
SM-15M — 基于 sm.js 的间隔重复算法

基于: https://github.com/slaypni/sm.js
原始 CoffeeScript (c) 2014 Kazuaki Tanida, MIT 许可证
"""

import datetime
import json
import math
import os
import pathlib
from typing import TypedDict

from heurams.context import config_var
from heurams.services.logger import get_logger
from heurams.services.timer import (
    get_daystamp,
    get_timestamp,
    get_timestamp_ms,
    daystamp_to_datetime,
    datetime_to_daystamp,
)

from .base import BaseAlgorithm

logger = get_logger(__name__)

# ============================================================================
# Constants
# ============================================================================

RANGE_AF = 20
RANGE_REPETITION = 20

MIN_AF = 1.2
NOTCH_AF = 0.3
MAX_AF = MIN_AF + NOTCH_AF * (RANGE_AF - 1)  # 6.9

MAX_GRADE = 5
THRESHOLD_RECALL = 3

# ============================================================================
# Math Helpers
# ============================================================================


def sum_values(values):
    return sum(values)


def exponential_regression(points):
    """y = a * exp(b * x)"""
    n = len(points)
    X = [p[0] for p in points]
    Y = [p[1] for p in points]
    logY = [math.log(y) for y in Y]
    sqX = [x * x for x in X]

    sum_logY = sum(logY)
    sum_sqX = sum(sqX)
    sumX = sum(X)
    sumX_logY = sum(X[i] * logY[i] for i in range(n))
    sq_sumX = sumX * sumX

    denom = n * sum_sqX - sq_sumX
    a_coeff = (sum_logY * sum_sqX - sumX * sumX_logY) / denom if denom else 0
    b_coeff = (n * sumX_logY - sumX * sum_logY) / denom if denom else 0

    a = math.exp(a_coeff)

    def y_func(x):
        return a * math.exp(b_coeff * x)

    def x_func(y):
        if b_coeff == 0:
            return 0
        return (-a_coeff + math.log(y)) / b_coeff

    return {"y": y_func, "x": x_func, "a": a, "b": b_coeff}


def linear_regression(points):
    """y = a + b * x"""
    n = len(points)
    X = [p[0] for p in points]
    Y = [p[1] for p in points]

    sumX = sum(X)
    sumY = sum(Y)
    sumXY = sum(X[i] * Y[i] for i in range(n))
    sum_sqX = sum(x * x for x in X)
    sq_sumX = sumX * sumX

    denom = n * sum_sqX - sq_sumX
    a = (sumY * sum_sqX - sumX * sumXY) / denom if denom else 0
    b = (n * sumXY - sumX * sumY) / denom if denom else 0

    def y_func(x):
        return a + b * x

    def x_func(y):
        if b == 0:
            return 0
        return (y - a) / b

    return {"y": y_func, "x": x_func, "a": a, "b": b}


def power_law_model(a, b):
    """y = a * x^b"""

    def y_func(x):
        return a * (x**b)

    def x_func(y):
        if a == 0 or b == 0:
            return 0
        return (y / a) ** (1.0 / b)

    return {"y": y_func, "x": x_func, "a": a, "b": b}


def fixed_point_power_law_regression(points, fixed_point):
    """y = q * (x/p)^b, through fixed point (p, q)"""
    n = len(points)
    p, q = fixed_point
    log_q = math.log(q)

    X = [math.log(point[0] / p) for point in points]
    Y = [math.log(point[1]) - log_q for point in points]

    sumXY = sum(X[i] * Y[i] for i in range(n))
    sum_sqX = sum(x * x for x in X)
    b = sumXY / sum_sqX if sum_sqX else 0

    return power_law_model(q / (p**b), b)


# ============================================================================
# FI-G Grade Graph
# ============================================================================


class FI_G:
    """Forgetting Index — Grade graph (exponential regression)."""

    MAX_POINTS_COUNT = 5000
    GRADE_OFFSET = 1

    def __init__(self, sm, points=None):
        self.sm = sm
        self._graph = None
        if points is not None:
            self.points = points
        else:
            self.points = []
            self._register_point(0, MAX_GRADE)
            self._register_point(100, 0)

    def _register_point(self, fi, grade):
        self.points.append([fi, grade + self.GRADE_OFFSET])
        if len(self.points) > self.MAX_POINTS_COUNT:
            self.points = self.points[-self.MAX_POINTS_COUNT :]
        self._graph = None

    def update(self, grade, item, now):
        def expected_fi():
            return (item.uf(now) / item.of) * self.sm.requested_fi

        self._register_point(expected_fi(), grade)

    def fi(self, grade):
        if not self.points:
            return 50.0
        if self._graph is None:
            self._graph = exponential_regression(self.points)
        return max(0.0, min(100.0, self._graph["x"](grade + self.GRADE_OFFSET)))

    def data(self):
        return {"points": self.points}

    @classmethod
    def load(cls, sm, data):
        return cls(sm, data.get("points"))


# ============================================================================
# Forgetting Curve (single cell)
# ============================================================================


class ForgettingCurve:
    MAX_POINTS_COUNT = 500
    FORGOTTEN = 1
    REMEMBERED = 100 + FORGOTTEN  # 101

    def __init__(self, points):
        self.points = points
        self._curve = None

    def register_point(self, grade, uf):
        is_remembered = grade >= THRESHOLD_RECALL
        self.points.append([uf, self.REMEMBERED if is_remembered else self.FORGOTTEN])
        if len(self.points) > self.MAX_POINTS_COUNT:
            self.points = self.points[-self.MAX_POINTS_COUNT :]
        self._curve = None

    def retention(self, uf):
        if not self.points:
            return 50.0
        if self._curve is None:
            self._curve = exponential_regression(self.points)
        clamped = max(self.FORGOTTEN, min(self._curve["y"](uf), self.REMEMBERED))
        return clamped - self.FORGOTTEN

    def uf(self, retention):
        if not self.points:
            return 1.0
        if self._curve is None:
            self._curve = exponential_regression(self.points)
        return max(0.0, self._curve["x"](retention + self.FORGOTTEN))


# ============================================================================
# Forgetting Curves Matrix (repetition × af)
# ============================================================================


class ForgettingCurves:
    FORGOTTEN = 1
    REMEMBERED = 100 + FORGOTTEN

    def __init__(self, sm, points=None):
        self.sm = sm
        self.curves = []
        for r in range(RANGE_REPETITION):
            row = []
            for a in range(RANGE_AF):
                if points is not None:
                    partial = points[r][a]
                else:
                    if r > 0:
                        pts = []
                        for i in range(21):
                            v = MIN_AF + NOTCH_AF * i
                            y = math.exp(
                                -(r + 1) / 200 * (i - a * math.sqrt(2.0 / (r + 1)))
                            ) * (self.REMEMBERED - self.sm.requested_fi)
                            pts.append([v, min(self.REMEMBERED, y)])
                        partial = [[0, self.REMEMBERED]] + pts
                    else:
                        pts = []
                        for i in range(21):
                            v = MIN_AF + NOTCH_AF * i
                            y = math.exp(-1.0 / (10 + 1 * (a + 1)) * (i - a**0.6)) * (
                                self.REMEMBERED - self.sm.requested_fi
                            )
                            pts.append([v, min(self.REMEMBERED, y)])
                        partial = [[0, self.REMEMBERED]] + pts
                row.append(ForgettingCurve(partial))
            self.curves.append(row)

    def register_point(self, grade, item, now):
        af_index = item.af_index() if item.repetition > 0 else item.lapse
        self.curves[item.repetition][af_index].register_point(grade, item.uf(now))

    def data(self):
        return {
            "points": [
                [self.curves[r][a].points for a in range(RANGE_AF)]
                for r in range(RANGE_REPETITION)
            ]
        }

    @classmethod
    def load(cls, sm, data):
        return cls(sm, data.get("points"))


# ============================================================================
# R-Factor Matrix
# ============================================================================


class RFM:
    def __init__(self, sm):
        self.sm = sm

    def rf(self, repetition, af_index):
        return self.sm.forgetting_curves.curves[repetition][af_index].uf(
            100 - self.sm.requested_fi
        )


# ============================================================================
# O-Factor Matrix
# ============================================================================


class OFM:
    INITIAL_REP_VALUE = 1

    def __init__(self, sm):
        self.sm = sm
        self._ofm = None
        self._ofm0 = None
        self.update()

    def update(self):
        def af_from_index(a):
            return a * NOTCH_AF + MIN_AF

        def rep_from_index(r):
            return r + self.INITIAL_REP_VALUE

        # D-factors: power law decay along repetition axis
        dfs = []
        for a in range(RANGE_AF):
            pts = [
                [rep_from_index(r), self.sm.rfm.rf(r, a)]
                for r in range(1, RANGE_REPETITION)
            ]
            fp = [rep_from_index(1), af_from_index(a)]
            model = fixed_point_power_law_regression(pts, fp)
            dfs.append(model["b"])

        # Transform D-factors
        dfs_t = [af_from_index(a) / (2.0 ** dfs[a]) for a in range(RANGE_AF)]

        # Linear regression of D-factor by A-Factor index
        decay_pts = [[a, dfs_t[a]] for a in range(RANGE_AF)]
        decay = linear_regression(decay_pts)

        # Build O-Factor model per A-Factor
        ofm_list = []
        for a in range(RANGE_AF):
            af = af_from_index(a)
            d_y = decay["y"](a)
            b = math.log(af / d_y) / math.log(rep_from_index(1)) if d_y != 0 else 0
            model = power_law_model(af / (rep_from_index(1) ** b), b)

            def make_ofm_funcs(m):
                return {
                    "y": lambda r, m=m: m["y"](rep_from_index(r)),
                    "x": lambda y, m=m: m["x"](y) - self.INITIAL_REP_VALUE,
                }

            ofm_list.append(make_ofm_funcs(model))

        self._ofm = ofm_list

        # O-Factor for repetition 0
        ofm0_pts = [[a, self.sm.rfm.rf(0, a)] for a in range(RANGE_AF)]
        ofm0 = exponential_regression(ofm0_pts)
        self._ofm0 = lambda a: ofm0["y"](a)

    def of(self, repetition, af_index):
        if repetition == 0:
            return self._ofm0(af_index)
        return self._ofm[af_index]["y"](repetition)

    def af(self, repetition, of_val):
        for a in range(RANGE_AF):
            if abs(self.of(repetition, a) - of_val) < 1e-10:
                return a * NOTCH_AF + MIN_AF
        # Find closest
        best, best_a = float("inf"), 0
        for a in range(RANGE_AF):
            d = abs(self.of(repetition, a) - of_val)
            if d < best:
                best, best_a = d, a
        return best_a * NOTCH_AF + MIN_AF


# ============================================================================
# Item (per-card state)
# ============================================================================


class Item:
    MAX_AFS_COUNT = 30

    def __init__(self, sm, value=None):
        self.sm = sm
        self.value = value
        self.lapse = 0
        self.repetition = -1
        self.of = 1.0
        self.optimum_interval = sm.interval_base  # ms
        self.due_date = datetime.datetime(1970, 1, 1)
        self.previous_date = None
        self._afs = []
        self._af = None

    def interval(self, now=None):
        if now is None:
            now = datetime.datetime.now()
        if self.previous_date is None:
            return self.sm.interval_base
        return (now - self.previous_date).total_seconds() * 1000

    def uf(self, now=None):
        if now is None:
            now = datetime.datetime.now()
        adjusted = self.optimum_interval / self.of
        return self.interval(now) / adjusted if adjusted else 0

    def af(self, value=None):
        if value is None:
            return self._af
        a = round((value - MIN_AF) / NOTCH_AF)
        self._af = max(MIN_AF, min(MAX_AF, MIN_AF + a * NOTCH_AF))
        return self._af

    def af_index(self):
        target = self.af() if self._af is not None else MIN_AF
        best, best_i = float("inf"), 0
        for i in range(RANGE_AF):
            d = abs(target - (MIN_AF + i * NOTCH_AF))
            if d < best:
                best, best_i = d, i
        return best_i

    def _I(self, now=None):
        if now is None:
            now = datetime.datetime.now()
        af_idx = self.lapse if self.repetition == 0 else self.af_index()
        of_val = self.sm.ofm.of(self.repetition, af_idx)
        self.of = max(
            1.0, (of_val - 1) * (self.interval(now) / self.optimum_interval) + 1
        )
        self.optimum_interval = round(self.optimum_interval * self.of)
        self.previous_date = now
        self.due_date = now + datetime.timedelta(milliseconds=self.optimum_interval)

    def _update_af(self, grade, now=None):
        if now is None:
            now = datetime.datetime.now()
        estimated_fi = max(1.0, self.sm.fi_g.fi(grade))
        corrected_uf = self.uf(now) * (self.sm.requested_fi / estimated_fi)
        if self.repetition > 0:
            estimated_af = self.sm.ofm.af(self.repetition, corrected_uf)
        else:
            estimated_af = max(MIN_AF, min(MAX_AF, corrected_uf))
        self._afs.append(estimated_af)
        if len(self._afs) > self.MAX_AFS_COUNT:
            self._afs = self._afs[-self.MAX_AFS_COUNT :]
        wsum = sum(af * (i + 1) for i, af in enumerate(self._afs))
        wtotal = sum(range(1, len(self._afs) + 1))
        self.af(wsum / wtotal if wtotal else estimated_af)

    def answer(self, grade, now=None):
        if now is None:
            now = datetime.datetime.now()
        if self.repetition >= 0:
            self._update_af(grade, now)
        if grade >= THRESHOLD_RECALL:
            if self.repetition < RANGE_REPETITION - 1:
                self.repetition += 1
            self._I(now)
        else:
            if self.lapse < RANGE_AF - 1:
                self.lapse += 1
            self.optimum_interval = self.sm.interval_base
            self.previous_date = None
            self.due_date = now
            self.repetition = -1

    def data(self):
        return {
            "value": self.value,
            "repetition": self.repetition,
            "lapse": self.lapse,
            "of": self.of,
            "optimumInterval": self.optimum_interval,
            "dueDate": self.due_date.isoformat(),
            "previousDate": (
                self.previous_date.isoformat() if self.previous_date else None
            ),
            "_afs": self._afs,
        }

    @classmethod
    def load(cls, sm, data):
        item = cls(sm)
        item.value = data.get("value")
        item.repetition = data.get("repetition", -1)
        item.lapse = data.get("lapse", 0)
        item.of = data.get("of", 1.0)
        item.optimum_interval = data.get("optimumInterval", sm.interval_base)
        item._afs = data.get("_afs", [])
        due_str = data.get("dueDate")
        if due_str:
            if isinstance(due_str, str):
                item.due_date = datetime.datetime.fromisoformat(
                    due_str.replace("Z", "+00:00")
                )
            else:
                item.due_date = datetime.datetime.fromtimestamp(due_str / 1000)
        prev_str = data.get("previousDate")
        if prev_str:
            if isinstance(prev_str, str):
                item.previous_date = datetime.datetime.fromisoformat(
                    prev_str.replace("Z", "+00:00")
                )
            else:
                item.previous_date = datetime.datetime.fromtimestamp(prev_str / 1000)
        if item._afs:
            item.af(sum(item._afs) / len(item._afs))
        return item


# ============================================================================
# SM (global scheduler)
# ============================================================================


class SM:
    def __init__(self):
        self.requested_fi = 10.0
        self.interval_base = 3 * 60 * 60 * 1000  # 3 hours in ms
        self.q = []
        self.fi_g = FI_G(self)
        self.forgetting_curves = ForgettingCurves(self)
        self.rfm = RFM(self)
        self.ofm = OFM(self)

    def _find_index_to_insert(self, item, r=None):
        if r is None:
            r = list(range(len(self.q)))
        if not r:
            return 0
        v = item.due_date
        i = len(r) // 2
        if len(r) == 1:
            return r[i] if v < self.q[r[i]].due_date else r[i] + 1
        if v < self.q[r[i]].due_date:
            return self._find_index_to_insert(item, r[:i])
        return self._find_index_to_insert(item, r[i:])

    def add_item(self, value):
        item = Item(self, value)
        idx = self._find_index_to_insert(item)
        self.q.insert(idx, item)

    def next_item(self, is_advanceable=False):
        if not self.q:
            return None
        now = datetime.datetime.now()
        if is_advanceable or self.q[0].due_date < now:
            return self.q[0]
        return None

    def answer(self, grade, item, now=None):
        if now is None:
            now = datetime.datetime.now()
        self._update(grade, item, now)
        self.discard(item)
        idx = self._find_index_to_insert(item)
        self.q.insert(idx, item)

    def _update(self, grade, item, now=None):
        if now is None:
            now = datetime.datetime.now()
        if item.repetition >= 0:
            self.forgetting_curves.register_point(grade, item, now)
            self.ofm.update()
            self.fi_g.update(grade, item, now)
        item.answer(grade, now)

    def discard(self, item):
        if item in self.q:
            self.q.remove(item)

    def data(self):
        return {
            "requestedFI": self.requested_fi,
            "intervalBase": self.interval_base,
            "q": [item.data() for item in self.q],
            "fi_g": self.fi_g.data(),
            "forgettingCurves": self.forgetting_curves.data(),
            "version": 1,
        }

    @classmethod
    def load(cls, data):
        sm = cls()
        sm.requested_fi = data.get("requestedFI", 10.0)
        sm.interval_base = data.get("intervalBase", 3 * 60 * 60 * 1000)
        sm.q = [Item.load(sm, d) for d in data.get("q", [])]
        sm.fi_g = FI_G.load(sm, data.get("fi_g", {}))
        sm.forgetting_curves = ForgettingCurves.load(
            sm, data.get("forgettingCurves", {})
        )
        sm.rfm = RFM(sm)
        sm.ofm = OFM(sm)
        return sm


# ============================================================================
# Global state management
# ============================================================================

_GLOBAL_STATE_FILE = (
    pathlib.Path(config_var.get()["global"]["paths"]["misc"])
    / "sm15m_global_state.json"
)


def _get_global_sm():
    if os.path.exists(_GLOBAL_STATE_FILE):
        try:
            with open(_GLOBAL_STATE_FILE, "r", encoding="utf-8") as f:
                return SM.load(json.load(f))
        except Exception:
            logger.warning("SM-15M 全局状态文件加载失败, 创建新实例")
    sm = SM()
    _save_global_sm(sm)
    return sm


def _save_global_sm(sm):
    try:
        _GLOBAL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_GLOBAL_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(sm.data(), f, indent=2)
    except Exception:
        logger.exception("SM-15M 全局状态保存失败")


# ============================================================================
# SM15MAlgorithm (HeurAMS interface)
# ============================================================================


class SM15MAlgorithm(BaseAlgorithm):
    algo_name = "SM-15M"
    desc = "基于 sm.js 的 SM-15 间隔重复算法"

    class AlgodataDict(TypedDict):
        # SM-15M 特有
        lapse: int
        repetition: int
        of_val: float  # O-Factor
        optimum_interval_days: int  # 最优间隔（天）
        afs: list  # A-Factor 历史
        af: float  # 当前 A-Factor
        # 毫秒精度（子日排程）
        last_date_ms: int
        next_date_ms: int
        # BaseAlgorithm 兼容（天精度, 向后兼容）
        real_rept: int
        rept: int
        interval: int
        last_date: int
        next_date: int
        is_activated: int
        last_modify: float

    defaults = {
        "lapse": 0,
        "repetition": -1,
        "of_val": 1.0,
        "optimum_interval_days": 0,
        "afs": [],
        "af": 0.0,
        "real_rept": 0,
        "rept": 0,
        "interval": 0,
        "last_date": 0,
        "next_date": 0,
        "is_activated": 0,
        # 毫秒精度字段
        "last_date_ms": 0,
        "next_date_ms": 0,
        "last_modify": get_timestamp(),
    }

    @classmethod
    def _algodata_to_item(cls, algodata, sm):
        data = algodata.get(cls.algo_name, cls.defaults.copy())
        item = Item(sm)
        item.repetition = data.get("repetition", -1)
        item.lapse = data.get("lapse", 0)
        item.of = data.get("of_val", 1.0)
        item._afs = list(data.get("afs", []))
        af = data.get("af", 0.0)
        if af > 0:
            item.af(af)
        if item._afs:
            if item._af is None and item._afs:
                item.af(sum(item._afs) / len(item._afs))

        opt_days = data.get("optimum_interval_days", 0)
        item.optimum_interval = (
            opt_days * 24 * 60 * 60 * 1000 if opt_days > 0 else sm.interval_base
        )

        # 毫秒精度优先, 退化至天精度
        last_date_ms = data.get("last_date_ms", 0)
        if last_date_ms:
            item.previous_date = datetime.datetime(1970, 1, 1) + datetime.timedelta(
                milliseconds=last_date_ms
            )
        else:
            last_date = data.get("last_date", 0)
            item.previous_date = (
                daystamp_to_datetime(last_date).replace(tzinfo=None)
                if last_date > 0
                else None
            )

        next_date_ms = data.get("next_date_ms", 0)
        if next_date_ms:
            item.due_date = datetime.datetime(1970, 1, 1) + datetime.timedelta(
                milliseconds=next_date_ms
            )
        else:
            next_date = data.get("next_date", 0)
            item.due_date = (
                daystamp_to_datetime(next_date).replace(tzinfo=None)
                if next_date > 0
                else datetime.datetime(1970, 1, 1)
            )

        item.value = {"_restored": True}
        return item

    @classmethod
    def _item_to_algodata(cls, item, algodata):
        if cls.algo_name not in algodata:
            algodata[cls.algo_name] = cls.defaults.copy()
        data = algodata[cls.algo_name]

        data["lapse"] = item.lapse
        data["repetition"] = item.repetition
        data["of_val"] = item.of

        opt_ms = max(item.optimum_interval, 0)
        data["optimum_interval_days"] = round(opt_ms / (24 * 60 * 60 * 1000))

        data["afs"] = list(item._afs)
        data["af"] = item.af() if item._af is not None else 0.0

        # 毫秒精度
        if item.previous_date:
            data["last_date_ms"] = int(item.previous_date.timestamp() * 1000)
            data["last_date"] = datetime_to_daystamp(item.previous_date)
        data["next_date_ms"] = int(item.due_date.timestamp() * 1000)
        data["next_date"] = datetime_to_daystamp(item.due_date)
        data["interval"] = max(0, data["next_date"] - (data.get("last_date", 0) or 0))
        data["last_modify"] = get_timestamp()
        return algodata

    @classmethod
    def revisor(
        cls, algodata: dict, feedback: int = 5, is_new_activation: bool = False
    ):
        logger.debug(
            "SM-15M.revisor 开始, feedback=%d, is_new_activation=%s",
            feedback,
            is_new_activation,
        )
        if feedback == -1:
            return

        sm = _get_global_sm()
        item = cls._algodata_to_item(algodata, sm)

        if is_new_activation:
            item.repetition = -1
            item.lapse = 0
            item.of = 1.0
            item.optimum_interval = sm.interval_base
            item.previous_date = None
            item.due_date = datetime.datetime(1970, 1, 1)
            item._afs = []
            item._af = None
            item.af(2.5)

        sm.answer(feedback, item)
        _save_global_sm(sm)

        cls._item_to_algodata(item, algodata)
        algodata[cls.algo_name]["real_rept"] += 1
        if feedback >= THRESHOLD_RECALL:
            algodata[cls.algo_name]["rept"] += 1

        logger.debug(
            "SM-15M.revisor 完成: repetition=%d, of=%.4f, next_date=%d",
            item.repetition,
            item.of,
            algodata[cls.algo_name]["next_date"],
        )

    @classmethod
    def is_due(cls, algodata):
        data = algodata.get(cls.algo_name, cls.defaults.copy())
        # 毫秒精度优先
        next_date_ms = data.get("next_date_ms", 0)
        if next_date_ms:
            result = next_date_ms <= get_timestamp_ms()
            logger.debug(
                "SM-15M.is_due: next_date_ms=%d, now_ms=%d, result=%s",
                next_date_ms,
                get_timestamp_ms(),
                result,
            )
            return result
        # 退化至天精度
        next_date = data.get("next_date", 0)
        current = get_daystamp()
        result = next_date <= current
        logger.debug(
            "SM-15M.is_due: next_date=%d, current=%d, result=%s",
            next_date,
            current,
            result,
        )
        return result

    @classmethod
    def get_rating(cls, algodata):
        data = algodata.get(cls.algo_name, cls.defaults.copy())
        af = data.get("af", 0.0)
        logger.debug("SM-15M.get_rating: af=%f", af)
        return str(af)

    @classmethod
    def nextdate(cls, algodata) -> int:
        data = algodata.get(cls.algo_name, cls.defaults.copy())
        n = data.get("next_date", 0)
        logger.debug("SM-15M.nextdate: %d", n)
        return n
