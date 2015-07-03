from watchdog.events import FileSystemEventHandler
from slice_proc import SliceProcessor, proc_epi_slice
import multiprocessing as mp
import os, time

class Watcher(FileSystemEventHandler):

    def __init__(self):
        self.sp = SliceProcessor()
        self.sp_pool = mp.Pool()

    def on_created(self, event):
        # try: self.sp.timer
        # except: self.sp.timer = 0; self.sp.time_last = time.time()
        img_file = event.src_path.rsplit('/')[-1]
        if img_file.endswith('imgdat'):
            if img_file.startswith('MB'):
                self.sp_pool.apply_async(func = proc_epi_slice,
                                         args = (img_file, event.src_path),
                                         callback = self.sp.add_to_proc_epi_dict)
            else:
                pass
        else:
            # os.rename(img_file)
            pass

# sample of reading new image file
# typ = file.split('-')[0]
# rep = file.split('R')[1].split('-')[0]
# eco = file.split('E')[1].split('-')[0]
# slc = file.split('S')[1].split('.')[0] 
