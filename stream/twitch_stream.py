# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""

import lib.irc as irc_
from lib.functions_general import *

class TwitchStream:

    def __init__(self, config, channel):
        self.config = config
        self.channel = channel
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object(channel)
        self.chat = {}

    def get_chat(self):
        return self.chat

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

            if config['debug']:
                print data

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
                #ppi(channel, message, username)
