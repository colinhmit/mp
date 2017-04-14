import multiprocessing
import json

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
    
    def parse(self, data):
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