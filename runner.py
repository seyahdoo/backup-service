import subprocess
from queue import Queue, Empty
from threading import Thread

class Runner:
    def __init__(self, args: [str]):
        self.return_code = None
        self.is_finished = None
        self.canceled = False
        self.std_out_thread = None
        self.std_err_thread = None

        self.process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        def enqueue_output(out, queue):
            for read_line in iter(out.readline, b''):
                queue.put(read_line.decode())
            out.close()
        
        self.std_out_queue = Queue()
        Thread(target=enqueue_output, args=(self.process.stdout, self.std_out_queue), daemon=True).start()
        self.std_err_queue = Queue()
        Thread(target=enqueue_output, args=(self.process.stderr, self.std_err_queue), daemon=True).start()
        return

    def poll(self):
        self.process.poll()
        if self.process.returncode != None:
            self.return_code = self.process.returncode
            self.is_finished = True

    def read_std_out_lines(self):
        list = []
        while True:
            try:
                list.append(self.std_out_queue.get_nowait())
            except Empty:
                break
        return list

    def read_std_err_lines(self):
        list = []
        while True:
            try:
                list.append(self.std_err_queue.get_nowait())
            except Empty:
                break
        return list

    def kill(self):
        self.canceled = True
        self.is_finished = True
        if self.process.returncode == None:
            self.process.kill()
