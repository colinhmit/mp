import datetime
import pickle
import zmq
import threading

from functions_general import *
from functions_matching import *
from strm import strm

class TwitterStream(strm):
    def __init__(self, config, stream):
        strm.__init__(self, config, stream)

        self.content = {}
        self.default_image = {'image': '', 'score': 0}
        self.init_threads()
        self.run()

    def init_threads(self):
        #stream helpers
        threading.Thread(target = self.filter_trending_thread).start()
        threading.Thread(target = self.filter_content_thread).start()
        threading.Thread(target = self.render_trending_thread).start()
        threading.Thread(target = self.reset_subjs_thread).start()
        threading.Thread(target = self.enrich_trending_thread).start()

        #data connections
        threading.Thread(target = self.send_stream).start()
        threading.Thread(target = self.send_analytics).start()

    def send_stream(self):
        self.send_stream_loop = True
        while self.send_stream_loop:
            #try: send stream could break?
            try:
                data = {
                    'type': 'stream',
                    'src': self.config['self'],
                    'stream': self.stream,
                    'enrichdecay': list(self.enrichdecay),
                    'ad_trigger': self.ad_trigger,
                    'data': {
                        'trending': dict(self.clean_trending), 
                        'content': dict(self.content),
                        'enrich': list(self.enrich),
                        'default_image': self.default_image['image']
                    }
                }
                pickled_data = pickle.dumps(data)
                self.http_socket.send(pickled_data)
                self.enrichdecay = []
            except Exception, e:
                pp('failed twitter send_stream')
                pp(e)
            time.sleep(self.config['send_stream_timeout'])

    def filter_content_thread(self):
        self.filter_content_loop = True
        while self.filter_content_loop:
            #try: filter content could break?
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
                            'src': self.config['self'],
                            'score': temp_trending[msg_key]['score'],
                            'last_mtch_time': temp_trending[msg_key]['last_mtch_time'],
                            'media_url': temp_trending[msg_key]['media_url'],
                            'mp4_url': temp_trending[msg_key]['mp4_url'],
                            'id': temp_trending[msg_key]['id'],
                            'src_id': temp_trending[msg_key]['src_id']
                        }
                    else:
                        min_key = min(self.content, key=lambda x: self.content[x]['score'])
                        if temp_trending[msg_key]['score'] > self.content[min_key]['score']:
                            del self.content[min_key]
                            self.content[msg_key] = {
                                'src': self.config['self'],
                                'score': temp_trending[msg_key]['score'],
                                'last_mtch_time': temp_trending[msg_key]['last_mtch_time'],
                                'media_url': temp_trending[msg_key]['media_url'],
                                'mp4_url': temp_trending[msg_key]['mp4_url'],
                                'id': temp_trending[msg_key]['id'],
                                'src_id': temp_trending[msg_key]['src_id']
                            }

                elif len(matched) == 1:
                    matched_msg = matched[0][0]
                    self.content[matched_msg]['score'] = max(self.content[matched_msg]['score'],temp_trending[msg_key]['score'])
                    # self.content[matched_msg]['last_mtch_time'] = temp_trending[msg_key]['last_mtch_time']

                else:
                    matched_msgs = [x[0] for x in matched]
                    (matched_msg, score) = fweo_tsort_compare(msg_key, matched_msgs)
                    self.content[matched_msg]['score'] = max(self.content[matched_msg]['score'],temp_trending[msg_key]['score'])
                    # self.content[matched_msg]['last_mtch_time'] = temp_trending[msg_key]['last_mtch_time']

            image_key = max(self.content, key=lambda x: self.content[x]['score'] if len(self.content[x]['media_url'])>0 else 0)
            if (len(self.content[image_key]['media_url'])>0):
                self.default_image = {'image':self.content[image_key]['media_url'][0], 'score':self.content[image_key]['score']}

    #Main func
    def run(self):
        for data in iter(self.input_socket.recv, 'STOP'):
            #try: msg_data may be unpickleable?
            try:
                msg_data = pickle.loads(data)
                if len(msg_data) == 0:
                    pp('Twitter connection was lost...')
                if (self.stream in msg_data['message'].lower()):
                    messagetime = datetime.datetime.now()
                    self.process_message(msg_data, messagetime)  
                    self.last_rcv_time = messagetime
            except Exception, e:
                pp(e)