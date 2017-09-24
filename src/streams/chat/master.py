import datetime
import zmq
import pickle
import threading
import importlib

from src.utils._functions_general import *
from src.streams.chat.trending import Trending
from src.streams.chat.content import Content
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

        # self.http_socket = context.socket(zmq.PUSH)
        # self.http_socket.connect('tcp://'+self.config['zmq_http_host']+':'+str(self.config['zmq_http_port']))

        # self.data_socket = context.socket(zmq.PUB)
        # self.data_socket.connect('tcp://'+self.config['zmq_data_host']+':'+str(self.config['zmq_data_port']))

    def init_components(self):
        self.trending = Trending(self.config['trending_config'], self.stream)
        #self.content = Content(self.config['content_config'], self.stream)
        self.components = NLP(self.config['nlp_config'], self.stream)

    def init_threads():
        pass

    # ZMQ Processes
    # def send_stream(self):
    #     self.send_stream_loop = True
    #     while self.send_stream_loop:
    #         # try: send stream could break?
    #         try:
    #             data = {
    #                 'type':     'stream',
    #                 'src':      self.config['src'],
    #                 'stream':   self.stream,
    #                 'data':     {k: dict(v.data) for k, v in self.components}
    #             }
    #             pickled_data = pickle.dumps(data)
    #             self.http_socket.send(pickled_data)
    #         except Exception, e:
    #             pp(self.config['src'] + ":" + self.stream + ': failed send_stream', 'error')
    #             pp(e)
    #         time.sleep(self.config['send_stream_refresh'])

    #Main func
    def run(self):
        module = importlib.import_module(self.config['modules'][self.config['src']])
        check_stream = getattr(module, 'check_stream')
        for data in iter(self.input_socket.recv, 'STOP'):
            #try: msg_data may be unpickleable?
            try:
                msg_data = pickle.loads(data)
                if len(msg_data) == 0:
                    pp(self.config['src'] + ":" + self.stream + ': connection lost', 'error')
                if check_stream(self.stream, msg_data):
                    messagetime = datetime.datetime.now()
                    self.trending.process(msg_data, messagetime)
                    #self.content.process(self.trending.data)
                    self.nlp.process(msg_data)
            except Exception, e:
                pp(e)
