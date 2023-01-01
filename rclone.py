import subprocess
import time
from queue import Queue, Empty
from threading import Thread


def copy(source, destination, handle_output_line_function, handle_error_line_function):
    process = subprocess.Popen(
        ["rclone/rclone",
         "copy",
         "--update",
         "--verbose",
         "--transfers", "1",
         "--checkers", "8",
         "--contimeout", "60s",
         "--timeout", "300s",
         "--retries", "3",
         "--low-level-retries", "10",
         "--stats", "1s",
         source,
         destination],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    def enqueue_output(out, queue):
        for read_line in iter(out.readline, b''):
            queue.put(read_line.decode('utf8'))
        out.close()

    std_out_queue = Queue()
    Thread(target=enqueue_output, args=(process.stdout, std_out_queue), daemon=True).start()
    std_err_queue = Queue()
    Thread(target=enqueue_output, args=(process.stderr, std_err_queue), daemon=True).start()

    while True:
        process.poll()
        time.sleep(1)
        while True:
            try:
                line = std_out_queue.get_nowait()
            except Empty:
                break
            else:
                handle_output_line_function(line)

        while True:
            try:
                line = std_err_queue.get_nowait()
            except Empty:
                break
            else:
                handle_error_line_function(line)

        if process.returncode is not None:
            break
