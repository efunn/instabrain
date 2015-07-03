import SimpleHTTPServer
import SocketServer

import requests as r
import time as tt
import numpy as np
import StringIO as sio

class silentHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return

def run(server_running_bool, port=27000):

    # figure out post request (to send from protocol to frontend)
    Handler = silentHandler 

    SocketServer.TCPServer.allow_reuse_address = True 
    SocketServer.TCPServer.timeout = 1.0 
    httpd = SocketServer.TCPServer(("", port), Handler)

    while server_running_bool.value:
        httpd.handle_request()

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
