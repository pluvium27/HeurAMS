"""
SM-15 接口兼容实现, 基于 SM-15 算法的逆向工程
全局状态保存在文件中, 项目状态通过 algodata 字典传递

基于: https://github.com/slaypni/sm.js
原始 CoffeeScript 代码: (c) 2014 Kazuaki Tanida
MIT 许可证
"""

import datetime
import json
import os
from typing import TypedDict

from heurams.kernel.algorithms.sm15m_calc import (MAX_AF, MIN_AF, NOTCH_AF,
                                                  RANGE_AF, RANGE_REPETITION,
                                                  SM, THRESHOLD_RECALL, Item)

# 全局状态文件路径
_GLOBAL_STATE_FILE = os.path.expanduser("~/.sm15_global_state.json")


def _get_global_sm():
    """获取全局 SM 实例, 从文件加载或创建新的"""
    if os.path.exists(_GLOBAL_STATE_FILE):
        try:
            with open(_GLOBAL_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            sm_instance = SM.load(data)
            return sm_instance
        except Exception:
            # 如果加载失败, 创建新的实例
            pass

    # 创建新的 SM 实例
    sm_instance = SM()
    # 保存初始状态
    _save_global_sm(sm_instance)
    return sm_instance


def _save_global_sm(sm_instance):
    """保存全局 SM 实例到文件"""
    try:
        data = sm_instance.data()
        with open(_GLOBAL_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        # 忽略保存错误
        pass


class SM15MAlgorithm:
    algo_name = "SM-15M"

    class AlgodataDict(TypedDict):
        efactor: float
        real_rept: int
        rept: int
        interval: int
        last_date: int
        next_date: int
        is_activated: int
        last_modify: float

    defaults = {
        "efactor": 2.5,
        "real_rept": 0,
        "rept": 0,
        "interval": 0,
        "last_date": 0,
        "next_date": 0,
        "is_activated": 0,
        "last_modify": 0.0,
    }

    @classmethod
    def _get_timestamp(cls):
        """获取当前时间戳(秒)"""
        return datetime.datetime.now().timestamp()

    @classmethod
    def _get_daystamp(cls):
        """获取当前天数戳(从某个纪元开始的天数)"""
        # 使用与原始 SM-2 相同的纪元：1970-01-01
        now = datetime.datetime.now()
        epoch = datetime.datetime(1970, 1, 1)
        delta = now - epoch
        return delta.days

    @classmethod
    def _algodata_to_item(cls, algodata, sm_instance):
        """将 algodata 转换为 Item 实例"""
        # 从 algodata 获取 SM-2 数据
        sm15_data = algodata.get(cls.algo_name, cls.defaults.copy())

        # 创建 Item 实例
        item = Item(sm_instance)

        # 映射字段
        # efactor -> A-Factor (需要转换)
        efactor = sm15_data.get("efactor", 2.5)
        # SM-2 的 efactor 范围 [1.3, 2.5+], SM-15 的 A-Factor 范围 [1.2, 6.9]
        # 简单线性映射：af = (efactor - 1.3) * (MAX_AF - MIN_AF) / (2.5 - 1.3) + MIN_AF
        # 但 efactor 可能大于 2.5, 所以需要限制
        af = max(MIN_AF, min(MAX_AF, efactor * 2.0))  # 粗略映射
        # 调试
        # print(f"DEBUG: efactor={efactor}, af before set={af}")
        item.af(af)
        # print(f"DEBUG: item.af() after set={item.af()}")

        # rept -> repetition (成功回忆次数)
        rept = sm15_data.get("rept", 0)
        item.repetition = (
            rept - 1 if rept > 0 else -1
        )  # SM-15 中 repetition=-1 表示新项目

        # real_rept -> lapse? 或者忽略
        real_rept = sm15_data.get("real_rept", 0)
        # 可以存储在 value 中或忽略

        # interval -> optimum_interval (需要从天数转换为毫秒)
        interval_days = sm15_data.get("interval", 0)
        if interval_days == 0:
            item.optimum_interval = sm_instance.interval_base
        else:
            item.optimum_interval = interval_days * 24 * 60 * 60 * 1000  # 天转毫秒

        # last_date -> previous_date
        last_date_days = sm15_data.get("last_date", 0)
        if last_date_days > 0:
            epoch = datetime.datetime(1970, 1, 1)
            item.previous_date = epoch + datetime.timedelta(days=last_date_days)

        # next_date -> due_date
        next_date_days = sm15_data.get("next_date", 0)
        if next_date_days > 0:
            epoch = datetime.datetime(1970, 1, 1)
            item.due_date = epoch + datetime.timedelta(days=next_date_days)

        # is_activated 和 last_modify 忽略

        # 将原始 algodata 保存在 value 中以便恢复
        item.value = {
            "front": "SM-15 item",
            "back": "SM-15 item",
            "_sm15_data": sm15_data,
        }

        return item

    @classmethod
    def _item_to_algodata(cls, item, algodata):
        """将 Item 实例状态写回 algodata"""
        if cls.algo_name not in algodata:
            algodata[cls.algo_name] = cls.defaults.copy()

        sm15_data = algodata[cls.algo_name]

        # A-Factor -> efactor (反向映射)
        af = item.af()
        if af is None:
            af = MIN_AF
        # 反向粗略映射
        efactor = max(1.3, min(af / 2.0, 10.0))  # 限制范围
        # 调试
        # print(f"DEBUG: item.af()={af}, computed efactor={efactor}")
        sm15_data["efactor"] = efactor

        # repetition -> rept
        rept = item.repetition + 1 if item.repetition >= 0 else 0
        sm15_data["rept"] = rept

        # real_rept: 递增在 revisor 中处理, 这里保持不变
        # 但如果没有 real_rept 字段, 则初始化为0
        if "real_rept" not in sm15_data:
            sm15_data["real_rept"] = 0

        # optimum_interval -> interval (毫秒转天)
        interval_ms = item.optimum_interval
        if interval_ms == item.sm.interval_base:
            sm15_data["interval"] = 0
        else:
            interval_days = max(0, round(interval_ms / (24 * 60 * 60 * 1000)))
            sm15_data["interval"] = interval_days

        # previous_date -> last_date
        if item.previous_date:
            epoch = datetime.datetime(1970, 1, 1)
            last_date_days = (item.previous_date - epoch).days
            sm15_data["last_date"] = last_date_days
        else:
            sm15_data["last_date"] = 0

        # due_date -> next_date
        if item.due_date:
            epoch = datetime.datetime(1970, 1, 1)
            next_date_days = (item.due_date - epoch).days
            sm15_data["next_date"] = next_date_days
        else:
            sm15_data["next_date"] = 0

        # is_activated: 保持不变或设为1
        if "is_activated" not in sm15_data:
            sm15_data["is_activated"] = 1

        # last_modify: 更新时间戳
        sm15_data["last_modify"] = cls._get_timestamp()

        return algodata

    @classmethod
    def revisor(
        cls, algodata: dict, feedback: int = 5, is_new_activation: bool = False
    ):
        """SM-15 算法迭代决策机制实现"""
        # 获取全局 SM 实例
        sm_instance = _get_global_sm()

        # 将 algodata 转换为 Item
        item = cls._algodata_to_item(algodata, sm_instance)

        # 处理 is_new_activation
        if is_new_activation:
            # 重置为初始状态
            item.repetition = -1
            item.lapse = 0
            item.optimum_interval = sm_instance.interval_base
            item.previous_date = None
            item.due_date = datetime.datetime.fromtimestamp(0)
            item.af(2.5)  # 重置 efactor

        # 将项目临时添加到 SM 实例(以便 answer 更新共享状态)
        sm_instance.q.append(item)

        # 处理反馈(评分)
        # SM-2 的 feedback 是 0-5, SM-15 的 grade 也是 0-5
        grade = feedback
        now = datetime.datetime.now()

        # 调用 answer 方法
        item.answer(grade, now)

        # 更新共享状态(FI-Graph, ForgettingCurves, OFM)
        if item.repetition >= 0:
            sm_instance.forgetting_curves.register_point(grade, item, now)
            sm_instance.ofm.update()
            sm_instance.fi_g.update(grade, item, now)

        # 从队列中移除项目
        sm_instance.q.remove(item)

        # 保存全局状态
        _save_global_sm(sm_instance)

        # 将更新后的 Item 状态写回 algodata
        cls._item_to_algodata(item, algodata)

        # 更新 real_rept(总复习次数)
        algodata[cls.algo_name]["real_rept"] += 1

    @classmethod
    def is_due(cls, algodata):
        """检查项目是否到期"""
        sm15_data = algodata.get(cls.algo_name, cls.defaults.copy())
        next_date_days = sm15_data.get("next_date", 0)
        current_daystamp = cls._get_daystamp()
        return next_date_days <= current_daystamp

    @classmethod
    def rate(cls, algodata):
        """获取项目的评分(返回 efactor 字符串)"""
        sm15_data = algodata.get(cls.algo_name, cls.defaults.copy())
        efactor = sm15_data.get("efactor", 2.5)
        return str(efactor)

    @classmethod
    def nextdate(cls, algodata) -> int:
        """获取下次复习日期(天数戳)"""
        sm15_data = algodata.get(cls.algo_name, cls.defaults.copy())
        next_date_days = sm15_data.get("next_date", 0)
        return next_date_days
