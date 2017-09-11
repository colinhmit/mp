import zmq
import pickle

#import utils
from inputs.utils._functions_general import *
from inputs.server import InputServer
from config.input_config import input_config

input_server = InputServer(input_config)

input_server.inputs['twitch'].join_stream('shroud')
#input_server.inputs['twitter'].join_stream('trump')
#input_server.inputs['reddit'].join_stream('soccer')

context = zmq.Context()
input_socket = context.socket(zmq.SUB)
input_socket.connect('tcp://'+'0.0.0.0'+':'+str(8030))
input_socket.connect('tcp://'+'0.0.0.0'+':'+str(8031))
input_socket.connect('tcp://'+'0.0.0.0'+':'+str(8032))
input_socket.connect('tcp://'+'0.0.0.0'+':'+str(8033))
input_socket.setsockopt(zmq.SUBSCRIBE, "")

for data in iter(input_socket.recv, '*STOP*'):
    #try: msg_data may be unpickleable?
    try:
        msg_data = pickle.loads(data)
        pp(msg_data)
    except Exception, e:
        pp(e)