import numpy as np
import time

class SliceProcessor(object):

    def __init__(self):
        self.mprage_slice_dim = 256
        self.mprage_slices = 192
        self.mprage_res = 1

        self.epi_slice_dim = 96 
        self.epi_slices = 64#56
        self.epi_res = 2.4

        self.epi_dims = (self.epi_slices, self.epi_slice_dim**2)
        self.last_vol_recv = 0
        self.last_slice_recv = 0
        self.ascii2img_cmd = ('fslascii2img {ascii_file} '
                              '{slice_dim} {slice_dim} {slices} '
                              '1 {res} {res} {res} 1 {img_file}')
        self.reset_epi_dicts()

    def reset_epi_dicts(self):
        self.vol_status_dict = {}
        self.proc_vol_dict = {}

    def add_to_proc_epi_dict(self, (rep,slc,slice_data)):
        if rep not in self.vol_status_dict:
            self.vol_status_dict[rep] = 0
        if rep not in self.proc_vol_dict:
            self.proc_vol_dict[rep] = np.zeros(self.epi_dims, dtype=np.uint16)
        self.vol_status_dict[rep] += 1
        self.proc_vol_dict[rep][int(slc)-1] = slice_data
        if self.vol_status_dict[rep] == self.epi_slices:
            self.proc_epi_volume(rep)


    def proc_epi_volume(self, rep):
        # self.timer += time.time() - self.time_last
        # self.time_last = time.time()
        # print 'volume {rep} complete in {time} s'.format(rep=str(rep),
        #                                                  time=str(self.timer))
        pass


def proc_epi_slice(img_file, path):
    rep = int(img_file.split('R')[1].split('-')[0])
    slc = int(img_file.split('S')[1].split('.')[0])
    with open(path) as f:
        slice_data = np.fromfile(f,dtype=np.uint16)
    return rep, slc, slice_data



