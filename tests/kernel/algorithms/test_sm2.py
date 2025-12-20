import unittest
from unittest.mock import MagicMock, patch

from heurams.kernel.algorithms.sm2 import SM2Algorithm


class TestSM2Algorithm(unittest.TestCase):
    """测试 SM2Algorithm 类"""

    def setUp(self):
        # 模拟 timer 函数
        self.timestamp_patcher = patch(
            "heurams.kernel.algorithms.sm2.timer.get_timestamp"
        )
        self.daystamp_patcher = patch(
            "heurams.kernel.algorithms.sm2.timer.get_daystamp"
        )
        self.mock_get_timestamp = self.timestamp_patcher.start()
        self.mock_get_daystamp = self.daystamp_patcher.start()

        # 设置固定返回值
        self.mock_get_timestamp.return_value = 1000.0
        self.mock_get_daystamp.return_value = 100

    def tearDown(self):
        self.timestamp_patcher.stop()
        self.daystamp_patcher.stop()

    def test_defaults(self):
        """测试默认值"""
        defaults = SM2Algorithm.defaults
        self.assertEqual(defaults["efactor"], 2.5)
        self.assertEqual(defaults["real_rept"], 0)
        self.assertEqual(defaults["rept"], 0)
        self.assertEqual(defaults["interval"], 0)
        self.assertEqual(defaults["last_date"], 0)
        self.assertEqual(defaults["next_date"], 0)
        self.assertEqual(defaults["is_activated"], 0)
        # last_modify 是动态的, 仅检查存在性
        self.assertIn("last_modify", defaults)

    def test_revisor_feedback_minus_one(self):
        """测试 feedback = -1 时跳过更新"""
        algodata = {SM2Algorithm.algo_name: SM2Algorithm.defaults.copy()}
        SM2Algorithm.revisor(algodata, feedback=-1)
        # 数据应保持不变
        self.assertEqual(algodata[SM2Algorithm.algo_name]["efactor"], 2.5)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["rept"], 0)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["interval"], 0)

    def test_revisor_feedback_less_than_3(self):
        """测试 feedback < 3 重置 rept 和 interval"""
        algodata = {
            SM2Algorithm.algo_name: {
                "efactor": 2.5,
                "rept": 5,
                "interval": 10,
                "real_rept": 3,
            }
        }
        SM2Algorithm.revisor(algodata, feedback=2)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["rept"], 0)
        # rept=0 导致 interval 被设置为 1
        self.assertEqual(algodata[SM2Algorithm.algo_name]["interval"], 1)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["real_rept"], 4)  # 递增

    def test_revisor_feedback_greater_equal_3(self):
        """测试 feedback >= 3 递增 rept"""
        algodata = {
            SM2Algorithm.algo_name: {
                "efactor": 2.5,
                "rept": 2,
                "interval": 6,
                "real_rept": 2,
            }
        }
        SM2Algorithm.revisor(algodata, feedback=4)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["rept"], 3)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["real_rept"], 3)
        # interval 应根据 rept 和 efactor 重新计算
        # rept=3, interval = round(6 * 2.5) = 15
        self.assertEqual(algodata[SM2Algorithm.algo_name]["interval"], 15)

    def test_revisor_new_activation(self):
        """测试 is_new_activation 重置 rept 和 efactor"""
        algodata = {
            SM2Algorithm.algo_name: {
                "efactor": 3.0,
                "rept": 5,
                "interval": 20,
                "real_rept": 5,
            }
        }
        SM2Algorithm.revisor(algodata, feedback=5, is_new_activation=True)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["rept"], 0)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["efactor"], 2.5)
        # interval 应为 1(因为 rept=0)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["interval"], 1)

    def test_revisor_efactor_calculation(self):
        """测试 efactor 计算"""
        algodata = {
            SM2Algorithm.algo_name: {
                "efactor": 2.5,
                "rept": 1,
                "interval": 6,
                "real_rept": 1,
            }
        }
        SM2Algorithm.revisor(algodata, feedback=5)
        # efactor = 2.5 + (0.1 - (5-5)*(0.08 + (5-5)*0.02)) = 2.5 + 0.1 = 2.6
        self.assertAlmostEqual(
            algodata[SM2Algorithm.algo_name]["efactor"], 2.6, places=6
        )

        # 测试 efactor 下限为 1.3
        algodata[SM2Algorithm.algo_name]["efactor"] = 1.2
        SM2Algorithm.revisor(algodata, feedback=5)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["efactor"], 1.3)

    def test_revisor_interval_calculation(self):
        """测试 interval 计算规则"""
        algodata = {
            SM2Algorithm.algo_name: {
                "efactor": 2.5,
                "rept": 0,
                "interval": 0,
                "real_rept": 0,
            }
        }
        SM2Algorithm.revisor(algodata, feedback=4)
        # rept 从 0 递增到 1, 因此 interval 应为 6
        self.assertEqual(algodata[SM2Algorithm.algo_name]["interval"], 6)

        # 现在 rept=1, 再次调用 revisor 递增到 2
        SM2Algorithm.revisor(algodata, feedback=4)
        # rept=2, interval = round(6 * 2.5) = 15
        self.assertEqual(algodata[SM2Algorithm.algo_name]["interval"], 15)

        # 单独测试 rept=1 的情况
        algodata2 = {
            SM2Algorithm.algo_name: {
                "efactor": 2.5,
                "rept": 1,
                "interval": 0,
                "real_rept": 0,
            }
        }
        SM2Algorithm.revisor(algodata2, feedback=4)
        # rept 递增到 2, interval = round(0 * 2.5) = 0
        self.assertEqual(algodata2[SM2Algorithm.algo_name]["interval"], 0)

    def test_revisor_updates_dates(self):
        """测试更新日期字段"""
        algodata = {SM2Algorithm.algo_name: SM2Algorithm.defaults.copy()}
        self.mock_get_daystamp.return_value = 200
        SM2Algorithm.revisor(algodata, feedback=5)
        self.assertEqual(algodata[SM2Algorithm.algo_name]["last_date"], 200)
        self.assertEqual(
            algodata[SM2Algorithm.algo_name]["next_date"],
            200 + algodata[SM2Algorithm.algo_name]["interval"],
        )
        self.assertEqual(algodata[SM2Algorithm.algo_name]["last_modify"], 1000.0)

    def test_is_due(self):
        """测试 is_due 方法"""
        algodata = {SM2Algorithm.algo_name: {"next_date": 100}}
        self.mock_get_daystamp.return_value = 150
        self.assertTrue(SM2Algorithm.is_due(algodata))

        algodata[SM2Algorithm.algo_name]["next_date"] = 200
        self.assertFalse(SM2Algorithm.is_due(algodata))

    def test_rate(self):
        """测试 rate 方法"""
        algodata = {SM2Algorithm.algo_name: {"efactor": 2.7}}
        self.assertEqual(SM2Algorithm.rate(algodata), "2.7")

    def test_nextdate(self):
        """测试 nextdate 方法"""
        algodata = {SM2Algorithm.algo_name: {"next_date": 12345}}
        self.assertEqual(SM2Algorithm.nextdate(algodata), 12345)


if __name__ == "__main__":
    unittest.main()
