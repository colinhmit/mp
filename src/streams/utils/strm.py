# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""

import datetime
import re
import zmq
import pickle

from functions_general import *
from functions_matching import *

class strm:
    def __init__(self, config, stream):
        self.config = config
        self.stream = stream
        self.trending = {}
        self.clean_trending = {}
        self.subjs = {}
        self.clusters = {}
        self.last_rcv_time = None
        self.log_file = None
        self.log_start_time = None
        self.kill = False
        self.init_sockets()

    def init_sockets(self):
        context = zmq.Context()
        self.data_socket = context.socket(zmq.SUB)
        self.data_socket.connect("tcp://127.0.0.1:"+str(self.config['zmq_sub_port']))
        self.data_socket.setsockopt(zmq.SUBSCRIBE, self.config['zmq_subscribe'])

    # GET/SET Functionality
    def get_trending(self):
        return dict(self.clean_trending)

    def get_default_image(self):
        return self.default_image['image']

    def get_subjs(self):
        return dict(self.subjs)

    def reset_subjs(self):
        self.subjs = {}

    def set_clusters(self, clusters):
        self.clusters = clusters

    def get_clusters(self):
        return dict(self.clusters)

    #Manager Processes
    def render_trending(self):
        if len(self.trending)>0:
            temp_trending = dict(self.trending)
            self.clean_trending = {msg_k: {'score':msg_v['score'], 'first_rcv_time': msg_v['first_rcv_time'].isoformat(), 'media_url':msg_v['media_url'], 'mp4_url':msg_v['mp4_url'], 'id':msg_v['id']} for msg_k, msg_v in temp_trending.items() if msg_v['visible']==1}

    def filter_trending(self):
        if len(self.trending)>0:
            temp_trending = dict(self.trending)
            max_key = max(temp_trending, key=lambda x: temp_trending[x]['score'] if temp_trending[x]['visible']==0 else 0)
            if self.trending.get(max_key,{'visible':1})['visible'] == 0:
                try:
                    self.trending[max_key]['visible'] = 1
                    self.trending[max_key]['first_rcv_time'] = self.last_rcv_time
                except Exception, e:
                    pp('Filter trending failed on race condition.')
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
                        'score': (self.trending[matched_msg]['score'] * self.trending[matched_msg]['msgs'][submatched_msg] / sum(self.trending[matched_msg]['msgs'].values())) + self.config['matched_add_base'], 
                        'last_mtch_time': msgtime,
                        'first_rcv_time': msgtime,
                        'media_url': msgdata['media_url'],
                        'mp4_url': msgdata['mp4_url'],
                        'svos': msgdata['svos'],
                        'users' : [msgdata['username']],
                        'msgs' : dict(self.trending[matched_msg]['msgs']),
                        'visible' : 1,
                        'id': msgdata['id']
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
            self.trending[msgdata['message']] = { 
                'score':  self.config['matched_init_base'],
                'last_mtch_time': msgtime,
                'first_rcv_time': msgtime,
                'media_url': msgdata['media_url'],
                'mp4_url': msgdata['mp4_url'],
                'svos': msgdata['svos'],
                'users' : [msgdata['username']],
                'msgs' : {msgdata['message']: 1.0},
                'visible' : 0,
                'id': msgdata['id']
            }

    def nlp_compare(self, msgdata):
        for svo in msgdata['svos']:
            for key in self.trending.keys():
                match_subj = fweo_threshold(svo['subj'], [x['subj'] for x in self.trending[key]['svos']], self.config['subj_compare_threshold'])
                if match_subj is None:
                    pass
                else:
                    matched_svos = [x for x in self.trending[key]['svos'] if x['subj']==match_subj[0]]

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
                try:
                    self.subjs[inc_subj['lower']] = {
                        'vector': inc_subj['vector'],
                        'score': 1,
                        'adjs': inc_subj['adjs']
                    }
                except Exception, e:
                    pp(e)
            else:
                try:
                    self.subjs[inc_subj['lower']]['score'] += 1
                    self.subjs[inc_subj['lower']]['adjs'] += inc_subj['adjs']
                except Exception, e:
                    pp(e)

    def get_match(self, msgdata):
        matched = fweb_compare(msgdata['message'], self.trending.keys(), self.config['fo_compare_threshold'])

        if (len(matched) == 0):
            try:
                return self.nlp_compare(msgdata) 
            except Exception, e:
                pp('SVO Matching Failed.')
                pp(e)
                return None

        elif len(matched) == 1:
            return matched[0][0]

        else:
            matched_msgs = [x[0] for x in matched]
            (matched_msg, score) = fweo_tsort_compare(msgdata['message'], matched_msgs)
            return matched_msg

    def decay(self, msgdata, msgtime):
        if (self.last_rcv_time is not None):
            prev_msgtime = self.last_rcv_time
            
            for key in self.trending.keys():
                if key == msgdata['message']:
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

    def process_message(self, msgdata, msgtime):
        self.process_subjs(msgdata)

        if self.log_file is not None:
            line = str(msgtime - self.log_start_time) + "*|*" + msgdata['username'] + "*|*" + msgdata['message'] + "*|*" + str(msgdata['media_url']) + "*|*" + msgdata['mp4_url']
            self.log_file.write(line.encode('utf8') + "\n")

        #cleanup RT
        if msgdata['message'][:4] == 'RT @':
            msgdata['message'] = msgdata['message'][msgdata['message'].find(':')+1:]

        if len(self.trending)>0:
            try:
                matched_msg = self.get_match(msgdata)
            except Exception, e:
                pp('Twitter matching failed.')
                pp(e)
                matched_msg = None

            if matched_msg is None:
                self.handle_new(msgdata, msgtime)

            else:
                self.handle_match(matched_msg, msgdata, msgtime)
        else:
            self.handle_new(msgdata, msgtime)

        self.decay(msgdata, msgtime)