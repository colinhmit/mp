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
    http_server = None
    
    #server protocol
    def render_GET(self, request):
        request.setHeader("content-type", "application/json")
        output = self.handle_GET(request.path, request.args)
        return output

    #get control
    def handle_GET(self, path, args):
        if path[0:7] == '/stream':
            return self.http_server.get_agg_streams(args)
        elif path[0:8] == '/content':
            return self.http_server.get_agg_content(args)
        elif path[0:9] == '/subjects':
            return self.http_server.get_agg_subjects(args)
        elif path[0:10] == '/sentiment':
            return self.http_server.get_agg_sentiment(args)
        elif path[0:8] == '/cpanel/':
            if path[8:14] == 'native':
                return self.http_server.handle_cpanel('native',args)
            elif path[8:14] == 'twitch':
                return self.http_server.handle_cpanel('twitch',args)
            elif path[8:15] == 'twitter':
                return self.http_server.handle_cpanel('twitter',args)
            elif path[8:14] == 'reddit':
                return self.http_server.handle_cpanel('reddit',args)
            else:
                return json.dumps('Invalid path! Valid paths: /cpanel/twitch and /cpanel/twitter')
        elif path[0:10] == '/featured/':
            if path[10:16] == 'native':
                return self.http_server.get_featured('native', args)
            elif path[10:16] == 'twitch':
                return self.http_server.get_featured('twitch', args)
            elif path[10:17] == 'twitter':
                return self.http_server.get_featured('twitter', args)
            elif path[10:16] == 'reddit':
                return self.http_server.get_featured('reddit', args)
            else:
                return json.dumps('Invalid path! Valid paths: /featured/twitch and /featured/twitter')
        else:
            return json.dumps('Invalid path! Valid paths: /stream and /cpanel/.../')

class HTTPServer():
    def __init__(self, config):
        pp('Initializing HTTPServer...')
        self.config = config
        self.init_sockets()

        self.native_streams = {}
        self.twitch_streams = {}
        self.twitter_streams = {}
        self.reddit_streams = {}

        self.native_featured = []
        self.twitch_featured = []
        self.twitter_featured = []
        self.reddit_featured = []

        self.native_analytics = {}
        self.twitter_analytics = {}
        self.twitch_analytics = {}
        self.reddit_analytics = {}

        self.ads = {}

        self.enrich_map = {}

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

        self.http_data_socket = context.socket(zmq.PULL)
        self.http_data_socket.bind('tcp://'+self.config['zmq_http_data_host']+':'+str(self.config['zmq_http_data_port']))

    def init_threads(self):
        threading.Thread(target = self.process_data).start()
        threading.Thread(target = self.process_analytics).start()
        #threading.Thread(target = self.twitch_monitor).start()
        #threading.Thread(target = self.twitter_monitor).start()
        #threading.Thread(target = self.reddit_monitor).start()

    def process_data(self):
        for raw_data in iter(self.http_socket.recv, 'STOP'):
            try:
                data = pickle.loads(raw_data)
            except Exception, e:
                pp(e)
                data = {'type': 'invalid'}

            if data['type'] == 'stream':
                self.process_stream(data)
            elif data['type'] == 'featured':
                self.process_featured(data)
            elif data['type'] == 'ad':
                self.process_ad(data)
            elif data['type'] == 'delete':
                self.process_delete(data)

    def process_analytics(self):
        for raw_data in iter(self.http_data_socket.recv, 'STOP'):
            try:
                data = pickle.loads(raw_data)
            except Exception, e:
                pp(e)
                data = {'type': 'invalid'}

            if data['type'] == 'clusters':
                self.process_clusters(data)

    def process_stream(self, data):
        if data['src'] == 'native':
            self.native_streams[data['stream']] = data['data']
        elif data['src'] == 'twitch':
            self.twitch_streams[data['stream']] = data['data']
        elif data['src'] == 'twitter':
            self.twitter_streams[data['stream']] = data['data']
        elif data['src'] == 'reddit':
            self.reddit_streams[data['stream']] = data['data']

        for enrich_msg in data['enrichdecay']:
            self.enrichdecay_helper(enrich_msg)

    def enrichdecay_helper(self, msg):
        try:
            if msg in self.enrich_map.keys():
                del self.enrich_map[msg]
        except Exception, e:
            pp(e)
        
    def process_delete(self, data):
        try:
            if data['src'] == 'native':
                for stream in data['data']:
                    if stream in self.native_streams:
                        del self.native_streams[stream]
            elif data['src'] == 'twitch':
                for stream in data['data']:
                    if stream in self.twitch_streams:
                        del self.twitch_streams[stream]
            elif data['src'] == 'twitter':
                for stream in data['data']:
                    if stream in self.twitter_streams:
                        del self.twitter_streams[stream]
            elif data['src'] == 'reddit':
                for stream in data['data']:
                    if stream in self.reddit_streams:
                        del self.reddit_streams[stream]
        except Exception, e:
            raise e
        
    def process_clusters(self, data):
        if data['src'] == 'native':
            self.native_analytics[data['stream']] = data['data']
        elif data['src'] == 'twitch':
            self.twitch_analytics[data['stream']] = data['data']
        elif data['src'] == 'twitter':
            self.twitter_analytics[data['stream']] = data['data']
        elif data['src'] == 'reddit':
            self.reddit_analytics[data['stream']] = data['data']

    def process_featured(self, data):
        if data['src'] == 'native':
            self.native_featured = data['data']
        elif data['src'] == 'twitch':
            self.twitch_featured = data['data']
        elif data['src'] == 'twitter':
            self.twitter_featured = self.featured_helper(data['data'], data['src'])
        elif data['src'] == 'reddit':
            self.reddit_featured = self.featured_helper(data['data'], data['src'])

    def process_ad(self, data):
        self.ads = data['data']
        
    def featured_helper(self, featured, src):
        if src == 'twitter':
            for feat in featured:
                if len(feat['image']) == 0:
                    feat['image'] = self.twitter_streams.get(feat['stream'][0],{}).get('default_image',"")

        elif src == 'twitter':
            for feat in featured:
                if len(feat['image']) == 0:
                    feat['image'] = self.reddit_streams.get(feat['stream'][0],{}).get('default_image',"")

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
        if src == 'native':
            output = self.native_streams.keys()
        elif src == 'twitch':
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

    # Aggregation functions
    def get_agg_streams(self, args):
        enrich_dict = {}
        if ('e_native' in args) and (len(args['e_native'][0])>0):
            enrich_dict['native'] = []
            for stream_id in [self.pattern.sub('',x).lower() for x in args['e_native'][0].split(',')]:
                enrich_dict['native'].append(stream_id)
        if ('e_twitch' in args) and (len(args['e_twitch'][0])>0):
            enrich_dict['twitch'] = []
            for stream_id in [self.pattern.sub('',x).lower() for x in args['e_twitch'][0].split(',')]:
                enrich_dict['twitch'].append(stream_id)
        if ('e_twitter' in args) and (len(args['e_twitter'][0])>0):
            enrich_dict['twitter'] = []
            for stream_id in [self.pattern.sub('',x).lower() for x in args['e_twitter'][0].split(',')]:
                enrich_dict['twitter'].append(stream_id)
        if ('e_reddit' in args) and (len(args['e_reddit'][0])>0):
            enrich_dict['reddit'] = []
            for stream_id in [self.pattern.sub('',x).lower() for x in args['e_reddit'][0].split(',')]:
                enrich_dict['reddit'].append(stream_id)
        if ('ad' in args) and (len(args['ad'][0])>0):
            enrich_dict['ad'] = []
            for ad_id in [self.pattern.sub('',x).lower() for x in args['ad'][0].split(',')]:
                enrich_dict['ad'].append(ad_id)
        hash_enrich_dict = hash(frozenset(enrich_dict))

        trend_dicts = []
        enrich_items = []
        if ('native' in args) and (len(args['native'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['native'][0].split(',')]:
                if stream_id not in self.native_streams:
                    self.native_streams[stream_id] = {'trending': {"This stream has no messages yet!": {"src": "native", "mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": ""}}}
                    self.request_stream(stream_id,'native')

                trend_dicts.append(self.native_streams.get(stream_id,{}).get('trending',{"This stream has no messages yet!": {"src": "native", "mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": ""}}))
                enrich_items += self.native_streams.get(stream_id,{}).get('enrich',[])

        if ('twitch' in args) and (len(args['twitch'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitch'][0].split(',')]:
                if stream_id not in self.twitch_streams:
                    self.twitch_streams[stream_id] = {'trending': {"This stream has no messages. If this message does not dissapear, please make sure "+stream_id+" is streaming": {"src": "twitch", "mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": ""}}}
                    self.request_stream(stream_id,'twitch')

                trend_dicts.append(self.twitch_streams.get(stream_id,{}).get('trending',{"This stream has no messages. If this message does not dissapear, please make sure "+stream_id+" is streaming": {"src": "twitch", "mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": ""}}))
                enrich_items += self.twitch_streams.get(stream_id,{}).get('enrich',[])

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                if stream_id not in self.twitter_streams:
                    self.twitter_streams[stream_id] = {'trending': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.twitter_streams.keys())): {"src": "twitter", "mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}}
                    self.request_stream(stream_id,'twitter')

                trend_dicts.append(self.twitter_streams.get(stream_id,{}).get('trending',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.twitter_streams.keys())): {"src": "twitter", "mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}))
                enrich_items += self.twitter_streams.get(stream_id,{}).get('enrich',[])

        if ('reddit' in args) and (len(args['reddit'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['reddit'][0].split(',')]:
                if stream_id not in self.reddit_streams:
                    self.reddit_streams[stream_id] = {'trending': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.reddit_streams.keys())): {"src": "reddit", "mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}}
                    self.request_stream(stream_id,'reddit')

                trend_dicts.append(self.reddit_streams.get(stream_id,{}).get('trending',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.reddit_streams.keys())): {"src": "reddit", "mp4_url": "", "score": 0.0001, "first_rcv_time": "2001-01-01T00:00:00.000000", "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif"}}))
                enrich_items += self.reddit_streams.get(stream_id,{}).get('enrich',[])

        trending_output = {}
        [trending_output.update(d) for d in trend_dicts]

        if len(enrich_dict) > 0:
            tot_score = 0
            for msg in trending_output.keys():
                tot_score += trending_output[msg]['score']

            num_enrich = len(enrich_dict)
            enrich_score = max(tot_score/(self.config['ad_slice']-num_enrich),1)

            i = 0
            for enrich_item in enrich_items:
                cache_enrich = self.enrich_map.get(enrich_item['id'],{}).get(hash_enrich_dict,None)
                if cache_enrich is not None:
                    trending_output[cache_enrich[0]+i*" "] = cache_enrich[1]
                else:
                    if enrich_item['id'] in self.enrich_map:
                        enrich = self.get_enrich(enrich_dict, enrich_score, enrich_item['time'])
                        self.enrich_map[enrich_item['id']][hash_enrich_dict] = enrich
                        trending_output[enrich[0]+i*" "] = enrich[1]
                    else:
                        self.enrich_map[enrich_item['id']] = {}
                        enrich = self.get_enrich(enrich_dict, enrich_score, enrich_item['time'])
                        self.enrich_map[enrich_item['id']][hash_enrich_dict] = enrich
                        trending_output[enrich[0]+i*" "] = enrich[1]
                i+=1

        if ('filter' in args) and (len(args['filter'][0])>0):
            for keyword in args['filter'][0].split(','):
                for msg in trending_output.keys():
                    if keyword.lower() in msg.lower():
                        del trending_output[msg]

        return json.dumps({'trending': trending_output})

    def get_agg_content(self, args):
        content_dicts = []
        horizon = 7200
        timestamp = datetime.datetime.now()

        if ('horizon' in args) and (len(args['horizon'][0])>0):
            horizon = int(args['horizon'][0])

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                if stream_id not in self.twitter_streams:
                    self.twitter_streams[stream_id] = {'content': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.twitter_streams.keys())): {"mp4_url": "", "score": 0.0001, "last_mtch_time": timestamp, "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif", "id":"123"}}}
                    self.request_stream(stream_id,'twitter')

                try:
                    content = self.twitter_streams.get(stream_id,{}).get('content',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.twitter_streams.keys())): {"mp4_url": "", "score": 0.0001, "last_mtch_time": timestamp, "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif", "id":"123"}})
                    content_dicts.append({msg_k: {'score':msg_v['score'], 'last_mtch_time': msg_v['last_mtch_time'].isoformat(), 'media_url':msg_v['media_url'], 'mp4_url':msg_v['mp4_url'], 'id':msg_v['id']} for msg_k, msg_v in content.items() if (timestamp - msg_v['last_mtch_time']).total_seconds() <= horizon})
                except Exception, e:
                    pp(e)

        if ('reddit' in args) and (len(args['reddit'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['reddit'][0].split(',')]:
                if stream_id not in self.reddit_streams:
                    self.reddit_streams[stream_id] = {'content': {("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.reddit_streams.keys())): {"mp4_url": "", "score": 0.0001, "last_mtch_time": timestamp, "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif", "id":"123"}}}
                    self.request_stream(stream_id,'reddit')

                try:
                    content = self.reddit_streams.get(stream_id,{}).get('content',{("This stream is not currently available. If this message does not dissapear, please try one of the following streams: " + str(self.reddit_streams.keys())): {"mp4_url": "", "score": 0.0001, "last_mtch_time": timestamp, "media_url": "https://media.giphy.com/media/a9xhxAxaqOfQs/giphy.gif", "id":"123"}})
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

    def get_enrich(self, enrich_dict, enrich_score, enrich_time):
        enrich_output = {}
        if ('ad' in enrich_dict):
            for ad_id in enrich_dict['ad']:
                enrich = self.ads.get(ad_id,{})
                if len(enrich) > 0:
                    max_key = max(enrich, key=lambda x: enrich[x]['score'])
                    enrich_output[max_key] = enrich[max_key]

        if ('native' in enrich_dict):
            for stream_id in enrich_dict['native']:
                enrich = self.native_streams.get(stream_id,{}).get('trending',{})
                if len(enrich) > 0:
                    max_key = max(enrich, key=lambda x: enrich[x]['score'])
                    enrich_output[max_key] = enrich[max_key]

        if ('twitch' in enrich_dict):
            for stream_id in enrich_dict['twitch']:
                enrich = self.twitch_streams.get(stream_id,{}).get('trending',{})
                if len(enrich) > 0:
                    max_key = max(enrich, key=lambda x: enrich[x]['score'])
                    enrich_output[max_key] = enrich[max_key]

        if ('twitter' in enrich_dict):
            for stream_id in enrich_dict['twitter']:
                enrich = self.twitter_streams.get(stream_id,{}).get('trending',{})
                if len(enrich) > 0:
                    max_key = max(enrich, key=lambda x: enrich[x]['score'])
                    enrich_output[max_key] = enrich[max_key]

        if ('reddit' in enrich_dict):
            for stream_id in enrich_dict['reddit']:
                enrich = self.reddit_streams.get(stream_id,{}).get('trending',{})
                if len(enrich) > 0:
                    max_key = max(enrich, key=lambda x: enrich[x]['score'])
                    enrich_output[max_key] = enrich[max_key]

        max_key = max(enrich_output, key=lambda x: enrich_output[x]['score'])
        enrich_output[max_key]['first_rcv_time'] = enrich_time.isoformat()
        enrich_output[max_key]['score'] = enrich_score
        return (max_key, enrich_output[max_key])

    def get_agg_subjects(self, args):
        subjects_list = []

        if ('native' in args) and (len(args['native'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['native'][0].split(',')]:
                subjects = self.native_analytics.get(stream_id,{}).get('subjects',[])
                subjects_list.append(subjects)

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                subjects = self.twitter_analytics.get(stream_id,{}).get('subjects',[])
                subjects_list.append(subjects)

        if ('twitch' in args) and (len(args['twitch'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitch'][0].split(',')]:
                subjects = self.twitch_analytics.get(stream_id,{}).get('subjects',{})
                subjects_list.append(subjects)

        if ('reddit' in args) and (len(args['reddit'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['reddit'][0].split(',')]:
                subjects = self.reddit_analytics.get(stream_id,{}).get('subjects',{})
                subjects_list.append(subjects)

        return json.dumps({'subjects': subjects_list})

    def get_agg_sentiment(self, args):
        sentiment_dicts = []
        subjects = []

        if ('subjects' in args) and (len(args['subjects'][0])>0):
            subjects = [self.pattern.sub('',x).lower() for x in args['subjects'][0].split(',')]

        if ('native' in args) and (len(args['native'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['native'][0].split(',')]:
                sentiment = self.native_analytics.get(stream_id,{}).get('sentiment',{})
                sentiment_dicts.append(sentiment)

        if ('twitter' in args) and (len(args['twitter'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitter'][0].split(',')]:
                sentiment = self.twitter_analytics.get(stream_id,{}).get('sentiment',{})
                sentiment_dicts.append(sentiment)

        if ('twitch' in args) and (len(args['twitch'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['twitch'][0].split(',')]:
                sentiment = self.twitch_analytics.get(stream_id,{}).get('sentiment',{})
                sentiment_dicts.append(sentiment)

        if ('reddit' in args) and (len(args['reddit'][0])>0):
            for stream_id in [self.pattern.sub('',x).lower() for x in args['reddit'][0].split(',')]:
                sentiment = self.reddit_analytics.get(stream_id,{}).get('sentiment',{})
                sentiment_dicts.append(sentiment)

        sentiment_output = {}
        [sentiment_output.update(d) for d in sentiment_dicts]

        for subj in sentiment_output.keys():
            if not subj in subjects:
                del sentiment_output[subj]

        return json.dumps({'sentiment': sentiment_output})

    def get_featured(self, src, args):
        output = []

        if src == 'native':
            output = self.native_featured
        elif src == 'twitch':
            output = self.twitch_featured
        elif src == 'twitter':
            output = self.twitter_featured
        elif src == 'reddit':
            output = self.reddit_featured

        if ('limit' in args) and (len(args['limit'][0])>0):
            limit = int(args['limit'][0])
            output = output[0:limit]

        return json.dumps(output)

    # Monitors
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
                    pp('monitor broke')
                    pp(stream)
                    #pp(e)

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

    # Main Function
    def run(self):
        pp('Initializing Web Server...')
        resource = WebServer()
        resource.http_server = self

        factory = Site(resource)

        reactor.listenTCP(self.config['port'], factory)

        pp('Starting Web Server...')
        reactor.run()

if __name__ == '__main__':
    client = HTTPServer(http_config)
