import threading

from src.utils._functions_general import *


class NLP:
    def __init__(self, config, stream):
        self.config = config
        self.stream = stream
        self.data = {}

        self.init_threads()

    def init_threads(self):
        threading.Thread(target=self.reset_subjs).start()

    def reset_subjs(self):
        self.reset_subjs_loop = True
        while self.reset_subjs_loop:
            # try: reset subjs could break?
            try:
                self.data = {}
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed reset_subjs', 'error')
                pp(e, 'error')
            time.sleep(self.config['reset_subjs_refresh'])

    def handle_subjs(self, msgdata):
        for inc_subj in msgdata['nlp']['subjects']:
            if inc_subj['lower'] not in self.data:
                # try: race condition if subjs is wiped
                try:
                    self.data[inc_subj['lower']] = {
                        'vector':   inc_subj['vector'],
                        'score':    1,
                        'adjs':     inc_subj['adjs']
                    }
                except Exception, e:
                    pp(self.config['src'] + ":" + self.stream + ': failed process_subjs new', 'error')
                    pp(e, 'error')
            else:
                # try: race condition if subjs is wiped
                try:
                    self.data[inc_subj['lower']]['score'] += 1
                    self.data[inc_subj['lower']]['adjs'] += inc_subj['adjs']
                except Exception, e:
                    pp(self.config['src'] + ":" + self.stream + ': failed process_subjs matched', 'error')
                    pp(e, 'error')

    def process(self, msgdata):
        self.handle_subjs(msgdata)
