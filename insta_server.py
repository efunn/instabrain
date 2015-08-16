import SimpleHTTPServer
import SocketServer
import argparse
from fsl_watcher import fslWatcher
from watchdog.observers import Observer
import multiprocessing as mp
import os, yaml, json, time

parser = argparse.ArgumentParser(description='Function arguments')
parser.add_argument('-s','--study', help='Study name',default='none')
args = parser.parse_args()

# replace with yaml load
with open('config.yaml') as f:
    CONFIG = yaml.load(f)
    CONFIG['fsldir'] = os.getenv('FSLDIR', '/usr/local/fsl')
    CONFIG['design'][0]['length'] = CONFIG['epi_vols']['loc']

try:
    OBS_TIMEOUT = 0.01
    PORT = CONFIG['server_port']
    WATCH_DIR = CONFIG['watch_dir']
except:
    print 'Error: config file incomplete/missing'

class instaHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.getheader('content-length'))
            data = self.rfile.read(length)
            if self.path == '/set_mode':
                with open(WATCH_DIR+'/insta_mode.json','w') as f:
                    f.write(data)
            elif self.path == '/set_ready':
                with open(WATCH_DIR+'/insta_complete.json','r') as f:
                    insta_complete = json.load(f)
                    insta_complete[data] = 'ready'
                with open(WATCH_DIR+'/insta_complete.json','w') as f:
                    f.write(json.dumps(insta_complete))
            elif self.path == '/set_complete':
                with open(WATCH_DIR+'/insta_complete.json','r') as f:
                    insta_complete = json.load(f)
                    insta_complete[data] = 'complete'
                with open(WATCH_DIR+'/insta_complete.json','w') as f:
                    f.write(json.dumps(insta_complete))
            self.send_response(200, "OK")
            self.finish()
        except:
            pass

    def log_message(self, format, *args):
        return

def serve_async(httpd):
    while True:
        httpd.handle_request()


if __name__ == "__main__":
    request_handler = instaHandler
    SocketServer.TCPServer.allow_reuse_address = True 
    SocketServer.TCPServer.timeout = 1.0 
    INSTA_DIR = os.getcwd()
    os.chdir(WATCH_DIR)
    httpd = SocketServer.TCPServer(("", PORT),
                                   request_handler)

    server_process = mp.Process(target = serve_async,
                                args = (httpd,))
    server_process.start()

    os.chdir(INSTA_DIR)
    event_observer = Observer(OBS_TIMEOUT)
    event_handler = fslWatcher(CONFIG)
    event_observer.schedule(event_handler,
                            WATCH_DIR,
                            recursive=False)
    event_observer.start()
    while True:
        pass
