import datetime
import pickle
import threading

from functions_general import *
from functions_matching import *
from strm import strm

class TwitchStream(strm):
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
                    pp('Twitch connection was lost...')
                if self.stream == msg_data['channel'][1:].lower():
                    messagetime = datetime.datetime.now()
                    self.process_message(msg_data, messagetime)  
                    self.last_rcv_time = messagetime
            except Exception, e:
                pp(e)
            