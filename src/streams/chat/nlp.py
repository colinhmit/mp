import threading
import datetime

from src.utils._functions_general import *


class NLP:
    def __init__(self, config, stream):
        self.config = config
        self.stream = stream
        self.subjs = {}
        self.data = {}

        self.init_threads()

    def init_threads(self):
        threading.Thread(target=self.render_nlp).start()

    def render_nlp(self):
        self.render_nlp_loop = True
        while self.render_nlp_loop:
            # nlp dict could get wiped out mid run
            try:
                if len(self.subjs) > 0:
                    temp_subjs = dict(self.subjs)
                    sorted_subjs = sorted(temp_subjs, key=lambda x: temp_subjs[x]['score'], reverse=True)
                    self.data = {
                        x: {
                                'score':            temp_subjs[x]['score'],
                                'messages':         temp_subjs[x]['messages']
                            }
                        for x in sorted_subjs[:self.config['render_nlp_limit']]
                    }
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed render_nlp', 'error')
                pp(e, 'error')
            time.sleep(self.config['render_nlp_refresh'])

    def handle_nlp(self, msgdata, msgtime):
        for inc_subj in msgdata['nlp']['subjects']:
            if inc_subj['lower'] not in self.subjs:
                # try: race condition if subjs is wiped
                try:
                    self.subjs[inc_subj['lower']] = {
                        'vector':       inc_subj['vector'],
                        'score':        self.config['init_base'],
                        'rcv_time':     msgtime,
                        'messages':     [msgdata['message']]
                    }
                except Exception, e:
                    pp(self.config['src'] + ":" + self.stream + ': failed handle_subjs new', 'error')
                    pp(e, 'error')
            else:
                # try: race condition if subjs is wiped
                try:
                    self.subjs[inc_subj['lower']]['score'] += self.config['add_base']
                    self.subjs[inc_subj['lower']]['rcv_time'] = msgtime
                    if len(self.subjs[inc_subj['lower']]['messages']) < 100:
                        self.subjs[inc_subj['lower']]['messages'].append(msgdata['message'])
                    else:
                        self.subjs[inc_subj['lower']]['messages'].pop(0)
                        self.subjs[inc_subj['lower']]['messages'].append(msgdata['message'])
                except Exception, e:
                    pp(self.config['src'] + ":" + self.stream + ': failed handle_subjs matched', 'error')
                    pp(e, 'error')

    def decay_nlp(self, msgdata, msgtime):
        for subj in self.subjs.keys():
            curr_score = self.subjs[subj]['score']

            rcvtime_secs = (msgtime - self.subjs[subj]['rcv_time']).total_seconds()
            curr_score *= self.config['decay_perc']
            curr_score -= self.config['decay_base'] * rcvtime_secs

            if curr_score <= 0.0:
                del self.subjs[subj]
            else:
                self.subjs[subj]['score'] = curr_score

    def process(self, msgdata, msgtime):
        self.handle_nlp(msgdata, msgtime)
        self.decay_nlp(msgdata, msgtime)
