# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""

import datetime
from utils.functions_general import *
from utils.functions_matching import *

class TwitterStream:

    def __init__(self, config, channel, curr_twtr):
        self.config = config
        self.channel = channel

        curr_twtr.join_channel(channel)

        #set the pipe object as the socket & go!
        self.pipe = curr_twtr.get_twtr_stream_object(channel)

        self.last_rcv_time = None
        self.trending = {}
        self.clean_trending = {}
        self.kill = False

    def get_trending(self):
        return self.clean_trending

    def render_trending(self):
        if len(self.trending)>0:
            temp_trending = dict(self.trending)
            self.clean_trending = {msg_k: {'score':msg_v['score'], 'first_rcv_time': msg_v['first_rcv_time'].isoformat(), 'media_url':msg_v['media_url'] } for msg_k, msg_v in temp_trending.items() if msg_v['visible']==1}

    def filter_trending(self):
        if len(self.trending)>0:
            temp_trending = dict(self.trending)
            max_key = max(temp_trending, key=lambda x: temp_trending[x]['score'] if temp_trending[x]['visible']==0 else 0)
            if self.trending.get(max_key,{'visible':1})['visible'] == 0:
                self.trending[max_key]['visible'] = 1
                self.trending[max_key]['first_rcv_time'] = self.last_rcv_time

    def handle_match(self, matched_msg, msg, msgtime, user):
        if user in self.trending[matched_msg]['users']:
            if self.config['debug']:
                pp("&&& DUPLICATE"+matched_msg+" + "+msg+" &&&")
        else:
            if self.config['debug']:
                pp("!!! "+matched_msg+" + "+msg+" !!!")

            #check transformation
            match_subs = fweo_threshold(msg, self.trending[matched_msg]['msgs'].keys(), self.config['so_compare_threshold'])

            #if no substring match
            if match_subs == None:
                self.trending[matched_msg]['score'] += max(0.1,1-((len(self.trending[matched_msg]['users'])**2)/self.config['matched_add_user_base']))*self.config['matched_add_base']
                self.trending[matched_msg]['last_mtch_time'] = msgtime
                self.trending[matched_msg]['users'].append(user)
                self.trending[matched_msg]['msgs'][msg] = 1.0

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
                        'media_url': self.trending[matched_msg]['media_url'],
                        'users' : [user],
                        'msgs' : dict(self.trending[matched_msg]['msgs']),
                        'visible' : 1
                    }
                    self.trending[matched_msg]['score'] *= ((sum(self.trending[matched_msg]['msgs'].values())-self.trending[matched_msg]['msgs'][submatched_msg]) / sum(self.trending[matched_msg]['msgs'].values()))
                    del self.trending[matched_msg]['msgs'][submatched_msg]
                    del self.trending[submatched_msg]['msgs'][matched_msg]

                else:
                    self.trending[matched_msg]['score'] += max(0.1,1-((len(self.trending[matched_msg]['users'])**2)/self.config['matched_add_user_base']))*self.config['matched_add_base']
                    self.trending[matched_msg]['last_mtch_time'] = msgtime
                    self.trending[matched_msg]['users'].append(user)

    def handle_new(self, msg, msgtime, user, media):
        if len(msg) > 0:
            if self.config['debug']:
                pp("??? "+msg+" ???")
            self.trending[msg] = { 
                'score':  self.config['matched_init_base'],
                'last_mtch_time': msgtime,
                'first_rcv_time': msgtime,
                'media_url': media,
                'users' : [user],
                'msgs' : {msg: 1.0},
                'visible' : 0
            }

    def decay(self, msg, msgtime):
        if (self.last_rcv_time!=None):
            prev_msgtime = self.last_rcv_time
            
            for key in self.trending.keys():
                if key == msg:
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
        msg = msgdata['message']
        user = msgdata['username']
        media = msgdata['media_url']

        #cleanup RT
        if msg[:4] == 'RT @':
            msg = msg[msg.find(':')+1:]

        if len(self.trending)>0:
            matched = fweb_compare(msg, self.trending.keys(), self.config['fo_compare_threshold'])

            if (len(matched) == 0):
                self.handle_new(msg, msgtime, user, media)

            elif len(matched) == 1:
                matched_msg = matched[0][0]
                self.handle_match(matched_msg, msg, msgtime, user)

            else:
                matched_msgs = [x[0] for x in matched]
                (matched_msg, score) = fweo_tsort_compare(msg, matched_msgs)
                self.handle_match(matched_msg, msg, msgtime, user)

        else:
            if self.config['debug']:
                    pp("Init trending")
            self.handle_new(msg, msgtime, user, media)

        self.decay(msg, msgtime)

    def run(self):
        pipe = self.pipe
        config = self.config
        
        while not self.kill:
            data = pipe.get()
            if len(data) == 0:
                pp('Connection was lost...')

            if self.channel.lower() in data['message'].lower():
                messagetime = datetime.datetime.now()
                self.process_message(data, messagetime)  
                self.last_rcv_time = messagetime
