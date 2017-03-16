# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""
import datetime
import pickle
import zmq
import threading

from utils.functions_general import *
from utils.functions_matching import *
from utils.strm import strm

class TwitterStream(strm):
    def __init__(self, config, stream):
        strm.__init__(self, config, stream)

        self.content = {}
        self.default_image = {'image': '', 'score': 0}
        self.init_threads()

    def init_threads(self):
        #stream helpers
        threading.Thread(target = self.filter_trending_thread).start()
        threading.Thread(target = self.filter_content_thread).start()
        threading.Thread(target = self.render_trending_thread).start()
        threading.Thread(target = self.garbage_cleanup_thread).start()
        threading.Thread(target = self.reset_subjs_thread).start()

        #data connections
        threading.Thread(target = self.send_stream).start()
        threading.Thread(target = self.send_analytics).start()

    def send_stream(self):
        self.send_stream_loop = True
        while self.send_stream_loop:
            try:
                data = {
                    'type': 'stream',
                    'src': self.config['self'],
                    'stream': self.stream,
                    'data': {
                        'trending': dict(self.clean_trending), 
                        'content': dict(self.content), 
                        'default_image': self.default_image['image']
                    }
                }
                pickled_data = pickle.dumps(data)
                self.http_socket.send(pickled_data)
            except Exception, e:
                pp('failed twitter send_stream')
                pp(e)
            time.sleep(self.config['send_stream_timeout'])

    def filter_content_thread(self):
        self.filter_content_loop = True
        while self.filter_content_loop:
            try:
                self.filter_content()
            except Exception, e:
                pp('failed twitter filter_content_thread')
                pp(e)
            time.sleep(self.config['filter_content_timeout'])

    #Manager Processes
    def filter_content(self):
        if len(self.trending)>0:
            # Clean content
            curr_time = datetime.datetime.now()
            for msg_key in self.content.keys():
                if (curr_time - self.content[msg_key]['last_mtch_time']).total_seconds() > self.config['content_max_time']:
                    del self.content[msg_key]

            temp_trending = dict(self.trending)
            for msg_key in temp_trending:
                matched = fweb_compare(msg_key, self.content.keys(), self.config['fo_compare_threshold'])

                if (len(matched) == 0):
                    if len(self.content)<self.config['content_max_size']:
                        self.content[msg_key] = {
                            'score': temp_trending[msg_key]['score'],
                            'last_mtch_time': temp_trending[msg_key]['last_mtch_time'],
                            'media_url': temp_trending[msg_key]['media_url'],
                            'mp4_url': temp_trending[msg_key]['mp4_url'],
                            'id': temp_trending[msg_key]['id']
                        }
                    else:
                        min_key = min(self.content, key=lambda x: self.content[x]['score'])
                        if temp_trending[msg_key]['score'] > self.content[min_key]['score']:
                            del self.content[min_key]
                            self.content[msg_key] = {
                                'score': temp_trending[msg_key]['score'],
                                'last_mtch_time': temp_trending[msg_key]['last_mtch_time'],
                                'media_url': temp_trending[msg_key]['media_url'],
                                'mp4_url': temp_trending[msg_key]['mp4_url'],
                                'id': temp_trending[msg_key]['id']
                            }

                elif len(matched) == 1:
                    matched_msg = matched[0][0]
                    self.content[matched_msg]['score'] = max(self.content[matched_msg]['score'],temp_trending[msg_key]['score'])
                    self.content[matched_msg]['last_mtch_time'] = temp_trending[msg_key]['last_mtch_time']

                else:
                    matched_msgs = [x[0] for x in matched]
                    (matched_msg, score) = fweo_tsort_compare(msg_key, matched_msgs)
                    self.content[matched_msg]['score'] = max(self.content[matched_msg]['score'],temp_trending[msg_key]['score'])
                    self.content[matched_msg]['last_mtch_time'] = temp_trending[msg_key]['last_mtch_time']

            image_key = max(temp_trending, key=lambda x: temp_trending[x]['score'] if len(temp_trending[x]['media_url'])>0 else 0)
            if (len(temp_trending[image_key]['media_url'])>0) and (temp_trending[image_key]['score']>self.default_image['score']):
                self.default_image = {'image':temp_trending[image_key]['media_url'][0], 'score':temp_trending[image_key]['score']}

    #Main func
    def run(self):        
        for data in iter(self.input_socket.recv, 'STOP'):
            msg_data = pickle.loads(data)
            if len(msg_data) == 0:
                pp('Twitter connection was lost...')
            if self.stream in msg_data['message'].lower():
                messagetime = datetime.datetime.now()
                self.process_message(msg_data, messagetime)  
                self.last_rcv_time = messagetime