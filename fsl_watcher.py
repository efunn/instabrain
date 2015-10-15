from watchdog.events import FileSystemEventHandler
from fsl_vol_proc import VolumeProcessor
import os, time, shutil, json

class fslWatcher(FileSystemEventHandler):

    def __init__(self, config):
        self.watch_dir = config['watch_dir']
        self.valid_run_modes = ['idle',
                                'rai',
                                'func']
        with open(self.watch_dir+'/insta_mode.json','w') as f:
            f.write(json.dumps({'mode': 'idle'}))
        with open(self.watch_dir+'/insta_complete.json','w') as f:
            f.write(json.dumps({'roi': 'incomplete',
                                'rai': 'incomplete',
                                'rfi': 'incomplete',
                                'warp2rfi': 'incomplete',
                                'glm': 'incomplete',
                                'loc': 'incomplete'}))
        self.vp = VolumeProcessor(config)
        self.set_run_mode('idle')

    def on_modified(self, event):
        mod_file = event.src_path.rsplit('/')[-1]
        if mod_file == 'insta_mode.json':
            with open(event.src_path, 'r') as f:
                mode = json.load(f)['mode']
                if mode in self.vp.EPI_MODES:
                    self.vp.select_epi_mode(mode)
                    self.set_run_mode('func')
                elif mode in ('idle', 'rai'):
                    self.set_run_mode(mode)

    def on_created(self, event):
        img_file = event.src_path.rsplit('/')[-1]
        if self.run_mode == 'idle':
            copy_and_remove(event.src_path, self.vp.proc_dirs['archive'])
        elif img_file.endswith('dcm') or img_file.endswith('nii'):
            self.vp.proc_image(self.run_mode, event.src_path)

    def set_run_mode(self, mode):
        if mode in self.valid_run_modes:
            self.run_mode = mode
        else:
            pass

def copy_and_remove(src, dst):
        try:
            shutil.copy(src,dst)
            os.remove(src)
        except:
            pass
