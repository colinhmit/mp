# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import socket
import threading
import logging
import sys
import struct
import json
import time
import requests
import re
import pickle
import operator
import datetime

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

from streams.utils.functions_general import *
from config.universal_config import *

class WebServer(Resource):

    isLeaf = True
    stream_client = None
    
    #server protocol
    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        output = self.handle_GET(request.path, request.args)
        return output

    #get control
    def handle_GET(self, path, args):
        if path[0:7] == '/stream':
            return self.stream_client.get_agg_streams(args)
        elif path[0:8] == '/content':
            return self.stream_client.get_agg_content(args)
        elif path[0:10] == '/analytics':
            return self.stream_client.get_agg_analytics(args)
        elif path[0:5] == '/top/':
            if path[5:12] == 'twitter':
                return self.get_top_twitter_streams(args)
            else:
                return json.dumps('Invalid path! Valid path: /top/twitter')
        elif path[0:8] == '/cpanel/':
            if path[8:14] == 'twitch':
                return self.stream_client.handle_cpanel('twitch',args)
            elif path[8:15] == 'twitter':
                return self.stream_client.handle_cpanel('twitter',args)
            else:
                return json.dumps('Invalid path! Valid paths: /cpanel/twitch and /cpanel/twitter')
        elif path[0:10] == '/featured/':
            if path[10:16] == 'twitch':
                return self.stream_client.get_featured('twitch', args)
            elif path[10:17] == 'twitter':
                return self.stream_client.get_featured('twitter', args)
            else:
                return json.dumps('Invalid path! Valid paths: /featured/twitch and /featured/twitter')
        else:
            return json.dumps('Invalid path! Valid paths: /stream and /cpanel/.../')

class StreamClient():
    def __init__(self, config):
        pp('Initializing Stream Client...')
        self.config = config
        self.init_sockets()

        self.twitch_streams = {}
        self.twitter_streams = {}

        self.twitch_featured = []
        self.twitter_featured = []
        self.target_twitter_streams = []

        self.analytics = {}

        #CJK regex
        self.pattern = re.compile('[^\w\s\'\"!.,$&?:;_-]+')

        self.init_threads()
        self.run()

    def init_sockets(self):
        config = self.config

        request_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request_sock.connect((config['request_host'], config['request_port']))
        self.request_sock = request_sock

        twitch_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        twitch_data_sock.connect((config['data_host'], config['twitch_data_port']))
        self.twitch_data_sock = twitch_data_sock

        twitter_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        twitter_data_sock.connect((config['data_host'], config['twitter_data_port']))
        self.twitter_data_sock = twitter_data_sock

        featured_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        featured_data_sock.connect((config['data_host'], config['featured_data_port']))
        self.featured_data_sock = featured_data_sock

        analytics_data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        analytics_data_sock.connect((config['data_host'], config['analytics_data_port']))
        self.analytics_data_sock = analytics_data_sock

    def init_threads(self):
        recv_twitch_thread = threading.Thread(target = self.recv_twitch_data).start()
        recv_twitter_thread = threading.Thread(target = self.recv_twitter_data).start()
        recv_featured_thread = threading.Thread(target = self.recv_featured_data).start()
        recv_analytics_thread = threading.Thread(target = self.recv_analytics_data).start()

    #cpanel response
    def handle_cpanel(self, src, args):
        request = {}
        request[src] = {}

        if 'add' in args:
            request[src]['add'] = [self.pattern.sub('',x).lower() for x in args['add'][0].split(',')]

        if 'delete' in args:
            request[src]['delete'] = [self.pattern.sub('',x).lower() for x in args['delete'][0].split(',')]

        if 'target_add' in args:
            request[src]['target_add'] = [self.pattern.sub('',x).lower() for x in args['target_add'][0].split(',')]

        if 'action' in args:
            for action in args['action'][0].split(','):
                if action == 'show':
                    pass
                elif action == 'refresh':
                    request[src]['refresh'] = True
                elif action == 'reset':
                    request[src]['reset'] = True
                else:
                    pass

        pp('handling cpanel request...')
        pp(request)
        self.request_sock.send(json.dumps(request))

        output = []
        if src == 'twitch':
            output = self.twitch_streams.keys()
        elif src == 'twitter':
            output = self.twitter_streams.keys()

        return json.dumps(output)

    def request_stream(self, stream, src):
        request = {}
        request[src] = {'add':[stream]}
        pp('Requesting stream on ' + src + ': '+stream)

        self.request_sock.send(json.dumps(request))

    def get_top_twitter_streams(self, args):
        config = self.config
        trend_dicts = []
        image_output = 'https://media.giphy.com/media/Nwz6NZkToYC4M/giphy.gif'

        for stream_id in self.twitter_streams:
            trend_dicts.append(self.twitter_streams.get(stream_id,{}).get('trending',{}))

        trending_output = {}
        [trending_output.update(d) for d in trend_dicts]

        if ('filter' in args) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in trending_output:
                    if keyword.lower() in msg.lower():
                        del trending_output[msg]

        return json.dumps({'default_image':image_output, 'trending': trending_output})

    def get_agg_content(self, args):
        config = self.config
        content_dicts = []

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                if stream_id not in self.twitter_streams:
                    self.twitter_streams[stream_id] = {'default_image':"https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif", 'content': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.target_twitter_streams)): {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}}
                    self.request_stream(stream_id,'twitter')

                content = self.twitter_streams.get(stream_id,{}).get('content',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.target_twitter_streams)): {"mp4_url": "", "score": 0.0001, "last_mtch_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}})
                content_dicts.append({msg_k: {'score':msg_v['score'], 'last_mtch_time': msg_v['last_mtch_time'].isoformat(), 'media_url':msg_v['media_url'], 'mp4_url':msg_v['mp4_url'], 'id':msg_v['id']} for msg_k, msg_v in content.items()})
                 
        content_output = {}
        [content_output.update(d) for d in content_dicts]

        if ('filter' in args) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in content_output:
                    if keyword.lower() in msg.lower():
                        del content_output[msg]

        return json.dumps({'content': content_output})

    def get_agg_analytics(self, args):
        config = self.config
        clusters_dicts = []

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                clusters = self.analytics.get(stream_id,{}).get('clusters',{})
                clusters_dicts.append(clusters)

        clusters_output = {}
        [clusters_output.update(d) for d in clusters_dicts]

        if ('keyword' in args) and (len(args['keyword'][0])>0):
            final_output = {}
            keywords = [self.pattern.sub('',x).lower() for x in args['keyword'][0].split(',')]
            for cluster_key in clusters_output:
                if set(clusters_output[cluster_key]['subjects']).isdisjoint(keywords):
                    pass
                else:
                    final_output[cluster_key] = clusters_output[cluster_key]
        else:
            final_output = clusters_output


        return json.dumps({'clusters': final_output})

    def get_agg_streams(self, args):
        config = self.config
        trend_dicts = []
        trend_images = []

        #WORKAROUND FOR TOP
        if ('twitter' in args) and (len(args['twitter'][0])>0) and ('top' in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]):
            return self.get_top_twitter_streams(args)

        if ('twitch' in args) and (len(args['twitch'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitch'][0].split(',')]:
                if stream_id not in self.twitch_streams:
                    self.twitch_streams[stream_id] = {'default_image':'', 'trending': {"This stream has no messages. If this message does not dissapear, please make sure "+stream_id+" is streaming": {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": ""}}}
                    self.request_stream(stream_id,'twitch')

                trend_dicts.append(self.twitch_streams.get(stream_id,{}).get('trending',{"This stream has no messages. If this message does not dissapear, please make sure "+stream_id+" is streaming": {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": ""}}))
                trend_images.append(self.twitch_streams.get(stream_id,{}).get('default_image',''))

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                if stream_id not in self.twitter_streams:
                    self.twitter_streams[stream_id] = {'default_image':"https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif", 'trending': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.target_twitter_streams)): {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}}
                    self.request_stream(stream_id,'twitter')

                trend_dicts.append(self.twitter_streams.get(stream_id,{}).get('trending',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.target_twitter_streams)): {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}))
                trend_images.append(self.twitter_streams.get(stream_id,{}).get('default_image',''))

        trending_output = {}
        [trending_output.update(d) for d in trend_dicts]

        if ('filter' in args) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in trending_output:
                    if keyword.lower() in msg.lower():
                        del trending_output[msg]

        if len(trend_images)>0:
            image_output = max(trend_images,key=len)
        else:
            image_output = '' 
        return json.dumps({'default_image':image_output, 'trending': trending_output})

    def get_featured(self, src, args):
        output = []

        if src == 'twitch':
            output = self.twitch_featured
        elif src == 'twitter':
            output = self.twitter_featured

        if ('limit' in args) and (len(args['limit'][0])>0):
            limit = int(args['limit'][0])
            output = output[0:limit]

        return json.dumps(output)

    def recv_helper(self, bytes, src):
        sock = None
        if src == 'twitch':
            sock = self.twitch_data_sock
        elif src == 'twitter':
            sock = self.twitter_data_sock
        elif src == 'featured':
            sock = self.featured_data_sock
        elif src == 'analytics':
            sock = self.analytics_data_sock

        data = ''
        while len(data) < bytes:
            packet = sock.recv(bytes - len(data))
            if not packet:
                return None
            data += packet
        return data

    def recv_featured_data(self):
        config = self.config
        self.recv_featured = True

        while self.recv_featured:
            raw_len = self.recv_helper(4, 'featured')
            msg_len = struct.unpack('>I', raw_len)[0]
            # Read the message data
            inc_pickle_data = self.recv_helper(msg_len, 'featured')

            pickle_data = pickle.loads(inc_pickle_data)
            self.twitch_featured = pickle_data['twitch_featured']
            self.twitter_featured = pickle_data['twitter_featured']
            self.target_twitter_streams = pickle_data['target_twitter_streams']

    def recv_analytics_data(self):
        config = self.config
        self.recv_analytics = True

        while self.recv_analytics:
            raw_len = self.recv_helper(4, 'analytics')
            msg_len = struct.unpack('>I', raw_len)[0]
            # Read the message data
            inc_pickle_data = self.recv_helper(msg_len, 'analytics')

            pickle_data = pickle.loads(inc_pickle_data)
            self.analytics = pickle_data['analytics']

    def recv_twitch_data(self):
        config = self.config
        self.recv_twitch = True

        while self.recv_twitch:
            raw_len = self.recv_helper(4, 'twitch')
            msg_len = struct.unpack('>I', raw_len)[0]
            # Read the message data
            inc_pickle_data = self.recv_helper(msg_len, 'twitch')

            pickle_data = pickle.loads(inc_pickle_data)
            self.twitch_streams = pickle_data['twitch_streams']

    def recv_twitter_data(self):
        config = self.config
        self.recv_twitter = True

        while self.recv_twitter:

            raw_len = self.recv_helper(4, 'twitter')
            msg_len = struct.unpack('>I', raw_len)[0]
            # Read the message data
            inc_pickle_data = self.recv_helper(msg_len, 'twitter')

            pickle_data = pickle.loads(inc_pickle_data)
            self.twitter_streams = pickle_data['twitter_streams']

    def run(self):
        pp('Initializing Web Server...')
        resource = WebServer()
        resource.stream_client = self

        factory = Site(resource)

        reactor.listenTCP(self.config['port'], factory)

        pp('Starting Web Server...')
        reactor.run()

if __name__ == '__main__':
    client = StreamClient(http_config)
