from heurams.interface import *
from heurams.context import config_var
from heurams.i18n import _
from heurams.services.logger import get_logger
import threading
import pickle

logger = get_logger(__name__)


def start_debug_server(app):
    import zmq
    logger = get_logger("zmq_debug")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    port = config_var.get()["global"].get("zmq_debug_port", 5555)
    socket.bind(f"tcp://*:{port}")
    logger.info(f"ZMQ Debug server started on port {port}")
    first = 1
    while True:
        msg = socket.recv()
        code = pickle.loads(msg)
        namespace = {"app": app, "logger": logger, "config_var": config_var}
        if first:
            app.title += _(" [Debug Connected]")
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

    app = HeurAMSApp()

    if config_var.get()["global"].get("zmq_debug", False):
        threading.Thread(target=start_debug_server, args=(app,), daemon=True).start()

    app.run(inline=False)


if __name__ == "__main__":
    main()
