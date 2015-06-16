import mask as ma
import align as al

def gen_all_masks(basedir='/belly/20150604-diffnfb-test'):

    threshold_value = 20 #percent probability

    refdir = basedir + '/ref'
    rai_img = basedir + '/rai{params}.nii.gz'

    rai_template = basedir + '/rai.nii.gz'
    rfi_template = basedir + '/rfi.nii.gz'

    roi_list = ['Primary motor cortex BA4a L',
                'Primary motor cortex BA4a R',
                'Primary motor cortex BA4p L',
                'Primary motor cortex BA4p R',
                'Premotor cortex BA6 L',
                'Premotor cortex BA6 R']
    roi_img_list = [refdir + '/ba4a_l{params}.nii.gz',
                    refdir + '/ba4a_r{params}.nii.gz',
                    refdir + '/ba4p_l{params}.nii.gz',
                    refdir + '/ba4p_r{params}.nii.gz',
                    refdir + '/ba6_l{params}.nii.gz',
                    refdir + '/ba6_r{params}.nii.gz']

    combo_rois_list = [refdir + '/ba4_l{params}.nii.gz',
                       refdir + '/ba4_r{params}.nii.gz',
                       refdir + '/ba46_l{params}.nii.gz',
                       refdir + '/ba46_r{params}.nii.gz',
                       refdir + '/ba4_bi{params}.nii.gz',
                       refdir + '/ba6_bi{params}.nii.gz',
                       refdir + '/ba46_bi{params}.nii.gz']

    for roi in range(len(roi_list)):
        ma.select_roi_mask(roi_name=roi_list[roi],
                           atlas='Juelich',
                           atlas_spec='-prob-1mm',
                           out_img=roi_img_list[roi].format(params=''))

        al.apply_align(roi_img_list[roi].format(params=''),
                       roi_img_list[roi].format(params='_rfi'),
                       align_mat=(refdir+'/std2rfi.mat'),
                       ref_img=rfi_template)
        ma.thresh_bin(roi_img_list[roi].format(params='_rfi'),
                      roi_img_list[roi].format(params='_rfi_20_bin'),
                      thr=str(threshold_value))

    ma.add_mask(roi_img_list[0].format(params='_rfi_20_bin'),
                roi_img_list[2].format(params='_rfi_20_bin'),
                combo_rois_list[0].format(params='_rfi_20_bin'))

    ma.add_mask(roi_img_list[1].format(params='_rfi_20_bin'),
                roi_img_list[3].format(params='_rfi_20_bin'),
                combo_rois_list[1].format(params='_rfi_20_bin'))

    ma.add_mask(roi_img_list[4].format(params='_rfi_20_bin'),
                combo_rois_list[0].format(params='_rfi_20_bin'),
                combo_rois_list[2].format(params='_rfi_20_bin'))

    ma.add_mask(roi_img_list[5].format(params='_rfi_20_bin'),
                combo_rois_list[1].format(params='_rfi_20_bin'),
                combo_rois_list[3].format(params='_rfi_20_bin'))

    ma.add_mask(combo_rois_list[0].format(params='_rfi_20_bin'),
                combo_rois_list[1].format(params='_rfi_20_bin'),
                combo_rois_list[4].format(params='_rfi_20_bin'))

    ma.add_mask(roi_img_list[4].format(params='_rfi_20_bin'),
                roi_img_list[5].format(params='_rfi_20_bin'),
                combo_rois_list[5].format(params='_rfi_20_bin'))

    ma.add_mask(combo_rois_list[4].format(params='_rfi_20_bin'),
                combo_rois_list[5].format(params='_rfi_20_bin'),
                combo_rois_list[6].format(params='_rfi_20_bin'))
