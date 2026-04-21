"""
基于: https://github.com/slaypni/sm.js
原始 CoffeeScript 代码: (c) 2014 Kazuaki Tanida
MIT 许可证

================================================================================

主要算法概念：

1. 间隔重复 (Spaced Repetition)
   - 根据记忆强度动态调整复习间隔
   - 使用遗忘曲线预测记忆保留率

2. A-Factor (难度因子)
   - 表示项目的记忆难度
   - 范围: MIN_AF (1.2) 到 MAX_AF (≈7.5)
   - 值越大表示项目越容易记忆

3. O-Factor (最优因子)
   - 基于重复次数和难度因子的最优间隔乘数
   - 存储在 O-Factor 矩阵中

4. R-Factor (回忆因子)
   - 基于重复次数和实际遗忘指数的实际间隔乘数
   - 存储在 R-Factor 矩阵中

5. 遗忘曲线 (Forgetting Curve)
   - 描述记忆保留率随时间衰减的曲线
   - 用于计算遗忘指数 (Forgetting Index)

6. 遗忘指数-评分图 (FI-Grade Graph)
   - 建立遗忘指数与用户评分之间的关系
   - 用于校正回忆因子

================================================================================
"""

import datetime
import json
import math
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

# ============================================================================
# Global Constants
# ============================================================================

# A-Factor 的取值范围大小(矩阵维度)
RANGE_AF = 20

# 重复次数的取值范围大小(矩阵维度)
RANGE_REPETITION = 20

# 最小 A-Factor 值(最简单的项目)
MIN_AF = 1.2

# A-Factor 的步长(每个等级的增量)
NOTCH_AF = 0.3

# 最大 A-Factor 值(最难的项目)
# 计算公式: MIN_AF + NOTCH_AF * (RANGE_AF - 1) = 1.2 + 0.3 * 19 = 6.9
MAX_AF = MIN_AF + NOTCH_AF * (RANGE_AF - 1)

# 最大评分值(用户评分的上限)
MAX_GRADE = 5

# 记忆阈值：评分 >= 此值表示成功回忆
THRESHOLD_RECALL = 3

# ============================================================================
# Helper Functions
# ============================================================================


def sum_values(values):
    """
    计算列表中所有数值的和

    参数:
        values: 数值列表

    返回:
        所有数值的总和
    """
    return sum(values)


def mse(y_func, points):
    """
    计算函数 y 与数据点之间的均方误差 (Mean Squared Error)

    参数:
        y_func: 函数 y = f(x)
        points: 数据点列表, 每个点为 (x, y)

    返回:
        均方误差值, 衡量函数拟合程度
    """
    errors = [(y_func(p[0]) - p[1]) ** 2 for p in points]
    return sum(errors) / len(points) if errors else 0


def exponential_regression(points):
    """
    指数回归: y = a * exp(b * x)

    使用最小二乘法拟合指数函数 y = a * e^(b*x)。
    算法参考: http://mathworld.wolfram.com/LeastSquaresFittingExponential.html

    参数:
        points: 数据点列表, 每个点为 (x, y)

    返回:
        包含以下键的字典:
        - 'y': 函数 y(x) = a * exp(b * x)
        - 'x': 反函数 x(y) = (ln(y) - ln(a)) / b
        - 'a': 系数 a
        - 'b': 指数系数 b
        - 'mse': 计算均方误差的函数

    数学推导:
        对 y = a * e^(b*x) 两边取对数: ln(y) = ln(a) + b*x
        令 Y' = ln(y), a' = ln(a), 转换为线性回归: Y' = a' + b*x
        使用最小二乘法求解 a' 和 b, 然后 a = exp(a')
    """
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

    a_coeff = (sum_logY * sum_sqX - sumX * sumX_logY) / (n * sum_sqX - sq_sumX)
    b_coeff = (n * sumX_logY - sumX * sum_logY) / (n * sum_sqX - sq_sumX)

    a = math.exp(a_coeff)
    b = b_coeff

    def y_func(x):
        return a * math.exp(b * x)

    def x_func(y):
        return (-a_coeff + math.log(y)) / b if b != 0 else 0

    result = {
        "y": y_func,
        "x": x_func,
        "a": a,
        "b": b,
        "mse": lambda: mse(y_func, points),
    }
    return result


def linear_regression(points):
    """
    线性回归: y = a + b * x

    使用最小二乘法拟合线性函数。

    参数:
        points: 数据点列表, 每个点为 (x, y)

    返回:
        包含以下键的字典:
        - 'y': 函数 y(x) = a + b * x
        - 'x': 反函数 x(y) = (y - a) / b
        - 'a': 截距
        - 'b': 斜率

    计算公式:
        b = (n*Σxy - ΣxΣy) / (n*Σx² - (Σx)²)
        a = (Σy - b*Σx) / n
    """
    n = len(points)
    X = [p[0] for p in points]
    Y = [p[1] for p in points]
    sqX = [x * x for x in X]

    sumY = sum(Y)
    sum_sqX = sum(sqX)
    sumX = sum(X)
    sumXY = sum(X[i] * Y[i] for i in range(n))
    sq_sumX = sumX * sumX

    a = (sumY * sum_sqX - sumX * sumXY) / (n * sum_sqX - sq_sumX)
    b = (n * sumXY - sumX * sumY) / (n * sum_sqX - sq_sumX)

    def y_func(x):
        return a + b * x

    def x_func(y):
        return (y - a) / b if b != 0 else 0

    return {"y": y_func, "x": x_func, "a": a, "b": b}


def power_law_model(a, b):
    """
    幂律模型: y = a * x^b

    创建幂律函数模型对象。

    参数:
        a: 系数
        b: 指数

    返回:
        包含以下键的字典:
        - 'y': 函数 y(x) = a * x^b
        - 'x': 反函数 x(y) = (y / a)^(1/b)
        - 'a': 系数 a
        - 'b': 指数 b
    """

    def y_func(x):
        return a * (x**b)

    def x_func(y):
        return (y / a) ** (1 / b) if a != 0 and b != 0 else 0

    return {"y": y_func, "x": x_func, "a": a, "b": b}


def power_law_regression(points):
    """
    幂律回归: y = a * x^b

    使用最小二乘法拟合幂律函数。
    算法参考: http://mathworld.wolfram.com/LeastSquaresFittingPowerLaw.html

    参数:
        points: 数据点列表, 每个点为 (x, y)

    返回:
        幂律模型字典(包含 'y', 'x', 'a', 'b', 'mse' 键)

    数学推导:
        对 y = a * x^b 两边取对数: ln(y) = ln(a) + b * ln(x)
        令 Y' = ln(y), X' = ln(x), a' = ln(a)
        转换为线性回归: Y' = a' + b * X'
        使用最小二乘法求解 a' 和 b, 然后 a = exp(a')
    """
    n = len(points)
    X = [p[0] for p in points]
    Y = [p[1] for p in points]
    logX = [math.log(x) for x in X]
    logY = [math.log(y) for y in Y]

    sum_logX_logY = sum(logX[i] * logY[i] for i in range(n))
    sum_logX = sum(logX)
    sum_logY = sum(logY)
    sum_sq_logX = sum(lx * lx for lx in logX)
    sq_sum_logX = sum_logX * sum_logX

    b = (n * sum_logX_logY - sum_logX * sum_logY) / (n * sum_sq_logX - sq_sum_logX)
    a_coeff = (sum_logY - b * sum_logX) / n
    a = math.exp(a_coeff)

    model = power_law_model(a, b)
    model["mse"] = lambda: mse(model["y"], points)
    return model


def fixed_point_power_law_regression(points, fixed_point):
    """
    定点幂律回归: y = q * (x/p)^b

    拟合经过固定点 (p, q) 的幂律函数。
    在 SM-15 算法中用于拟合 O-Factor 矩阵。

    参数:
        points: 数据点列表, 每个点为 (x, y)
        fixed_point: 固定点 (p, q), 函数必须经过此点

    返回:
        幂律模型字典(包含 'y', 'x', 'a', 'b' 键)

    数学推导:
        给定固定点 (p, q), 模型为: y = q * (x/p)^b
        对两边取对数: ln(y) = b * ln(x/p) + ln(q)
        令 Y' = ln(y) - ln(q), X' = ln(x/p)
        转换为通过原点的线性回归: Y' = b * X'
        使用最小二乘法求解 b
    """
    n = len(points)
    p, q = fixed_point
    logQ = math.log(q)

    X = [math.log(point[0] / p) for point in points]
    Y = [math.log(point[1]) - logQ for point in points]

    # Linear regression through origin on transformed points
    sumXY = sum(X[i] * Y[i] for i in range(n))
    sum_sqX = sum(x * x for x in X)
    b = sumXY / sum_sqX if sum_sqX != 0 else 0

    model = power_law_model(q / (p**b), b)
    return model


def linear_regression_through_origin(points):
    """
    通过原点的线性回归: y = b * x

    拟合通过原点的线性函数, 即截距为 0。

    参数:
        points: 数据点列表, 每个点为 (x, y)

    返回:
        包含以下键的字典:
        - 'y': 函数 y(x) = b * x
        - 'x': 反函数 x(y) = y / b
        - 'b': 斜率

    计算公式:
        b = Σ(x_i * y_i) / Σ(x_i²)
    """
    n = len(points)
    X = [p[0] for p in points]
    Y = [p[1] for p in points]

    sumXY = sum(X[i] * Y[i] for i in range(n))
    sum_sqX = sum(x * x for x in X)
    b = sumXY / sum_sqX if sum_sqX != 0 else 0

    def y_func(x):
        return b * x

    def x_func(y):
        return y / b if b != 0 else 0

    return {"y": y_func, "x": x_func, "b": b}


# ============================================================================
# Core Classes
# ============================================================================


class Item:
    """
    表示单个闪卡项目(记忆项目)。

    在 SM-15 算法中, 每个项目代表一个需要记忆的单元(如单词、概念等)。
    项目包含记忆状态、复习历史和算法参数。

    属性:
        sm: 所属的 SM 实例
        value: 项目内容(通常是字典, 包含 front/back)
        lapse: 遗忘次数
        repetition: 成功回忆次数(-1 表示新项目)
        of: O-Factor 值(最优因子)
        optimum_interval: 最优复习间隔(毫秒)
        due_date: 下次复习到期时间
        previous_date: 上次复习时间
        _afs: 估计的 A-Factor 历史记录
        _af: 当前 A-Factor 值

    主要功能:
        1. 计算实际间隔和 UF(使用因子)
        2. 管理 A-Factor(难度因子)
        3. 处理用户评分并更新记忆状态
        4. 计算下一次复习间隔
        5. 序列化和反序列化

    算法原理:
        - 间隔重复基于最优间隔和 O-Factor 调整
        - A-Factor 反映项目难度, 通过历史估计值加权平均计算
        - UF(使用因子)是实际间隔与调整后最优间隔的比率
        - 当评分低于阈值时, 项目被标记为遗忘(lapse增加)
    """

    MAX_AFS_COUNT = 30

    def __init__(self, sm, value=None):
        """
        初始化新的闪卡项目。

        参数:
            sm: 所属的 SM 实例
            value: 项目内容(通常是包含 front/back 的字典)

        初始状态:
            - lapse(遗忘次数): 0
            - repetition(重复次数): -1(表示新项目)
            - of(O-Factor): 1.0(默认值)
            - optimum_interval(最优间隔): 等于 SM 的基础间隔
            - due_date(到期时间): 1970-01-01(立即到期)
            - previous_date(上次复习): None(尚未复习)
            - _afs(A-Factor 历史): 空列表
            - _af(当前 A-Factor): None(尚未计算)
        """
        self.sm = sm
        self.value = value
        self.lapse = 0
        self.repetition = -1
        self.of = 1.0
        self.optimum_interval = sm.interval_base
        self.due_date = datetime.datetime.fromtimestamp(0)  # epoch start
        self.previous_date = None
        self._afs = []  # estimated A-Factor history
        self._af = None  # current A-Factor

    def interval(self, now=None):
        """
        计算自上次复习以来的实际间隔。

        参数:
            now: 当前时间(默认为当前时间)

        返回:
            实际间隔(毫秒)

        注意:
            - 如果项目尚未复习过(previous_date为None), 返回基础间隔
            - 间隔计算使用实际经过的时间, 而非计划的间隔
            - 返回值为毫秒, 与SM-15算法内部表示一致
        """
        if now is None:
            now = datetime.datetime.now()

        if self.previous_date is None:
            return self.sm.interval_base
        return (
            now - self.previous_date
        ).total_seconds() * 1000  # convert to milliseconds

    def uf(self, now=None):
        """
        计算 UF(使用因子, Utilization Factor)。

        UF 是实际间隔与调整后最优间隔的比率：
            UF = 实际间隔 / (最优间隔 / O-Factor)

        参数:
            now: 当前时间(默认为当前时间)

        返回:
            UF 值

        算法意义:
            - UF = 1: 实际间隔等于调整后最优间隔
            - UF > 1: 实际间隔长于最优间隔(可能更难回忆)
            - UF < 1: 实际间隔短于最优间隔(可能更容易回忆)
            - UF 用于估计 A-Factor 和校正记忆模型
        """
        if now is None:
            now = datetime.datetime.now()

        interval = self.interval(now)
        adjusted_optimum = self.optimum_interval / self.of
        return interval / adjusted_optimum if adjusted_optimum != 0 else 0

    def af(self, value=None):
        """
        获取或设置 A-Factor(难度因子)。

        A-Factor 表示项目的记忆难度, 值越大表示项目越容易记忆。
        取值范围: MIN_AF (1.2) 到 MAX_AF (≈7.5), 步长为 NOTCH_AF (0.3)。

        参数:
            value: 要设置的 A-Factor 值(如果为None则返回当前值)

        返回:
            当前或设置后的 A-Factor 值

        处理逻辑:
            - 如果 value 为 None: 返回当前 _af 值
            - 如果提供 value: 将其舍入到最近的 notch 值, 确保在有效范围内
            - 舍入公式: a = round((value - MIN_AF) / NOTCH_AF)
            - 最终值: MIN_AF + a * NOTCH_AF, 限制在 [MIN_AF, MAX_AF] 范围内
        """
        if value is None:
            return self._af

        # Round to nearest notch
        a = round((value - MIN_AF) / NOTCH_AF)
        self._af = max(MIN_AF, min(MAX_AF, MIN_AF + a * NOTCH_AF))
        return self._af

    def af_index(self):
        """
        获取最接近的 A-Factor 在矩阵中的索引。

        由于 A-Factor 矩阵使用离散值(20个等级), 需要将连续的实际 A-Factor
        映射到最接近的离散值索引。

        返回:
            A-Factor 矩阵中的索引(0 到 RANGE_AF-1)

        算法:
            1. 生成所有可能的 A-Factor 值: MIN_AF + i * NOTCH_AF
            2. 计算当前 A-Factor 与每个可能值的绝对差
            3. 返回差值最小的索引

        用途:
            用于从 O-Factor 矩阵和 R-Factor 矩阵中查找对应的值。
        """
        afs = [MIN_AF + i * NOTCH_AF for i in range(RANGE_AF)]

        # Find index with minimum difference
        min_diff = float("inf")
        min_index = 0

        for i, af_val in enumerate(afs):
            diff = abs(self.af() - af_val)  # type: ignore
            if diff < min_diff:
                min_diff = diff
                min_index = i

        return min_index

    def _I(self, now=None):
        """
        计算新的最优间隔(SM-15 算法的第1步)。

        注意：此实现与原始 SM-15 的不同之处在于使用实际间隔而非先前计算的间隔。

        参数:
            now: 当前时间(默认为当前时间)

        算法步骤:
            1. 根据重复次数和 A-Factor 索引从 O-Factor 矩阵获取 O-Factor 值
            2. 计算新的 O-Factor: of = max(1, (of_val - 1) * (实际间隔/最优间隔) + 1)
            3. 更新最优间隔: 最优间隔 = round(最优间隔 * of)
            4. 更新时间: previous_date = now, due_date = now + 最优间隔

        特殊处理:
            - 对于第一次重复(repetition == 0), 使用 lapse 作为 A-Factor 索引
            - 对于后续重复, 使用 af_index() 计算的索引

        数学意义:
            - O-Factor 根据实际表现动态调整
            - 如果实际间隔长于最优间隔, O-Factor 增加(下次间隔更长)
            - 如果实际间隔短于最优间隔, O-Factor 减小(下次间隔更短)
        """
        if now is None:
            now = datetime.datetime.now()

        # Get O-Factor from matrix
        if self.repetition == 0:
            af_index = self.lapse
        else:
            af_index = self.af_index()

        of_val = self.sm.ofm.of(self.repetition, af_index)

        # Calculate new O-Factor
        actual_interval = self.interval(now)
        self.of = max(1.0, (of_val - 1) * (actual_interval / self.optimum_interval) + 1)

        # Update optimum interval
        self.optimum_interval = round(self.optimum_interval * self.of)

        # Update dates
        self.previous_date = now
        self.due_date = now + datetime.timedelta(milliseconds=self.optimum_interval)

    def _update_af(self, grade, now=None):
        """
        基于评分更新 A-Factor(SM-15 算法的第9、11步)。

        参数:
            grade: 用户评分(0-5)
            now: 当前时间(默认为当前时间)

        算法步骤:
            1. 从 FI-Grade 图估计遗忘指数 (FI)
            2. 校正 UF: corrected_uf = UF * (requested_FI / estimated_FI)
            3. 估计 A-Factor:
               - 如果 repetition > 0: 从 O-Factor 矩阵反推 A-Factor
               - 否则: 直接使用 corrected_uf, 限制在有效范围内
            4. 将估计值加入历史记录(保留最近的 MAX_AFS_COUNT 个)
            5. 计算加权平均值(最近的值权重更高)
            6. 更新当前 A-Factor

        算法意义:
            - 使用遗忘指数校正 UF, 考虑实际记忆表现
            - 通过 O-Factor 矩阵反推 A-Factor, 建立 UF 与 A-Factor 的关系
            - 使用加权平均平滑估计值, 避免单次表现的过度影响
        """
        if now is None:
            now = datetime.datetime.now()

        estimated_fi = max(1.0, self.sm.fi_g.fi(grade))
        corrected_uf = self.uf(now) * (self.sm.requested_fi / estimated_fi)

        # Estimate A-Factor
        if self.repetition > 0:
            estimated_af = self.sm.ofm.af(self.repetition, corrected_uf)
        else:
            estimated_af = max(MIN_AF, min(MAX_AF, corrected_uf))

        # Add to history (keep only recent values)
        self._afs.append(estimated_af)
        if len(self._afs) > self.MAX_AFS_COUNT:
            self._afs = self._afs[-self.MAX_AFS_COUNT :]

        # Calculate weighted average
        weights = list(range(1, len(self._afs) + 1))
        weighted_sum = sum(af * weight for af, weight in zip(self._afs, weights))
        total_weight = sum(weights)

        self.af(weighted_sum / total_weight if total_weight != 0 else estimated_af)

    def answer(self, grade, now=None):
        """
        处理用户评分, 更新项目状态。

        这是 SM-15 算法的核心方法, 根据用户评分决定项目下一步的状态。

        参数:
            grade: 用户评分(0-5, 0表示完全遗忘, 5表示完美回忆)
            now: 当前时间(默认为当前时间)

        处理逻辑:
            1. 如果不是新项目(repetition >= 0), 更新 A-Factor
            2. 如果评分 >= THRESHOLD_RECALL (3):
                - 增加重复次数(如果未达到上限)
                - 调用 _I() 计算新的最优间隔和到期时间
            3. 如果评分 < THRESHOLD_RECALL:
                - 增加遗忘次数(如果未达到上限)
                - 重置最优间隔为基础间隔
                - 重置 previous_date 为 None(下次 interval() 返回基础间隔)
                - 设置 due_date 为当前时间(立即重新复习)
                - 重置重复次数为 -1(重新开始学习)

        算法意义:
            - 成功回忆时, 项目进入下一轮间隔重复周期
            - 遗忘时, 项目重置为初始状态, 需要重新学习
            - 阈值 THRESHOLD_RECALL 区分成功与失败回忆
        """
        if now is None:
            now = datetime.datetime.now()

        # Update A-Factor if not a new item
        if self.repetition >= 0:
            self._update_af(grade, now)

        if grade >= THRESHOLD_RECALL:
            # Remembered successfully
            if self.repetition < RANGE_REPETITION - 1:
                self.repetition += 1
            self._I(now)
        else:
            # Forgotten
            if self.lapse < RANGE_AF - 1:
                self.lapse += 1
            self.optimum_interval = self.sm.interval_base
            self.previous_date = None  # reset interval calculation
            self.due_date = now
            self.repetition = -1

    def data(self):
        """
        序列化项目数据, 用于保存和加载。

        返回:
            包含项目所有状态的字典, 可转换为 JSON 格式保存。

        数据结构:
            - value: 项目内容
            - repetition: 重复次数
            - lapse: 遗忘次数
            - of: O-Factor 值
            - optimumInterval: 最优间隔(毫秒)
            - dueDate: 到期时间(ISO 格式字符串)
            - previousDate: 上次复习时间(ISO 格式字符串或 null)
            - _afs: A-Factor 历史记录列表

        注意:
            - 日期对象转换为 ISO 格式字符串以便序列化
            - 反序列化时需要在 load() 方法中转换回 datetime 对象
            - 保持与原始 JavaScript 版本的数据格式兼容
        """
        return {
            "value": self.value,
            "repetition": self.repetition,
            "lapse": self.lapse,
            "of": self.of,
            "optimumInterval": self.optimum_interval,
            "dueDate": (
                self.due_date.isoformat()
                if isinstance(self.due_date, datetime.datetime)
                else self.due_date
            ),
            "previousDate": (
                self.previous_date.isoformat()
                if isinstance(self.previous_date, datetime.datetime)
                else self.previous_date
            ),
            "_afs": self._afs,
        }

    @classmethod
    def load(cls, sm, data):
        """
        从序列化数据加载项目。

        参数:
            sm: 所属的 SM 实例
            data: 序列化的项目数据字典

        返回:
            恢复状态的 Item 实例

        处理逻辑:
            1. 创建新的 Item 实例
            2. 复制基本属性(value, repetition, lapse, of, optimumInterval, _afs)
            3. 转换日期字符串为 datetime 对象
            4. 如果 previousDate 存在则转换, 否则设为 None
            5. 如果 _af 历史记录不为空, 设置当前 A-Factor 为最后一个值

        注意:
            - 日期字符串应为 ISO 格式(如 data() 方法生成的格式)
            - 保持与原始 JavaScript 版本的数据兼容性
            - 加载后项目状态完全恢复, 包括历史记录
        """
        item = cls(sm)

        # Copy basic properties
        item.value = data.get("value")
        item.repetition = data.get("repetition", -1)
        item.lapse = data.get("lapse", 0)
        item.of = data.get("of", 1.0)
        item.optimum_interval = data.get("optimumInterval", sm.interval_base)
        item._afs = data.get("_afs", [])

        # Parse dates
        due_date_str = data.get("dueDate")
        if due_date_str:
            if isinstance(due_date_str, str):
                item.due_date = datetime.datetime.fromisoformat(
                    due_date_str.replace("Z", "+00:00")
                )
            else:
                # Handle numeric timestamp
                item.due_date = datetime.datetime.fromtimestamp(due_date_str / 1000)

        previous_date_str = data.get("previousDate")
        if previous_date_str:
            if isinstance(previous_date_str, str):
                item.previous_date = datetime.datetime.fromisoformat(
                    previous_date_str.replace("Z", "+00:00")
                )
            else:
                item.previous_date = datetime.datetime.fromtimestamp(
                    previous_date_str / 1000
                )

        # Initialize A-Factor if we have history
        if item._afs:
            item.af(sum(item._afs) / len(item._afs))

        return item


class FI_G:
    """
    遗忘指数-评分图(FI-Grade Graph)。

    建立遗忘指数(Forgetting Index)与用户评分(Grade)之间的关系。
    用于根据用户评分估计实际遗忘指数, 从而校正记忆模型。

    属性:
        sm: 所属的 SM 实例
        points: 数据点列表, 每个点为 [fi, grade]
        _graph: 缓存的回归模型
        MAX_POINTS_COUNT: 最大数据点数(5000)
        GRADE_OFFSET: 评分偏移量(1), 避免评分为0时的数学问题

    算法原理:
        1. 收集 (遗忘指数, 评分) 数据点
        2. 使用指数回归拟合 FI-Grade 关系
        3. 根据评分估计遗忘指数, 用于校正 UF 和 A-Factor

    默认初始化:
        - 点1: (0, MAX_GRADE) - 遗忘指数为0时, 评分应为最高
        - 点2: (100, 0) - 遗忘指数为100时, 评分应为最低

    主要功能:
        1. 记录新的数据点
        2. 根据评分估计遗忘指数
        3. 更新图形(SM-15 算法的第10步)
    """

    MAX_POINTS_COUNT = 5000
    GRADE_OFFSET = 1

    def __init__(self, sm, points=None):
        self.sm = sm
        self._graph = None

        if points is not None:
            self.points = points
        else:
            # Initialize with default points
            self.points = []
            self._register_point(0, MAX_GRADE)
            self._register_point(100, 0)

    def _register_point(self, fi, g):
        """Add a point to the graph."""
        self.points.append([fi, g + self.GRADE_OFFSET])

        # Keep only recent points
        if len(self.points) > self.MAX_POINTS_COUNT:
            self.points = self.points[-self.MAX_POINTS_COUNT :]

        self._graph = None  # Invalidate cached regression

    def update(self, grade, item, now=None):
        """Update FI-G graph with new data (Step 10 in SM-15)."""
        if now is None:
            now = datetime.datetime.now()

        # Expected forgetting index
        def expected_fi():
            # Simple linear forgetting curve assumption
            return (item.uf(now) / item.of) * self.sm.requested_fi

            # Alternative method using forgetting curves (commented out)
            # curve = self.sm.forgetting_curves.curves[item.repetition][item.af_index()]
            # uf_val = curve.uf(100 - self.sm.requested_fi)
            # return 100 - curve.retention(item.uf() / uf_val)

        self._register_point(expected_fi(), grade)

    def fi(self, grade):
        """Estimate forgetting index for given grade."""
        if not self.points:
            return 50.0  # Default value

        if self._graph is None:
            self._graph = exponential_regression(self.points)

        estimated = self._graph["x"](grade + self.GRADE_OFFSET)
        return max(0.0, min(100.0, estimated))

    def grade(self, fi):
        """Estimate grade for given forgetting index."""
        if not self.points:
            return 2.5  # Default value

        if self._graph is None:
            self._graph = exponential_regression(self.points)

        estimated = self._graph["y"](fi)
        return estimated - self.GRADE_OFFSET

    def data(self):
        """Serialize FI-G data."""
        return {"points": self.points}

    @classmethod
    def load(cls, sm, data):
        """Deserialize FI-G from data."""
        return cls(sm, data.get("points"))


class ForgettingCurve:
    """
    单个遗忘曲线, 针对特定的重复次数和 A-Factor。

    描述记忆保留率(Retention)随时间(通过 UF 表示)衰减的曲线。
    每个曲线对应一个特定的(重复次数, A-Factor)组合。

    属性:
        points: 数据点列表, 每个点为 [uf, retention]
        _curve: 缓存的指数回归模型
        MAX_POINTS_COUNT: 最大数据点数(500)
        FORGOTTEN: 遗忘状态的保留率值(1)
        REMEMBERED: 成功回忆状态的保留率值(101)

    数据表示:
        - UF(使用因子): x轴, 表示时间(实际间隔/调整后最优间隔)
        - 保留率: y轴, 1表示完全遗忘, 101表示完全回忆(实际为0-100%加偏移)
        - 偏移量 FORGOTTEN=1 避免取对数时的数学问题

    算法原理:
        1. 收集 (UF, 回忆结果) 数据点
        2. 使用指数回归拟合遗忘曲线
        3. 根据 UF 预测保留率, 或根据保留率反推 UF

    主要功能:
        1. 注册新的数据点(回忆结果)
        2. 计算给定 UF 的保留率
        3. 计算给定保留率的 UF
        4. 序列化和反序列化
    """

    MAX_POINTS_COUNT = 500
    FORGOTTEN = 1
    REMEMBERED = 100 + FORGOTTEN

    def __init__(self, points):
        self.points = points
        self._curve = None

    def register_point(self, grade, uf):
        """Add a data point to the curve."""
        is_remembered = grade >= THRESHOLD_RECALL
        self.points.append([uf, self.REMEMBERED if is_remembered else self.FORGOTTEN])

        # Keep only recent points
        if len(self.points) > self.MAX_POINTS_COUNT:
            self.points = self.points[-self.MAX_POINTS_COUNT :]

        self._curve = None  # Invalidate cached regression

    def retention(self, uf):
        """Calculate retention probability for given UF."""
        if not self.points:
            return 50.0  # Default retention

        if self._curve is None:
            self._curve = exponential_regression(self.points)

        estimated = self._curve["y"](uf)
        clamped = max(self.FORGOTTEN, min(estimated, self.REMEMBERED))
        return clamped - self.FORGOTTEN

    def uf(self, retention):
        """Calculate UF for given retention probability."""
        if not self.points:
            return 1.0  # Default UF

        if self._curve is None:
            self._curve = exponential_regression(self.points)

        target = retention + self.FORGOTTEN
        return max(0.0, self._curve["x"](target))

    def data(self):
        """Serialize curve data."""
        return self.points


class ForgettingCurves:
    """
    遗忘曲线矩阵(重复次数 × A-Factor)。

    包含 RANGE_REPETITION × RANGE_AF 个遗忘曲线, 每个曲线对应一个
    (重复次数, A-Factor)组合。这是 SM-15 算法的核心数据结构之一。

    属性:
        sm: 所属的 SM 实例
        curves: 二维列表的遗忘曲线矩阵 [重复次数][A-Factor索引]
        FORGOTTEN: 遗忘状态的保留率值(1)
        REMEMBERED: 成功回忆状态的保留率值(101)

    矩阵结构:
        - 行: 重复次数(0 到 RANGE_REPETITION-1)
        - 列: A-Factor 索引(0 到 RANGE_AF-1)
        - 每个单元格: 一个 ForgettingCurve 实例

    初始化:
        - 如果提供 points 参数: 从现有数据加载曲线
        - 否则: 生成初始曲线, 基于数学公式创建初始数据点

    主要功能:
        1. 为特定项目和评分注册数据点
        2. 获取特定重复次数和 A-Factor 的曲线
        3. 序列化和反序列化整个矩阵
        4. 管理遗忘曲线数据的收集和更新

    算法作用:
        - 建立 UF 与保留率之间的定量关系
        - 为 R-Factor 矩阵提供数据基础
        - 帮助估计项目的记忆强度随时间的变化
    """

    FORGOTTEN = 1
    REMEMBERED = 100 + FORGOTTEN

    def __init__(self, sm, points=None):
        self.sm = sm
        self.curves = []

        # Initialize curves matrix
        for r in range(RANGE_REPETITION):
            row = []
            for a in range(RANGE_AF):
                if points is not None:
                    partial_points = points[r][a]
                else:
                    # Generate initial points
                    if r > 0:
                        partial_points = [[0, self.REMEMBERED]] + [
                            [
                                MIN_AF + NOTCH_AF * i,
                                min(
                                    self.REMEMBERED,
                                    math.exp(
                                        -(r + 1)
                                        / 200
                                        * (i - a * math.sqrt(2 / (r + 1)))
                                    )
                                    * (self.REMEMBERED - self.sm.requested_fi),
                                ),
                            ]
                            for i in range(21)
                        ]
                    else:
                        partial_points = [[0, self.REMEMBERED]] + [
                            [
                                MIN_AF + NOTCH_AF * i,
                                min(
                                    self.REMEMBERED,
                                    math.exp(-1 / (10 + 1 * (a + 1)) * (i - (a**0.6)))
                                    * (self.REMEMBERED - self.sm.requested_fi),
                                ),
                            ]
                            for i in range(21)
                        ]

                row.append(ForgettingCurve(partial_points))
            self.curves.append(row)

    def register_point(self, grade, item, now=None):
        """Register a data point in the appropriate curve."""
        if item.repetition > 0:
            af_index = item.af_index()
        else:
            af_index = item.lapse

        self.curves[item.repetition][af_index].register_point(grade, item.uf(now))

    def data(self):
        """Serialize forgetting curves data."""
        return {
            "points": [
                [self.curves[r][a].data() for a in range(RANGE_AF)]
                for r in range(RANGE_REPETITION)
            ]
        }

    @classmethod
    def load(cls, sm, data):
        """Deserialize forgetting curves from data."""
        return cls(sm, data.get("points"))


class RFM:
    """
    R-Factor 矩阵(回忆因子矩阵)。

    R-Factor 表示在给定重复次数和 A-Factor 下, 达到目标遗忘指数所需的 UF 值。
    实际上是遗忘曲线的包装器, 提供便捷的接口访问。

    属性:
        sm: 所属的 SM 实例

    计算公式:
        R-Factor = curve.uf(100 - requested_fi)
        其中 curve 是对应 (repetition, af_index) 的遗忘曲线
        uf() 方法返回达到指定保留率所需的 UF 值

    算法意义:
        - R-Factor 是实际观察到的间隔乘数
        - 表示在特定记忆强度下, 达到目标遗忘水平所需的时间倍数
        - 用于与 O-Factor(最优因子)比较, 校正记忆模型
        - 是 O-Factor 矩阵计算的基础

    主要功能:
        获取特定重复次数和 A-Factor 索引的 R-Factor 值
    """

    def __init__(self, sm):
        self.sm = sm

    def rf(self, repetition, af_index):
        """Get R-Factor for given repetition and A-Factor index."""
        return self.sm.forgetting_curves.curves[repetition][af_index].uf(
            100 - self.sm.requested_fi
        )


class OFM:
    """
    O-Factor 矩阵(最优因子矩阵)。

    O-Factor 表示在给定重复次数和 A-Factor 下的最优间隔乘数。
    基于 R-Factor 矩阵通过幂律回归计算得出。

    属性:
        sm: 所属的 SM 实例
        _ofm: 缓存的 O-Factor 矩阵
        _ofm0: 缓存的重复次数为0时的 O-Factor 数组
        INITIAL_REP_VALUE: 初始重复值(1)

    矩阵结构:
        - 行: 重复次数(0 到 RANGE_REPETITION-1)
        - 列: A-Factor 索引(0 到 RANGE_AF-1)
        - 每个单元格: O-Factor 值

    算法原理(update() 方法, SM-15 第8步):
        1. 对于每个 A-Factor 索引:
            a. 收集 (重复次数, R-Factor) 数据点
            b. 使用定点幂律回归拟合, 固定点 (1, 1)
            c. 生成该 A-Factor 对应的 O-Factor 数组
        2. 对于重复次数0:
            a. 收集 (A-Factor, R-Factor) 数据点
            b. 使用幂律回归拟合
            c. 生成重复次数0时的 O-Factor 数组

    主要功能:
        1. 更新 O-Factor 矩阵
        2. 获取特定重复次数和 A-Factor 索引的 O-Factor
        3. 从 O-Factor 和 UF 反推 A-Factor
    """

    INITIAL_REP_VALUE = 1

    def __init__(self, sm):
        self.sm = sm
        self._ofm = None
        self._ofm0 = None
        self.update()

    def update(self):
        """Update O-Factor matrix (Step 8 in SM-15)."""

        # Helper functions
        def af_from_index(a):
            return a * NOTCH_AF + MIN_AF

        def rep_from_index(r):
            return r + self.INITIAL_REP_VALUE

        # Calculate D-factors
        dfs = []
        for a in range(RANGE_AF):
            points = [
                [rep_from_index(r), self.sm.rfm.rf(r, a)]
                for r in range(1, RANGE_REPETITION)
            ]
            fixed_point = [rep_from_index(1), af_from_index(a)]
            model = fixed_point_power_law_regression(points, fixed_point)
            dfs.append(model["b"])

        # Transform D-factors
        dfs_transformed = [af_from_index(a) / (2 ** dfs[a]) for a in range(RANGE_AF)]

        # Linear regression on D-factors
        decay_points = [[a, dfs_transformed[a]] for a in range(RANGE_AF)]
        decay = linear_regression(decay_points)

        # Create O-Factor model for each A-Factor
        def create_ofm(a):
            af = af_from_index(a)
            b = (
                math.log(af / decay["y"](a)) / math.log(rep_from_index(1))
                if decay["y"](a) != 0
                else 0
            )
            model = power_law_model(af / (rep_from_index(1) ** b), b)

            return {
                "y": lambda r: model["y"](rep_from_index(r)),
                "x": lambda y: model["x"](y) - self.INITIAL_REP_VALUE,
            }

        self._ofm = [create_ofm(a) for a in range(RANGE_AF)]

        # Create O-Factor model for repetition 0
        ofm0_points = [[a, self.sm.rfm.rf(0, a)] for a in range(RANGE_AF)]
        ofm0 = exponential_regression(ofm0_points)
        self._ofm0 = lambda a: ofm0["y"](a)

    def of(self, repetition, af_index):
        """Get O-Factor for given repetition and A-Factor index."""
        if repetition == 0:
            return self._ofm0(af_index)  # type: ignore
        else:
            return self._ofm[af_index]["y"](repetition)  # type: ignore

    def af(self, repetition, of_val):
        """Get A-Factor index for given repetition and O-Factor."""
        af_from_idx = lambda a: a * NOTCH_AF + MIN_AF

        # Find closest A-Factor index
        min_diff = float("inf")
        min_index = 0

        for a in range(RANGE_AF):
            diff = abs(self.of(repetition, a) - of_val)
            if diff < min_diff:
                min_diff = diff
                min_index = a

        return af_from_idx(min_index)


class SM:
    """
    SM-15 算法主调度器。

    这是 SM-15 间隔重复算法的核心类, 负责协调所有组件和算法流程。
    管理项目队列、处理用户交互、执行算法更新步骤。

    属性:
        requested_fi: 目标遗忘指数(默认10%, 表示希望10%的项目被遗忘)
        interval_base: 基础间隔(3小时, 毫秒单位)
        q: 项目队列, 按 due_date 排序
        fi_g: FI-Grade 图实例
        forgetting_curves: 遗忘曲线矩阵实例
        rfm: R-Factor 矩阵实例
        ofm: O-Factor 矩阵实例

    主要功能:
        1. 项目管理: 添加、删除、查询项目
        2. 复习调度: 获取到期项目, 处理用户评分
        3. 算法协调: 调用各组件更新算法参数
        4. 数据持久化: 保存和加载学习状态
        5. 队列管理: 维护按到期时间排序的项目队列

    算法流程概览:
        1. 添加项目时创建 Item 实例, 插入排序队列
        2. 复习时获取到期项目, 接收用户评分
        3. 调用 answer() 处理评分, 更新项目状态
        4. 更新 FI-Grade 图、遗忘曲线、O-Factor 矩阵
        5. 重新计算项目的最优间隔和下次到期时间
        6. 将项目重新插入队列的适当位置

    使用方式:
        1. 创建 SM 实例
        2. 使用 add_item() 添加学习项目
        3. 使用 next_item() 获取需要复习的项目
        4. 使用 answer() 处理用户评分
        5. 使用 data() 和 load() 保存/加载学习进度
    """

    def __init__(self):
        """
        初始化 SM-15 调度器。

        设置默认参数并初始化所有算法组件。

        默认参数:
            - requested_fi: 10.0(目标遗忘指数10%)
            - interval_base: 3 * 60 * 60 * 1000(3小时, 毫秒单位)
            - q: 空项目队列(按到期时间排序)

        初始化的组件:
            - fi_g: FI-Grade 图, 管理遗忘指数与评分的关系
            - forgetting_curves: 遗忘曲线矩阵, 存储记忆保留率数据
            - rfm: R-Factor 矩阵, 包装遗忘曲线提供 R-Factor 查询
            - ofm: O-Factor 矩阵, 计算和管理最优因子

        注意:
            - interval_base 是算法的基础时间单位, 所有间隔计算基于此值
            - requested_fi 是算法的核心目标, 控制复习间隔的激进程度
            - 组件间存在依赖关系, 初始化顺序重要
        """
        self.requested_fi = 10.0  # target forgetting index (10%)
        self.interval_base = 3 * 60 * 60 * 1000  # 3 hours in milliseconds
        self.q = []  # items sorted by due_date

        # Initialize components
        self.fi_g = FI_G(self)
        self.forgetting_curves = ForgettingCurves(self)
        self.rfm = RFM(self)
        self.ofm = OFM(self)

    def _find_index_to_insert(self, item, r=None):
        """Binary search to find insertion index for sorted procession."""
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
        else:
            return self._find_index_to_insert(item, r[i:])

    def add_item(self, value):
        """Add a new item to the procession."""
        item = Item(self, value)
        index = self._find_index_to_insert(item)
        self.q.insert(index, item)

    def next_item(self, is_advanceable=False):
        """Get next item due for review."""
        if not self.q:
            return None

        now = datetime.datetime.now()
        if is_advanceable or self.q[0].due_date < now:
            return self.q[0]

        return None

    def answer(self, grade, item, now=None):
        """Process answer for given item."""
        if now is None:
            now = datetime.datetime.now()

        self._update(grade, item, now)
        self.discard(item)

        index = self._find_index_to_insert(item)
        self.q.insert(index, item)

    def _update(self, grade, item, now=None):
        """Internal update method."""
        if now is None:
            now = datetime.datetime.now()

        if item.repetition >= 0:
            self.forgetting_curves.register_point(grade, item, now)
            self.ofm.update()
            self.fi_g.update(grade, item, now)

        item.answer(grade, now)

    def discard(self, item):
        """Remove item from procession."""
        if item in self.q:
            self.q.remove(item)

    def data(self):
        """Serialize SM state."""
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
        """Deserialize SM from data."""
        sm = cls()
        sm.requested_fi = data.get("requestedFI", 10.0)
        sm.interval_base = data.get("intervalBase", 3 * 60 * 60 * 1000)

        # Load items
        items_data = data.get("q", [])
        sm.q = [Item.load(sm, item_data) for item_data in items_data]

        # Load components
        sm.fi_g = FI_G.load(sm, data.get("fi_g", {}))
        sm.forgetting_curves = ForgettingCurves.load(
            sm, data.get("forgettingCurves", {})
        )

        # Reinitialize RFM and update OFM
        sm.rfm = RFM(sm)
        sm.ofm = OFM(sm)
        sm.ofm.update()

        return sm


# ============================================================================
# Test Functions (for internal testing)
# ============================================================================

_test = {
    "exponentialRegression": exponential_regression,
    "linearRegression": linear_regression,
    "powerLawRegression": power_law_regression,
    "fixedPointPowerLawRegression": fixed_point_power_law_regression,
    "linearRegressionThroughOrigin": linear_regression_through_origin,
}

# ============================================================================
# CLI Interface
# ============================================================================


def main():
    """
    简单的闪卡命令行应用程序。

    提供交互式命令行界面, 使用户能够使用 SM-15 算法进行闪卡学习。

    可用命令:
        - a/add: 添加新卡片
        - n/next: 复习下一个到期的卡片
        - N/Next: 复习下一个卡片(即使未到期)
        - s/save: 保存学习进度到文件
        - l/load: 从文件加载学习进度
        - e/exit: 退出程序
        - eval: 执行 Python 表达式(调试用)
        - list: 列出所有卡片

    使用流程:
        1. 启动程序显示命令提示
        2. 输入 'a' 添加新卡片, 依次输入正面和背面内容
        3. 输入 'n' 复习到期的卡片
        4. 对显示的卡片输入评分 (0-5) 或 'D' 丢弃卡片
        5. 重复步骤3-4进行复习
        6. 使用 's' 保存进度, 'l' 加载进度

    数据文件:
        - 默认保存文件: data.json
        - 格式: JSON, 包含所有卡片状态和算法数据
        - 兼容性: 与原始 JavaScript 版本的数据格式兼容

    注意事项:
        - 评分范围: 0 (完全遗忘) 到 5 (完美回忆)
        - 阈值: 评分 >= 3 表示成功回忆
        - 时间单位: 内部使用毫秒, 但用户界面使用自然时间表示
    """
    import sys

    print("(a)add, (n)next, (N)next advanceably, (s)save, (l)load, (e)exit")

    mode = ["entrance"]
    data = None
    sm = SM()

    def goto_entrance():
        nonlocal mode, data
        mode = ["entrance"]
        data = None
        sys.stdout.write("sm> ")
        sys.stdout.flush()

    goto_entrance()

    while True:
        try:
            user_input = input().strip()
        except EOFError:
            break

        if mode[0] == "entrance":
            if user_input in ["a", "add"]:
                mode = ["add"]
            elif user_input in ["n", "next"]:
                mode = ["next"]
            elif user_input in ["N", "Next"]:
                mode = ["next", "_adv"]
            elif user_input in ["s", "save"]:
                mode = ["save"]
            elif user_input in ["l", "load"]:
                mode = ["load"]
            elif user_input in ["e", "exit"]:
                mode = ["exit"]
            elif user_input == "eval":
                mode = ["eval"]
            elif user_input == "list":
                mode = ["list"]
            else:
                goto_entrance()
                continue

        if mode[0] == "add":
            if len(mode) == 1:
                data = {"front": None, "back": None}
                print("Enter the front of the new card:")
                mode.append("front")
            elif mode[1] == "front":
                data["front"] = user_input  # type: ignore
                print("Enter the back of the new card:")
                mode[1] = "back"
            elif mode[1] == "back":
                data["back"] = user_input  # type: ignore
                sm.add_item(data)
                goto_entrance()

        elif mode[0] == "next":
            if mode[1] in ["_adv", None]:
                is_advanceable = mode[1] == "_adv"
                data = sm.next_item(is_advanceable)

                if data is None:
                    if sm.q:
                        next_due = sm.q[0].due_date
                        print(
                            f'There is no card that can be shown now. The next card is due at "{next_due}".'
                        )
                    else:
                        print("There is no card.")
                    goto_entrance()
                else:
                    print(
                        f"How much do you remember [{data.value.get('front', 'No front')}]:"
                    )
                    mode[1] = "review"

            elif mode[1] == "review":
                try:
                    g = int(user_input)
                    if 0 <= g <= 5:
                        sm.answer(g, data)
                        print(f"The answer was [{data.value.get('back', 'No back')}].")  # type: ignore
                        goto_entrance()
                    elif user_input == "D":
                        sm.discard(data)
                        goto_entrance()
                    else:
                        print(
                            "The value should be from '0' (bad) to '5' (good). Otherwise 'D' to discard:"
                        )
                except ValueError:
                    print("Please enter a number from 0 to 5, or 'D' to discard:")

        elif mode[0] == "save":
            if len(mode) == 1:
                print(
                    "Enter file name to save configuration. (default name is [data.json]):"
                )
                mode.append(True)  # type: ignore
            else:
                filename = user_input if user_input else "data.json"
                with open(filename, "w") as f:
                    json.dump(sm.data(), f, indent=2)
                print(f"Saved to {filename}")
                goto_entrance()

        elif mode[0] == "load":
            if len(mode) == 1:
                print(
                    "Enter file name to load configuration. (default name is [data.json]):"
                )
                mode.append(True)  # type: ignore
            else:
                filename = user_input if user_input else "data.json"
                with open(filename, "r") as f:
                    data = json.load(f)
                sm = SM.load(data)
                print(f"Loaded from {filename}")
                goto_entrance()

        elif mode[0] == "exit":
            if len(mode) == 1:
                print("Exiting...")
                break

        elif mode[0] == "eval":
            if len(mode) == 1:
                mode.append(True)  # type: ignore
            else:
                try:
                    result = eval(user_input)
                    print(result)
                except Exception as e:
                    print(f"Error: {e}")
                goto_entrance()

        elif mode[0] == "list":
            for item in sm.q:
                print(json.dumps(item.data()))
            goto_entrance()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"An error occurred: {error}")
        sys.exit(1)
