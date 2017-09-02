import json
import multiprocessing
import uuid

#import utils
from inputs.utils.functions_general import *
from std_inpt import std_inpt

class RedditInput(std_inpt):
    def __init__(self, config, nlp):
        std_inpt.__init__(self, config, nlp)
        pp('Initializing Reddit Input Server...')

        multiprocessing.Process(target=self.distribute).start()

        for _ in xrange(self.config['num_procs']):
            multiprocessing.Process(target=self.process, args=(self.nlp_parser,)).start()
    
    def parse(self, data):
        jsondata = json.loads(data)
        msg = {
                'src': 'reddit',
                'subreddit': jsondata['subreddit'],
                'username': jsondata['username'],
                'message': jsondata['message'],
                'media_url': [jsondata['media_url']],
                'mp4_url': '',
                'id': str(uuid.uuid1()),
                'src_id': jsondata['id']
                }
        return msg