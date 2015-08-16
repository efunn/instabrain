# Instabrain

Instabrain is a hackable python tool for real-time fMRI, using FSL commands for some image processing. Currently working for Siemens scanners on Linux and OSX.

## Requirements

You will need the following installed:
* Python 2.7 with numpy, argparse, watchdog
* FSL with FSLView 
* dcm2nii or dcm2niix

## Getting Started

You will need to set your configuration in `instabrain/config.yaml`. Here you let instabrain know things such as:
* where images arrive from the scanner
* how many functional volumes you are collecting each run
* what TR you are using
* any reference brain regions you want to pull from atlases
* and much, much more! Check the comments in `config.yaml` for more details

Once properly configured, you can run with `python insta_server.py`
