import subprocess
import shlex
import threading
import time
import os

from ..utils import yellow_text, red_text

std_print = print
def print(*args, end='\n'):
    text = [yellow_text(str(arg)) for arg in args]
    std_print("[Mineflayer]", *text, end=end)
def print_error(*args, end='\n'):
    text = [red_text(str(arg)) for arg in args]
    std_print("[Mineflayer Error]", *text, end=end)

class MineflayerManager:
    def __init__(
        self,
        is_printing_mineflayer_info: bool = False,
        wait_interval: float = 0.1
    ):
        self.path = os.path.join(os.path.dirname(__file__), 'mineflayer')
        self.process = None
        self.stdout_thread = None
        self.stderr_thread = None
        self.is_printing_mineflayer_info = is_printing_mineflayer_info
        self.is_running = False
        self.wait_interval = wait_interval

        self.output_filter = [
            'physicTick',
            'GLib-GIO-WARNING',
        ]
        self.version_not_match_filter = [
            'DeprecationWarning',
        ]
    
    def start(self):
        if not self.process or self.process.poll() is not None:
            command = f"node index.js"
            args = shlex.split(command)

            self.process = subprocess.Popen(
                args,
                cwd=self.path,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

            # TODO: Lack of exception handling

            if self.is_printing_mineflayer_info:
                self.stdout_thread = threading.Thread(target=self.listen_stdout)
                if os.name == 'nt':
                    self.stdout_thread.setDaemon(True)
                self.stdout_thread.start()
            
            self.stderr_thread = threading.Thread(target=self.listen_stderr)
            if os.name == 'nt':
                self.stderr_thread.setDaemon(True)
            self.stderr_thread.start()

    def shutdown(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
    
    def listen_stdout(self) :
        print('Start to listen stdout.')
        while True and self.process:
            output = self.process.stdout.readline()
            output_str = output.decode('utf-8', errors='ignore')

            if output == '' or output.isspace() or output_str == '' or output_str.isspace():
                continue
            elif any(substr in output_str for substr in self.version_not_match_filter):
                print_error("Warning: Node.js version is not matched! Please use v18.18.2!")

            # Here must be an independent if statement to avoid program freezing
            if 'started' in output_str:
                self.is_running = True

            print(output_str, end='')

        print("Mineflayer is end.")
    
    def listen_stderr(self) :
        while True and self.process:
            output = self.process.stderr.readline()
            output_str = output.decode('utf-8', errors='ignore')

            if output == '' or output.isspace() or output_str == '' or output_str.isspace():
                continue
            elif any(substr in output_str for substr in self.output_filter):
                continue
            elif any(substr in output_str for substr in self.version_not_match_filter):
                print_error("Warning: Node.js version is not matched! Please use v18.18.2!")

            print(output_str, end='')
    
    def get(self, clear=True) :
        ret = self.stdout[:]
        if clear:
            self.stdout = []
        return ret

    def wait_for_running(self):
        while not self.is_running:
            time.sleep(self.wait_interval)
        self.is_running = False
