# Instabrain

Instabrain is a hackable python tool for real-time fMRI, using FSL commands for some image processing. 

## Requirements

You will need the following installed:
* Python 2.7 with numpy, argparse, multiprocessing, subprocess, shlex
* FSL with FSLView 

## Getting Started

You will need to put the following items in `instabrain/config.txt`:
* Directory where instabrain can store temporary images: `scratch_dir=/path/to/scratch`
* Directory where you store .txt files of study details: `study_dir=/path/to/study/files`
* Directory where incoming images appear: `watch_dir=/path/to/watch`
* IP to serve realtime output files on: `server_ip=127.0.0.1`
* Port to serve realtime output files on: `server_port=1234`

It is recommended that you keep all directories on the same hard disk.

In `study_dir`, you can then input a .txt file of your study, for example:
```
tr_time_s={TR time in your study}
smooth_fwhm_mm={smoothing in millimeters; set to 0 for no smoothing}
localizer_run_volumes={number of volumes in localizer runs}
nfb_run_volumes={number of volumes in localizer runs}
localizer_design_onsets={volume number for each condition change}
localizer_design_conditions={condition for each condition change}
```

Then you can run with `python insta.py -s name_of_your_study`, where `name_of_your_study.txt` exists in `study_dir`.
