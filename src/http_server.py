# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import socket
import threading
import json
import time
import re
import pickle
import datetime
import zmq

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
        elif path[0:9] == '/subjects':
            return self.stream_client.get_agg_subjects(args)
        elif path[0:10] == '/sentiment':
            return self.stream_client.get_agg_sentiment(args)
        elif path[0:8] == '/cpanel/':
            if path[8:14] == 'twitch':
                return self.stream_client.handle_cpanel('twitch',args)
            elif path[8:15] == 'twitter':
                return self.stream_client.handle_cpanel('twitter',args)
            elif path[8:14] == 'reddit':
                return self.stream_client.handle_cpanel('reddit',args)
            else:
                return json.dumps('Invalid path! Valid paths: /cpanel/twitch and /cpanel/twitter')
        elif path[0:10] == '/featured/':
            if path[10:16] == 'twitch':
                return self.stream_client.get_featured('twitch', args)
            elif path[10:17] == 'twitter':
                return self.stream_client.get_featured('twitter', args)
            elif path[10:16] == 'reddit':
                return self.stream_client.get_featured('reddit', args)
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
        self.reddit_streams = {}

        self.twitch_featured = []
        self.twitter_featured = []
        self.reddit_featured = []

        self.twitter_analytics = {}
        self.twitch_analytics = {}
        self.reddit_analytics = {}

        self.twitch_hash = None
        self.twitter_hash = None
        self.reddit_hash = None

        #CJK regex
        self.pattern = re.compile('[^\w\s\'\"!.,$&?:;_-]+')

        self.init_threads()
        self.run()

    def init_sockets(self):
        context = zmq.Context()
        self.server_socket = context.socket(zmq.PUSH)
        self.server_socket.connect('tcp://'+self.config['zmq_server_host']+':'+str(self.config['zmq_server_port']))

        self.http_socket = context.socket(zmq.PULL)
        self.http_socket.bind('tcp://'+self.config['zmq_http_host']+':'+str(self.config['zmq_http_port']))

    def init_threads(self):
        threading.Thread(target = self.process_data).start()
        #threading.Thread(target = self.twitch_monitor).start()
        threading.Thread(target = self.twitter_monitor).start()
        threading.Thread(target = self.reddit_monitor).start()

    def process_data(self):
        for raw_data in iter(self.http_socket.recv, 'STOP'):
            
            try:
                data = pickle.loads(raw_data)
            except Exception, e:
                pp(e)
                data = {'type': 'invalid'}

            if data['type'] == 'stream':
                self.process_stream(data)
            elif data['type'] == 'clusters':
                self.process_clusters(data)
            elif data['type'] == 'featured':
                self.process_featured(data)

    def process_stream(self, data):
        if data['src'] == 'twitch':
            self.twitch_streams[data['stream']] = data['data']
        elif data['src'] == 'twitter':
            self.twitter_streams[data['stream']] = data['data']
        elif data['src'] == 'reddit':
            self.reddit_streams[data['stream']] = data['data']

    def process_clusters(self, data):
        if data['src'] == 'twitch':
            self.twitch_analytics[data['stream']] = data['data']
        elif data['src'] == 'twitter':
            self.twitter_analytics[data['stream']] = data['data']
        elif data['src'] == 'reddit':
            self.reddit_analytics[data['stream']] = data['data']

    def process_featured(self, data):
        if data['src'] == 'twitch':
            self.twitch_featured = data['data']
        elif data['src'] == 'twitter':
            self.twitter_featured = self.featured_helper(data['data'], data['src'])
        elif data['src'] == 'reddit':
            self.reddit_featured = self.featured_helper(data['data'], data['src'])

    def featured_helper(self, featured, src):
        if src == 'twitter':
            for feat in featured:
                if len(feat['image']) == 0:
                    feat['image'] = self.twitter_streams[feat['stream'][0]]['default_image']

        elif src == 'twitter':
            for feat in featured:
                if len(feat['image']) == 0:
                    feat['image'] = self.reddit_streams[feat['stream'][0]]['default_image']

        return featured

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

        self.server_socket.send(pickle.dumps(request))

        output = []
        if src == 'twitch':
            output = self.twitch_streams.keys()
        elif src == 'twitter':
            output = self.twitter_streams.keys()
        elif src == 'reddit':
            output = self.reddit_streams.keys()

        return json.dumps(output)

    def request_stream(self, stream, src):
        request = {}
        request[src] = {'add':[stream]}
        pp('Requesting stream on ' + src + ': '+stream)
        self.server_socket.send(pickle.dumps(request))

    def get_agg_content(self, args):
        content_dicts = []
        horizon = 7200
        timestamp = datetime.datetime.now()

        if ('horizon' in args) and (len(args['horizon'][0])>0):
            horizon = int(args['horizon'][0])

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                if stream_id not in self.twitter_streams:
                    self.twitter_streams[stream_id] = {'content': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.twitter_streams)): {"mp4_url": "", "score": 0.0001, "last_mtch_time": timestamp, "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}}
                    self.request_stream(stream_id,'twitter')

                try:
                    content = self.twitter_streams.get(stream_id,{}).get('content',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.twitter_streams)): {"mp4_url": "", "score": 0.0001, "last_mtch_time": timestamp, "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}})
                    content_dicts.append({msg_k: {'score':msg_v['score'], 'last_mtch_time': msg_v['last_mtch_time'].isoformat(), 'media_url':msg_v['media_url'], 'mp4_url':msg_v['mp4_url'], 'id':msg_v['id']} for msg_k, msg_v in content.items() if (timestamp - msg_v['last_mtch_time']).total_seconds() <= horizon})
                except Exception, e:
                    pp(e)

        if ('reddit' in args) and (len(args['reddit'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['reddit'][0].split(',')]:
                if stream_id not in self.reddit_streams:
                    self.reddit_streams[stream_id] = {'content': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.reddit_streams)): {"mp4_url": "", "score": 0.0001, "last_mtch_time": timestamp, "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}}
                    self.request_stream(stream_id,'reddit')

                try:
                    content = self.reddit_streams.get(stream_id,{}).get('content',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.reddit_streams)): {"mp4_url": "", "score": 0.0001, "last_mtch_time": timestamp, "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}})
                    content_dicts.append({msg_k: {'score':msg_v['score'], 'last_mtch_time': msg_v['last_mtch_time'].isoformat(), 'media_url':msg_v['media_url'], 'mp4_url':msg_v['mp4_url'], 'id':msg_v['id']} for msg_k, msg_v in content.items() if (timestamp - msg_v['last_mtch_time']).total_seconds() <= horizon})
                except Exception, e:
                    pp(e)

        content_output = {}
        [content_output.update(d) for d in content_dicts]

        if ('filter' in args) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in content_output.keys():
                    if keyword.lower() in msg.lower():
                        del content_output[msg]

        if ('limit' in args) and (len(args['limit'][0])>0):
            limit = int(args['limit'][0])
            msgkeys = sorted(content_output, key = lambda x:content_output[x]['score'], reverse=True)
            msgkeys = msgkeys[0:limit]
            for msg in content_output.keys():
                if msg not in msgkeys:
                    del content_output[msg]

        return json.dumps({'content': content_output})

    def get_agg_subjects(self, args):
        subjects_dicts = []

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                clusters = self.twitter_analytics.get(stream_id,{}).get('clusters',{})
                subjects_dicts.append({msg_k: {'avgscore':msg_v['avgscore'], 'subjects': msg_v['subjects']} for msg_k, msg_v in clusters.items()})

        if ('twitch' in args) and (len(args['twitch'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitch'][0].split(',')]:
                clusters = self.twitch_analytics.get(stream_id,{}).get('clusters',{})
                subjects_dicts.append({msg_k: {'avgscore':msg_v['avgscore'], 'subjects': msg_v['subjects']} for msg_k, msg_v in clusters.items()})

        if ('reddit' in args) and (len(args['reddit'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['reddit'][0].split(',')]:
                clusters = self.reddit_analytics.get(stream_id,{}).get('clusters',{})
                subjects_dicts.append({msg_k: {'avgscore':msg_v['avgscore'], 'subjects': msg_v['subjects']} for msg_k, msg_v in clusters.items()})

        subjects_output = {}
        [subjects_output.update(d) for d in subjects_dicts]

        if ('keyword' in args) and (len(args['keyword'][0])>0):
            final_output = {}
            keywords = [self.pattern.sub('',x).lower() for x in args['keyword'][0].split(',')]
            for cluster_key in subjects_output:
                if not set(subjects_output[cluster_key]['subjects']).isdisjoint(keywords):
                    final_output[cluster_key] = subjects_output[cluster_key]
        else:
            final_output = subjects_output

        return json.dumps({'clusters': final_output})

    def get_agg_sentiment(self, args):
        sentiment_dicts = []

        if ('subjects' in args) and (len(args['subjects'][0])>0):
            subjects = [self.pattern.sub('',x).lower() for x in args['subjects'][0].split(',')]

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                clusters = self.twitter_analytics.get(stream_id,{}).get('clusters',{})
                sentiment_dicts.append({msg_k: {'subjects': msg_v['subjects'], 'sentiment': msg_v['adjs']} for msg_k, msg_v in clusters.items() if not set(msg_v['subjects']).isdisjoint(subjects)})

        if ('twitch' in args) and (len(args['twitch'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitch'][0].split(',')]:
                clusters = self.twitch_analytics.get(stream_id,{}).get('clusters',{})
                sentiment_dicts.append({msg_k: {'subjects': msg_v['subjects'], 'sentiment': msg_v['adjs']} for msg_k, msg_v in clusters.items() if not set(msg_v['subjects']).isdisjoint(subjects)})

        if ('reddit' in args) and (len(args['reddit'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['reddit'][0].split(',')]:
                clusters = self.reddit_analytics.get(stream_id,{}).get('clusters',{})
                sentiment_dicts.append({msg_k: {'subjects': msg_v['subjects'], 'sentiment': msg_v['adjs']} for msg_k, msg_v in clusters.items() if not set(msg_v['subjects']).isdisjoint(subjects)})

        sentiment_output = {}
        [sentiment_output.update(d) for d in sentiment_dicts]

        return json.dumps({'sentiment': sentiment_output})

    def get_agg_streams(self, args):
        trend_dicts = []

        if ('twitch' in args) and (len(args['twitch'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitch'][0].split(',')]:
                if stream_id not in self.twitch_streams:
                    self.twitch_streams[stream_id] = {'trending': {"This stream has no messages. If this message does not dissapear, please make sure "+stream_id+" is streaming": {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": ""}}}
                    self.request_stream(stream_id,'twitch')

                trend_dicts.append(self.twitch_streams.get(stream_id,{}).get('trending',{"This stream has no messages. If this message does not dissapear, please make sure "+stream_id+" is streaming": {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": ""}}))

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                if stream_id not in self.twitter_streams:
                    self.twitter_streams[stream_id] = {'trending': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.twitter_streams)): {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}}
                    self.request_stream(stream_id,'twitter')

                trend_dicts.append(self.twitter_streams.get(stream_id,{}).get('trending',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.twitter_streams)): {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}))

        if ('reddit' in args) and (len(args['reddit'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['reddit'][0].split(',')]:
                if stream_id not in self.reddit_streams:
                    self.reddit_streams[stream_id] = {'trending': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.reddit_streams)): {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}}
                    self.request_stream(stream_id,'reddit')

                trend_dicts.append(self.reddit_streams.get(stream_id,{}).get('trending',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.reddit_streams)): {"mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}))

        trending_output = {}
        [trending_output.update(d) for d in trend_dicts]

        if ('filter' in args) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in trending_output.keys():
                    if keyword.lower() in msg.lower():
                        del trending_output[msg]

        return json.dumps({'trending': trending_output})

    def get_featured(self, src, args):
        output = []

        if src == 'twitch':
            output = self.twitch_featured
        elif src == 'twitter':
            output = self.twitter_featured
        elif src == 'reddit':
            output = self.reddit_featured

        if ('limit' in args) and (len(args['limit'][0])>0):
            limit = int(args['limit'][0])
            output = output[0:limit]

        return json.dumps(output)

    def run(self):
        pp('Initializing Web Server...')
        resource = WebServer()
        resource.stream_client = self

        factory = Site(resource)

        reactor.listenTCP(self.config['port'], factory)

        pp('Starting Web Server...')
        reactor.run()

    def twitch_monitor(self):
        self.twitch_monitor_loop = True
        while self.twitch_monitor_loop:
            curr_dict = {}

            for stream in self.twitch_streams.values():
                try:
                    curr_dict.update(stream['trending'])
                except Exception, e:
                    pp(e)

            curr_hash = hash(frozenset(curr_dict))
            if curr_hash == self.twitch_hash:
                pp('Twitch Monitor triggered - refreshing!')
                request = {'twitch':{'refresh':True}}
                self.server_socket.send(pickle.dumps(request))
            else:
                self.twitch_hash = curr_hash

            time.sleep(self.config['twitch_monitor_timeout'])

    def twitter_monitor(self):
        self.twitter_monitor_loop = True
        while self.twitter_monitor_loop:
            curr_dict = {}

            for stream in self.twitter_streams.values():
                try:
                    curr_dict.update(stream['trending'])
                except Exception, e:
                    pp(e)

            curr_hash = hash(frozenset(curr_dict))
            if curr_hash == self.twitter_hash:
                pp('Twitter Monitor triggered - refreshing!')
                request = {'twitter':{'refresh':True}}
                self.server_socket.send(pickle.dumps(request))
            else:
                self.twitter_hash = curr_hash

            time.sleep(self.config['twitter_monitor_timeout'])

    def reddit_monitor(self):
        self.reddit_monitor_loop = True
        while self.reddit_monitor_loop:
            curr_dict = {}

            for stream in self.reddit_streams.values():
                try:
                    curr_dict.update(stream['trending'])
                except Exception, e:
                    pp(e)

            curr_hash = hash(frozenset(curr_dict))
            if curr_hash == self.reddit_hash:
                pp('Reddit Monitor triggered - refreshing!')
                request = {'reddit':{'refresh':True}}
                self.server_socket.send(pickle.dumps(request))
            else:
                self.reddit_hash = curr_hash

            time.sleep(self.config['reddit_monitor_timeout'])

if __name__ == '__main__':
    client = StreamClient(http_config)
