#################################
# python insta.py -s study_name #
#################################

import argparse
import multiprocessing as mp
import os
from insta_data import InstaData
import insta_run as ir

FSLDIR = os.getenv('FSLDIR', '/usr/local/fsl')

parser = argparse.ArgumentParser(description='Function arguments')
parser.add_argument('-s','--study', help='Study name',default='none')
args = parser.parse_args()

def run():

    idata = InstaData()

    while idata.run_mode != 'quit':
        execute(idata)

def execute(idata):
    pass


if __name__ == "__main__":
    run()