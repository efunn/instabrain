import struct
import time
import numpy as np
import subprocess
import shlex


def run_bash(cmd):
    cmd_line = shlex.split(cmd)
    subprocess.call(cmd_line)


def read_epi_slice(idata, slc, rep):
    with open(idata.base_epi.format(slice=format(slc,'03'),
                                    rep=format(rep,'04'))) as f:
        idata.working_epi[slc-1] = np.fromfile(f,dtype=np.uint16)

    
def save_epi_vol(idata, vol, rep, name='vol'):
    vol = vol.reshape((idata.epi_slice_dim*idata.epi_slices,
                       idata.epi_slice_dim))
    np.savetxt(name,vol)
    cmd = idata.ascii2img_cmd.format(ascii_file=name,
                                     slice_dim=str(idata.epi_slice_dim),
                                     slices=str(idata.epi_slices),
                                     res=str(idata.epi_res))
    run_bash(cmd)


def save_mprage_vol(idata, vol, rep, name='vol'):
    vol = vol.reshape((idata.mprage_slice_dim*idata.mprage_slices,
                       idata.mprage_slice_dim))
    np.savetxt(name,vol)
    cmd = idata.ascii2img_cmd.format(ascii_file=name,
                                     slice_dim=str(idata.mprage_slice_dim),
                                     slices=str(idata.mprage_slices),
                                     res=str(idata.mprage_res))
    run_bash(cmd)
