import os
import subprocess, shlex

default_fsldir = '/usr/local/fsl'
FSLDIR = os.getenv('FSLDIR', default_fsldir)

def run_bash(cmd):
    cmd_line = shlex.split(cmd)
    subprocess.call(cmd_line)


def select_roi_mask(roi_name='Primary motor cortex BA4p L',
                    atlas='Juelich',
                    atlas_spec = '-prob-1mm',
                    out_img = '/path/to/out.nii.gz'):
    atlas_dir = FSLDIR + '/data/atlases/' + atlas + '.xml'
    atlas_img = (FSLDIR + '/data/atlases/' + atlas
                 + '/' + atlas + atlas_spec + '.nii.gz')
    cmd = (os.getcwd() + '/scripts/process/select_roi_mask.sh -r \"'
           + roi_name + '\" -a '
           + atlas_dir + ' -i ' + atlas_img + ' -o ' + out_img)
    run_bash(cmd)


def thresh(in_img,
           out_img,
           thr='0.5'):
    cmd = ('fslmaths ' + in_img + ' -thr ' + thr
           + ' ' + out_img)
    run_bash(cmd)


def thresh_bin(in_img,
               out_img,
               thr='0.5'):
    cmd = ('fslmaths ' + in_img + ' -thr ' + thr 
           + ' -bin ' + out_img)
    run_bash(cmd)


def add_mask(in_mask_1,
             in_mask_2,
             out_mask):
    cmd = ('fslmaths ' + in_mask_1 + ' -add '
           + in_mask_2 + ' -bin ' + out_mask)
    run_bash(cmd)


def extract_roi(in_img,
                out_txt,
                in_mask):
    cmd = (os.getcwd() + '/scripts/process/extract_roi.sh -i ' + in_img
           + ' -o ' + out_txt
           + ' -m ' + in_mask)
    run_bash(cmd)

