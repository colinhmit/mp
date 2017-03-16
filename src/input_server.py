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
    def __init__(self, config, init_streams):
        pp('Initializing Input Server...')
        self.config = config

        self.irc = irc(self.config['irc_config'], init_streams['twitch'])
        self.twtr = twtr(self.config['twtr_config'], init_streams['twitter'])
        self.rddt = rddt(self.config['rddt_config'], init_streams['reddit'])

        self.nlp_parser = nlpParser()

        self.distribute()
        self.process(self.nlp_parser)

    def process(self, nlp):
        for _ in xrange(self.config['num_irc_procs']):
            multiprocessing.Process(target=self.process_irc, args=(nlp,)).start()
    
        for _ in xrange(self.config['num_twtr_procs']):
            multiprocessing.Process(target=self.process_twtr, args=(nlp,)).start()
    
        for _ in xrange(self.config['num_rddt_procs']):
            multiprocessing.Process(target=self.process_rddt, args=(nlp,)).start()
    
    def process_irc(self, nlp):
        context = zmq.Context()
        recvr = context.socket(zmq.PULL)
        recvr.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_irc_input_port']))
        sendr = context.socket(zmq.PUB)
        sendr.connect('tcp://'+self.config['zmq_proc_host']+':'+str(self.config['zmq_irc_proc_port']))

        svomap = {}
        svorefresh = random.randint(750, 1000)

        for data in iter(recvr.recv_string, 'STOP'):
            msg = self.parse_irc(data)
            if len(msg) > 0:
                # WHILE CONSTRAINTED, TWITCH TAGGING OFF
                # hashid = hash(msg['message'])
                # if hashid in svomap:
                #     svos, subjs = svomap[hashid]
                # else:
                #     clean_msg = re.sub(r"http\S+", "", msg['message'])
                #     clean_msg = re.sub(r"[#@]", "", clean_msg)
                #     clean_msg = re.sub(r"[^\w\s\'\"!.,&?:;_%-]+", "", clean_msg)
                #     try:
                #         svos, subjs = nlp.parse_text(clean_msg)
                #     except Exception, e:
                #         svos = []
                #         subjs = []
                #     svomap[hashid] = svos, subjs

                # msg['svos'] = svos
                # msg['subjs'] = subjs

                # if len(svomap)>svorefresh:
                #     svomap = {}
                #     nlp.flush()
                #     gc.collect()
                msg['svos'] = []
                msg['subjs'] = []
                
                pickled_data = pickle.dumps(msg)
                sendr.send(pickled_data)

    def process_twtr(self, nlp):
        context = zmq.Context()
        recvr = context.socket(zmq.PULL)
        recvr.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_twtr_input_port']))
        sendr = context.socket(zmq.PUB)
        sendr.connect('tcp://'+self.config['zmq_proc_host']+':'+str(self.config['zmq_twtr_proc_port']))

        svomap = {}
        svorefresh = random.randint(250, 500)

        for data in iter(recvr.recv_string, 'STOP'):
            msg = self.parse_twtr(data)
            
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
                sendr.send(pickled_data)

    def process_rddt(self, nlp):
        context = zmq.Context()
        recvr = context.socket(zmq.PULL)
        recvr.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_rddt_input_port']))
        sendr = context.socket(zmq.PUB)
        sendr.connect('tcp://'+self.config['zmq_proc_host']+':'+str(self.config['zmq_rddt_proc_port']))

        svomap = {}
        svorefresh = random.randint(750, 1000)

        for data in iter(recvr.recv_string, 'STOP'):
            msg = self.parse_rddt(data)
            if len(msg) > 0:
                # WHILE CONSTRAINTED, REDDIT TAGGING OFF
                # hashid = hash(msg['message'])
                # if hashid in svomap:
                #     svos, subjs = svomap[hashid]
                # else:
                #     clean_msg = re.sub(r"http\S+", "", msg['message'])
                #     clean_msg = re.sub(r"[#@]", "", clean_msg)
                #     clean_msg = re.sub(r"[^\w\s\'\"!.,&?:;_%-]+", "", clean_msg)
                #     try:
                #         svos, subjs = nlp.parse_text(clean_msg)
                #     except Exception, e:
                #         svos = []
                #         subjs = []
                #     svomap[hashid] = svos, subjs

                # msg['svos'] = svos
                # msg['subjs'] = subjs

                # if len(svomap)>svorefresh:
                #     svomap = {}
                #     nlp.flush()
                #     gc.collect()
                msg['svos'] = []
                msg['subjs'] = []

                pickled_data = pickle.dumps(msg)
                sendr.send(pickled_data)

    def distribute(self):
        multiprocessing.Process(target=self.distribute_irc).start()
        multiprocessing.Process(target=self.distribute_twtr).start()
        multiprocessing.Process(target=self.distribute_rddt).start()

    def distribute_irc(self):
        distributing = True
        while distributing:
            try:
                context = zmq.Context(1)
                frontend = context.socket(zmq.SUB)
                frontend.bind("tcp://*:"+str(self.config['zmq_irc_proc_port']))
                frontend.setsockopt(zmq.SUBSCRIBE, "")

                backend = context.socket(zmq.PUB)
                backend.bind("tcp://*:"+str(self.config['zmq_irc_output_port']))
                zmq.device(zmq.FORWARDER, frontend, backend)
            except Exception, e:
                pp(e)

    def distribute_twtr(self):
        distributing = True
        while distributing:
            try:
                context = zmq.Context(1)
                frontend = context.socket(zmq.SUB)
                frontend.bind("tcp://*:"+str(self.config['zmq_twtr_proc_port']))
                frontend.setsockopt(zmq.SUBSCRIBE, "")

                backend = context.socket(zmq.PUB)
                backend.bind("tcp://*:"+str(self.config['zmq_twtr_output_port']))
                zmq.device(zmq.FORWARDER, frontend, backend)
            except Exception, e:
                pp(e)

    def distribute_rddt(self):
        distributing = True
        while distributing:
            try:
                context = zmq.Context(1)
                frontend = context.socket(zmq.SUB)
                frontend.bind("tcp://*:"+str(self.config['zmq_rddt_proc_port']))
                frontend.setsockopt(zmq.SUBSCRIBE, "")

                backend = context.socket(zmq.PUB)
                backend.bind("tcp://*:"+str(self.config['zmq_rddt_output_port']))
                zmq.device(zmq.FORWARDER, frontend, backend)
            except Exception, e:
                pp(e)
    
    def parse_irc(self, data):
        msg = {
                'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
                'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
                'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0],
                'media_url': [],
                'mp4_url': '',
                'id': ''
                }
        return msg

    def parse_twtr(self, data):
        jsondata = json.loads(data)
        msg = {}
        if not jsondata.get('possibly_sensitive', False):
                urls = jsondata.get('entities',{}).get('urls',[])
                for url in [x['expanded_url'] for x in urls]:
                    if url:
                        for blacklink in self.config['blacklinks']:
                            if blacklink in url:
                                return {}
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
        return msg

    def parse_rddt(self, data):
        jsondata = json.loads(data)
        msg = {
                'subreddit': jsondata['subreddit'],
                'username': jsondata['username'],
                'message': jsondata['message'],
                'media_url': [jsondata['media_url']],
                'mp4_url': '',
                'id': jsondata['id']
                }
        return msg