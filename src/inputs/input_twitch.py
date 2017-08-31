import multiprocessing
import socket
import re
import zmq

from utils._functions_general import *
from utils.input_base import Base

# 1. Twitch Input Handler
# 2. Twitch Parser

class Twitch(Base):
    def __init__(self, config, init_streams):
        Base.__init__(self, config, init_streams)
        self.stream_conn = multiprocessing.Process(target=self.stream_connection)
        if len(self.streams) > 0:
            self.stream_conn.start()

    def stream_connection(self):
        self.context = zmq.Context()
        self.set_sock()
        self.set_pipe()
            
        self.alive = True
        while self.alive:
            data = self.sock.recv(self.config['socket_buffer_size']).rstrip()
            if len(data) == 0:
                self.set_sock()
            self.check_for_ping(data)
            if self.check_for_message(data):
                self.pipe.send_string(self.config['self']
                                      + data.decode('utf-8', errors='ignore'))
    
    def set_sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        #try: connection might fail.
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

        for stream in self.streams:
            self.sock.send('JOIN #%s\r\n' % stream)
    
    def set_pipe(self):
        self.pipe = self.context.socket(zmq.PUSH)
        connected = False
        while not connected:
            #try: bind may fail if prev bind hasn't cleaned up.
            try:
                self.pipe.bind('tcp://'
                               + self.config['input_host']
                               + ':'
                               + str(self.config['input_port']))
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

def parse_twitch(data):
    #try: data may be corrupt
    try:
        data = json.loads(data)
        msg = {
               'src':           'twitch',
               'stream':        re.findall(r'^:.+\![a-zA-Z0-9_]'
                                           r'+@[a-zA-Z0-9_]'
                                           r'+.+ PRIVMSG (.*?) :',
                                           data)[0],
               'username':      re.findall(r'^:([a-zA-Z0-9_]+)\!',
                                           data)[0],
               'message':       re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)',
                                           data)[0],
               'media_urls':    [],
               'mp4_url':       '',
               'id':            str(uuid.uuid1()),
               'src_id':        ''
              }
        return msg
    except Exception, e:
        pp('parse_twitch failed', 'error')
        pp(e, 'error')
        return {}