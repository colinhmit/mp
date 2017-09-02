import multiprocessing
import re
import uuid

#import utils
from utils.functions_general import *
from std_inpt import std_inpt

class TwitchInput(std_inpt):
    def __init__(self, config, nlp):
        std_inpt.__init__(self, config, nlp)
        pp('Initializing Twitch Input Server...')
        
        multiprocessing.Process(target=self.distribute).start()

        for _ in xrange(self.config['num_procs']):
            multiprocessing.Process(target=self.process, args=(self.nlp_parser,)).start()
    
    def parse(self, data):
        msg = {
                'src': 'twitch',
                'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
                'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
                'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0],
                'media_url': [],
                'mp4_url': '',
                'id': str(uuid.uuid1()),
                'src_id': ''
                }
        return msg