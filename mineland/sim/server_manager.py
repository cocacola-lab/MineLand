'''
ServerManager is used to manage the server process.
'''

import subprocess
import shlex
import threading
import time
import os
import shutil

from ..utils import blue_text, red_text

std_print = print
def print(*args, end='\n'):
    text = [blue_text(str(arg)) for arg in args]
    std_print("[Server]", *text, end=end)
def print_error(*args, end='\n'):
    text = [red_text(str(arg)) for arg in args]
    std_print("[Server Error]", *text, end=end)

# TODO: 多线程管理！ServerManager和MineflayerManager都需要多线程管理！
#       特别是 is_running 和 is_runtick_finished 这两个变量，如果数据不一致的话，会导致整个服务器卡死！

class ServerManager:
    def __init__(
        self,
        max_memory="2G",
        wait_interval: float = 0.1,
        is_printing_server_info: bool = False
    ):
        '''
        Initialize the server manager.

        Args:
            path (str): The path of the server.
            max_memory (str): The maximum memory of the server.
            wait_interval (float): The minimum unit of time for waiting for the server to start and complete a tick.
            is_printing_server_info (bool): Whether to print the server information.
        '''
        self.path = os.path.join(os.path.dirname(__file__), 'server')
        self.max_memory = max_memory
        if max_memory != "2G":
            assert False, "TODO: Only 2G memory is supported for now"
        self.process = None
        self.thread = None
        self.outputs = []
        self.is_running = False
        self.is_runtick_finished = True
        self.wait_interval = wait_interval
        self.is_printing_server_info = is_printing_server_info

        self.output_filter = [
            "[Server thread/INFO]: Server unpaused.",
            "[Server thread/INFO]: commands.pause.pausing",
            "[Server thread/INFO]: Server paused.",
            "[Server thread/INFO]: Saving and pausing game...",
            "[Server thread/INFO]: Saving chunks for level",
            # "[Server thread/INFO]: runtick command started",
            "[Server thread/INFO]: runtick command is finished",
            "commands.pause.unpausing",
            "Teleported",
        ]

        self.another_server_is_running_filter = [
            'Perhaps a server is already running on that port'
        ]

    def select_to_construction_world(self) :
        src_folder = os.path.join(self.path, 'construction_world')
        dst_folder = os.path.join(self.path, 'world')
        if not os.path.exists(src_folder):
            return
        if os.path.exists(dst_folder):
            shutil.rmtree(dst_folder)
        shutil.copytree(src_folder, dst_folder)
        pass


    def select_to_normal_world(self) :
        src_folder = os.path.join(self.path, 'normal_world')
        dst_folder = os.path.join(self.path, 'world')
        if not os.path.exists(src_folder):
            return
        if os.path.exists(dst_folder):
            shutil.rmtree(dst_folder)
        shutil.copytree(src_folder, dst_folder)
        pass

    def start(self):
        if not self.process or self.process.poll() is not None:
            command = f"java -Xmx8G -jar fabric-server-mc.1.19-loader.0.14.18-launcher.0.11.2.jar nogui"
            args = shlex.split(command)

            self.process = subprocess.Popen(
                args,
                cwd=self.path,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )

            # TODO: Lack of exception handling
            
            self.thread = threading.Thread(target=self.listen_outputs)
            if os.name == 'nt':
                self.thread.setDaemon(True)
            self.thread.start()

    def shutdown(self):
        if self.process and self.process.poll() is None:

            # TODO: Send stop command to server (instead of terminate!)
            self.execute("stop")

            self.process.terminate()
            self.process.wait()

    def execute(self, command):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(f"{command}\n".encode()) 
                self.process.stdin.flush()
                print(f"Command '{command}' is sent successfully.")
                return("ok")
            except Exception as e:
                print_error(f"Command '{command}' is failed. Exception: {str(e)}")
                return "", "Exception: " + str(e)
        else:
            print_error(f"Command '{command}' is failed. Server is not running.")
            return "", "Server not running"
    
    def listen_outputs(self) :
        if self.is_printing_server_info:
            print('Start to listen outputs.')
        
        while True and self.process:
            output = self.process.stdout.readline()
            output_str = output.decode('utf-8', errors='ignore')
            
            # should be an independent if statement
            if 'Done' in output_str:
                self.is_running = True
            if 'runtick command is finished now' in output_str:
                self.is_runtick_finished = True

            if output == '' or output.isspace() or output_str == '' or output_str.isspace():
                continue
            elif any(substr in output_str for substr in self.output_filter):
                continue
            elif any(substr in output_str for substr in self.another_server_is_running_filter):
                print_error('Another server is running! You may need to restart MineLand.')

            if self.is_printing_server_info:
                print(output_str, end='')
            self.outputs.append(output_str)

        if self.is_printing_server_info:
            print("Server is end.")
    
    def get(self, clear=True) :
        ret = self.outputs[:]
        if clear:
            self.outputs = []
        return ret
    
    def wait_for_running(self):
        while not self.is_running:
            time.sleep(self.wait_interval)
        self.is_running = False
    
    def wait_for_runtick_finish(self):
        while not self.is_runtick_finished:
            time.sleep(self.wait_interval)
        self.is_runtick_finished = False

# manager = ServerManager()
# result = manager.start()
# print('ok start')
# print(result)
# print(result.stdout)

# while(True) : 
#     # pass
#     x=input().strip()
#     message = manager.get()
#     print(message)
#     # out = manager.execute(x)
#     # print('output is: ' + out)
