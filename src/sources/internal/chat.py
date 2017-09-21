import json
import zmq
import multiprocessing

from src.utils._functions_general import *
from src.sources.template.chat_base import ChatBase

# 1. Internal Input Handler


class InternalChat(ChatBase):
    def __init__(self, config, streams):
        ChatBase.__init__(self, config, streams)
        self.config = config

        self.conn = multiprocessing.Process(target=self.chat_connection)
        self.conn.start()

    def chat_connection(self):
        self.context = zmq.Context()
        self.set_sock()
        self.set_pipe()

        for data in iter(self.sock.recv, '*STOP*'):
            packet = {
                'src':      self.config['src'],
                'data':     data.decode('utf-8', errors='ignore')
            }
            self.pipe.send_string(json.dumps(packet))

    def set_sock(self):
        self.sock = self.context.socket(zmq.SUB)
        connected = False
        while not connected:
            # try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.sock.bind('tcp://' +
                               self.config['host'] +
                               ':' +
                               str(self.config['port']))
                self.sock.setsockopt(zmq.SUBSCRIBE, "")
                connected = True
            except Exception, e:
                pass

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUSH)
        connected = False
        while not connected:
            # try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.pipe.bind('tcp://' +
                               self.config['input_host'] +
                               ':' +
                               str(self.config['input_port']))
                connected = True
            except Exception, e:
                pass
