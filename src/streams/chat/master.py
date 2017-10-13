import datetime
import zmq
import pickle
import threading
import psycopg2
import importlib

from src.utils._functions_general import *
from src.streams.chat.trending import Trending
from src.streams.chat.nlp import NLP


class StreamChatMaster:
    def __init__(self, config, stream):
        self.config = config
        self.stream = stream
        
        self.init_db()
        self.init_sockets()
        self.init_components()
        self.init_threads()

        self.run()

    def init_sockets(self):
        self.context = zmq.Context()
        self.input_socket = self.context.socket(zmq.SUB)
        self.input_socket.connect('tcp://'+self.config['stream_host']+':'+str(self.config['stream_port']))
        self.input_socket.setsockopt(zmq.SUBSCRIBE, "")

        self.fwd_socket = self.context.socket(zmq.PUB)
        self.fwd_socket.connect('tcp://'+self.config['fwd_host']+':'+str(self.config['fwd_port']))

    def init_components(self):
        self.components = {}
        if self.config['trending']:
            self.components['trending'] = Trending(self.config['trending_config'], self.stream)
        if self.config['nlp']:
            self.components['nlp'] = NLP(self.config['nlp_config'], self.stream)

    def init_db(self):
        self.con = psycopg2.connect(dbname=self.config['db_str'],
                                    host=self.config['host_str'],
                                    port=self.config['port_str'],
                                    user=self.config['user_str'],
                                    password=self.config['pw_str'])
        self.cur = self.con.cursor()

    def init_threads(self):
        # zmq connections
        if self.config['trending']:
            threading.Thread(target = self.send_trending).start()
        if self.config['nlp']:
            threading.Thread(target = self.send_nlp).start()

    # ZMQ Processes
    def send_trending(self):
        query = "SELECT max(num) FROM trending WHERE src='%s' AND stream='%s';" % (self.config['src'], self.stream)
        num_set = False
        while not num_set:
            try:
                self.cur.execute(query)
                max_num = self.cur.fetchall()
                if max_num[0][0]:
                    self.trending_num = max_num[0][0] + 1
                else:
                    self.trending_num = 0
                num_set = True
            except Exception, e:
                pp('error setting num trending', 'error')
                time.sleep(self.config['set_num_refresh'])

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
        query = "SELECT max(num) FROM subjects WHERE src='%s' AND stream='%s';" % (self.config['src'], self.stream)
        num_set = False
        while not num_set:
            try:
                self.cur.execute(query)
                max_num = self.cur.fetchall()
                if max_num[0][0]:
                    self.nlp_num = max_num[0][0] + 1
                else:
                    self.nlp_num = 0
                num_set = True
            except Exception, e:
                pp('error setting num nlp', 'error')
                time.sleep(self.config['set_num_refresh'])
        

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