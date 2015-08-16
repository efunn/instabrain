##################################################
# python control.py -i ip_address -p port_number #
##################################################

import argparse
import multiprocessing as mp
import requests as r
import json
import time as tt
import numpy as np
import StringIO as sio



def set_mode(mode, watch_dir='/home/rewire/rt_data'):
    with open(watch_dir+'/insta_mode.json','w') as f:
        f.write(json.dumps({'mode': mode}))


def requests_loop(target, wait_time, running_bool,
                  last_volume_received, bold_data):
    while running_bool.value:
        text_data = send_request(target)
        num_complete_lines = text_data.count('\n')
        text_data = text_data.rpartition('\n')[0]
        if text_data != '':
            np_data = np.loadtxt(sio.StringIO(text_data))
        else:
            np_data = []
        while last_volume_received.value < num_complete_lines:
            last_volume_received.value += 1
            j = last_volume_received.value-1
            if num_complete_lines > 1:
                if len(bold_data) > 1:
                    for i in range (len(bold_data)):
                        bold_data[i][j] = np_data[j][i]
                else:
                    bold_data[0][j] = np_data[j]
            elif num_complete_lines == 0:
                for i in range (len(bold_data)):
                    bold_data[i][j] = np_data[i]
            tt.sleep(wait_time)
        tt.sleep(wait_time)

def send_request(target):
    try:
        response = r.get(target,timeout=(0.01,0.01)).text
    except:
        response = ''
    return response
