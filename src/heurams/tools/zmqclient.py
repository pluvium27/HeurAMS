import zmq
import pickle
import readline
import sys


class DebugClient:
    def __init__(self, port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")
        print(f"已连接到调试服务器 (端口 {port})")
        print("输入Python代码并按回车执行, 输入 'exit' 退出")
        print("可用变量: app, logger")
        print("-" * 50)

    def execute(self, code):
        """执行代码并返回结果"""
        try:
            self.socket.send(pickle.dumps(code))
            response = pickle.loads(self.socket.recv())
            return response
        except Exception as e:
            return f"连接错误: {e}"

    def repl(self):
        """交互式REPL循环"""
        self.execute('print("test")')
        while True:
            try:
                # 获取用户输入
                code = input(">>> ").strip()

                if not code:
                    continue

                if code.lower() in ["exit", "quit"]:
                    print("退出调试客户端")
                    break

                # 执行代码
                result = self.execute(code)
                print(f"结果: {result}\n")

            except KeyboardInterrupt:
                print("\n退出调试客户端")
                break
            except EOFError:
                break


if __name__ == "__main__":
    # 从命令行参数获取端口
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5555

    client = DebugClient(port)
    client.repl()
