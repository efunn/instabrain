#################################
# python insta.py -s study_name #
#################################

import argparse
import multiprocessing as mp


parser = argparse.ArgumentParser(description='Function arguments')
parser.add_argument('-s','--study', help='Study name',default='none')
args = parser.parse_args()

def run():
    # init:
    # reads in config and study details
    # starts processes accordingly

    # main process: do the heavy lifting

    #--------------------------------

    # watcher process: watches /watch_dir and, depending on protocol stage, moves files accordingly

    #--------------------------------

    # server process: serves data.txt

    #--------------------------------


    ###--------------###
    # workflow:

    # options:
    # 1) test realtime
    # 2) reference anatomical
    # 3) reference functional
    # 4) functional localizer
    # 5) re-localizer
    # 6) neurofeedback


    ###--------------###

    return

if __name == "__main__":
    run()