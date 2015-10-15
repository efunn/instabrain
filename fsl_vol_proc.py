import scripts.process.fsl_align as fa
import scripts.process.fsl_mask as fm
import scripts.process.fsl_glm as fg
import multiprocessing as mp
import requests as r
import os, shutil, subprocess, shlex
from time import sleep

class VolumeProcessor(object):
    def __init__(self, config):
        self.pool = mp.Pool()
        # bring reference rois and images from fsl
        base_proc_dir = config['proc_dir']
        base_watch_dir = config['watch_dir']
        self.roi_masks = config['rois']
        self.loc_design = config['design']
        SERVER_TARGET = 'http://127.0.0.1:' + str(config['server_port'])
        self.insta_targets = {}
        self.insta_targets['set_mode'] = SERVER_TARGET + '/set_mode'
        self.insta_targets['get_mode'] = (SERVER_TARGET
                                          + '/insta_mode.json')
        self.insta_targets['set_ready'] = SERVER_TARGET + '/set_ready'
        self.insta_targets['set_complete'] = SERVER_TARGET + '/set_complete'
        self.insta_targets['get_complete'] = (SERVER_TARGET
                                              + '/insta_complete.json')
        self.proc_dirs = {}
        self.proc_dirs['proc'] = base_proc_dir + '/proc'
        self.proc_dirs['ref'] = base_proc_dir + '/ref'
        self.proc_dirs['rai'] = base_proc_dir + '/rai_imgs'
        self.proc_dirs['rfi'] = base_proc_dir + '/rfi_imgs'
        self.proc_dirs['loc'] = base_proc_dir + '/loc_imgs'
        self.proc_dirs['serve'] = base_proc_dir + '/serve'
        self.proc_dirs['archive'] = base_proc_dir + '/archive'
        for directory in self.proc_dirs:
            try:
                os.mkdir(self.proc_dirs[directory])
            except:
                pass
        self.proc_dirs['serve_betas'] = base_proc_dir + '/serve/betas'
        os.mkdir(self.proc_dirs['serve_betas'])

        self.proc_dirs['rai_img'] = self.proc_dirs['ref'] + '/rai'
        self.proc_dirs['rfi_img'] = self.proc_dirs['ref'] + '/rfi'
        self.proc_dirs['loc_img'] = self.proc_dirs['loc'] + '/bold'
        self.proc_dirs['std_img'] = (config['fsldir']
                                     + '/data/standard/'
                                     + config['ref_mprage'])
        self.proc_dirs['tstats_img'] = self.proc_dirs['ref'] + '/tstats'
        self.proc_dirs['betas_img'] = self.proc_dirs['ref'] + '/betas'

        self.MPRAGE_SLICES = config['mprage_slices']
        self.EPI_MODES = ['rfi', 'loc', 'nfb']
        self.select_epi_mode(self.EPI_MODES[0])
        self.dcm_mode = config['dcm_converter']
        self.fwhm = config['epi_fwhm']/2.355
        self.tr = config['epi_tr']
        self.EPI_VOLS = config['epi_vols']
        self.mprage_slice_count = 0
        if (os.path.isfile(self.proc_dirs['rai_img']+'.nii')
            and os.path.isfile(self.proc_dirs['ref']+'/std2rai.mat')):
            self.set_complete_stage('rai')
        if os.path.isfile(self.proc_dirs['rfi_img']+'.nii.gz'):
            self.set_complete_stage('rfi')
        if os.path.isfile(self.proc_dirs['rai_img']+'_rfi.nii.gz'):
            self.set_complete_stage('warp2rfi')
        if os.path.isfile(self.proc_dirs['tstats_img']+'.nii.gz'):
            self.set_complete_stage('glm')
            self.set_complete_stage('loc')
        if all(os.path.isfile(self.proc_dirs['ref'] + '/'
                              + self.roi_masks[roi]['name']
                              + '_std.nii.gz')
               for roi in range(len(self.roi_masks))):
            self.set_complete_stage('roi')
        else:
            self.proc_rois_async()
        self.get_complete_stages()

    def proc_rois_async(self):
        self.pool.apply_async(func = proc_rois,
                              args = (self.proc_dirs,
                                      self.roi_masks),
                              callback = self.on_stage_complete)

    def select_epi_mode(self, mode):
        self.epi_vol_count = 0
        for f in os.listdir(self.proc_dirs['serve']):
            full_f = self.proc_dirs['serve']+'/'+f
            if os.path.isfile(full_f):
                os.remove(full_f)
        if mode in self.EPI_MODES:
            self.epi_mode = mode

    def get_epi_mode(self):
        mode = r.get(self.insta_complete_file).json()['mode']
        self.select_epi_mode(mode)

    def set_ready_stage(self, stage):
        r.post(self.insta_targets['set_ready'],stage)

    def set_complete_stage(self, stage):
        r.post(self.insta_targets['set_complete'],stage)

    def get_complete_stages(self):
        self.complete_stages = r.get(self.insta_targets['get_complete']).json()

    def proc_image(self, run_mode, src_path):
        if run_mode == 'rai':
            self.pool.apply_async(func = copy_and_remove,
                                  args = (src_path,
                                          self.proc_dirs['rai']),
                                  callback = self.on_mprage_slice)
        elif run_mode == 'func':
            self.pool.apply_async(func = proc_epi_vol,
                                  args = (src_path,
                                          self.proc_dirs,
                                          self.roi_masks,
                                          self.epi_mode,
                                          self.dcm_mode,
                                          self.fwhm),
                                  callback = self.on_epi_vol_complete)

    def on_mprage_slice(self, arg):
        self.mprage_slice_count += 1
        if self.mprage_slice_count >= self.MPRAGE_SLICES:
            self.pool.apply_async(func = proc_rai,
                                  args = (self.proc_dirs,
                                          self.dcm_mode),
                                  callback = self.on_stage_complete)
            self.mprage_slice_count = 0

    def on_epi_vol_complete(self, (epi_mode, in_name)):
        self.epi_vol_count += 1
        if self.epi_vol_count >= self.EPI_VOLS[epi_mode]:
                self.on_epi_run_complete(epi_mode)

    def on_epi_run_complete(self, epi_mode):
        if epi_mode == 'rfi': 
            self.pool.apply_async(func = proc_rfi,
                                  args = (self.proc_dirs,
                                          self.roi_masks),
                                  callback = self.on_stage_complete)
        elif epi_mode == 'loc':
            self.on_stage_ready(epi_mode)
        elif epi_mode == 'nfb':
            pass # wait for next run

    def on_stage_ready(self, stage):
        self.set_ready_stage(stage)
        self.get_complete_stages()
        if (stage == 'loc'
                and self.complete_stages['warp2rfi'] == 'complete'):
            self.on_stage_complete('warp2rfi')

    def on_stage_complete(self, stage):
        self.set_complete_stage(stage)
        self.get_complete_stages()
        if ((stage == 'roi' or stage == 'rai' or stage == 'rfi')
                and self.complete_stages['roi'] == 'complete'
                and self.complete_stages['rai'] == 'complete'
                and self.complete_stages['rfi'] == 'complete'):
            self.pool.apply_async(func = proc_warp2rfi,
                                  args = (self.proc_dirs,
                                          self.roi_masks),
                                  callback = self.on_stage_complete)
        elif (stage == 'warp2rfi'
                and self.complete_stages['loc'] == 'ready'):
            self.pool.apply_async(func = proc_glm,
                                  args = (self.proc_dirs,
                                          self.loc_design,
                                          self.tr),
                                  callback = self.on_stage_complete)
        elif stage == 'glm':
            self.pool.apply_async(func = proc_loc,
                                  args = (self.proc_dirs,
                                          self.loc_design,
                                          self.roi_masks),
                                  callback = self.on_stage_complete)


def proc_rois(proc_dirs, roi_masks):
    for roi in range(len(roi_masks)):
        base_roi = (proc_dirs['ref'] + '/'
                    + roi_masks[roi]['name'])
        fm.select_roi_mask(roi_name=roi_masks[roi]['id'],
                           atlas=roi_masks[roi]['atlas'],
                           atlas_spec=roi_masks[roi]['spec'],
                           out_img=(base_roi+'_std'))
    return 'roi'

def proc_rai(proc_dirs, dcm_mode):
    fa.gen_struct_from_slice(proc_dirs['rai'],
                             proc_dirs['rai_img'],
                             dcm_mode)
    # extract brain
    fa.gen_struct_brain(in_struct=proc_dirs['rai_img'],
                        out_struct=proc_dirs['rai_img']+'_brain',
                        extra_params=' -B')
    # generate std to rai
    fa.gen_struct2struct(in_struct=proc_dirs['std_img'],
                         ref_struct=proc_dirs['rai_img']+'_brain',
                         in_name='std',
                         ref_name='rai',
                         outdir=proc_dirs['ref'])
    return 'rai'

def proc_rfi(proc_dirs, roi_masks):
    # combine rfi into 4d image
    fa.gen_bold_4d(proc_dirs['rfi'],
                   proc_dirs['rfi_img']+'_4d')
    # mcflirt to a single 3D ref image
    fa.gen_bold_mc(in_bold=proc_dirs['rfi_img']+'_4d',
                   out_bold=proc_dirs['rfi_img']+'_4d_mc',
                   ref_bold='none')
    fa.gen_bold_mean(in_bold=proc_dirs['rfi_img']+'_4d_mc',
                     out_bold=proc_dirs['rfi_img'])
    fa.gen_bold_3d_brain(proc_dirs['rfi_img'],
                         proc_dirs['rfi_img']+'_brain')
    return 'rfi'

def proc_warp2rfi(proc_dirs, roi_masks):
    # generate struct2rfi and combine std2struct and struct2rfi
    fa.gen_bold2struct(in_bold=proc_dirs['rfi_img']+'_brain',
                       ref_struct=proc_dirs['rai_img']+'_brain',
                       in_name='rfi',
                       ref_name='rai',
                       outdir=proc_dirs['ref'])

    fa.add_align(align1=(proc_dirs['ref']+'/rfi2rai.mat'),
                 align2=(proc_dirs['ref']+'/rai2std.mat'),
                 namefirst='rfi',
                 namelast='std',
                 outdir=proc_dirs['ref'])
    # warp rai into rfi space
    fa.apply_align(proc_dirs['rai_img'],
                   proc_dirs['rai_img'] + '_rfi',
                   align_mat=(proc_dirs['ref']+'/rai2rfi.mat'),
                   ref_img=proc_dirs['rfi_img'])
    # warp all rois into rfi space
    for roi in range(len(roi_masks)):
        base_roi = (proc_dirs['ref'] + '/'
                    + roi_masks[roi]['name'])
        fa.apply_align(base_roi + '_std',
                       base_roi + '_rfi',
                       align_mat=(proc_dirs['ref']+'/std2rfi.mat'),
                       ref_img=proc_dirs['rfi_img'])
        fm.thresh_bin(base_roi + '_rfi',
                      base_roi,
                      thr=str(110)) # set below 100 to use probability mask
    return 'warp2rfi'

def proc_glm(proc_dirs, design, tr):
    # generate 4d loc image
    fa.gen_bold_4d(proc_dirs['loc'],
                   proc_dirs['loc_img'])
    # run fsl_glm and generate functional masks
    fg.run_glm(proc_dirs, design, tr)
    return 'glm'

def proc_loc(proc_dirs, design, roi_masks):
    # view glm and select rois
    fg.show_glm(proc_dirs, roi_masks)

    # post-process glm and extract betas
    for roi in range(len(roi_masks)):
        base_roi = (proc_dirs['ref'] + '/'
                    + roi_masks[roi]['name'])
        out_dir = (proc_dirs['serve_betas'] + '/'
                   + roi_masks[roi]['name'])
        fm.extract_roi(proc_dirs['betas_img'],
                       out_dir,
                       (proc_dirs['ref'] + '/'
                        + roi_masks[roi]['name']))
        cmd = ('split -l 1 -d ' + out_dir + ' '
               + out_dir + '_')
        run_bash(cmd)
        for beta in range(len(design)+4):
            if beta < len(design):
                cmd = ('mv ' + out_dir + '_' + str(beta).zfill(2) + ' '
                       + out_dir + '_' + design[beta]['label']) 
            elif beta == len(design):
                cmd = ('mv ' + out_dir + '_' + str(beta).zfill(2) + ' '
                       + out_dir + '_constant') 
            else:
                cmd = ('rm ' + out_dir + '_' + str(beta).zfill(2)) 
            run_bash(cmd)
    return 'loc'

def proc_epi_vol(in_img, proc_dirs, roi_masks,
                 epi_mode, dcm_mode, fwhm):
    in_img = in_img.rsplit('.',1)[0]
    in_name = '/' + in_img.rsplit('/',1)[-1]
    if dcm_mode == 'none':
        copy_and_remove(in_img+'.nii',
                        proc_dirs['proc'])
    else:
        fa.dcm2nii(in_img+'.dcm', proc_dirs['proc'], dcm_mode)
    if dcm_mode == 'dcm2nii':
        copy_and_remove(in_img+'.dcm',
                        proc_dirs['archive'])
    if epi_mode == 'rfi':
        copy_and_remove(proc_dirs['proc'] + in_name + '.nii',
                        proc_dirs['rfi'])
        return (epi_mode, in_name)
    else:
        if fwhm == 0:
            fa.gen_bold_mc_rt(proc_dirs['proc'] + in_name,
                              proc_dirs['proc'] + in_name + '_mc_s',
                              proc_dirs['rfi_img'])
        else:
            fa.gen_bold_mc_rt(proc_dirs['proc'] + in_name,
                              proc_dirs['proc'] + in_name + '_mc',
                              proc_dirs['rfi_img'])
            fa.smooth_bold(proc_dirs['proc'] + in_name + '_mc',
                           proc_dirs['proc'] + in_name + '_mc_s',
                           fwhm)
            copy_and_remove(proc_dirs['proc'] + in_name + '_mc.nii.gz',
                            proc_dirs['archive'])
        copy_and_remove(proc_dirs['proc'] + in_name + '.nii',
                        proc_dirs['archive'])
    if epi_mode == 'nfb':
        for roi in range(len(roi_masks)):
            roi_name = roi_masks[roi]['name']
            fm.extract_roi(proc_dirs['proc'] + in_name + '_mc_s',
                           proc_dirs['serve'] + '/' + in_name[-3:],
                           proc_dirs['ref'] + '/' + roi_name)
    elif epi_mode == 'loc':
        copy_and_remove(proc_dirs['proc'] + in_name + '_mc_s.nii.gz',
                         proc_dirs['loc'])
    return (epi_mode, in_name)

def run_bash(cmd):
    cmd_line = shlex.split(cmd)
    subprocess.call(cmd_line)

def copy_and_remove(src,dst):
        while True:
            try:
                shutil.copy(src,dst)
                break
            except:
                pass
        while True:
            try:
                os.remove(src)
                break
            except:
                pass
