import struct
import time
import numpy as np
import subprocess
import shlex

def run_bash(cmd):
    cmd_line = shlex.split(cmd)
    subprocess.call(cmd_line)

def testdata():
    base_file = 'MB-R{vol}-E1-S{slice}.imgdat'
    x_dim = 96
    y_dim = 96
    z_dim = 64
    vols = 50
    vol_range = np.arange(vols)
    z_range = np.arange(z_dim)
    empty_data = np.zeros((z_dim,x_dim*y_dim))
    t = time.time()
    for v in vol_range:
        data = empty_data 
        for z in z_range:
            with open(base_file.format(slice=format(z+1,'03'),vol=format(v+1,'04'))) as f:
                data[z] = np.fromfile(f,dtype=np.uint16)
        data = data.reshape((96*64,96))
        np.savetxt('vol.txt'.format(vol=format(v+1,'04')),data)
        # cmd = 'fslascii2img out.txt 96 96 64 1 2.4 2.4 2.4 1 {vol}.nii'.format(vol=format(v+1,'04'))
        # run_bash(cmd)
    e = time.time() - t
    print e
    return data

def testdata():
    x_dim = 96
    y_dim = 96
    z_dim = 1
    x_range = np.arange(x_dim)
    y_range = np.arange(y_dim)
    z_range = np.arange(z_dim)
    data = np.zeros((x_dim,y_dim,z_dim))
    base_file = 'MB-R0016-E1-S{slice}.imgdat'
    new_data = np.zeros(x_dim*y_dim*z_dim)
    t = time.time()
    count = 0
    for z in z_range:
        with open(base_file.format(slice=format(z+1,'03'))) as f:
            for y in y_range:
                for x in x_range:
                    # data[x][y][z]=struct.unpack('H',f.read(2))[0]
                    new_data[count]=struct.unpack('H',f.read(2))[0]
                    count += 1
    new_data = np.reshape(new_data,(x_dim,y_dim,z_dim))
    e = time.time() - t
    print e
    return new_data
