import heurams.services.version as ver


# __main__.py
def main():
    prompt = f"""HeurAMS {ver.ver} 已经被成功地安装在系统中.
HeurAMS 被设计为一个带有辅助记忆调度器功能的软件包, 无法直接被执行, 但可被其他 Python 程序调用.
若您想启动内置的基本用户界面:
 请运行 python -m heurams.interface,
 或者 python -m heurams.interface.__main__
python 代指您使用的解释器, 在某些发行版中可能是 python3, 而 python 命令被指向了 python2.
尽管项目保留了 requirements.txt, 我们仍不推荐使用系统 python 和原始 venv 进行开发.
项目的推荐开发环境工具是 uv.
如果你的环境已经安装了 uv:
 先运行 uv sync --all-extras 同步环境, 此命令只需要执行一遍, uv 会自动处理依赖.
 然后通过运行 uv run heurams-tui 启动内置基本用户界面.
 此时您的解释器在项目目录里的 .venv/bin 中, 使用 IDE 开发前, 务必切换解释器!
注意: 一个常见的误区是, 执行 interface 下的 __main__.py 运行基本用户界面, 这会导致 Python 上下文环境异常, 请不要这样做."""
    print(prompt)


if __name__ == "__main__":
    main()