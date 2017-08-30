import threading
import multiprocessing
import zmq
import Queue
import json
import praw

from utils._functions_general import *
from utils.input_base import base

class reddit(base):
    def __init__(self, config, init_streams):
        base.__init__(self, config, init_streams)
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams)>0:
            self.stream_conn.start()

    def stream_connection(self):
        self.context = zmq.Context()
        self.set_sock()
        self.set_pipe()

        for data in iter(self.sock.get, '*STOP*'):
            self.pipe.send_string(self.config['self']+data.decode('utf-8', errors='ignore'))

    def set_sock(self):
        self.reddit = praw.Reddit(client_id=self.config['client_token'],
                     client_secret=self.config['client_secret'],
                     user_agent=self.config['user_agent'])
        self.sock = Queue.Queue()
        for stream in self.streams:
            threading.Thread(target=self.subreddit_monitor, args=(stream,)).start()

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUSH)
        connected = False
        while not connected:
            #try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.pipe.bind('tcp://'+self.config['input_host']+':'+str(self.config['input_port']))
                connected = True
            except Exception, e:
                pass

    def subreddit_monitor(self, stream):
        subreddit = self.reddit.subreddit(stream)
        content = {}

        alive = True
        while alive:
            #try: reddit praw may fail on hot iteration.
            try:
                if len(content)>1000:
                    content = {}

                max_diff = 0
                max_post = None
                hot = subreddit.hot(limit=100)
                for post in hot:
                    if post.id not in content:
                        content[post.id] = post.score
                    else:
                        if (post.score - content[post.id])>max_diff:
                            max_diff = post.score - content[post.id]
                            max_post = post
                        content[post.id] = post.score

                if max_post:
                    if not max_post.author:
                        data = {
                                'subreddit': stream,
                                'username': 'deleted',
                                'message': max_post.title,
                                'media_url': max_post.url,
                                'id': max_post.id
                                }
                    else:
                        data = {
                                'subreddit': stream,
                                'username': max_post.author.name,
                                'message': max_post.title,
                                'media_url': max_post.url,
                                'id': max_post.id
                                }
                    self.sock.put(json.dumps(data)) 
            except Exception, e:
                pp('////Reddit Subreddit Failed////','error')
                pp(e,'error')