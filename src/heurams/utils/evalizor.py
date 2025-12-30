
from typing import Any


class Evalizer():
    def __init__(self, environment: dict) -> None:
        self.env = environment
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        

def do_eval(self):
    """
    执行并以结果替换当前单元的所有 eval 语句
    TODO: 带有限制的 eval, 异步/多线程执行避免堵塞
    """

    # eval 环境设置
    def eval_with_env(s: str):
        default = config_var.get()["puzzles"]
        payload = self.registry["nucleon"].payload
        metadata = self.registry["nucleon"].metadata
        eval_value = eval(s)
        if isinstance(eval_value, (int, float)):
            ret = str(eval_value)
        else:
            ret = eval_value
        return ret