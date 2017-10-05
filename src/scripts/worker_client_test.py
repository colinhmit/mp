import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.bind("tcp://0.0.0.0:8050")
data = {'src': 'internal', 'start_num': 5, 'end_num': 5, 'stream': 'skt_rox', 'table': 'stream_chat', 'type': 'num_req', 'columns': ['time', 'src', 'stream', 'num', 'username', 'score', 'message', 'first_rcv_time']}

while True:
    socket.send(json.dumps(data))
    a = socket.recv()