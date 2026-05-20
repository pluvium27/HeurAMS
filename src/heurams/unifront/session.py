"""复习会话管理"""

import uuid
import inspect

import heurams.kernel.particles as pt
import heurams.kernel.reactor as rt
import heurams.kernel.puzzles as puz
from heurams.context import config_var
from heurams.kernel.repolib.repo import Repo
from heurams.services.logger import get_logger

logger = get_logger(__name__)

# 已知谜题类型及其构造参数白名单
_PUZZLE_PARAM_MAP = {
    "MCQPuzzle": {"mapping", "jammer", "max_riddles_num", "prefix"},
    "ClozePuzzle": {"text", "min_denominator", "delimiter"},
    "RecognitionPuzzle": set(),
}


class SessionError(Exception):
    """会话错误"""


class Session:
    """管理单次复习会话的生命周期"""

    def __init__(self, repo: Repo):
        self.id = str(uuid.uuid4())[:8]
        self.repo = repo
        self.router: rt.Router | None = None
        self.procession: rt.Procession | None = None
        self.expander: rt.Expander | None = None
        self.finished = False

    def start(self, scheduled_num: int = -1):
        """开始复习，创建 Router and 处理第一个阶段"""
        if scheduled_num == -1:
            scheduled_num = config_var.get()["interface"]["global"]["scheduled_num"]

        atoms = self._build_atoms()
        atoms_to_provide = self._filter_atoms(atoms, scheduled_num)
        if not atoms_to_provide:
            raise SessionError("没有待复习的原子")

        self.router = rt.Router(atoms_to_provide)
        self._advance()
        logger.debug("会话 %s 启动，原子数 %d", self.id, len(atoms_to_provide))

    def _build_atoms(self) -> list[pt.Atom]:
        """从 repo 构建所有原子"""
        atoms = []
        for i in self.repo.ident_index:
            n = pt.Nucleon.from_data(
                nucleonic_data=self.repo.nucleonic_data_lict.get_itemic_unit(i)
            )
            e = pt.Electron.from_data(
                electronic_data=self.repo.electronic_data_lict.get_itemic_unit(i),
                algo_name=self.repo.config["algorithm"],
            )
            a = pt.Atom(n, e, self.repo.orbitic_data)
            atoms.append(a)
        return atoms

    def _filter_atoms(self, atoms: list[pt.Atom], scheduled_num: int) -> list[pt.Atom]:
        """筛选出待复习和新记忆的原子"""
        result = []
        left_new = scheduled_num
        for atom in atoms:
            if atom.registry["electron"].is_activated():
                if atom.registry["electron"].is_due():
                    result.append(atom)
            else:
                left_new -= 1
                if left_new >= 0:
                    result.append(atom)
        return result

    @property
    def progress(self) -> dict:
        """当前复习进度"""
        if not self.procession:
            return {"phase": "unknown", "current": 0, "total": 0}
        return {
            "phase": self.procession.route.value,
            "current": self.procession.process() + 1,
            "total": self.procession.total_length(),
        }

    def _advance(self) -> bool:
        """推进到下一个阶段/原子。返回 False 表示全部完成"""
        if not self.router:
            return False

        self.procession = self.router.current_procession()
        if self.procession.route == rt.RouterState.FINISHED:
            # 全部完成
            self.finished = True
            self._persist()
            return False

        self.expander = self.procession.get_expander()
        return True

    def get_current_puzzle(self) -> dict | None:
        """获取当前谜题的可序列化数据"""
        if self.finished or not self.expander or not self.procession:
            return None

        puzzle_inf = self.expander.get_current_puzzle_inf()
        puzzle_class = puzzle_inf["puzzle"]
        alia = puzzle_inf["alia"]
        atom = self.procession.current_atom

        if self.expander.state == "retronly":
            return {
                "category": "recognition",
                "alia": alia,
                "atom_ident": atom.ident,
                "phase": self.procession.route.value,
                "puzzle": {
                    "content": atom.registry["nucleon"].get("content", ""),
                    "tts_text": atom.registry["nucleon"].get("tts_text", ""),
                },
            }

        # 通过 atom 配置构造并刷新谜题
        puzzle_cfg = atom.registry["nucleon"]["puzzles"].get(alia, {})
        try:
            # 过滤出 puzzle 构造器接受的参数
            sig = inspect.signature(puzzle_class.__init__)
            valid_params = set(sig.parameters.keys()) - {"self"}
            filtered_cfg = {}
            for k, v in puzzle_cfg.items():
                if k not in valid_params:
                    continue
                # TOML/Evalizer 可能返回字符串，尝试类型转换
                if isinstance(v, str):
                    vs = v.strip()
                    try:
                        v = int(vs) if vs.isdigit() or (vs.startswith('-') and vs[1:].isdigit()) else float(vs)
                    except (ValueError, TypeError):
                        v = vs
                filtered_cfg[k] = v
            puz_instance = puzzle_class(**filtered_cfg) if filtered_cfg else puzzle_class()
            puz_instance.refresh()
        except Exception as e:
            logger.warning("谜题生成失败 %s: %s", alia, e)
            return {
                "category": "unknown",
                "alia": alia,
                "atom_ident": atom.ident,
                "phase": self.procession.route.value,
                "puzzle": {"error": str(e)},
            }

        alias = puzzle_class.__name__.lower().replace("puzzle", "")
        data = {
            "category": alias,
            "alia": alia,
            "atom_ident": atom.ident,
            "phase": self.procession.route.value,
            "puzzle": self._serialize_puzzle(puz_instance),
        }
        return data

    def _serialize_puzzle(self, puz) -> dict:
        """将谜题对象序列化为字典"""
        data = {}
        if hasattr(puz, "wording"):
            data["wording"] = puz.wording
        if hasattr(puz, "answer"):
            data["answer"] = puz.answer
        if hasattr(puz, "options"):
            data["options"] = puz.options
        if hasattr(puz, "prefix"):
            data["primary"] = getattr(puz, "prefix", "")
        if hasattr(puz, "primary"):
            # 对于 MCQ，从 atom puzzle config 获取 primary
            pass
        # 补充 primary/提示字段
        atom = self.procession.current_atom if self.procession else None
        if atom:
            alia = self.expander.get_current_puzzle_inf()["alia"] if self.expander else ""
            cfg = atom.registry["nucleon"]["puzzles"].get(alia, {})
            if "primary" in cfg:
                data["primary"] = cfg["primary"]
        return data

    def rate(self, rating: int) -> bool:
        """评分当前谜题并推进，返回 False 表示所有流程完成"""
        if self.finished or not self.expander or not self.procession:
            return False

        self.expander.report(rating)

        # 决定是否向前推进（SM-2 尺度：>=4 表示正确）
        if rating >= 4:
            self.expander.forward()

        # 如果是 retronly 阶段，处理原子完成
        if self.expander.state == "retronly":
            quality = self.expander.get_quality()
            atom = self.procession.current_atom

            # 报告评分给原子
            if not atom.registry["electron"].is_activated():
                atom.registry["electron"].activate()
                atom.lock(1)
                atom.minimize(5)
            else:
                atom.minimize(quality)

            # 若质量差则放回队列
            if quality <= 3 and atom:
                self.procession.append()

            # 前进到下一个原子
            self.procession.forward(1)
            self._advance()

        # 检查当前阶段的 Procession 是否已完成
        if self.procession and self.procession.state == rt.ProcessionState.FINISHED.value:
            self._advance()

        return not self.finished

    def _persist(self):
        """保存 algodata 到文件"""
        try:
            self.repo.persist_to_repodir()
            logger.debug("会话 %s: algodata 已持久化", self.id)
        except Exception as e:
            logger.warning("持久化失败: %s", e)

    def cleanup(self):
        """清理会话"""
        self.router = None
        self.procession = None
        self.expander = None
        logger.debug("会话 %s 已清理", self.id)
