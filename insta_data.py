from watchdog.observers import Observer
from watcher import Watcher

class InstaData(object):
    def __init__(self, watch_dir='/Users/efun/rt_data'):
        # run modes: { 'idle', 'test', 'rai', 'rfi', 'loc', 'nfb'}
        TIMEOUT = 1/64.0
        self.set_run_mode('idle')

        self.set_watcher(watch_dir, TIMEOUT)

    def set_watcher(self, watch_dir, timeout):
        self.observer = Observer(timeout)
        event_handler = Watcher()
        self.observer.schedule(event_handler, watch_dir, recursive=False)
        self.observer.start()

    def set_run_mode(self, mode):
        self.run_mode = mode