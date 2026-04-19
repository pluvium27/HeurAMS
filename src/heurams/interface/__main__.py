from heurams.interface import *
from heurams.context import config_var
from heurams.services.logger import get_logger
import threading
import zmq
import pickle

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

def start_debug_server(app):
    logger = get_logger("zmq_debug")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    port = config_var.get()['global'].get('zmq_debug_port', 5555)
    socket.bind(f"tcp://*:{port}")
    logger.info(f"ZMQ Debug server started on port {port}")
    first = 1
    while True:
        msg = socket.recv()
        code = pickle.loads(msg)
        namespace = {"app": app, "logger": logger, "config_var": config_var}
        if first:
            app.title += ' [调试已连接]'
            first = 0
        try:
            # 先尝试 eval
            result = eval(code, namespace)
            socket.send(pickle.dumps(f"成功: {result}"))
        except SyntaxError:
            # 再尝试 exec
            try:
                exec(code, namespace)
                socket.send(pickle.dumps(f"成功: 执行完成"))
            except Exception as e:
                socket.send(pickle.dumps(f"错误: {e}"))
        except Exception as e:
            socket.send(pickle.dumps(f"错误: {e}"))

def main():
    environment_check()
    
    app = HeurAMSApp()
    
    if config_var.get()['global'].get('zmq_debug', False):
        threading.Thread(target=start_debug_server, args=(app,), daemon=True).start()
    
    app.run(inline=False)

if __name__ == "__main__":
    main()