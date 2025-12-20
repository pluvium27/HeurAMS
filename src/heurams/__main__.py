prompt = """HeurAMS 已经被成功地安装在系统中.
但 HeurAMS 被设计为一个带有辅助记忆调度器功能的软件包, 无法直接被执行, 但可被其他 Python 程序调用.
若您想启动内置的基本用户界面,
 请运行 python -m heurams.interface,
 或者 python -m heurams.interface.__main__
注意: 一个常见的误区是, 执行 interface 下的 __main__.py 运行基本用户界面, 这会导致 Python 上下文环境异常, 请不要这样做."""
print(prompt)
