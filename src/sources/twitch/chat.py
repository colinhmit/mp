import json
import socket
import re
import zmq
import multiprocessing
from functools import partial

from src.utils._functions_general import *
from src.sources._template.chat_base import ChatBase


class Chat(ChatBase):
    def __init__(self, config, streams):
        ChatBase.__init__(self, config, streams)
        self.config = config

        self.conn = multiprocessing.Process(target=self.chat_connection)
        self.conn.start()

    def chat_connection(self):
        chat_streams = [k for k, v in self.streams.items() if v['chat']]
        if len(chat_streams) > 0:        
            self.context = zmq.Context()
            self.set_sock(chat_streams)
            self.set_pipe()

            connected = True
            while connected:
                try:
                    data = self.sock.recv(self.config['socket_buffer_size']).rstrip()
                    if data == '*STOP*':
                        connected = False
                    if len(data) == 0:
                        self.set_sock()
                    self.check_for_ping(data)
                    if self.check_for_message(data):
                        packet = {
                            'src':      self.config['src'],
                            'data':     data.decode('utf-8', errors='ignore')
                        }
                        self.pipe.send_string(json.dumps(packet))
                except Exception, e:
                    pp('EINTR?', 'error')
                    pp(e, 'error')
            
    def set_sock(self,streams):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        # try: connection might fail.
        try:
            self.sock.connect((self.config['server'], self.config['port']))
        except:
            pp('Cannot connect to server (%s:%s).' % (self.config['server'],
                                                      self.config['port']),
                                                      'error')
        self.sock.settimeout(None)

        self.sock.send('USER %s\r\n' % self.config['username'])
        self.sock.send('PASS %s\r\n' % self.config['oauth_password'])
        self.sock.send('NICK %s\r\n' % self.config['username'])

        if self.check_login_status():
            pass
        else:
            pp('Login unsuccessful.', 'error')

        for stream in streams:
            self.sock.send('JOIN #%s\r\n' % stream)

    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUSH)
        connected = False
        while not connected:
            # try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.pipe.bind('tcp://' +
                               self.config['input_host'] +
                               ':' +
                               str(self.config['input_port']))
                connected = True
            except Exception, e:
                pass

    def check_for_message(self, data):
        if re.match(r'^:[a-zA-Z0-9_]'
                    r'+\![a-zA-Z0-9_]'
                    r'+@[a-zA-Z0-9_]'
                    r'+(\.tmi\.twitch\.tv|\.testserver\.local)'
                    r' PRIVMSG #[a-zA-Z0-9_]+ :.+$',
                    data):
            return True

    def check_for_ping(self, data):
        if data[:4] == "PING":
            self.sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

    def check_login_status(self):
        data = self.sock.recv(1024)
        if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE '
                    r'\* :Login unsuccessful\r\n$',
                    data):
            return False
        else:
            return True
