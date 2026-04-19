from heurams.interface import *
from heurams.context import config_var
from heurams.services.logger import get_logger

logger = get_logger(__name__)

def environment_check():
    from pathlib import Path

    logger.debug("检查环境路径")
    subdir = ["cache/voice", "repo", "global", "config"]
    for i in subdir:
        i = Path(config_var.get()["global"]["paths"]["data"]) / i
        if not i.exists():
            logger.info("创建目录: %s", i)
            print(f"创建 {i}")
            i.mkdir(exist_ok=True, parents=True)
        else:
            logger.debug("目录已存在: %s", i)
            print(f"找到 {i}")
    logger.debug("环境检查完成")

def main():
    environment_check()
    app = HeurAMSApp()
    app.run(inline=False)

if __name__ == "__main__":
    main()