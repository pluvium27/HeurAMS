class Evalizer:
    """几乎无副作用的模板系统

    接受环境信息并创建一个模板解析工具, 递归遍历数据结构,
    对 "eval:" 前缀的字符串执行表达式求值. 

    副作用问题: 仅存在于 eval 函数调用. 

    Attributes:
        env: 模板求值时的环境变量字典
    """

    # TODO: 弃用风险极高的 eval
    # TODO: 异步/多线程执行避免堵塞
    def __init__(self, environment: dict) -> None:
        """初始化模板解析器

        Args:
            environment: 模板求值时的环境变量字典
        """
        self.env = environment

    def __call__(self, anyobj):
        """调用入口, 等同于 travel"""
        return self.travel(anyobj)

    def travel(self, anyobj):
        """递归遍历数据结构并展开模板表达式

        支持 list, dict, tuple 的嵌套结构. 
        字符串以 "eval:" 开头时执行表达式求值. 

        Args:
            anyobj: 任意 Python 对象

        Returns:
            展开后的对象
        """
        if isinstance(anyobj, list):
            return list(map(self.travel, anyobj))
        elif isinstance(anyobj, dict):
            return dict(map(self.travel, anyobj.items()))
        elif isinstance(anyobj, tuple):
            return tuple(map(self.travel, anyobj))
        elif isinstance(anyobj, str):
            if anyobj.startswith("eval:"):
                return self.eval_with_env(anyobj[5:])
            else:
                return anyobj
        else:
            return anyobj

    def eval_with_env(self, s: str):
        """在环境变量上下文中执行表达式

        Args:
            s: Python 表达式字符串

        Returns:
            表达式求值结果
        """
        ret = eval(s, globals(), self.env)
        return ret
