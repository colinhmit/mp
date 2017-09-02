import json
import threading
import time
import Queue

from _functions_general import *


class rply:
    def __init__(self, queue, logpath, logfile, stream, timestart):
        pp('Initializing Replay...')
        self.Q = queue
        self.logpath = logpath
        self.logfile = logfile
        self.stream = stream
        self.timestart = timestart
        self.stop = False

        threading.Thread(target = self.run).start()

    def run(self):
        pp('Starting replay for... '+self.logfile)
        f = open(self.logpath+self.logfile+'.txt', 'r')
        
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
        while (len(timekeys) > 0) & (not self.stop):
            timekey = timekeys[0]
            if (time.time() - ts_start) > (timekey-self.timestart):
                self.Q.put(json.dumps(strmdict[timekey]))
                timekeys.pop(0)