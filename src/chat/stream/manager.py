import re
import time
import zmq
import requests
import pickle

from utils.functions_general import *

class strm_mgr:
    def __init__(self, config, src, inpt):
        self.config = config
        self.src = src 
        self.inpt = inpt

        self.streams = {}
        self.featured = []

        self.pattern = re.compile('[^\w\s\'\"!.,$&?:;_-]+')
        self.init_sockets()

    def init_sockets(self):
        context = zmq.Context()
        self.http_socket = context.socket(zmq.PUSH)
        self.http_socket.connect('tcp://'+self.config['zmq_http_host']+':'+str(self.config['zmq_http_port']))

    def delete_stream(self, stream):
        if stream in self.streams:
            try:
                self.streams[stream].terminate()
                del self.streams[stream]
                self.inpt.leave_stream(stream)
                self.send_delete([stream])
            except Exception, e:
                pp(e)

    # Helper threads
    def refresh_featured(self, config):
        self.refresh_loop = True
        while self.refresh_loop:
            self.get_featured()
            self.send_featured()
            time.sleep(config['refresh_featured_timeout'])

    def get_featured(self):
        pass

    def send_featured(self):
        try:
            data = {
                'type': 'featured',
                'src': self.src,
                'data': self.featured
            }
            pickled_data = pickle.dumps(data)
            self.http_socket.send(pickled_data)
        except Exception, e:
            pp(e)

    def send_delete(self, streams):
        try:
            data = {
                'type': 'delete',
                'src': self.src,
                'data': streams
            }
            pickled_data = pickle.dumps(data)
            self.http_socket.send(pickled_data)
        except Exception, e:
            pp(e)