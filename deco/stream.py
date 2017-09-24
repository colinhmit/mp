import datetime
import zmq
import pickle
import threading

from _functions_general import *


class StreamBase:
    def __init__(self, config, stream):
        self.config = config
        self.stream = stream
       
        self.init_sockets()
        self.init_components()
        self.init_threads()
        self.run()

    def init_sockets(self):
        context = zmq.Context()
        self.input_socket = context.socket(zmq.SUB)
        self.input_socket.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port']))
        self.input_socket.setsockopt(zmq.SUBSCRIBE, "")

        self.http_socket = context.socket(zmq.PUSH)
        self.http_socket.connect('tcp://'+self.config['zmq_http_host']+':'+str(self.config['zmq_http_port']))

        self.data_socket = context.socket(zmq.PUB)
        self.data_socket.connect('tcp://'+self.config['zmq_data_host']+':'+str(self.config['zmq_data_port']))

    # ZMQ Processes
    def send_stream(self):
        self.send_stream_loop = True
        while self.send_stream_loop:
            #try: send stream could break?
            try:
                data = {
                    'type': 'stream',
                    'src': self.config['self'],
                    'stream': self.stream,
                    'enrichdecay': list(self.enrichdecay),
                    'ad_trigger': self.ad_trigger,
                    'data': {
                        'trending': dict(self.clean_trending),
                        'enrich': list(self.enrich)
                    }
                }
                pickled_data = pickle.dumps(data)
                self.http_socket.send(pickled_data)
                self.enrichdecay = []
                self.ad_trigger = False
            except Exception, e:
                pp('failed send_stream')
                pp(e)
            time.sleep(self.config['send_stream_timeout'])

    def send_analytics(self):
        self.send_analytics_loop = True
        while self.send_analytics_loop:
            #try: send analytics could break?
            try:
                data = {
                    'type': 'subjects',
                    'src': self.config['self'],
                    'stream': self.stream,
                    'data': dict(self.subjs)
                }
                pickled_data = pickle.dumps(data)
                self.data_socket.send(pickled_data)
            except Exception, e:
                pp('failed send_analytics')
                pp(e)
            time.sleep(self.config['send_analytics_timeout'])

    # Manager Processes
    def reset_subjs_thread(self):
        self.reset_subjs_loop = True
        while self.reset_subjs_loop:
            #try: reset subjs could break?
            try:
                self.subjs = {}
            except Exception, e:
                pp('failed reset_subjs_thread')
                pp(e)
            time.sleep(self.config['reset_subjs_timeout'])
