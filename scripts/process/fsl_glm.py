import subprocess
import shlex
import os
import numpy as np
from math import factorial

def run_glm(proc_dirs, design, tr):
    design_file = proc_dirs['ref'] + '/design.mat'
    contrast_file = proc_dirs['ref'] + '/design.con'
    beta_file = proc_dirs['ref'] + '/betas'
    script_dir = os.getcwd() + '/scripts/process'
    mat_template_file = script_dir + '/fsl_mat_template.txt'
    con_template_file = script_dir + '/fsl_con_template.txt'

    design_mat = gen_design(design)
    hrf = gen_hrf(tr=tr)
    conv_design_mat = hrf_conv(design_mat, hrf)
    contrast_design_mat = [1]
    with open(design_file,'w') as f:
        f.write(gen_design_mat_txt(conv_design_mat,
                                   mat_template_file))
    with open(contrast_file,'w') as f:
        f.write(gen_design_con_txt(contrast_design_mat,
                                   con_template_file))

    # - currently removing linear and quadratic trends
    # - add high pass filtering of localizer image here
    #   prior to running GLM
    cmd = ('fsl_glm -i ' + proc_dirs['loc_img']
           + ' -d ' + design_file
           + ' -o ' + beta_file
           + ' -c ' + contrast_file
           + ' -m ' + proc_dirs['rfi_img'] + '_brain_mask'
           + ' --out_t=' + proc_dirs['tstats_img'])
    run_bash(cmd)


def hrf_conv(design_mat, hrf):
    conv_design_mat = np.zeros(np.shape(design_mat))
    for idx in range(len(design_mat)):
        conv_design_mat[idx][:] = (
            np.convolve(design_mat[idx],hrf)[:len(design_mat[idx])])
    return conv_design_mat

def gen_design(design):
    design_mat = np.zeros((len(design),design[0]['length']))
    for idx in range(len(design)):
        for jdx in range(len(design[idx]['onsets'])):
            onset = design[idx]['onsets'][jdx]
            duration = design[idx]['durations'][jdx]
            design_mat[idx][onset-1:onset-1+duration] = (
                design[idx]['heights'][jdx])
    return design_mat

def gen_design_mat_txt(design_mat, template):
    # - currently, hard-coded to work with 6 regressors
    # - will be updated to work with as many predictors
    #   as there are design components
    with open(template,'r') as f_template:
        template_txt = f_template.read()
    num_waves = 6
    num_points = len(design_mat[0])
    pp_heights = '1.25 1.25 1.25 0 1 1'
    np_matrix = np.zeros((num_points,6))
    np_matrix[:,0] = design_mat[0]
    np_matrix[:,1] = design_mat[1]
    np_matrix[:,2] = design_mat[2]
    # constant regressor
    np_matrix[:,3] = np.ones(num_points)
    # linear regressor
    np_matrix[:,4] = (np.arange(num_points)
                      /float(num_points-1))
    # quadratic regressor
    np_matrix[:,5] = np_matrix[:,4]**2
    np.set_printoptions(threshold='nan',
                        linewidth='nan')
    matrix = (np.array_str(np_matrix)
              .replace('[','').replace(']',''))
    # num_waves = 1
    # num_points = len(design_mat)
    # pp_heights = 1
    # matrix = (np.array_str(np.array(design_mat),num_waves)
    #           .rsplit('[')[1].rsplit(']')[0].replace(' ',''))
    design_mat_txt = template_txt.format(num_waves=str(num_waves),
                                         num_points=str(num_points),
                                         pp_heights=str(pp_heights),
                                         matrix=matrix)
    return design_mat_txt

def gen_design_con_txt(design_con, template):
    with open(template,'r') as f_template:
        template_txt = f_template.read()
    num_waves = 6
    num_contrasts = 1
    pp_heights = '1'
    # might play with contrast matrix?
    # could also run just an active glm to get better map
    matrix = '1 0 0 0 0 0'
    # num_waves = len(design_con)
    # num_contrasts = 1
    # pp_heights = 1
    # matrix = '1 0 0'
    # matrix = (np.array_str(np.array(design_con),num_waves)
    #           .rsplit('[')[1].rsplit(']')[0].replace(' ',''))
    design_con_txt = template_txt.format(num_waves=str(num_waves),
                                         num_contrasts=str(num_contrasts),
                                         pp_heights=str(pp_heights),
                                         matrix=matrix)
    return design_con_txt

def gen_hrf(tr=1, tf=30, c=1/6.0,
            a1=6, a2=16, A=1/0.833657):
    A = A*tr # scaled to give unit step response to HRF
    t = np.arange(0.5*tr,tf,tr)
    h = (A*np.exp(-t)*(t**(a1-1)/float(factorial(a1-1))
         - c*t**(a2-1)/float(factorial(a2-1))))
    return h

def show_glm(proc_dirs, roi_masks):
    cmd = ('fslview '
           + proc_dirs['rai_img'] + '_rfi '
           + proc_dirs['tstats_img'] + ' -l Red-Yellow')
    for roi in range(len(roi_masks)):
        cmd = (cmd + ' ' + proc_dirs['ref'] + '/'
               + roi_masks[roi]['name']
               + ' -l Blue')
    run_bash(cmd)

def run_bash(cmd):
    cmd_line = shlex.split(cmd)
    subprocess.call(cmd_line)
