import datetime
import uuid
import threading

from _functions_general import *


class Enricher:
    def __init__(self, config, src, stream):
        self.config = config
        self.src = src
        self.stream = stream
        self.last_rcv_time = datetime.datetime.now()
        self.last_enrch_time = datetime.datetime.now()
        self.last_decay_time = datetime.datetime.now()
        self.last_ad_time = datetime.datetime.now()

        self.trending = {}
        self.enrich = []
        self.enrichdecay = []
        self.enrich_trigger = False

        self.start()

    def start(self):
        threading.Thread(target=self.enrich_trending).start()
        threading.Thread(target=self.ad_trigger).start()

    def enrich_trending(self):
        self.enrich_trending_loop = True
        while self.enrich_trending_loop:
            curr_time = datetime.datetime.now()
            last_rcv_time = (curr_time -
                             max(self.last_rcv_time, self.last_enrch_time)
                            ).total_seconds()
            last_enrch_time = (curr_time - self.last_enrch_time).total_seconds()
            last_decay_time = (curr_time - self.last_decay_time).total_seconds()
            timer_trigger = (last_rcv_time > self.config['last_rcv_enrich_timer'] or
                             last_enrch_time > self.config['last_enrch_enrich_timeout'])
            if (timer_trigger and self.config['enrich_timer']) or self.enrich_trigger:
                enrich_item = {
                    'id':       str(uuid.uuid1()),
                    'time':     curr_time
                }
                self.enrich.append(enrich_item)
                self.decay_enrich()
                self.last_enrch_time = curr_time
                self.last_decay_time = curr_time
                self.enrich_trigger = False
            elif last_decay_time > self.config['last_rcv_enrich_timer']:
                self.decay_enrich()
                self.last_decay_time = curr_time
            time.sleep(self.config['enrich_trending_refresh'])

    def ad_trigger(self):
        self.ad_trigger_loop = True
        while self.ad_trigger_loop:
            curr_time = datetime.datetime.now()
            last_ad_time = (curr_time - self.last_ad_time).total_seconds()
            if last_ad_time > self.config['ad_timer'] and self.config['ad_trigger']:
                self.ad_trigger = True
                self.last_ad_time = curr_time
            time.sleep(self.config['ad_refresh'])

    def decay_enrich(self):
        oldest = False
        temp_trending = dict(self.trending)
        if (len(temp_trending) > 0) and (len(self.enrich) > 0):
            min_key = min(temp_trending, key=lambda x: temp_trending[x]['first_rcv_time'])
            oldest = self.enrich[0]['time'] < temp_trending[min_key]['first_rcv_time']

        if (len(self.enrich) > self.config['enrich_min_len']) or oldest:
            try:
                old_enrich = self.enrich.pop(0)
                self.enrichdecay.append(old_enrich['id'])
            except Exception, e:
                pp(self.stream + ': decay_enrich failed', 'error')
                pp(e, 'error')

    def check_triggers(self, msgdata):
        if "|ADTRIGGER|" in msgdata['message']:
            self.ad_trigger = True
            curr_time = datetime.datetime.now()
            self.last_ad_time = curr_time
            enrich_item = {
                'id':       str(uuid.uuid1()),
                'time':     curr_time
            }
            self.enrich.append(enrich_item)
        elif "|ENRICHTRIGGER|" in msgdata['message']:
            self.enrich_trigger = True

    def process_message(self, msgdata, trending):
        self.check_triggers(msgdata)
        self.trending = trending
