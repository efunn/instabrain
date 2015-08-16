import subprocess
import shlex
import numpy as np
from math import factorial

def run_glm(proc_dirs, design, tr):
    design_file = proc_dirs['ref'] + '/design.mat'
    contrast_file = proc_dirs['ref'] + '/design.con'
    beta_file = proc_dirs['ref'] + '/betas'
    # *** need to code in script dir ***
    script_dir = '/home/rewire/Dropbox/instabrain/scripts/process'
    mat_template_file = script_dir + '/fsl_mat_template.txt'
    con_template_file = script_dir + '/fsl_con_template.txt'
    
    design_mat = gen_design(design)
    hrf = gen_hrf(tr=tr)
    # hrf_conv only works with vectors so far
    conv_design_mat = hrf_conv(design_mat, hrf)
    contrast_design_mat = [1]
    with open(design_file,'w') as f:
        f.write(gen_design_mat_txt(conv_design_mat,
                                   mat_template_file))
    with open(contrast_file,'w') as f:
        f.write(gen_design_con_txt(contrast_design_mat,
                                   con_template_file))

    cmd = ('fsl_glm -i ' + proc_dirs['loc_img']
           + ' -d ' + design_file
           + ' -o ' + beta_file
           + ' -c ' + contrast_file
           + ' -m ' + proc_dirs['rfi_img'] + '_brain_mask'
           + ' --out_t=' + proc_dirs['tstats_img'])
    run_bash(cmd)


def hrf_conv(design_vec, hrf):
    return np.convolve(design_vec,hrf)[:len(design_vec)]

def gen_design(design):
    design_vec = np.zeros(design[0]['length'])
    for idx in range(len(design[0]['onsets'])):
        onset = design[0]['onsets'][idx]
        duration = design[0]['durations'][idx]
        design_vec[onset-1:onset-1+duration] = 1
    return design_vec

def gen_design_mat_txt(design_mat, template):
    with open(template,'r') as f_template:
        template_txt = f_template.read()
    num_waves = 4
    num_points = len(design_mat)
    pp_heights = '1.25 0 1 1'
    np_matrix = np.zeros((len(design_mat),4))
    np_matrix[:,0] = design_mat
    # constant regressor
    np_matrix[:,1] = np.ones(len(design_mat))
    # linear regressor
    np_matrix[:,2] = (np.arange(len(design_mat))
                      /float(len(design_mat)-1))
    np_matrix[:,3] = np_matrix[:,2]**2
    # quadratic regressor
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
    num_waves = 4
    num_contrasts = 1
    pp_heights = '1'
    matrix = '1 0 0 0'
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
