import multiprocessing
import zmq
import gc
import json
import uuid

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

from utils._functions_general import *
from utils.input_base import InputBase

# 1. Twitter Input Handler
# 2. STDListener
# 3. Twitter Parser


class Input(InputBase):
    def __init__(self, config):
        InputBase.__init__(self, config)
        self.set_sock()
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams) > 0:
            self.stream_conn.start()

    def stream_connection(self):
        self.context = zmq.Context()
        self.set_pipe()
        # try: connection dies occasionally
        try:
            self.sock.filter(track=self.streams)
            gc.collect()
        except Exception, e:
            pp('////Twitter Connection Died, Restarting////', 'error')
            pp(e, 'error')

    def set_sock(self):
        self.l = Listener(self.config)
        self.auth = OAuthHandler(self.config['consumer_token'],
                                 self.config['consumer_secret'])
        self.auth.set_access_token(self.config['access_token'],
                                   self.config['access_secret'])
        self.api = API(self.auth)
        self.sock = Stream(self.auth, self.l)

    def set_pipe(self):
        self.l.pipe = self.context.socket(zmq.PUSH)
        connected = False
        while not connected:
            # try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.l.pipe.bind('tcp://' +
                                 self.config['input_host'] +
                                 ':' +
                                 str(self.config['input_port']))
                connected = True
            except Exception, e:
                pass


class Listener(StreamListener):
    def __init__(self, config):
        self.config = config
        self.pipe = None

    def on_data(self, data):
        packet = {
            'src':      self.config['src'],
            'data':     data.decode('utf-8', errors='ignore')
        }
        self.pipe.send_string(json.dumps(packet))
        return True

    def on_error(self, status):
        pp(status, 'error')

    def on_timeout(self):
        pp('Timeout...')


def parse(data):
    # try: data may be corrupt
    try:
        data = json.loads(data)

        if data.get('possibly_sensitive', False):
            return {}

        msg = {
               'src':           'twitter',
               'username':      data['user']['name'],
               'message':       '',
               'media_urls':    [],
               'mp4_url':       '',
               'id':            str(uuid.uuid1()),
               'src_id':        data['id_str']
              }

        if data.get('retweeted_status', {}).get('text', False):
            msg['message'] = data['retweeted_status']['text']
            if data['retweeted_status']['entities'].get('media', False):
                msg['media_urls'] = [data['retweeted_status']['entities']['media'][0]['media_url']]
                if (data.get('extended_entities', {})
                        .get('media', [{}])[0]
                        .get('video_info', {})
                        .get('variants', False)):
                    msg['mp4_url'] = max(data['extended_entities']
                                             ['media'][0]['video_info']
                                             ['variants'],
                                         key=lambda x: x['bitrate']
                                         if x['content_type'] == "video/mp4"
                                         else 0)['url']
        elif data.get('text', False):
            msg['message'] = data['text']
            if data['entities'].get('media', False):
                msg['media_urls'] = [data['entities']['media'][0]['media_url']]
                if (data.get('extended_entities', {})
                        .get('media', [{}])[0]
                        .get('video_info', {})
                        .get('variants', False)):
                    msg['mp4_url'] = max(data['extended_entities']
                                             ['media'][0]['video_info']
                                             ['variants'],
                                         key=lambda x: x['bitrate']
                                         if x['content_type'] == "video/mp4"
                                         else 0)['url']

        if msg['message'][:4] == 'RT @':
            msg['message'] = msg['message'][msg['message'].find(':')+1:]

        return msg
    except Exception, e:
        pp('parse_twitter failed', 'error')
        pp(e, 'error')
        return {}
