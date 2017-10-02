import zmq
import json
import time

from src.utils._functions_general import *


class Replay:
    def __init__(self, config, params, api):
        pp('Initializing Replay...')
        self.config = config
        self.threadid = params['thread_id']
        self.stream = params['stream']
        self.timestart = params['timestart']
        self.mod = params['mod']
        self.api = api

        self.context = zmq.Context()
        self.set_pipe()
        self.run()

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUB)
        self.pipe.connect('tcp://' +
                          self.config['host'] +
                          ':' +
                           str(self.config['port']))

    def run(self):
        pp('Prepping replay for... '+self.threadid)
        thread = self.api.submission(id=self.threadid)

        posts = []

        thread.comments.replace_more()
        for top_level_comment in thread.comments:
            posts.append(top_level_comment)

        min_time = min(posts, key=lambda x: x.created).created

        strmdict = {}
        for post in posts:
            msg = {
                'type': 'message',
                'stream': self.stream,
                'username': post.name,
                'message': post.body,
                'src_id': post.id
            }
            strmdict[float((post.created - min_time)/self.mod)] = msg

        pp('Starting replay for... '+self.threadid)
        timekeys = sorted(strmdict.iterkeys())
        pp(timekeys)
        ts_start = time.time()
        while (len(timekeys) > 0):
            timekey = timekeys[0]
            if (time.time() - ts_start) > (timekey-self.timestart):
                packet = {}
                packet['data'] = json.dumps(strmdict[timekey]).decode('utf-8', errors='ignore')
                packet['src'] = 'reddit'
                self.pipe.send(json.dumps(packet))
                timekeys.pop(0)
