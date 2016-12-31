# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""

import socket
import threading
import logging
import sys
import json
import time
import requests
import re

logging.basicConfig()

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

from streams.twitch_stream import *
from streams.twitter_stream import *
from config.universal_config import *

import streams.utils.twtr as twtr_

class WebServer(Resource):

    isLeaf = True
    stream_server = None
    
    #server protocol
    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        output = self.handle_GET(request.path, request.args)
        return output

    #get control
    def handle_GET(self, path, args):
        if path[0:7] == '/stream':
            return self.stream_server.get_agg_streams(args)
        elif path[0:8] == '/cpanel/':
            if path[8:14] == 'twitch':
                return self.stream_server.handle_cpanel('twitch',args)
            elif path[8:15] == 'twitter':
                return self.stream_server.handle_cpanel('twitter',args)
            else:
                return json.dumps('Invalid path! Valid paths: /cpanel/twitch and /cpanel/twitter')
        elif path[0:10] == '/featured/':
            if path[10:16] == 'twitch':
                return self.stream_server.get_twitch_featured(args)
            elif path[10:17] == 'twitter':
                return self.stream_server.get_twitter_featured(args)
            else:
                return json.dumps('Invalid path! Valid paths: /featured/twitch and /featured/twitter')
        else:
            return json.dumps('Invalid path! Valid paths: /stream and /cpanel/.../')

class StreamServer():
    def __init__(self, config):
        pp('Initializing Stream Server...')
        self.config = config

        self.twitch_streams = {}
        self.twitter_streams = {}

        #init twitter
        self.twit = twtr_.twtr(twitter_config)

        #CJK regex
        self.pattern = re.compile('[\W_]+')

    #stream control
    def create_stream(self, stream, src):
        threading.Thread(target=self.add_stream, args=(stream,src)).start()

    def add_stream(self, stream, src):
        if src == 'twitch':
            self.twitch_streams[stream] = TwitchStream(twitch_config, stream)
            self.twitch_streams[stream].run()
        elif src == 'twitter':
            self.twitter_streams[stream] = TwitterStream(twitch_config, stream, self.twit)
            self.twitter_streams[stream].run()
        else:
            pass

    #cpanel response
    def handle_cpanel(self, src, args):
        output = []

        if src == 'twitch':
            if 'action' in args.keys():
                for action in args['action'][0].split(','):
                    if action == 'show':
                        pass
                    elif action == 'reset':
                        for stream in self.twitch_streams.keys():
                            self.twitch_streams[stream].kill = True
                            del self.twitch_streams[stream]

            elif 'delete' in args.keys():
                for stream in args['delete'][0].split(','):
                    if stream in self.twitch_streams.keys():
                        self.twitch_streams[stream].kill = True
                        del self.twitch_streams[stream]

            elif 'add' in args.keys():
                for stream in args['add'][0].split(','):
                    if stream in self.twitch_streams.keys():
                        pass
                    else:
                        self.create_stream(stream, 'twitch')

            output = self.twitch_streams.keys()

        elif src == 'twitter':
            if 'action' in args.keys():
                for action in args['action'][0].split(','):
                    if action == 'show':
                        pass
                    elif action == 'refresh':
                        self.twit.refresh_channels()
                    elif action == 'reset':
                        for channel in self.twitter_streams.keys():
                            self.twitter_streams[channel].kill = True
                            del self.twitter_streams[channel]
                        self.twit.reset_channels()  

            elif 'delete' in args.keys():
                for channel in args['delete'][0].split(','):
                    if channel in self.twitter_streams.keys():
                        self.twitter_streams[channel].kill = True
                        del self.twitter_streams[channel]
                        self.twit.leave_channel(channel)

            elif 'add' in args.keys():
                for channel in args['add'][0].split(','):
                    if not channel in self.twitter_streams.keys():
                        self.create_stream(channel, 'twitter')

            output = self.twitter_streams.keys()

        else:
            output = 'INVALID SRC'

        return json.dumps(output)

    def get_agg_streams(self, args):
        config = self.config
        trend_dicts = []

        if ('twitch' in args.keys()) and (len(args['twitch'][0])>0):
            for stream_id in args['twitch'][0].split(','):
                trend_dicts.append(self.get_stream(stream_id, 'twitch'))

        if ('twitter' in args.keys()) and (len(args['twitter'][0])>0):
            for stream_id in args['twitter'][0].split(','):
                trend_dicts.append(self.get_stream(stream_id, 'twitter'))
        
        output = {}
        [output.update(d) for d in trend_dicts]

        if ('filter' in args.keys()) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in output.keys():
                    if keyword.lower() in msg.lower():
                        del output[msg]

        return json.dumps(output)

    def get_stream(self, stream_id, src):
        config = self.config
        stream_id = stream_id.lower()
        stream_id = self.pattern.sub('', stream_id)

        #CJK break
        if len(stream_id) == 0:
            return {}

        if src == 'twitch':
            if not stream_id in self.twitch_streams.keys():
                self.create_stream(stream_id, src)
                stream_exists = False
                while not stream_exists:
                    stream_exists = stream_id in self.twitch_streams.keys()

            output = self.twitch_streams[stream_id].get_trending()

        elif src == 'twitter':
            if not stream_id in self.twitter_streams.keys():
                self.create_stream(stream_id, src)
                stream_exists = False
                while not stream_exists:
                    stream_exists = stream_id in self.twitter_streams.keys()
            output = self.twitter_streams[stream_id].get_trending()

        else:
            output = {}

        return output

    def get_twitter_featured(self, args):
        trends = self.twit.api.trends_place(1)
        output = [{'stream':x['name'],'description':x['name'],'count':x['tweet_volume']} for x in trends[0]['trends'] if x['tweet_volume']!=None]
        sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 
        if ('limit' in args.keys()) and (len(args['limit'][0])>0):
            limit = int(args['limit'][0])
            sorted_output = sorted_output[0:limit]
        return json.dumps(sorted_output)

    def get_twitch_featured(self,args):
        headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Client-ID':self.config['twitch_client_id']}
        r = requests.get('https://api.twitch.tv/kraken/streams/featured', headers = headers)
        output = [{'stream':x['stream']['channel']['name'], 'image': x['stream']['preview']['medium'], 'description': x['title'], 'count': x['stream']['viewers']} for x in (json.loads(r.content))['featured']]
        sorted_output = sorted(output, key=lambda k: k['count'], reverse=True) 
        if ('limit' in args.keys()) and (len(args['limit'][0])>0):
            limit = int(args['limit'][0])
            sorted_output = sorted_output[0:limit]
        return json.dumps(sorted_output)

    def filter_twitch(self):
        self.filter_loop = True
        while self.filter_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    self.twitch_streams[stream_key].filter_trending()

            time.sleep(0.8)

    def render_twitch(self):
        self.clean_loop = True
        while self.clean_loop:
            if len(self.twitch_streams.keys()) > 0:
                for stream_key in self.twitch_streams.keys():
                    self.twitch_streams[stream_key].render_trending()

            time.sleep(0.17)

    def filter_twitter(self):
        self.filter_loop = True
        while self.filter_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    self.twitter_streams[stream_key].filter_trending()

            time.sleep(0.8)

    def render_twitter(self):
        self.clean_loop = True
        while self.clean_loop:
            if len(self.twitter_streams.keys()) > 0:
                for stream_key in self.twitter_streams.keys():
                    self.twitter_streams[stream_key].render_trending()

            time.sleep(0.17)

    def run(self):
        pp('Initializing Web Server...')
        resource = WebServer()
        resource.stream_server = self

        factory = Site(resource)
        #prod aws
        reactor.listenTCP(self.config['port'], factory)

        #local testing
        #reactor.listenTCP(4808, factory)

        pp('Starting Web Server...')
        reactor.run()

if __name__ == '__main__':
    #init
    pythonserver = StreamServer(server_config)
    #twitch helpers
    filter_twitch_thread = threading.Thread(target = pythonserver.filter_twitch).start()
    render_twitch_thread = threading.Thread(target = pythonserver.render_twitch).start()
    #twitter helpers
    filter_twitter_thread = threading.Thread(target = pythonserver.filter_twitter).start()
    render_twitter_thread = threading.Thread(target = pythonserver.render_twitter).start()
    #serve
    pythonserver.run()
