# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""
import datetime

import utils.irc as irc_
from utils.functions_general import *
from utils.functions_matching import *

class TwitchStream:

    def __init__(self, config, channel):
        self.config = config
        self.channel = channel
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object(channel)

        self.last_rcv_time = None
        self.trending = {}
        self.clean_trending = {}

    def get_trending(self):
        return self.clean_trending

    def render_trending(self):
        if len(self.trending)>0:
            self.clean_trending = {msg_k: {'score':msg_v['score'], 'first_rcv_time': msg_v['first_rcv_time'].isoformat() } for msg_k, msg_v in self.trending.items() if msg_v['visible']==1}

    def filter_trending(self):
        if len(self.trending)>0:
            temp_trending = dict(self.trending)
            max_key = max(temp_trending, key=lambda x: temp_trending[x]['score'] if temp_trending[x]['visible']==0 else 0)
            if self.trending[max_key]['visible'] == 0:
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
                self.trending[matched_msg]['score'] += min(1,3/len(self.trending[matched_msg]['users']))*self.config['matched_add_base']
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
                        'users' : [user],
                        'msgs' : dict(self.trending[matched_msg]['msgs']),
                        'visible' : 1
                    }
                    self.trending[matched_msg]['score'] *= ((sum(self.trending[matched_msg]['msgs'].values())-self.trending[matched_msg]['msgs'][submatched_msg]) / sum(self.trending[matched_msg]['msgs'].values()))
                    del self.trending[matched_msg]['msgs'][submatched_msg]
                    del self.trending[submatched_msg]['msgs'][matched_msg]

                else:
                    self.trending[matched_msg]['score'] += min(1,3/len(self.trending[matched_msg]['users']))*self.config['matched_add_base']
                    self.trending[matched_msg]['last_mtch_time'] = msgtime
                    self.trending[matched_msg]['users'].append(user)

    def handle_new(self, msg, msgtime, user):
        if len(msg) > 0:
            if self.config['debug']:
                pp("??? "+msg+" ???")
            self.trending[msg] = { 
                'score':  self.config['matched_init_base'],
                'last_mtch_time': msgtime,
                'first_rcv_time': msgtime,
                'users' : [user],
                'msgs' : {msg: 1.0},
                'visible' : 0
            }

    def decay(self, msgtime):
        if (self.last_rcv_time!=None):
            prev_msgtime = self.last_rcv_time
        else:
            prev_msgtime = msgtime
            
        for key in self.trending.keys():
            curr_score = self.trending[key]['score']
            curr_score -= self.config['decay_msg_base']
            curr_score -= ((msgtime - self.trending[key]['last_mtch_time']).total_seconds())/(max(1,(msgtime-prev_msgtime).total_seconds())) * max(1, (msgtime - self.trending[key]['first_rcv_time']).total_seconds()) * self.config['decay_time_base']
                        
            if curr_score<=0.0:
                del self.trending[key]
            else:
                self.trending[key]['score'] = curr_score

    def process_message(self, msg, msgtime, user):
        if len(self.trending)>0:
            matched = fweb_compare(msg, self.trending.keys(), self.config['fo_compare_threshold'])

            if (len(matched) == 0):
                self.handle_new(msg, msgtime, user)

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
            self.handle_new(msg, msgtime, user)

        self.decay(msgtime)
    
    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config
        
        while True:
            data = sock.recv(config['socket_buffer_size']).rstrip()
            if len(data) == 0:
                pp('Connection was lost, reconnecting.')
                sock = self.irc.get_irc_socket_object(self.channel)
            # check for ping, reply with pong
            irc.check_for_ping(data)

            if irc.check_for_message(data):
                #print 'Processing message'
                message_dict = irc.get_message(data)
                message_time = datetime.datetime.now()
                
                self.process_message(message_dict['message'], message_time, message_dict['username'])  
                self.last_rcv_time = message_time
