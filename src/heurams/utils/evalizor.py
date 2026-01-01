class Evalizer:
    """几乎无副作用的模板系统

    接受环境信息并创建一个模板解析工具, 工具传入参数支持list, dict及其嵌套
    副作用问题: 仅存在于 eval 函数
    """

    # TODO: 弃用风险极高的 eval
    # 理论上已经限制了全局函数 但eval仍有风险
    # TODO: 异步/多线程执行避免堵塞
    def __init__(self, environment: dict) -> None:
        self.env = environment

    def __call__(self, anyobj):
        return self.travel(anyobj)

    def travel(self, anyobj):
        if isinstance(anyobj, list):
            return list(map(self.travel, anyobj))
        elif isinstance(anyobj, dict):
            return dict(map(self.travel, anyobj.items()))
        elif isinstance(anyobj, str):
            if anyobj.startswith("eval:"):
                return self.eval_with_env(anyobj[5:])
            else:
                return anyobj
        else:
            return anyobj

    def eval_with_env(self, s: str):
        ret = eval(s, {}, self.env)
        if not isinstance(ret, str):
            ret = str(ret)
        return ret
