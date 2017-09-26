import zmq

# import utils
from src.utils._functions_general import *


class Distributor:
    def __init__(self, config):
        self.config = config
        self.context = zmq.Context(1)
        self.set_sock()
        self.set_pipe()

        self.distribute()

    def set_sock(self):
        self.sock = self.context.socket(zmq.SUB)
        self.sock.bind("tcp://*:" + str(self.config['dist_port']))
        self.sock.setsockopt(zmq.SUBSCRIBE, "")

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUB)
        self.pipe.bind("tcp://*:" + str(self.config['stream_port']))

    def distribute(self):
        distributing = True
        while distributing:
            # zmq distributor might die?
            try:
                zmq.device(zmq.FORWARDER, self.sock, self.pipe)
            except Exception, e:
                pp('ZMQ Distributor died!', 'error')
                pp(e, 'error')
