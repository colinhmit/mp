import zmq
import multiprocessing

# import utils
from src.utils._functions_general import *


class Forwarder:
    def __init__(self, config):
        self.config = config
        
        self.forwarder = multiprocessing.Process(target=self.forward)
        self.forwarder.start()

    def set_sock(self):
        self.sock = self.context.socket(zmq.SUB)
        self.sock.bind("tcp://*:" + str(self.config['fwd_port_input']))
        self.sock.setsockopt(zmq.SUBSCRIBE, "")

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUB)
        self.pipe.bind("tcp://*:" + str(self.config['fwd_port_output']))

    def forward(self):
        self.context = zmq.Context(1)
        self.set_sock()
        self.set_pipe()

        forwarding = True
        while forwarding:
            # zmq forwarder might die?
            try:
                zmq.device(zmq.FORWARDER, self.sock, self.pipe)
            except Exception, e:
                pp('ZMQ Forwarder died!', 'error')
                pp(e, 'error')
