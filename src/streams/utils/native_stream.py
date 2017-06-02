import datetime
import pickle
import threading

from functions_general import *
from functions_matching import *
from strm import strm

class NativeStream(strm):
    def __init__(self, config, stream):
        strm.__init__(self, config, stream)

        self.init_threads()
        self.run()

    def init_threads(self):
        #stream helpers
        threading.Thread(target = self.filter_trending_thread).start()
        threading.Thread(target = self.render_trending_thread).start()
        threading.Thread(target = self.reset_subjs_thread).start()
        threading.Thread(target = self.enrich_trending_thread).start()
        threading.Thread(target = self.set_nlp_match_thread).start()
        threading.Thread(target = self.set_ad_trigger_thread).start()

        #data connections
        threading.Thread(target = self.send_stream).start()
        threading.Thread(target = self.send_analytics).start()

    #Main func
    def run(self):
        for data in iter(self.input_socket.recv, 'STOP'):
            #try: msg_data may be unpickleable?
            try:
                msg_data = pickle.loads(data)
                if len(msg_data) == 0:
                    pp('Native connection was lost...')
                if self.stream == msg_data['stream']:
                    messagetime = datetime.datetime.now()
                    self.process_message(msg_data, messagetime)  
                    self.last_rcv_time = messagetime
                    self.freq_count += 1
            except Exception, e:
                pp(e)

    # Manager Processes
    def set_nlp_match_thread(self):
        self.set_nlp_match_loop = True
        self.freq_mavgs = []
        self.freq_count = 0
        while self.set_nlp_match_loop:
            #try: reset subjs could break?
            try:
                self.freq_mavgs.append(self.freq_count)
                if len(self.freq_mavgs) >= 5:
                    self.freq_mavgs.pop(0)
                    if (float(sum(self.freq_mavgs))/max(len(self.freq_mavgs), 1)) < self.config['nlp_match_threshold']:
                        self.nlp_match = False
                    else:
                        self.nlp_match = True
                self.freq_count = 0
            except Exception, e:
                pp('failed set_nlp_match')
                pp(e)
            time.sleep(self.config['set_nlp_match_timeout'])

    def set_ad_trigger_thread(self):
        self.set_ad_trigger_loop = True
        self.last_ad_time = datetime.datetime.now()
        while self.set_nlp_match_loop:
            curr_time = datetime.datetime.now()
            if (curr_time - self.last_ad_time).total_seconds() > self.config['ad_timeout_base']:
                self.ad_trigger = True
                self.last_ad_time = curr_time
            time.sleep(self.config['ad_loop_timeout'])