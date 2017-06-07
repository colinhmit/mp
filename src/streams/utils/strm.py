import datetime
import re
import zmq
import pickle
import uuid

from functions_general import *
from functions_matching import *

class strm:
    def __init__(self, config, stream):
        self.config = config
        self.stream = stream
        self.last_rcv_time = datetime.datetime.now()
        self.last_enrch_time = datetime.datetime.now()
        self.last_decay_time = datetime.datetime.now()

        self.trending = {}
        self.clean_trending = {}
        self.subjs = {}
        self.enrich = []
        self.enrichdecay = []

        self.nlp_match = True
        self.ad_trigger = False
        self.enrich_trigger = False

        self.init_sockets()

    def init_sockets(self):
        context = zmq.Context()
        self.input_socket = context.socket(zmq.SUB)
        self.input_socket.connect('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port']))
        self.input_socket.setsockopt(zmq.SUBSCRIBE, "")

        self.http_socket = context.socket(zmq.PUSH)
        self.http_socket.connect('tcp://'+self.config['zmq_http_host']+':'+str(self.config['zmq_http_port']))

        self.data_socket = context.socket(zmq.PUB)
        self.data_socket.connect('tcp://'+self.config['zmq_data_host']+':'+str(self.config['zmq_data_port']))

    # ZMQ Processes
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
                    'data': {
                        'trending': dict(self.clean_trending),
                        'enrich': list(self.enrich),
                        'ad_trigger': self.ad_trigger
                    }
                }
                pickled_data = pickle.dumps(data)
                self.http_socket.send(pickled_data)
                self.enrichdecay = []
                self.ad_trigger = False
            except Exception, e:
                pp('failed send_stream')
                pp(e)
            time.sleep(self.config['send_stream_timeout'])

    def send_analytics(self):
        self.send_analytics_loop = True
        while self.send_analytics_loop:
            #try: send analytics could break?
            try:
                data = {
                    'type': 'subjects',
                    'src': self.config['self'],
                    'stream': self.stream,
                    'data': dict(self.subjs)
                }
                pickled_data = pickle.dumps(data)
                self.data_socket.send(pickled_data)
            except Exception, e:
                pp('failed send_analytics')
                pp(e)
            time.sleep(self.config['send_analytics_timeout'])

    # Manager Processes
    def reset_subjs_thread(self):
        self.reset_subjs_loop = True
        while self.reset_subjs_loop:
            #try: reset subjs could break?
            try:
                self.subjs = {}
            except Exception, e:
                pp('failed reset_subjs_thread')
                pp(e)
            time.sleep(self.config['reset_subjs_timeout'])

    def filter_trending_thread(self):
        self.filter_trending_loop = True
        while self.filter_trending_loop:
            #try: filter trending could break?
            try:
                self.filter_trending()
            except Exception, e:
                pp('failed filter_trending_thread')
                pp(e)
            time.sleep(self.config['filter_trending_timeout'])

    def render_trending_thread(self):
        self.render_trending_loop = True
        while self.render_trending_loop:
            #try: render trending could break?
            try:
                self.render_trending()
            except Exception, e:
                pp('failed render_trending_thread')
                pp(e)
            time.sleep(self.config['render_trending_timeout'])

    def enrich_trending_thread(self):
        self.enrich_trending_loop = True
        while self.enrich_trending_loop:
            curr_time = datetime.datetime.now()
            if ((curr_time - max(self.last_rcv_time,self.last_enrch_time)).total_seconds()>self.config['last_rcv_enrich_timeout']) or ((curr_time - self.last_enrch_time).total_seconds()>self.config['last_enrch_enrich_timeout']) or self.enrich_trigger:
                idstr = str(uuid.uuid1())
                enrich_item = {
                    'id': idstr,
                    'time': curr_time
                }
                self.enrich.append(enrich_item)
                self.decay_enrich()
                self.last_enrch_time = curr_time
                self.last_decay_time = curr_time
                self.enrich_trigger = False
            elif (curr_time - self.last_decay_time).total_seconds()>self.config['last_rcv_enrich_timeout']:
                self.decay_enrich()
                self.last_decay_time = curr_time
            time.sleep(self.config['enrich_trending_timeout'])

    #Manager Processes
    def render_trending(self):
        if len(self.trending)>0:
            temp_trending = dict(self.trending)
            self.clean_trending = {msg_k: {'src':msg_v['src'], 'score':msg_v['score'], 'first_rcv_time': msg_v['first_rcv_time'].isoformat(), 'media_url':msg_v['media_url'], 'mp4_url':msg_v['mp4_url'], 'id':msg_v['id'], 'src_id':msg_v['src_id'], 'username':msg_v['username']} for msg_k, msg_v in temp_trending.items() if msg_v['visible']==1}

    def filter_trending(self):
        if len(self.trending)>0:
            temp_trending = dict(self.trending)
            max_key = max(temp_trending, key=lambda x: temp_trending[x]['score'] if temp_trending[x]['visible']==0 else 0)
            if self.trending.get(max_key,{'visible':1})['visible'] == 0:
                #try: race condition if key is decayed out
                try:
                    self.trending[max_key]['visible'] = 1
                    self.trending[max_key]['first_rcv_time'] = self.last_rcv_time
                except Exception, e:
                    pp(self.config['self']+' filter trending failed on race condition.')
                    pp(e)

    #Matching Logic
    def handle_match(self, matched_msg, msgdata, msgtime):
        if msgdata['username'] in self.trending[matched_msg]['users']:
            if self.config['debug']:
                pp("&&& DUPLICATE"+matched_msg+" + "+msgdata['message']+" &&&")
        else:
            if self.config['debug']:
                pp("!!! "+matched_msg+" + "+msgdata['message']+" !!!")

            #check transformation
            match_subs = fweo_threshold(msgdata['message'], self.trending[matched_msg]['msgs'].keys(), self.config['so_compare_threshold'])

            #if no substring match
            if match_subs is None:
                self.trending[matched_msg]['score'] += max(0.1,1-((len(self.trending[matched_msg]['users'])**2)/self.config['matched_add_user_base']))*self.config['matched_add_base']
                self.trending[matched_msg]['last_mtch_time'] = msgtime
                self.trending[matched_msg]['users'].append(msgdata['username'])
                self.trending[matched_msg]['msgs'][msgdata['message']] = 1.0

            #if substring match
            else:
                submatched_msg = match_subs[0]
                self.trending[matched_msg]['msgs'][submatched_msg] += 1

                #if enough to branch
                if self.trending[matched_msg]['msgs'][submatched_msg] > self.trending[matched_msg]['msgs'][matched_msg]:
                    self.trending[submatched_msg] = {
                        'src': self.config['self'],
                        'score': (self.trending[matched_msg]['score'] * self.trending[matched_msg]['msgs'][submatched_msg] / sum(self.trending[matched_msg]['msgs'].values())) + self.config['matched_add_base'], 
                        'last_mtch_time': msgtime,
                        'first_rcv_time': msgtime,
                        'media_url': msgdata['media_url'],
                        'mp4_url': msgdata['mp4_url'],
                        'svos': msgdata['svos'],
                        'username': msgdata['username'],
                        'users' : [msgdata['username']],
                        'msgs' : dict(self.trending[matched_msg]['msgs']),
                        'visible' : 1,
                        'id': msgdata['id'],
                        'src_id': msgdata['src_id']
                    }
                    self.trending[matched_msg]['score'] *= ((sum(self.trending[matched_msg]['msgs'].values())-self.trending[matched_msg]['msgs'][submatched_msg]) / sum(self.trending[matched_msg]['msgs'].values()))
                    del self.trending[matched_msg]['msgs'][submatched_msg]
                    del self.trending[submatched_msg]['msgs'][matched_msg]
                else:
                    self.trending[matched_msg]['score'] += max(0.1,1-((len(self.trending[matched_msg]['users'])**2)/self.config['matched_add_user_base']))*self.config['matched_add_base']
                    self.trending[matched_msg]['last_mtch_time'] = msgtime
                    self.trending[matched_msg]['users'].append(msgdata['username'])

    def handle_new(self, msgdata, msgtime):
        if len(msgdata['message']) > 0:
            if self.config['debug']:
                pp("??? "+msgdata['message']+" ???")
            vis_bool = (msgtime - self.last_rcv_time).total_seconds() > self.config['filter_trending_timeout']
            self.trending[msgdata['message']] = { 
                'src': self.config['self'],
                'score':  self.config['matched_init_base'],
                'last_mtch_time': msgtime,
                'first_rcv_time': msgtime,
                'media_url': msgdata['media_url'],
                'mp4_url': msgdata['mp4_url'],
                'svos': msgdata['svos'],
                'username': msgdata['username'],
                'users' : [msgdata['username']],
                'msgs' : {msgdata['message']: 1.0},
                'visible' : vis_bool,
                'id': msgdata['id'],
                'src_id': msgdata['src_id']
            }

    def nlp_compare(self, msgdata):
        temp_trending = dict(self.trending)
        for svo in msgdata['svos']:
            for key in temp_trending.keys():
                match_subj = fweo_threshold(svo['subj'], [x['subj'] for x in temp_trending[key]['svos']], self.config['subj_compare_threshold'])
                if match_subj is None:
                    pass
                else:
                    matched_svos = [x for x in temp_trending[key]['svos'] if x['subj']==match_subj[0]]

                    for matched_svo in matched_svos:
                        verb_diff = cosine(svo['verb'], matched_svo['verb'])

                        if (verb_diff<self.config['verb_compare_threshold']) or (svo['neg'] != matched_svo['neg']):
                            pass
                        else:
                            obj_diff = cosine(svo['obj'], matched_svo['obj'])

                            if (obj_diff<self.config['obj_compare_threshold']):
                                pass
                            else:
                                return key
        return None

    def process_subjs(self, msgdata):
        for inc_subj in msgdata['subjs']:
            if inc_subj['lower'] not in self.subjs:
                #try: race condition if subj is decayed out or subjs is wiped
                try:
                    self.subjs[inc_subj['lower']] = {
                        'vector': inc_subj['vector'],
                        'score': 1,
                        'adjs': inc_subj['adjs']
                    }
                except Exception, e:
                    pp('failed process_subjs 1')
                    pp(e)
            else:
                #try: race condition if subj is decayed out or subjs is wiped
                try:
                    self.subjs[inc_subj['lower']]['score'] += 1
                    self.subjs[inc_subj['lower']]['adjs'] += inc_subj['adjs']
                except Exception, e:
                    pp('failed process_subjs 2')
                    pp(e)

    def get_match(self, msgdata):
        if self.nlp_match:
            matched = fweb_compare(msgdata['message'], self.trending.keys(), self.config['fo_compare_threshold'])
            if (len(matched) == 0):
                #try: nlp compare can fail if global is flushed
                try:
                    return self.nlp_compare(msgdata) 
                except Exception, e:
                    pp(self.config['self']+' SVO Matching Failed.')
                    pp(e)
                    return None
            elif len(matched) == 1:
                return matched[0][0]
            else:
                matched_msgs = [x[0] for x in matched]
                (matched_msg, score) = fweo_tsort_compare(msgdata['message'], matched_msgs)
                return matched_msg
        else:
            if msgdata['message'] in self.trending.keys():
                return msgdata['message']
            else:
                return None

    def decay(self, msgdata, msgtime):
        prev_msgtime = self.last_rcv_time
        for key in self.trending.keys():
            if (key == msgdata['message']):
                pass
            else:
                curr_score = self.trending[key]['score']

                msgtime_secs = (msgtime - prev_msgtime).total_seconds()
                rcvtime_secs = (msgtime - self.trending[key]['first_rcv_time']).total_seconds()
                lastmtch_secs = (msgtime - self.trending[key]['last_mtch_time']).total_seconds()

                buffer_constant = min(msgtime_secs*self.config['buffer_mult'],1)
                #msg event decay
                curr_score -= buffer_constant*(1/max(self.config['decay_msg_min_limit'],rcvtime_secs))*self.config['decay_msg_base']
                #time decay
                curr_score -=  buffer_constant*max(rcvtime_secs,(lastmtch_secs**2)/self.config['decay_time_mtch_base']) * self.config['decay_time_base']
                            
                if curr_score<=0.0:
                    del self.trending[key]
                else:
                    self.trending[key]['score'] = curr_score
                
    def decay_enrich(self):
        temp_trending = dict(self.trending)
        oldest = False
        if (len(temp_trending) > 0) and (len(self.enrich) > 0):
            min_key = min(temp_trending, key=lambda x: temp_trending[x]['first_rcv_time'])
            oldest = (self.enrich[0]['time'] < temp_trending[min_key]['first_rcv_time'])

        if (len(self.enrich) > self.config['enrich_min_len']) or oldest:
            try:
                old_enrich = self.enrich.pop(0)
                self.enrichdecay.append(old_enrich['id'])
            except Exception, e:
                pp('decay enrich failed')
                pp(e)

    def check_triggers(self, msgdata):
        if "|AD_TRIGGER|" in msgdata['message']:
            self.ad_trigger = True
            self.last_ad_time = curr_time

        if "|ENRICH_TRIGGER|" in msgdata['message']:
            self.enrich_trigger = True

    def process_message(self, msgdata, msgtime):
        #SET UP ANALYTICS CONFIG
        self.process_subjs(msgdata)
        self.check_triggers(msgdata)

        #cleanup RT
        if msgdata['message'][:4] == 'RT @':
            msgdata['message'] = msgdata['message'][msgdata['message'].find(':')+1:]

        if len(self.trending)>0:
            try:
                matched_msg = self.get_match(msgdata)
            except Exception, e:
                pp(self.config['self']+' matching failed.')
                pp(e)
                matched_msg = None

            if matched_msg is None:
                self.handle_new(msgdata, msgtime)
            else:
                self.handle_match(matched_msg, msgdata, msgtime)

        else:
            self.handle_new(msgdata, msgtime)

        self.decay(msgdata, msgtime)