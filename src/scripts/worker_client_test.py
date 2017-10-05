import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.bind("tcp://0.0.0.0:8050")

for num in range(10,3999):
    print num
    data = {'src': 'internal', 'start_num': num, 'end_num': num, 'stream': 'skt_rox', 'table': 'stream_chat', 'type': 'num_req', 'columns': ['time', 'src', 'stream', 'num', 'username', 'score', 'message', 'first_rcv_time']}
    socket.send(json.dumps(data))
    a = socket.recv()