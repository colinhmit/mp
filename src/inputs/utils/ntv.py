import json
import zmq
import threading
import Queue

from functions_general import *

class ntv:
    def __init__(self, config):
        pp('Initializing Native Input...')
        self.config = config
        self.replays = {}

        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        self.stream_conn.start()

    def stream_connection(self):
        context = zmq.Context()
        self.out_pipe = context.socket(zmq.PUSH)
        out_connected = False
        while not out_connected:
            #try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.out_pipe.bind('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port']))
                out_connected = True
            except Exception, e:
                pass

        self.in_pipe = context.socket(zmq.SUB)
        in_connected = False
        while not in_connected:
            #try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.in_pipe.bind('tcp://'+self.config['ntv_host']+':'+str(self.config['ntv_port']))
                self.in_pipe.setsockopt(zmq.SUBSCRIBE, "")
                in_connected = True
            except Exception, e:
                pass

        for raw_data in iter(self.in_pipe.recv, 'STOP'):
            pp(raw_data)
            self.out_pipe.send(raw_data)