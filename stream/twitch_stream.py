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
        self.fw_threshold = 65

    def get_chat(self):
        return self.chat
        
    def get_trending(self):
        return self.trending

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
                
                self.chat[messagetime] = {'channel':channel, 'message':message, 'username':username}
                
                if len(self.trending)>0:
                    (matched_msg, score) = fweo_compare(message,self.trending.keys())
                    if score > self.fw_threshold:
                        if config['debug']:
                            pp("!!!!!!!!")
                            pp("Matched w/ score: "+str(score))
                            pp(message)
                            pp(matched_msg)
                            pp("!!!!!!!!")
                        self.trending[matched_msg] += 20
                    else:
                        if config['debug']:
                            pp("????????")
                            pp(message)
                            pp("No match w/ max score: "+str(score))
                            pp("????????")
                        self.trending[message] = 5
                else:
                    if config['debug']:
                            pp("Init trending")
                    self.trending[message] = 5
                
                for key in self.trending.keys():
                    self.trending[key] -= 1
                    if self.trending[key]<1:
                        del self.trending[key]
                    
                    
                #ppi(channel, message, username)
