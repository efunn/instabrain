import os
import subprocess
import shlex
import shutil
import numpy as np


def run_bash(cmd):
    cmd_line = shlex.split(cmd)
    subprocess.call(cmd_line)


def gen_align_names(name1, name2, outdir=''):
    fwd_align = outdir + '/' + name1 + '2' + name2 + '.mat'
    back_align = outdir + '/' + name2 + '2' + name1 + '.mat'
    return fwd_align, back_align


def rev_align(fwd_align, back_align):
    cmd = ('convert_xfm -omat ' + back_align
           + ' -inverse ' + fwd_align)
    run_bash(cmd)


def add_align(align1, align2, namefirst, namelast, outdir):
    fwd_align, back_align = gen_align_names(namefirst, namelast, outdir)
    cmd = ('convert_xfm -omat ' + fwd_align 
           + ' -concat ' + align2 + ' ' + align1)
    run_bash(cmd)
    rev_align(fwd_align, back_align)


def gen_struct2struct(in_struct='/path/to/s1.nii.gz',
                      ref_struct='/path/to/s2.nii.gz',
                      in_name='first',
                      ref_name='second',
                      outdir='/path/to/out/'):
    fwd_align, back_align = gen_align_names(in_name, ref_name, outdir)
    cmd = ('flirt -in ' + in_struct 
           + ' -ref ' + ref_struct 
           + ' -omat ' + fwd_align
           + ' -bins 256 -cost corratio -searchrx -90 90'
           + ' -searchry -90 90 -searchrz -90 90 -dof 12 -interp trilinear')
    run_bash(cmd)
    rev_align(fwd_align, back_align)


def gen_bold2struct(in_bold='/path/to/s1',
                    ref_struct='/path/to/b1',
                    in_name='first',
                    ref_name='second',
                    outdir='/path/to/out'):
    fwd_align, back_align = gen_align_names(in_name, ref_name, outdir)
    cmd = ('flirt -in ' + in_bold
           + ' -ref ' + ref_struct 
           + ' -omat ' + fwd_align
           + ' -bins 256 -cost corratio -searchrx -90 90'
           + ' -searchry -90 90 -searchrz -90 90 -dof 6 -interp trilinear')
    run_bash(cmd)
    rev_align(fwd_align, back_align)


def gen_bold2bold(in_bold='/path/to/b1',
                  ref_bold='/path/to/b2',
                  in_name='first',
                  ref_name='second',
                  outdir='/path/to/out'):
    fwd_align, back_align = gen_align_names(in_name, ref_name, outdir)
    cmd = ('flirt -in ' + in_bold 
           + ' -ref ' + ref_bold
           + ' -omat ' + fwd_align
           + ' -bins 256 -cost corratio -searchrx -90 90'
           + ' -searchry -90 90 -searchrz -90 90 -dof 6 -interp trilinear')
    run_bash(cmd)
    rev_align(fwd_align, back_align)


def gen_bold_mc(in_bold,
                out_bold,
                ref_bold='none'):
    if ref_bold == 'none':
        cmd = ('mcflirt -in ' + in_bold + ' -o ' + out_bold
               + ' -meanvol -sinc_final -plots')
    else:
        cmd = ('mcflirt -in ' + in_bold + ' -o ' + out_bold
               + ' -r ' + ref_bold + ' -sinc_final -plots')
    run_bash(cmd)


def gen_bold_mean(in_bold,
                  out_bold):
    cmd = 'fslmaths ' + in_bold + ' -Tmean ' + out_bold
    run_bash(cmd)

def gen_struct_brain(in_struct,
                     out_struct,
                     extra_params=''):
    cmd = 'bet ' + in_struct + ' ' + out_struct + ' -f 0.5 -g 0' + extra_params
    run_bash(cmd)

def gen_bold_3d_brain(in_bold,
                      out_bold):
    cmd = 'bet ' + in_bold + ' ' + out_bold + ' -f 0.5 -g 0'
    run_bash(cmd)

def gen_bold_4d_brain(in_bold,
                      out_bold):
    cmd = 'bet ' + in_bold + ' ' + out_bold + ' -F'
    run_bash(cmd)

def apply_align(input_img,
                output_img,
                align_mat,
                ref_img='none'):
    if ref_img == 'none':
        ref_img = input_img
    cmd = ('applywarp -i ' + input_img
           + ' -r ' + ref_img
           + ' -o ' + output_img
           + ' --premat=' + align_mat)
    run_bash(cmd)
