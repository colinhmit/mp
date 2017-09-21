import json
import zmq
import multiprocessing
import uuid

from src.utils._functions_general import *
from src.sources.template.chat_base import ChatBase

# 1. Internal Input Handler
# 2. Internal Parser


class Chat(ChatBase):
    def __init__(self, config):
        ChatBase.__init__(self, config)
        self.config = config

        self.chat_conn = multiprocessing.Process(target=self.chat_connection)
        self.chat_conn.start()

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


def parse(data):
    # try: data may be corrupt
    try:
        data = json.loads(data)
        msg = {
               'src':           'internal',
               'stream':        data.get('stream', ''),
               'username':      data.get('username', ''),
               'message':       data.get('message', ''),
               'media_urls':    data.get('media_urls', []),
               'mp4_url':       '',
               'id':            str(uuid.uuid1()),
               'src_id':        data.get('src_id', '')
              }
        return msg
    except Exception, e:
        pp('parse_internal failed', 'error')
        pp(e, 'error')
        return {}
