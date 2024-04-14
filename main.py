import subprocess
import threading
import time
from enum import Enum
from threading import Thread
from mail import send_mail_to_myself
from infi.systray import SysTrayIcon
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='backup-service.log', level=logging.INFO)
quit_event = threading.Event()

class State(Enum):
    Idle = 1
    Syncing = 2
    Error = 3

TRAY_TEXT = "Backup Service"

class SyncThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lock = threading.Lock()
        self.canceled = False
        self.last_sync_time = 0
    
    def run(self):
        while not self.canceled:
            if time.time() > self.last_sync_time + (60 * 60):
                self.do_sync()
            time.sleep(1)
            
    def do_sync(self):
        with self.lock:
            self.last_sync_time = time.time()
            icon_update(State.Syncing)
            return_code = self.sync("C:/Users/seyyid/Videos", "Z:/beast/Videos")
            if return_code != 0:
                icon_update(State.Error)
                # send_mail_to_myself("ERROR on Backup Service", "backup task failed, please check logs")
            else:
                icon_update(State.Idle)
    
    def sync(self, source, destination):
        process = subprocess.Popen(
            ["rclone/rclone",
             "copy",
             "--update",
             "--transfers", "1",
             "--checkers", "8",
             "--contimeout", "60s",
             "--timeout", "300s",
             "--retries", "3",
             "--low-level-retries", "10",
             "--config", "NUL",
             "--verbose",
             "--stats", "1",
             "--stats-one-line",
             source,
             destination],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        
        while not self.canceled:
            time.sleep(1)
            process.poll()
            for line in process.stdout.readlines():
                logger.info(line)
            for line in process.stderr.readlines():
                logger.error(line)
            if process.returncode is not None:
                return process.returncode
    
class IconThread(Thread):
    def __init__(self, state:State):
        Thread.__init__(self)
        self.canceled = False
        self.state = state
        self.animation_time = 0

    def run(self):
        while not self.canceled:
            self.update_visual()
            time.sleep(1)
            
    def set_state(self, state:State):
        self.animation_time = 0
        self.state = state
        
    def update_visual(self):
        match self.state:
            case State.Idle:
                if self.animation_time == 0:
                    systray.update("tray_icons/idle.ico", TRAY_TEXT)
            case State.Syncing:
                index = self.animation_time % 3
                systray.update(f"tray_icons/syncing{index}.ico", TRAY_TEXT)
            case State.Error:
                index = self.animation_time % 2
                systray.update(f"tray_icons/error{index}.ico", TRAY_TEXT)
        self.animation_time += 1
        return 
    
def icon_update(state:State):
    icon_update_thread.set_state(state)    

def sync_now(systray:SysTrayIcon):
    sync_thread.do_sync()

def on_quit_callback(systray:SysTrayIcon):
    quit_event.set()
    
if __name__ == '__main__':
    menu_options = (("Sync Now", None, sync_now),)
    systray = SysTrayIcon("tray_icons/idle.ico", TRAY_TEXT, menu_options, on_quit=on_quit_callback)
    systray.start()
    icon_update_thread:IconThread = IconThread(State.Idle)
    icon_update_thread.start()
    sync_thread:SyncThread = SyncThread()
    sync_thread.start()
        
    quit_event.wait()
    
    icon_update_thread.canceled = True
    sync_thread.canceled = True
    icon_update_thread.join()
    sync_thread.join()
    systray.shutdown()
    logging.shutdown()
    exit(0)
