import datetime
import threading

from _functions_general import *
from _functions_matching import *


class Aggregator:
    def __init__(self, config, stream):
        self.config = config
        self.stream = stream

        self.passed_trending = {}
        self.content = {}
        self.content_image = {'image': '', 'score': 0}

        self.init_threads()

    def init_threads(self):
        threading.Thread(target=self.filter_content).start()

    def filter_content(self):
        self.filter_content_loop = True
        while self.filter_content_loop:
            # try: get_content could break?
            try:
                self.get_content()
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed filter_content', 'error')
                pp(e, 'error')
            time.sleep(self.config['filter_content_refresh'])

    def get_content(self):
        if len(self.passed_trending)>0:
            # Clean content
            curr_time = datetime.datetime.now()
            for item in self.content.keys():
                item_life = (curr_time - self.content[item]['last_mtch_time']).total_seconds()
                if item_life > self.config['content_max_time']:
                    del self.content[item]

            temp_trending = dict(self.passed_trending)
            for msg in temp_trending:
                matched = fweb_compare(msg,
                                       self.content.keys(),
                                       self.config['fo_compare_threshold'])

                if len(matched) == 0:
                    if len(self.content) < self.config['content_max_size']:
                        self.content[msg] = {
                            'src':              self.config['src'],
                            'score':            temp_trending[msg]['score'],
                            'last_mtch_time':   temp_trending[msg]['last_mtch_time'],
                            'media_urls':       temp_trending[msg]['media_urls'],
                            'mp4_url':          temp_trending[msg]['mp4_url'],
                            'id':               temp_trending[msg]['id'],
                            'src_id':           temp_trending[msg]['src_id']
                        }
                    else:
                        min_msg = min(self.content, key=lambda x: self.content[x]['score'])
                        if temp_trending[msg]['score'] > self.content[min_msg]['score']:
                            del self.content[min_msg]
                            self.content[msg] = {
                                'src':              self.config['src'],
                                'score':            temp_trending[msg]['score'],
                                'last_mtch_time':   temp_trending[msg]['last_mtch_time'],
                                'media_urls':       temp_trending[msg]['media_urls'],
                                'mp4_url':          temp_trending[msg]['mp4_url'],
                                'id':               temp_trending[msg]['id'],
                                'src_id':           temp_trending[msg]['src_id']
                            }

                elif len(matched) == 1:
                    matched_msg = matched[0][0]
                    self.content[matched_msg]['score'] = max(self.content[matched_msg]['score'],
                                                             temp_trending[msg]['score'])

                else:
                    matched_msgs = [x[0] for x in matched]
                    (matched_msg, score) = fweo_tsort_compare(msg, matched_msgs)
                    self.content[matched_msg]['score'] = max(self.content[matched_msg]['score'],
                                                             temp_trending[msg]['score'])

            image_key = max(self.content, key=lambda x: self.content[x]['score']
                                          if len(self.content[x]['media_urls']) > 0 else 0)
            if len(self.content[image_key]['media_urls']) > 0:
                self.content_image = {
                    'image':    self.content[image_key]['media_url'][0],
                    'score':    self.content[image_key]['score']
                }

    def process(self, trending):
        self.passed_trending = trending
