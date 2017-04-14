import json
import zmq
import threading
import Queue

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

from functions_general import *
from rply import rply

class mnlWebServer(Resource):
    isLeaf = True
    manual_server = None
    
    #server protocol
    def render_POST(self, data):
        input_msg = data.content.getvalue()
        self.manual_server.handle_msg(input_msg)
        return ''

class mnl:
    def __init__(self, config):
        pp('Initializing Manual Input...')
        self.config = config
        self.init_sockets()
        self.Q = Queue.Queue()
        self.replays = {}

        threading.Thread(target = self.serve).start()
        threading.Thread(target = self.run).start()

    def init_sockets(self):
        context = zmq.Context()
        self.pipe = context.socket(zmq.PUSH)
        self.pipe.bind('tcp://'+self.config['zmq_input_host']+':'+str(self.config['zmq_input_port']))

    def handle_msg(self, input_msg):
        #try: json may not be set up properly.
        try:
            json_msg = json.loads(input_msg)
        except Exception, e:
            json_msg = {'type':'null'}
            pp(e)

        if json_msg['type'] == 'message':
            self.Q.put(input_msg)
        elif json_msg['type'] == 'replay':
            if json_msg['stream'] in self.replays:
                self.replays[json_msg['stream']].stop = True
            self.replays[json_msg['stream']] = rply(self.Q, self.config['log_path'], json_msg['logfile'], json_msg['stream'], json_msg['timestart'])

    def serve(self):
        self.alive = True
        while self.alive:
            data = self.Q.get()
            self.pipe.send_string(data)

    def run(self):
        pp('Initializing Manual Web Server...')
        resource = mnlWebServer()
        resource.manual_server = self
        factory = Site(resource)
        reactor.listenTCP(self.config['port'], factory)

        pp('Starting Manual Web Server...')
        reactor.run(installSignalHandlers=False)