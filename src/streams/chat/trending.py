import datetime
import threading

from src.utils._functions_general import *
from src.streams.chat._functions_matching import *


class Trending:
    def __init__(self, config, stream):
        self.config = config
        self.stream = stream
        self.last_rcv_time = datetime.datetime.now()

        self.trending = {}
        self.data = {}
        self.svo_match = self.config['base_svo_match']

        self.init_threads()

    def init_threads(self):
        # stream helpers
        threading.Thread(target=self.filter_trending).start()
        threading.Thread(target=self.render_trending).start()

        if self.config['dynamic_svo_match']:
            threading.Thread(target=self.set_svo_match).start()

    # filter logic (brad's filter)
    def filter_trending(self):
        self.filter_trending_loop = True
        while self.filter_trending_loop:
            # try: max_key could have decayed out
            try:
                if len(self.trending) > 0:
                    temp_trending = dict(self.trending)
                    max_key = max(temp_trending,
                                  key=lambda x: temp_trending[x]['score']
                                  if not temp_trending[x]['visible']
                                  else 0)
                    if not self.trending.get(max_key, {'visible': True})['visible']:
                        self.trending[max_key]['visible'] = True
                        self.trending[max_key]['first_rcv_time'] = self.last_rcv_time
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed filter_trending', 'error')
                pp(e, 'error')
            time.sleep(self.config['filter_trending_refresh'])

    # visual render dictionary
    def render_trending(self):
        self.render_trending_loop = True
        while self.render_trending_loop:
            # try: render trending could break?
            try:
                if len(self.trending) > 0:
                    temp_trending = dict(self.trending)
                    self.data = {
                        msg_k: {
                                'src':              msg_v['src'],
                                'username':         msg_v['username'],
                                'score':            msg_v['score'],
                                'first_rcv_time':   msg_v['first_rcv_time'].isoformat(),
                                'media_url':        msg_v['media_url'],
                                'mp4_url':          msg_v['mp4_url'],
                                'id':               msg_v['id'],
                                'src_id':           msg_v['src_id']
                               }
                        for msg_k, msg_v in temp_trending.items() if msg_v['visible']
                    }
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed render_trending', 'error')
                pp(e, 'error')
            time.sleep(self.config['render_trending_timeout'])

    # nlp comparison
    def set_svo_match(self):
        self.set_svo_match_loop = True
        self.freq_mavgs = []
        self.freq_count = 0
        while self.set_svo_match_loop:
            # try: reset subjs could break?
            try:
                self.freq_mavgs.append(self.freq_count)
                if len(self.freq_mavgs) >= 5:
                    self.freq_mavgs.pop(0)
                    if (float(sum(self.freq_mavgs)) /
                            max(len(self.freq_mavgs), 1)) < self.config['svo_match_threshold']:
                        self.svo_match = False
                    else:
                        self.svo_match = True
                self.freq_count = 0
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': failed set_nlp_match', 'error')
                pp(e, 'error')
            time.sleep(self.config['set_svo_match_refresh'])

    def nlp_svo_compare(self, msgdata):
        temp_trending = dict(self.trending)
        for svo in msgdata['nlp']['svos']:
            for key in temp_trending.keys():
                match_subj = fweo_threshold(
                                svo['subj'],
                                [x['subj'] for x in temp_trending[key]['svos']],
                                self.config['subj_compare_threshold'])
                if match_subj is not None:
                    matched_svos = [x for x in temp_trending[key]['svos']
                                    if x['subj'] == match_subj[0]]
                    for matched_svo in matched_svos:
                        verb_diff = cosine(svo['verb'], matched_svo['verb'])
                        if (verb_diff > self.config['verb_compare_threshold'] and
                                svo['neg'] == matched_svo['neg']):
                            obj_diff = cosine(svo['obj'], matched_svo['obj'])
                            if obj_diff > self.config['obj_compare_threshold']:
                                return key
        return None

    def get_match(self, msgdata):
        matched_msg = None
        if self.config['string_match']:
            matched = fweb_compare(
                        msgdata['message'],
                        self.trending.keys(),
                        self.config['fo_compare_threshold'])
            if len(matched) == 0:
                if self.svo_match:
                    # try: nlp compare can fail if global is flushed
                    try:
                        matched_msg = self.nlp_svo_compare(msgdata)
                    except Exception, e:
                        pp(self.src + ":" + self.stream+': SVO Matching Failed.', 'error')
                        pp(e, 'error')
            elif len(matched) == 1:
                matched_msg = matched[0][0]
            else:
                matched_msgs = [x[0] for x in matched]
                (matched_msg, score) = fweo_tsort_compare(msgdata['message'], matched_msgs)
        else:
            if msgdata['message'] in self.trending.keys():
                matched_msg = msgdata['message']
        return matched_msg

    # matching Logic
    def handle_match(self, matched_msg, msgdata, msgtime):
        if (msgdata['username'] not in self.trending[matched_msg]['users'] or
                self.config['ignore_user']):
            # check substrings
            match_subs = fweo_threshold(
                            msgdata['message'],
                            self.trending[matched_msg]['msgs'].keys(),
                            self.config['so_compare_threshold'])

            # if no substring match
            if match_subs is None:
                # score scales w/ len users
                self.trending[matched_msg]['score'] += self.config['matched_add_base'] * max(0.1,
                        1 - ((len(self.trending[matched_msg]['users']) ** 2) /
                        self.config['matched_add_user_base']))
                self.trending[matched_msg]['last_mtch_time'] = msgtime
                self.trending[matched_msg]['users'].append(msgdata['username'])
                self.trending[matched_msg]['msgs'][msgdata['message']] = 1.0

            # if substring match
            else:
                submatched_msg = match_subs[0]
                self.trending[matched_msg]['msgs'][submatched_msg] += 1

                # if enough to branch
                if (self.trending[matched_msg]['msgs'][submatched_msg] >
                        self.trending[matched_msg]['msgs'][matched_msg]):
                    # subscore is proportionate to matched_msg
                    submatch_score = (self.trending[matched_msg]['score'] *
                                      self.trending[matched_msg]['msgs'][submatched_msg] /
                                      sum(self.trending[matched_msg]['msgs'].values()))
                    self.trending[submatched_msg] = {
                        'src':              self.config['src'],
                        'score':            submatch_score + self.config['matched_add_base'],
                        'last_mtch_time':   msgtime,
                        'first_rcv_time':   msgtime,
                        'media_url':        msgdata['media_url'],
                        'mp4_url':          msgdata['mp4_url'],
                        'svos':             msgdata['svos'],
                        'username':         msgdata['username'],
                        'users':            [msgdata['username']],
                        'msgs':             dict(self.trending[matched_msg]['msgs']),
                        'visible':          True,
                        'id':               msgdata['id'],
                        'src_id':           msgdata['src_id']
                    }
                    self.trending[matched_msg]['score'] -= submatch_score
                    del self.trending[matched_msg]['msgs'][submatched_msg]
                    del self.trending[submatched_msg]['msgs'][matched_msg]
                else:
                    self.trending[matched_msg]['score'] += max(0.1,
                            1 - ((len(self.trending[matched_msg]['users']) ** 2) /
                            self.config['matched_add_user_base'])
                        ) * self.config['matched_add_base']
                    self.trending[matched_msg]['last_mtch_time'] = msgtime
                    self.trending[matched_msg]['users'].append(msgdata['username'])

    def handle_new(self, msgdata, msgtime):
        if len(msgdata['message']) > 0:
            vis_bool = ((msgtime - self.last_rcv_time).total_seconds() >
                        self.config['filter_trending_timeout'])
            self.trending[msgdata['message']] = {
                'src':              self.config['src'],
                'score':            self.config['matched_init_base'],
                'last_mtch_time':   msgtime,
                'first_rcv_time':   msgtime,
                'media_url':        msgdata['media_url'],
                'mp4_url':          msgdata['mp4_url'],
                'svos':             msgdata['svos'],
                'username':         msgdata['username'],
                'users':            [msgdata['username']],
                'msgs':             {msgdata['message']: 1.0},
                'visible':          vis_bool,
                'id':               msgdata['id'],
                'src_id':           msgdata['src_id']
            }

    def decay(self, msgdata, msgtime):
        for msg in self.trending.keys():
            if msg == msgdata['message']:
                pass
            else:
                curr_score = self.trending[msg]['score']

                rcvtime_secs = (msgtime - self.last_rcv_time).total_seconds()
                msglife_secs = (msgtime - self.trending[msg]['first_rcv_time']).total_seconds()
                lastmtch_secs = (msgtime - self.trending[msg]['last_mtch_time']).total_seconds()

                buffer_constant = min(rcvtime_secs * self.config['buffer_mult'], 1)
                # msg event decay
                curr_score -= (buffer_constant * self.config['decay_msg_base'] /
                               max(self.config['decay_msg_min_limit'], msglife_secs))
                # time decay
                curr_score -= (buffer_constant * self.config['decay_time_base'] *
                               max(msglife_secs,
                               (lastmtch_secs ** 2) / self.config['decay_time_mtch_base']))

                if curr_score <= 0.0:
                    del self.trending[msg]
                else:
                    self.trending[msg]['score'] = curr_score

    def process(self, msgdata, msgtime):
        if len(self.trending) > 0:
            # get match could fail? remove if not
            try:
                matched_msg = self.get_match(msgdata)
            except Exception, e:
                pp(self.config['src'] + ":" + self.stream + ': matching failed.', 'error')
                pp(e, 'error')
                matched_msg = None
            if matched_msg is None:
                self.handle_new(msgdata, msgtime)
            else:
                self.handle_match(matched_msg, msgdata, msgtime)
        else:
            self.handle_new(msgdata, msgtime)
        self.decay(msgdata, msgtime)
        self.freq_count += 1

