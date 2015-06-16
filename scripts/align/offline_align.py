import align as al
import os

#########################################
# grabbing FSL directory for atlas info #
#########################################

default_fsldir = '/usr/local/fsl'
FSLDIR = os.getenv('FSLDIR', default_fsldir)


def gen_all_aligns(basedir='/belly/20150604-diffnfb-test', num_runs=5):

    #########################
    # set up file structure #
    #########################

    refdir = basedir + '/ref' # all aligns xxx2xxx.mat files saved here
    bold_img = basedir + '/run{run_num}/bold{params}.nii.gz' # generic format for bold runs
    mni_img = FSLDIR + '/data/standard/MNI152_T1_1mm_brain.nii.gz' # reference for atlases
    rai_img = basedir + '/rai{params}.nii.gz' # reference anatomical image
    rfi_img = basedir + '/rfi{params}.nii.gz' # future reference functional image (to be created)

    #----------------------------------------------------#
    # Generate all alignment and apply motion correction #
    #----------------------------------------------------#


    ##############################
    # extract brain from RAI     #
    # (use -B for removing neck) #
    ##############################
    
    al.gen_struct_brain(in_struct=rai_img.format(params=''),
                        out_struct=rai_img.format(params='_brain'),
                        extra_params=' -B')

    #######################
    # register STD to RAI #
    #######################

    al.gen_struct2struct(in_struct=mni_img,
                         ref_struct=rai_img.format(params='_brain'),
                         in_name='std',
                         ref_name='rai',
                         outdir=refdir)


    #########################################
    # motion correct run 1 to mean of run 1 #
    # and extract brain                     #
    #########################################

    run_num = format(1,'02')
    al.gen_bold_mc(in_bold=bold_img.format(run_num=run_num,params=''),
                   out_bold=bold_img.format(run_num=run_num,params='_mc'),
                   ref_bold='none')
    al.gen_bold_4d_brain(bold_img.format(run_num=run_num,params='_mc'),
                         bold_img.format(run_num=run_num,params='_mc_brain'))


    ########################################################
    # generate RFI by averaging motion corrected first run #
    # and extracting brain                                 #
    ########################################################

    al.gen_bold_mean(in_bold=bold_img.format(run_num=format(1,'02'),params='_mc'),
                     out_bold=rfi_img.format(params=''))
    al.gen_bold_3d_brain(rfi_img.format(params=''),
                         rfi_img.format(params='_brain'))


    #######################
    # register RFI to RAI #
    #######################

    al.gen_bold2struct(in_bold=rfi_img.format{params='_brain'},
                       ref_struct=rai_img.format{params='_brain'},
                       in_name='rfi',
                       ref_name='rai',
                       outdir=refdir)

    al.add_align(align1=(refdir+'/rfi2rai.mat'),
                 align2=(refdir+'/rai2std.mat'),
                 namefirst='rfi',
                 namelast='std',
                 outdir=refdir)


    ######################################
    # motion correct rest of runs to RFI #
    # (RFI not brain extracted)          #
    # and then extract brain             #
    ######################################
 
     for run in range(2, num_runs+1):
        run_num=format(run,'02')
        al.gen_bold_mc(in_bold=bold_img.format(run_num=run_num,params=''),
                       out_bold=bold_img.format(run_num=run_num,params='_mc'),
                       ref_bold=rfi_img.format(params=''))
        al.gen_bold_4d_brain(bold_img.format(run_num=run_num,params='_mc'),
                             bold_img.format(run_num=run_num,params='_mc_brain'))

