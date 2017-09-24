import datetime
import zmq
import pickle
import threading

from _functions_general import *
from utils.aggregator import Aggregator
from utils.analyzer import Analyzer
from utils.consolidator import Consolidator
from utils.enricher import Enricher

class Stream:
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
                        'content': dict(self.content),
                        'enrich': list(self.enrich),
                        'default_image': self.default_image['image']
                    }
                }
                pickled_data = pickle.dumps(data)
                self.http_socket.send(pickled_data)
                self.enrichdecay = []
            except Exception, e:
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

    #Main func
    def run(self):
        for data in iter(self.input_socket.recv, 'STOP'):
            #try: msg_data may be unpickleable?
            try:
                msg_data = pickle.loads(data)
                if len(msg_data) == 0:
                    pp('Native connection was lost...')
                if self.stream == msg_data['stream']:
                    messagetime = datetime.datetime.now()
                    self.process_message(msg_data, messagetime)  
                    self.last_rcv_time = messagetime
                    self.freq_count += 1
            except Exception, e:
                pp(e)


    #Main func
    def run(self):        
        for data in iter(self.input_socket.recv, 'STOP'):
            #try: msg_data may be unpickleable?
            try:
                msg_data = pickle.loads(data)
                if len(msg_data) == 0:
                    pp('Reddit connection was lost...')
                if self.stream == msg_data['subreddit']:
                    messagetime = datetime.datetime.now()
                    self.process_message(msg_data, messagetime)  
                    self.last_rcv_time = messagetime
            except Exception, e:
                pp(e)

    #Main func
    def run(self):
        for data in iter(self.input_socket.recv, 'STOP'):
            #try: msg_data may be unpickleable?
            try:
                msg_data = pickle.loads(data)
                if len(msg_data) == 0:
                    pp('Twitch connection was lost...')
                if self.stream == msg_data['channel'][1:].lower():
                    messagetime = datetime.datetime.now()
                    self.process_message(msg_data, messagetime)  
                    self.last_rcv_time = messagetime
            except Exception, e:
                pp(e)
        

    #Main func
    def run(self):
        for data in iter(self.input_socket.recv, 'STOP'):
            #try: msg_data may be unpickleable?
            try:
                msg_data = pickle.loads(data)
                if len(msg_data) == 0:
                    pp('Twitter connection was lost...')
                if (self.stream in msg_data['message'].lower()):
                    messagetime = datetime.datetime.now()
                    self.process_message(msg_data, messagetime)  
                    self.last_rcv_time = messagetime
            except Exception, e:
                pp(e)
