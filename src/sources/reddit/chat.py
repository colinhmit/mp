import json
import zmq
import Queue
import multiprocessing
import threading

from src.utils._functions_general import *
from src.sources.template.chat_base import ChatBase


class RedditChat(ChatBase):
    def __init__(self, config, streams, api):
        ChatBase.__init__(self, config, streams)
        self.config = config
        self.api = api

        self.conn = multiprocessing.Process(target=self.chat_connection)
        if len(self.streams) > 0:
            self.conn.start()

    def chat_connection(self):
        self.context = zmq.Context()
        self.set_sock()
        self.set_pipe()

        for data in iter(self.sock.get, '*STOP*'):
            packet = {
                'src':      self.config['src'],
                'data':     data.decode('utf-8', errors='ignore')
            }
            self.pipe.send_string(json.dumps(packet))

    def set_sock(self):
        self.sock = Queue.Queue()
        for stream in self.streams:
            threading.Thread(target=self.subreddit_monitor,
                             args=(stream,)).start()

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUSH)
        connected = False
        while not connected:
            # try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.pipe.bind('tcp://' +
                               self.config['input_host'] +
                               ':' +
                               str(self.config['input_port']))
                connected = True
            except Exception, e:
                pass

    def subreddit_monitor(self, stream):
        subreddit = self.api.subreddit(stream)
        content = {}

        alive = True
        while alive:
            # try: reddit praw may fail on hot iteration.
            try:
                if len(content) > 1000:
                    content = {}

                max_diff = 0
                max_post = None
                hot = subreddit.hot(limit=100)
                for post in hot:
                    if post.id not in content:
                        content[post.id] = post.score
                    else:
                        if (post.score - content[post.id]) > max_diff:
                            max_diff = post.score - content[post.id]
                            max_post = post
                        content[post.id] = post.score

                if max_post:
                    if not max_post.author:
                        data = {
                                'stream':       stream,
                                'username':     'deleted',
                                'message':      max_post.title,
                                'media_urls':   max_post.url,
                                'src_id':       max_post.id
                                }
                    else:
                        data = {
                                'stream':       stream,
                                'username':     max_post.author.name,
                                'message':      max_post.title,
                                'media_urls':   max_post.url,
                                'src_id':       max_post.id
                                }
                    self.sock.put(json.dumps(data))
            except Exception, e:
                pp('////Reddit Subreddit Failed////', 'error')
                pp(e, 'error')
