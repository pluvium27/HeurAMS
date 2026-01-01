import unittest
from unittest.mock import MagicMock, Mock, patch

from heurams.kernel.particles.atom import Atom
from heurams.kernel.particles.electron import Electron
from heurams.kernel.reactor.procession import Phaser
from heurams.kernel.reactor.states import PhaserState, ProcessionState


class TestPhaser(unittest.TestCase):
    """测试 Phaser 类"""

    def setUp(self):
        # 创建模拟的 Atom 对象
        self.atom_new = Mock(spec=Atom)
        self.atom_new.registry = {"electron": Mock(spec=Electron)}
        self.atom_new.registry["electron"].is_activated.return_value = False

        self.atom_old = Mock(spec=Atom)
        self.atom_old.registry = {"electron": Mock(spec=Electron)}
        self.atom_old.registry["electron"].is_activated.return_value = True

        # 模拟 Procession 类以避免复杂依赖
        self.procession_patcher = patch("heurams.kernel.reactor.phaser.Procession")
        self.mock_procession_class = self.procession_patcher.start()

    def tearDown(self):
        self.procession_patcher.stop()

    def test_init_with_mixed_atoms(self):
        """测试混合新旧原子的初始化"""
        atoms = [self.atom_old, self.atom_new, self.atom_old]
        phaser = Phaser(atoms)

        # 应该创建两个 Procession: 一个用于旧原子, 一个用于新原子, 以及一个总体复习
        self.assertEqual(self.mock_procession_class.call_count, 3)

        # 检查调用参数
        calls = self.mock_procession_class.call_args_list
        # 第一个调用应该是旧原子的初始复习
        self.assertEqual(calls[0][0][0], [self.atom_old, self.atom_old])
        self.assertEqual(calls[0][0][1], PhaserState.QUICK_REVIEW)
        # 第二个调用应该是新原子的识别阶段
        self.assertEqual(calls[1][0][0], [self.atom_new])
        self.assertEqual(calls[1][0][1], PhaserState.RECOGNITION)
        # 第三个调用应该是所有原子的总体复习
        self.assertEqual(calls[2][0][0], atoms)
        self.assertEqual(calls[2][0][1], PhaserState.FINAL_REVIEW)

    def test_init_only_old_atoms(self):
        """测试只有旧原子"""
        atoms = [self.atom_old, self.atom_old]
        phaser = Phaser(atoms)

        # 应该创建两个 Procession: 一个初始复习, 一个总体复习
        self.assertEqual(self.mock_procession_class.call_count, 2)
        calls = self.mock_procession_class.call_args_list
        self.assertEqual(calls[0][0][0], atoms)
        self.assertEqual(calls[0][0][1], PhaserState.QUICK_REVIEW)
        self.assertEqual(calls[1][0][0], atoms)
        self.assertEqual(calls[1][0][1], PhaserState.FINAL_REVIEW)

    def test_init_only_new_atoms(self):
        """测试只有新原子"""
        atoms = [self.atom_new, self.atom_new]
        phaser = Phaser(atoms)

        self.assertEqual(self.mock_procession_class.call_count, 2)
        calls = self.mock_procession_class.call_args_list
        self.assertEqual(calls[0][0][0], atoms)
        self.assertEqual(calls[0][0][1], PhaserState.RECOGNITION)
        self.assertEqual(calls[1][0][0], atoms)
        self.assertEqual(calls[1][0][1], PhaserState.FINAL_REVIEW)

    def test_current_procession_finds_unfinished(self):
        """测试 current_procession 找到未完成的 Procession"""
        # 创建模拟 Procession 实例
        mock_proc1 = Mock()
        mock_proc1.state = ProcessionState.FINISHED
        mock_proc2 = Mock()
        mock_proc2.state = ProcessionState.RUNNING
        mock_proc2.phase = PhaserState.QUICK_REVIEW

        phaser = Phaser([])
        phaser.processions = [mock_proc1, mock_proc2]

        result = phaser.current_procession()
        self.assertEqual(result, mock_proc2)
        self.assertEqual(phaser.state, PhaserState.QUICK_REVIEW)

    def test_current_procession_all_finished(self):
        """测试所有 Procession 都完成"""
        mock_proc = Mock()
        mock_proc.state = ProcessionState.FINISHED

        phaser = Phaser([])
        phaser.processions = [mock_proc]

        result = phaser.current_procession()
        self.assertEqual(result, 0)
        self.assertEqual(phaser.state, PhaserState.FINISHED)

    def test_current_procession_empty(self):
        """测试没有 Procession"""
        phaser = Phaser([])
        phaser.processions = []

        result = phaser.current_procession()
        self.assertEqual(result, 0)
        self.assertEqual(phaser.state, PhaserState.FINISHED)


if __name__ == "__main__":
    unittest.main()
