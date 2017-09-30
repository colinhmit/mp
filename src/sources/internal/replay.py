import zmq
import json
import time

from src.utils._functions_general import *


class Replay:
    def __init__(self, config, logfile, stream, timestart):
        pp('Initializing Replay...')
        self.config = config
        self.logfile = logfile
        self.stream = stream
        self.timestart = timestart

        self.context = zmq.Context()
        self.set_pipe()
        self.run()

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUB)
        self.pipe.connect('tcp://' +
                          self.config['host'] +
                          ':' +
                           str(self.config['port']))

    def run(self):
        pp('Starting replay for... '+self.logfile)
        f = open(self.config['logpath'] + self.logfile + '.txt', 'r')
        
        strmdict = {}
        for line in f:
            str_msg = line.split("_")
            if len(str_msg) == 3:
                msg = {
                    'type': 'message',
                    'stream': self.stream,
                    'username': str_msg[1],
                    'message': str_msg[2].decode('utf-8')
                }
                strmdict[float(str_msg[0])] = msg
            elif len(str_msg) == 5:
                msg = {
                    'type': 'message',
                    'stream': self.stream,
                    'username': str_msg[1],
                    'message': str_msg[2].decode('utf-8'),
                    'media_url': [str_msg[3]],
                    'src_id': str_msg[4]
                }
                strmdict[float(str_msg[0])] = msg
            
        timekeys = sorted(strmdict.iterkeys())
        ts_start = time.time()
        while (len(timekeys) > 0):
            timekey = timekeys[0]
            if (time.time() - ts_start) > (timekey-self.timestart):
                packet = {}
                packet['data'] = json.dumps(strmdict[timekey]).decode('utf-8', errors='ignore')
                packet['src'] = 'twitch'
                self.pipe.send(json.dumps(packet))
                timekeys.pop(0)
