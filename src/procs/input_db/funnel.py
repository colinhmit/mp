import zmq

# import utils
from src.utils._functions_general import *


class Funnel:
    def __init__(self, config):
        self.config = config
        self.context = zmq.Context()
        self.set_sock()
        self.set_pipe()

        self.funnel()

    def set_sock(self):
        self.sock = self.context.socket(zmq.SUB)
        for src in self.config['input_ports'].keys():
            self.sock.connect('tcp://' +
                              self.config['input_host'] +
                              ':' +
                              str(self.config['input_ports'][src]))
        self.sock.setsockopt(zmq.SUBSCRIBE, "")

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUSH)
        self.pipe.bind('tcp://' +
                       self.config['funnel_host'] +
                       ':' +
                       str(self.config['funnel_port']))

    def funnel(self):
        for data in iter(self.sock.recv, '*STOP*'):
            self.pipe.send(data)