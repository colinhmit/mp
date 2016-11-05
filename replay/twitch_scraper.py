# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""

import src.streams.lib.irc as irc_
from src.streams.lib.functions_general import *
from src.streams.lib.functions_matching import *

twitch_scraper_config = {
    # details required to login to twitch IRC server
    'server': 'irc.twitch.tv',
    'port': 6667,
    'username': 'stepthirtytwo',
    'oauth_password': 'oauth:3chiev6dslmp2t4f07ndd7znqm1ygf', # get this from http://twitchapps.com/tmi/
    
    # if set to true will display any data received
    'debug': False,

    # if set to true will log all messages from all channels
    # TODO
    'log_messages': False,

    'log_path': '/Users/colinh/Repositories/mp/replay/logs/',
                       
    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 4096
}

class TwitchScraper:

    def __init__(self, config, channel, filename):
        self.config = config
        self.channel = channel
        self.filename = filename
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object(channel)

    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config
        ts_start = time.time()
        f = open(config['log_path']+self.filename+'_stream.txt', 'w')
        
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
                
                channel = message_dict['channel']
                message = message_dict['message']
                username = message_dict['username']
                messagetime = time.time() - ts_start
                
                #Only works after twitch is done announcing stuff (MODT = Message of the day)

                lne = str(messagetime) + "_" + username + "_" + message
                pp(lne)
                f.write(lne.encode('utf8') + "\n")
                # You can add all your plain commands here
                #if message == "Hey":
                    #Send_message("Welcome to my stream, " + username)


if __name__ == '__main__':
    stream = raw_input('Enter the stream ID: ')
    savefile = raw_input('Enter the file name: ')
    server = TwitchScraper(twitch_scraper_config,stream,savefile)
    server.run()

    
 