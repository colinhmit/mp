import multiprocessing
import zmq
import gc

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

from utils._functions_general import *
from utils.input_base import base

class Listener(StreamListener):
    def __init__(self, config):
        self.config = config
        self.pipe = None

    def on_data(self, data):
        self.pipe.send_string(self.config['self']+data.decode('utf-8', errors='ignore'))
        return True

    def on_error(self, status):
        pp(status, 'error')

    def on_timeout(self):
        pp('Timeout...')

class twitter(base):
    def __init__(self, config, init_streams):
        base.__init__(self, config, init_streams)
        self.set_sock()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def stream_connection(self):
        self.context = zmq.Context()
        self.set_pipe()
        #try: connection dies occasionally
        try:
            self.sock.filter(track=self.streams)
            gc.collect()
        except Exception, e:
            pp('////Twitter Connection Died, Restarting////','error')
            pp(e,'error')

     def set_sock(self):
        self.l = Listener(self.config['input_port'])
        self.auth = OAuthHandler(self.config['consumer_token'], self.config['consumer_secret'])
        self.auth.set_access_token(self.config['access_token'], self.config['access_secret'])
        self.api = API(self.auth)
        self.sock = Stream(self.auth, self.l)

    def set_pipe(self):
        self.l.pipe = self.context.socket(zmq.PUSH)
        connected = False
        while not connected:
            #try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.l.pipe.bind('tcp://'+self.config['input_host']+':'+str(self.config['input_port']))
                connected = True
            except Exception, e:
                pass
