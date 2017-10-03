import datetime
import zmq
import pickle
import threading
import importlib

from src.utils._functions_general import *
from src.streams.chat.trending import Trending
from src.streams.chat.nlp import NLP


class StreamChatMaster:
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
        self.input_socket.connect('tcp://'+self.config['stream_host']+':'+str(self.config['stream_port']))
        self.input_socket.setsockopt(zmq.SUBSCRIBE, "")

        self.fwd_socket = context.socket(zmq.PUB)
        self.fwd_socket.connect('tcp://'+self.config['fwd_host']+':'+str(self.config['fwd_port']))

    def init_components(self):
        self.components = {}
        if self.config['trending']:
            self.components['trending'] = Trending(self.config['trending_config'], self.stream)
        if self.config['nlp']:
            self.components['nlp'] = NLP(self.config['nlp_config'], self.stream)

    def init_threads(self):
        # zmq connections
        if self.config['trending']:
            threading.Thread(target = self.send_trending).start()
        if self.config['nlp']:
            threading.Thread(target = self.send_nlp).start()

    # ZMQ Processes
    def send_trending(self):
        self.trending_num = 0

        self.send_trending_loop = True
        while self.send_trending_loop:
            # try: send stream could break?
            try:
                data = {
                    'type':     'stream_trending',
                    'time':     datetime.datetime.now().isoformat(),
                    'num':      self.trending_num,
                    'src':      self.config['src'],
                    'stream':   self.stream,
                    'data':     dict(self.components['trending'].data)
                }
                pickled_data = pickle.dumps(data)
                self.fwd_socket.send(pickled_data)
                self.trending_num += 1
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed send_trending', 'error')
                pp(e)
            time.sleep(self.config['send_trending_refresh'])

    # ZMQ Processes
    def send_nlp(self):
        self.nlp_num = 0

        self.send_nlp_loop = True
        while self.send_nlp_loop:
            # try: send stream could break?
            try:
                data = {
                    'type':     'stream_nlp',
                    'time':     datetime.datetime.now().isoformat(),
                    'num':      self.nlp_num,
                    'src':      self.config['src'],
                    'stream':   self.stream,
                    'data':     dict(self.components['nlp'].data)
                }
                pickled_data = pickle.dumps(data)
                self.fwd_socket.send(pickled_data)
                self.nlp_num += 1
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed send_nlp', 'error')
                pp(e)
            time.sleep(self.config['send_nlp_refresh'])

    #Main func
    def run(self):
        module = importlib.import_module(self.config['module'])
        check_stream = getattr(module, 'check_stream')
        for data in iter(self.input_socket.recv, 'STOP'):
            #try: msg_data may be unpickleable?
            try:
                msg_data = pickle.loads(data)
                if len(msg_data) == 0:
                    pp(self.config['src'] + ":" + self.stream + ': connection lost', 'error')
                if check_stream(self.stream, msg_data):
                    messagetime = datetime.datetime.now()
                    if self.config['trending']:
                        self.components['trending'].process(msg_data, messagetime)
                    if self.config['nlp']:
                        self.components['nlp'].process(msg_data, messagetime)
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed run!', 'error')
                pp(e, 'error')
