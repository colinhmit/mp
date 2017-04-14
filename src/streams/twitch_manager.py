import threading
import multiprocessing
import requests
import json

from utils.functions_general import *
from utils.twitch_stream import TwitchStream
from strm_mgr import strm_mgr

class TwitchManager(strm_mgr):
    def __init__(self, config, irc, init_streams):
        pp('Initializing Twitch Stream Manager...')
        strm_mgr.__init__(self, config, config['twitch_config']['self'], irc)

        for stream in init_streams:
            self.add_stream(stream)

        self.init_featured()
        self.init_threads()

    def init_featured(self):
        self.sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.sess.mount('https://api.twitch.tv', adapter)

    def init_threads(self):
        threading.Thread(target = self.refresh_featured, args=(self.config['twitch_featured'],)).start()
        threading.Thread(target = self.send_featured, args=(self.config['twitch_featured'],)).start()

    def add_stream(self, stream):
        try:
            if stream not in self.streams:
                self.streams[stream] = multiprocessing.Process(target=TwitchStream, args=(self.config['twitch_config'], stream)) 
                self.inpt.join_stream(stream)
                self.streams[stream].start()
        except Exception, e:
            pp(e)
        
    def get_featured(self):
        headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Client-ID':self.config['twitch_featured']['twitch_client_id']}
        try:
            r = self.sess.get('https://api.twitch.tv/kraken/streams', headers = headers)
            output = [{'title':x['channel']['name'], 'stream':[x['channel']['name']], 'image': x['preview']['medium'], 'description': x['channel']['status'], 'game': x['game'], 'count': x['viewers']} for x in (json.loads(r.content))['streams']]
            sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 
            self.featured = sorted_output[0:self.config['twitch_featured']['num_featured']]
        except Exception, e:
            pp('Get Twitch featured failed.')
            pp(e)