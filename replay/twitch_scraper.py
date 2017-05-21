# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""
import sys
import socket
import re

reload(sys)
sys.setdefaultencoding('utf-8')

# Add the mp folder path to the sys.path list
sys.path.append('/Users/colinh/Repositories/mp')

from src.inputs.utils.functions_general import *
from src.streams.utils.functions_matching import *

twitch_scraper_config = {
    # details required to login to twitch IRC server
    'server': 'irc.twitch.tv',
    'port': 6667,
    'username': 'currentsdev',
    'oauth_password': 'oauth:l338omp6pm1fen2jar1kqamz7gll9t', # get this from http://twitchapps.com/tmi/
    
    # if set to true will display any data received
    'debug': False,

    # if set to true will log all messages from all channels
    # TODO
    'log_messages': False,

    'log_path': '/Users/colinh/Repositories/mp/replay/logs/',
                       
    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 4096
}

class twitch_scraper:
    def __init__(self, config, channel,filename):
        self.config = config
        self.channel = channel
        self.filename = filename

        self.set_irc_socket()
        self.stream_connection()

    def set_irc_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        #try: connection might fail.
        try:
            self.sock.connect((self.config['server'], self.config['port']))
        except:
            pp('Cannot connect to server (%s:%s).' % (self.config['server'], self.config['port']), 'error')
        self.sock.settimeout(None)

        self.sock.send('USER %s\r\n' % self.config['username'])
        self.sock.send('PASS %s\r\n' % self.config['oauth_password'])
        self.sock.send('NICK %s\r\n' % self.config['username'])

        if self.check_login_status():
            pass
        else:
            pp('Login unsuccessful. (hint: make sure your oauth token is set in self.config/self.config.py).', 'error')

        self.sock.send('JOIN #%s\r\n' % self.channel)

    def stream_connection(self):
        ts_start = time.time()
        f = open(self.config['log_path']+self.filename+'_stream.txt', 'w')

        self.alive = True
        while self.alive:
            data = self.sock.recv(self.config['socket_buffer_size']).rstrip()
            
            if len(data) == 0:
                pp('Connection was lost, reconnecting.')
                self.sock = self.set_irc_socket()

            # check for ping, reply with pong
            self.check_for_ping(data)

            if self.check_for_message(data):
                #print 'Processing message'
                message_dict = self.get_message(data)
                
                channel = message_dict['channel']
                message = message_dict['message']
                username = message_dict['username']
                messagetime = time.time() - ts_start
                
                #Only works after twitch is done announcing stuff (MODT = Message of the day)

                lne = str(messagetime) + "_" + username + "_" + message
                pp(lne)
                f.write(lne.decode('utf8') + "\n")
    
    def check_for_message(self, data):
        if re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data):
            return True

    def check_for_ping(self, data):
        if data[:4] == "PING": 
            self.sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

    def check_login_status(self):
        data = self.sock.recv(1024)
        if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
            return False
        else:
            return True

    def get_message(self, data):
        msg = {
                'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
                'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
                'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0]
                }
        return msg

if __name__ == '__main__':
    stream = raw_input('Enter the stream ID: ')
    savefile = raw_input('Enter the file name: ')
    server = twitch_scraper(twitch_scraper_config,stream,savefile)
 