import json
import zmq
import multiprocessing

from tweepy.streaming import StreamListener
from tweepy import Stream

from src.utils._functions_general import *
from src.sources._template.chat_base import ChatBase


class Chat(ChatBase):
    def __init__(self, config, streams, auth):
        ChatBase.__init__(self, config, streams)
        self.config = config
        self.auth = auth
        self.set_sock()

        self.conn = multiprocessing.Process(target=self.chat_connection)
        self.conn.start()

    def chat_connection(self):
        chat_streams = [k for k, v in self.streams.items() if v['chat_con']]
        if len(chat_streams) > 0:      
            self.context = zmq.Context()
            self.set_pipe()
            # try: connection dies occasionally
            try:
                pp(chat_streams)
                self.sock.filter(track=chat_streams)
                gc.collect()
            except Exception, e:
                pp('////Twitter Connection Died, Restarting////', 'error')
                pp(e, 'error')

    def set_sock(self):
        self.l = Listener(self.config)
        self.sock = Stream(self.auth, self.l)

    def set_pipe(self):
        self.l.pipe = self.context.socket(zmq.PUSH)
        connected = False
        while not connected:
            # try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.l.pipe.bind('tcp://' +
                                 self.config['input_host'] +
                                 ':' +
                                 str(self.config['input_port']))
                connected = True
            except Exception, e:
                pass


class Listener(StreamListener):
    def __init__(self, config):
        self.config = config
        self.pipe = None

    def on_data(self, data):
        packet = {
            'src':      self.config['src'],
            'data':     data.decode('utf-8', errors='ignore')
        }
        self.pipe.send_string(json.dumps(packet))
        return True

    def on_error(self, status):
        pp(status, 'error')

    def on_timeout(self):
        pp('Timeout...')