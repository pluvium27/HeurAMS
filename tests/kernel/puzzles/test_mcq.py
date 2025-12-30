import unittest
from unittest.mock import MagicMock, call, patch

from heurams.kernel.evaluators.mcq import MCQPuzzle


class TestMCQPuzzle(unittest.TestCase):
    """测试 MCQPuzzle 类"""

    def test_init(self):
        """测试初始化"""
        mapping = {"q1": "a1", "q2": "a2"}
        jammer = ["j1", "j2", "j3"]
        puzzle = MCQPuzzle(mapping, jammer, max_riddles_num=3, prefix="选择")
        self.assertEqual(puzzle.prefix, "选择")
        self.assertEqual(puzzle.mapping, mapping)
        self.assertEqual(puzzle.max_riddles_num, 3)
        # jammer 应合并正确答案并去重
        self.assertIn("a1", puzzle.jammer)
        self.assertIn("a2", puzzle.jammer)
        self.assertIn("j1", puzzle.jammer)
        # 初始状态
        self.assertEqual(puzzle.wording, "选择题 - 尚未刷新谜题")
        self.assertEqual(puzzle.answer, ["选择题 - 尚未刷新谜题"])
        self.assertEqual(puzzle.options, [])

    def test_init_max_riddles_num_clamping(self):
        """测试 max_riddles_num 限制在 1-5 之间"""
        puzzle1 = MCQPuzzle({}, [], max_riddles_num=0)
        self.assertEqual(puzzle1.max_riddles_num, 1)
        puzzle2 = MCQPuzzle({}, [], max_riddles_num=10)
        self.assertEqual(puzzle2.max_riddles_num, 5)

    def test_init_jammer_ensures_minimum(self):
        """测试干扰项至少保证 4 个"""
        puzzle = MCQPuzzle({}, [])
        # 正确答案为空, 干扰项为空, 应填充空格
        self.assertEqual(len(puzzle.jammer), 4)
        self.assertEqual(set(puzzle.jammer), {"   "})  # 三个空格? 实际上循环填充空格

    @patch("random.sample")
    @patch("random.shuffle")
    def test_refresh(self, mock_shuffle, mock_sample):
        """测试 refresh 方法生成题目"""
        mapping = {"q1": "a1", "q2": "a2", "q3": "a3"}
        jammer = ["j1", "j2", "j3", "j4"]
        puzzle = MCQPuzzle(mapping, jammer, max_riddles_num=2)
        # 模拟 random.sample 返回前两个映射项
        mock_sample.side_effect = [
            [("q1", "a1"), ("q2", "a2")],  # 选择问题
            ["j1", "j2", "j3"],  # 为每个问题选择干扰项(实际调用两次)
        ]
        puzzle.refresh()

        # 检查 wording 是列表
        self.assertIsInstance(puzzle.wording, list)
        self.assertEqual(len(puzzle.wording), 2)
        # 检查 answer 列表
        self.assertEqual(puzzle.answer, ["a1", "a2"])
        # 检查 options 列表
        self.assertEqual(len(puzzle.options), 2)
        # 每个选项列表应包含 4 个选项(正确答案 + 3 个干扰项)
        self.assertEqual(len(puzzle.options[0]), 4)
        self.assertEqual(len(puzzle.options[1]), 4)
        # random.shuffle 应被调用
        self.assertEqual(mock_shuffle.call_count, 2)

    def test_refresh_empty_mapping(self):
        """测试空 mapping 的 refresh"""
        puzzle = MCQPuzzle({}, [])
        puzzle.refresh()
        self.assertEqual(puzzle.wording, "无可用题目")
        self.assertEqual(puzzle.answer, ["无答案"])
        self.assertEqual(puzzle.options, [])

    def test_get_question_count(self):
        """测试 get_question_count 方法"""
        puzzle = MCQPuzzle({"q": "a"}, [])
        self.assertEqual(puzzle.get_question_count(), 0)  # 未刷新
        puzzle.refresh = MagicMock()
        puzzle.wording = ["Q1", "Q2"]
        self.assertEqual(puzzle.get_question_count(), 2)
        puzzle.wording = "无可用题目"
        self.assertEqual(puzzle.get_question_count(), 0)
        puzzle.wording = "单个问题"
        self.assertEqual(puzzle.get_question_count(), 1)

    def test_get_correct_answer_for_question(self):
        """测试 get_correct_answer_for_question 方法"""
        puzzle = MCQPuzzle({}, [])
        puzzle.answer = ["ans1", "ans2"]
        self.assertEqual(puzzle.get_correct_answer_for_question(0), "ans1")
        self.assertEqual(puzzle.get_correct_answer_for_question(1), "ans2")
        self.assertIsNone(puzzle.get_correct_answer_for_question(2))
        puzzle.answer = "not a list"
        self.assertIsNone(puzzle.get_correct_answer_for_question(0))

    def test_get_options_for_question(self):
        """测试 get_options_for_question 方法"""
        puzzle = MCQPuzzle({}, [])
        puzzle.options = [["a", "b", "c", "d"], ["e", "f", "g", "h"]]
        self.assertEqual(puzzle.get_options_for_question(0), ["a", "b", "c", "d"])
        self.assertEqual(puzzle.get_options_for_question(1), ["e", "f", "g", "h"])
        self.assertIsNone(puzzle.get_options_for_question(2))

    def test_str(self):
        """测试 __str__ 方法"""
        puzzle = MCQPuzzle({}, [])
        puzzle.wording = "选择题 - 尚未刷新谜题"
        puzzle.answer = ["选择题 - 尚未刷新谜题"]
        self.assertIn("选择题 - 尚未刷新谜题", str(puzzle))
        self.assertIn("正确答案", str(puzzle))

        puzzle.wording = ["Q1", "Q2"]
        puzzle.answer = ["A1", "A2"]
        str_repr = str(puzzle)
        self.assertIn("Q1", str_repr)
        self.assertIn("A1, A2", str_repr)


if __name__ == "__main__":
    unittest.main()
