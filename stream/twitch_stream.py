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
        self.chat = {}
        self.trending = {}

    def get_chat(self):
        return self.chat
        
    def get_trending(self):
        return self.trending

    def process_message(self, msg, msgtime):
        if len(self.trending)>0:
            (matched_msg, score) = fweo_compare(msg,self.trending.keys())
            
            if score > self.config['fw_eo_threshold']:
                if self.config['debug']:
                    pp("!!! "+matched_msg+" + "+msg+" = "+str(score)+" !!!")
                self.trending[matched_msg] = ((self.trending[matched_msg][0]+self.config['matched_add_base']), msgtime)
                
            else:
                if self.config['debug']:
                    pp("??? "+matched_msg+" + "+msg+" = "+str(score)+" ???")
                self.trending[msg] = (self.config['matched_init_base'], msgtime)
        else:
            if self.config['debug']:
                    pp("Init trending")
            self.trending[msg] = (self.config['matched_init_base'], msgtime)
        
        if len(self.chat)>0:
            prev_msgtime = max(self.chat.keys())
        else:
            prev_msgtime = msgtime
            
        for key in self.trending.keys():
            curr_score, last_mtch_time = self.trending[key]
            curr_score -= self.config['decay_msg_base']
            curr_score -= (msgtime - last_mtch_time)/(max(1,msgtime-prev_msgtime)) * self.config['decay_time_base']
                        
            if curr_score<=0.0:
                del self.trending[key]
            else:
                self.trending[key] = (curr_score, last_mtch_time)
    
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
                
                self.process_message(message, messagetime)   

                self.chat[messagetime] = {'channel':channel, 'message':message, 'username':username}             
                