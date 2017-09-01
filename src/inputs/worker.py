import random
import zmq
import pickle
import gc
import re
import multiprocessing

# import utils
from utils._functions_general import *


class Worker:
    def __init__(self, config, nlp):
        self.config = config
        self.nlp_parser = nlp

        self.context = zmq.Context()
        self.set_sock()
        self.set_pipe()

        self.process(nlp)

    def set_sock(self):
        self.sock = self.context.socket(zmq.PULL)
        for port in self.config['input_ports']:
       		self.sock.connect('tcp://'+self.config['input_host']+':'+str(port))
        
    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUB)
       	for port in self.config['dist_ports']:
       		self.pipe.connect('tcp://'+self.config['zmq_proc_host']+':'+str(self.config['zmq_proc_port']))
	

    def process(self, nlp):
        
        recvr = 
        recvr.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port']))
        recvr.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port']))
        recvr.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port']))


        sendr = context.socket(zmq.PUB)
        sendr.connect('tcp://'+self.config['zmq_proc_host']+':'+str(self.config['zmq_proc_port']))

        svomap = {}
        svorefresh = random.randint(500, 1000)

        for data in iter(recvr.recv_string, 'STOP'):
            msg = self.parse(data)
            if len(msg) > 0:
                hashid = hash(msg['message'])
                if hashid in svomap:
                    svos, subjs = svomap[hashid]
                else:
                    clean_msg = re.sub(r"http\S+", "", msg['message'])
                    clean_msg = re.sub(r"[#@]", "", clean_msg)
                    clean_msg = re.sub(r"[^\w\s\'\"!.,&?:;_%-]+", "", clean_msg)
                    try:
                        svos, subjs = nlp.parse_text(clean_msg)
                    except Exception, e:
                        svos = []
                        subjs = []
                    svomap[hashid] = svos, subjs

                msg['svos'] = svos
                msg['subjs'] = subjs

                if len(svomap)>svorefresh:
                    svomap = {}
                    nlp.flush()
                    gc.collect()

                # constrained off
                # msg['svos'] = []
                # msg['subjs'] = []
                pickled_data = pickle.dumps(msg)
                sendr.send(pickled_data)