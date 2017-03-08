# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
#Import the necessary methods from tweepy library
import re
import json
import multiprocessing
import datetime
import random
import zmq
import pickle
import gc

#import utils
from streams.utils.irc import irc
from streams.utils.twtr import twtr
from streams.utils.rddt import rddt
from streams.utils.nlp import nlpParser
from streams.utils.functions_general import *

class InputServer:
    def __init__(self, config, init_twitter_streams, init_reddit_streams):
        pp('Initializing Input Server...')
        self.config = config

        self.irc = irc(self.config['irc_config'])
        self.twtr = twtr(self.config['twtr_config'], init_twitter_streams)
        self.rddt = rddt(self.config['rddt_config'], init_reddit_streams)

        self.nlp_parser = nlpParser()

        for _ in xrange(self.config['num_dist_threads']):
            multiprocessing.Process(target=self.distribute).start()

        for _ in xrange(self.config['num_proc_threads']):
            multiprocessing.Process(target=self.process, args=(self.nlp_parser,)).start()
    
    
    def process(self, nlp):
        context = zmq.Context()
        recvr = context.socket(zmq.PULL)
        recvr.connect("tcp://127.0.0.1:"+str(self.config['zmq_irc_port']))
        recvr.connect("tcp://127.0.0.1:"+str(self.config['zmq_twtr_port']))
        recvr.connect("tcp://127.0.0.1:"+str(self.config['zmq_rddt_port']))

        sendr = context.socket(zmq.PUB)
        sendr.connect("tcp://127.0.0.1:"+str(self.config['zmq_pub_port']))

        svomap = {}
        svorefresh = random.randint(750, 1000)

        for data in iter(recvr.recv_string, 'STOP'):
            src, msg = self.parse_data(data)
            if len(msg) > 0:
                hashid = hash(msg['message'])

                if hashid in svomap:
                    svos, subjs = svomap[hashid]
                else:
                    clean_msg = re.sub(r"http\S+", "", msg['message'])
                    clean_msg = re.sub(r"[#@]", "", clean_msg)
                    clean_msg = re.sub(r"[^\w\s\'\"!.,&?:;_%-]+", "", clean_msg)
                    try:
                        svos, subjs = nlp.parse_text(clean_msg)
                    except Exception, e:
                        svos = []
                        subjs = []
                    svomap[hashid] = svos, subjs

                msg['svos'] = svos
                msg['subjs'] = subjs

                if len(svomap)>svorefresh:
                    svomap = {}
                    nlp.flush()
                    gc.collect()

                pickled_data = pickle.dumps(msg)
                sendr.send(src+pickled_data)
    
    def distribute(self):
        distributing = True

        while distributing:
            try:
                context = zmq.Context(1)
                frontend = context.socket(zmq.SUB)
                frontend.bind("tcp://*:"+str(self.config['zmq_pub_port']))
                frontend.setsockopt(zmq.SUBSCRIBE, "")

                backend = context.socket(zmq.PUB)
                backend.bind("tcp://*:"+str(self.config['zmq_sub_port']))
                zmq.device(zmq.FORWARDER, frontend, backend)
            except Exception, e:
                pp(e)
    
    def parse_data(self, data):
        msg = {}
        src = "n/a"
        if data[0:12] == "|src:twitch|":
            stringdata = data[12:]
            src = "|src:twitch|"
            msg = {
                'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', stringdata)[0],
                'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', stringdata)[0],
                'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', stringdata)[0],
                'media_url': [],
                'mp4_url': '',
                'id': ''
                }
        elif data[0:12] == "|src:reddit|":
            jsondata = json.loads(data[12:])
            src = "|src:reddit|"
            msg = {
                'subreddit': jsondata['subreddit'],
                'username': jsondata['username'],
                'message': jsondata['message'],
                'media_url': [jsondata['media_url']],
                'mp4_url': '',
                'id': jsondata['id']
                }
        elif data[0:13] == "|src:twitter|":
            jsondata = json.loads(data[13:])
            if not jsondata.get('possibly_sensitive', False):
                urls = jsondata.get('entities',{}).get('urls',[])
                for url in [x['expanded_url'] for x in urls]:
                    if url:
                        for blacklink in self.config['blacklinks']:
                            if blacklink in url:
                                pp(url)
                                return src, {}
                src = "|src:twitter|"
                if 'retweeted_status' in jsondata:
                    if 'text' in jsondata['retweeted_status']:
                        if 'media' in jsondata['retweeted_status']['entities']:
                            if 'extended_entities' in jsondata:
                                if jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[]):
                                    msg = {
                                        'username': jsondata['user']['name'],
                                        'message': jsondata['retweeted_status']['text'],
                                        'media_url': [jsondata['retweeted_status']['entities']['media'][0]['media_url']],
                                        'mp4_url': max(jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[{'url':'','bitrate':1,'content_type':"video/mp4"}]), key=lambda x:x['bitrate'] if x['content_type']=="video/mp4" else 0)['url'],
                                        'id': jsondata['id_str']
                                        }
                                else:
                                    msg = {
                                        'username': jsondata['user']['name'],
                                        'message': jsondata['retweeted_status']['text'],
                                        'media_url': [jsondata['retweeted_status']['entities']['media'][0]['media_url']],
                                        'mp4_url': '',
                                        'id': jsondata['id_str']
                                        }
                            else:
                                msg = {
                                    'username': jsondata['user']['name'],
                                    'message': jsondata['retweeted_status']['text'],
                                    'media_url': [jsondata['retweeted_status']['entities']['media'][0]['media_url']],
                                    'mp4_url': '',
                                    'id': jsondata['id_str']
                                    }
                        else:
                            msg = {
                                'username': jsondata['user']['name'],
                                'message': jsondata['retweeted_status']['text'],
                                'media_url': [],
                                'mp4_url': '',
                                'id': jsondata['id_str']
                                }
                elif 'text' in jsondata:
                    if 'media' in jsondata['entities']:
                        if 'extended_entities' in jsondata:
                            if jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[]):
                                msg = {
                                    'username': jsondata['user']['name'],
                                    'message': jsondata['text'],
                                    'media_url': [jsondata['entities']['media'][0]['media_url']],
                                    'mp4_url': max(jsondata['extended_entities']['media'][0].get('video_info',{}).get('variants',[{'url':'','bitrate':1,'content_type':"video/mp4"}]), key=lambda x:x['bitrate'] if x['content_type']=="video/mp4" else 0)['url'],
                                    'id': jsondata['id_str']
                                    }
                            else:
                                msg = {
                                    'username': jsondata['user']['name'],
                                    'message': jsondata['text'],
                                    'media_url': [jsondata['entities']['media'][0]['media_url']],
                                    'mp4_url': '',
                                    'id': jsondata['id_str']
                                    }
                        else:
                            msg = {
                                'username': jsondata['user']['name'],
                                'message': jsondata['text'],
                                'media_url': jsondata['entities']['media'][0]['media_url'],
                                'mp4_url': [],
                                'id': jsondata['id_str']
                                }
                    else:
                        msg = {
                            'username': jsondata['user']['name'],
                            'message': jsondata['text'],
                            'media_url': [],
                            'mp4_url': '',
                            'id': jsondata['id_str']
                            }

        return src, msg