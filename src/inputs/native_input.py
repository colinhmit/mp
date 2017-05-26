import multiprocessing
import json
import zmq
import re
import random
import pickle
import gc
import uuid

#import utils
from utils.functions_general import *
from std_inpt import std_inpt

class NativeInput(std_inpt):
    def __init__(self, config, nlp):
        std_inpt.__init__(self, config, nlp)
        pp('Initializing Native Input Server...')
        
        multiprocessing.Process(target=self.distribute).start()

        for _ in xrange(self.config['num_procs']):
            multiprocessing.Process(target=self.process, args=(self.nlp_parser,)).start()
    
    def process(self, nlp):
        context = zmq.Context()
        recvr = context.socket(zmq.PULL)
        recvr.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port']))
        recvr.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port_2']))

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

    def parse(self, data):
        try:
            jsondata = json.loads(data)
            msg = {
                    'src': 'native',
                    'stream': jsondata['stream'],
                    'username': jsondata['username'],
                    'message': jsondata['message'],
                    'media_url': [],
                    'mp4_url': '',
                    'id': ''
                    }
            return msg
        except Exception, e:
            pp('parse native failed')
            pp(e)
            return {}
        