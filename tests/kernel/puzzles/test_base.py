import unittest
from unittest.mock import Mock

from heurams.kernel.evaluators.base import BasePuzzle


class TestBasePuzzle(unittest.TestCase):
    """测试 BasePuzzle 基类"""

    def test_refresh_not_implemented(self):
        """测试 refresh 方法未实现时抛出异常"""
        puzzle = BasePuzzle()
        with self.assertRaises(NotImplementedError):
            puzzle.refresh()

    def test_str(self):
        """测试 __str__ 方法"""
        puzzle = BasePuzzle()
        self.assertEqual(str(puzzle), "谜题: BasePuzzle")


if __name__ == "__main__":
    unittest.main()
