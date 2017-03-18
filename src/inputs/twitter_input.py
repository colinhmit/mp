# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
import json
import multiprocessing

#import utils
from utils.functions_general import *
from std_inpt import std_inpt

class TwitterInput(std_inpt):
    def __init__(self, config, nlp):
        std_inpt.__init__(self, config, nlp)
        pp('Initializing Twitch Input Server...')

        #distribute
        multiprocessing.Process(target=self.distribute).start()

        for _ in xrange(self.config['num_procs']):
            multiprocessing.Process(target=self.process, args=(self.nlp_parser,)).start()
    
    def parse(self, data):
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