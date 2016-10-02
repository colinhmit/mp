# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""

import lib.irc as irc_
from lib.functions_general import *
from lib.functions_matching import *

class TwitchStream:

    def __init__(self, config, channel):
        self.config = config
        self.channel = channel
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object(channel)
        # self.chat = {}
        self.last_rcv_time = None
        self.trending = {}

    # def get_chat(self):
    #     return self.chat
        
    def get_trending(self):
        return self.trending

    def process_message(self, msg, msgtime, user):
        if len(self.trending)>0:
            matched = fweb_compare(msg, self.trending.keys(), self.config['fo_compare_threshold'])

            if len(matched) == 0:
                if self.config['debug']:
                    pp("??? "+msg+" ???")
                self.trending[msg] = { 
                    'score': self.config['matched_init_base'], 
                    'last_mtch_time': msgtime,
                    'first_rcv_time': msgtime,
                    'users' : [user],
                    'msgs' : {msg: 1.0}
                }

            elif len(matched) == 1:
                matched_msg = matched[0][0]

                if user in self.trending[matched_msg]['users']:
                    if self.config['debug']:
                        pp("&&& DUPLICATE"+matched_msg+" + "+msg+" &&&")
                else:
                    if self.config['debug']:
                        pp("!!! "+matched_msg+" + "+msg+" !!!")

                    #check transformation
                    check_output = check_msg(msg, self.trending[matched_msg]['msgs'].keys(), self.config['so_compare_threshold'])

                    #if no substring match
                    if check_output == None:
                        self.trending[matched_msg]['score'] = self.trending[matched_msg]['score']+self.config['matched_add_base']
                        self.trending[matched_msg]['last_mtch_time'] = msgtime
                        self.trending[matched_msg]['users'].append(user)
                        self.trending[matched_msg]['msgs'][msg] = 1.0

                    #if substring match
                    else:
                        submatched_msg = check_output[0]
                        self.trending[matched_msg]['msgs'][submatched_msg] += 1

                        #if enough to branch
                        if self.trending[matched_msg]['msgs'][submatched_msg] > self.trending[matched_msg]['msgs'][matched_msg]:
                            self.trending[submatched_msg] = {
                                'score': (self.trending[matched_msg]['score'] * self.trending[matched_msg]['msgs'][submatched_msg] / sum(self.trending[matched_msg]['msgs'].values())) + self.config['matched_add_base'], 
                                'last_mtch_time': msgtime,
                                'first_rcv_time': msgtime,
                                'users' : [user],
                                'msgs' : dict(self.trending[matched_msg]['msgs'])
                            }
                            self.trending[matched_msg]['score'] *= ((sum(self.trending[matched_msg]['msgs'].values())-self.trending[matched_msg]['msgs'][submatched_msg]) / sum(self.trending[matched_msg]['msgs'].values()))
                            del self.trending[matched_msg]['msgs'][submatched_msg]
                            del self.trending[submatched_msg]['msgs'][matched_msg]

                        else:
                            self.trending[matched_msg]['score'] = self.trending[matched_msg]['score']+self.config['matched_add_base']
                            self.trending[matched_msg]['last_mtch_time'] = msgtime
                            self.trending[matched_msg]['users'].append(user)

            else:
                matched_msgs = [x[0] for x in matched]
                (matched_msg, score) = fweo_tsort_compare(msg, matched_msgs)

                if user in self.trending[matched_msg]['users']:
                    if self.config['debug']:
                        pp("&&& DUPLICATE"+matched_msg+" + "+msg+" &&&")
                else:
                    if self.config['debug']:
                        pp("!!! "+matched_msg+" + "+msg+" !!!")
                    
                    #check transformation
                    check_output = check_msg(msg, self.trending[matched_msg]['msgs'].keys(), self.config['so_compare_threshold'])

                    #if no substring match
                    if check_output == None:
                        self.trending[matched_msg]['score'] = self.trending[matched_msg]['score']+self.config['matched_add_base']
                        self.trending[matched_msg]['last_mtch_time'] = msgtime
                        self.trending[matched_msg]['users'].append(user)
                        self.trending[matched_msg]['msgs'][msg] = 1.0

                    #if substring match
                    else:
                        submatched_msg = check_output[0]
                        self.trending[matched_msg]['msgs'][submatched_msg] += 1

                        #if enough to branch
                        if self.trending[matched_msg]['msgs'][submatched_msg] > self.trending[matched_msg]['msgs'][matched_msg]:
                            self.trending[submatched_msg] = {
                                'score': (self.trending[matched_msg]['score'] * self.trending[matched_msg]['msgs'][submatched_msg] / sum(self.trending[matched_msg]['msgs'].values())) + self.config['matched_add_base'], 
                                'last_mtch_time': msgtime,
                                'first_rcv_time': msgtime,
                                'users' : [user],
                                'msgs' : dict(self.trending[matched_msg]['msgs'])
                            }
                            self.trending[matched_msg]['score'] *= ((sum(self.trending[matched_msg]['msgs'].values())-self.trending[matched_msg]['msgs'][submatched_msg]) / sum(self.trending[matched_msg]['msgs'].values()))
                            del self.trending[matched_msg]['msgs'][submatched_msg]
                            del self.trending[submatched_msg]['msgs'][matched_msg]

                        else:
                            self.trending[matched_msg]['score'] = self.trending[matched_msg]['score']+self.config['matched_add_base']
                            self.trending[matched_msg]['last_mtch_time'] = msgtime
                            self.trending[matched_msg]['users'].append(user)

        else:
            if self.config['debug']:
                    pp("Init trending")
            self.trending[msg] = { 
                'score': self.config['matched_init_base'], 
                'last_mtch_time': msgtime,
                'first_rcv_time': msgtime,
                'users' : [user],
                'msgs' : {msg: 1.0}
            }

        # if (len(self.chat)>0):
            # prev_msgtime = max(self.chat.keys())
        if (self.last_rcv_time!=None):
            prev_msgtime = self.last_rcv_time
        else:
            prev_msgtime = msgtime
            
        for key in self.trending.keys():
            curr_score = self.trending[key]['score']
            curr_score -= self.config['decay_msg_base']
            curr_score -= (msgtime - self.trending[key]['last_mtch_time'])/(max(1,msgtime-prev_msgtime)) * max(1, msgtime - self.trending[key]['first_rcv_time']) * self.config['decay_time_base']
                        
            if curr_score<=0.0:
                del self.trending[key]
            else:
                self.trending[key]['score'] = curr_score
    
    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config
        ts_start = time.time() 
        
        while True:
            data = sock.recv(config['socket_buffer_size']).rstrip()
            
            if len(data) == 0:
                pp('Connection was lost, reconnecting.')
                sock = self.irc.get_irc_socket_object(self.channel)

            #if config['debug']:
            #    pp(data)

            # check for ping, reply with pong
            irc.check_for_ping(data)

            if irc.check_for_message(data):
                #print 'Processing message'
                message_dict = irc.get_message(data)
                
                channel = message_dict['channel']
                message = message_dict['message']
                username = message_dict['username']
                messagetime = time.time() - ts_start
                
                self.process_message(message, messagetime, username)  

                self.last_rcv_time = messagetime
                #self.chat[messagetime] = {'channel':channel, 'message':message, 'username':username}             
                