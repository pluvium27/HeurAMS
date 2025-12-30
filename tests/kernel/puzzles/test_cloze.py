import unittest
from unittest.mock import MagicMock, patch

from heurams.kernel.evaluators.cloze import ClozePuzzle


class TestClozePuzzle(unittest.TestCase):
    """测试 ClozePuzzle 类"""

    def test_init(self):
        """测试初始化"""
        puzzle = ClozePuzzle("hello/world/test", min_denominator=3, delimiter="/")
        self.assertEqual(puzzle.text, "hello/world/test")
        self.assertEqual(puzzle.min_denominator, 3)
        self.assertEqual(puzzle.delimiter, "/")
        self.assertEqual(puzzle.wording, "填空题 - 尚未刷新谜题")
        self.assertEqual(puzzle.answer, ["填空题 - 尚未刷新谜题"])

    @patch("random.sample")
    def test_refresh(self, mock_sample):
        """测试 refresh 方法"""
        mock_sample.return_value = [0, 2]  # 选择索引 0 和 2
        puzzle = ClozePuzzle("hello/world/test", min_denominator=2, delimiter="/")
        puzzle.refresh()

        # 检查 wording 和 answer
        self.assertNotEqual(puzzle.wording, "填空题 - 尚未刷新谜题")
        self.assertNotEqual(puzzle.answer, ["填空题 - 尚未刷新谜题"])
        # 根据模拟, 应该有两个填空
        self.assertEqual(len(puzzle.answer), 2)
        self.assertEqual(puzzle.answer, ["hello", "test"])
        # wording 应包含下划线
        self.assertIn("__", puzzle.wording)

    def test_refresh_empty_text(self):
        """测试空文本的 refresh"""
        puzzle = ClozePuzzle("", min_denominator=3, delimiter="/")
        puzzle.refresh()  # 不应引发异常
        # 空文本导致 wording 和 answer 为空
        self.assertEqual(puzzle.wording, "")
        self.assertEqual(puzzle.answer, [])

    def test_str(self):
        """测试 __str__ 方法"""
        puzzle = ClozePuzzle("hello/world", min_denominator=2, delimiter="/")
        str_repr = str(puzzle)
        self.assertIn("填空题 - 尚未刷新谜题", str_repr)


if __name__ == "__main__":
    unittest.main()
