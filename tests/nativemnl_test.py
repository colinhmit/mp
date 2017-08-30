import requests
import json
import time
import zmq

#MNL TEST
mnl_url = 'http://35.166.70.54:8001'
ntv_msg = {'type':'message','stream':'test', 'message': 'Hi its colin', 'username':'testuser'}
r = requests.post(mnl_url,data=json.dumps(ntv_msg), headers={'Content-Type': 'application/json'})

#NTV TEST
context = zmq.Context()
zmq_socket = context.socket(zmq.PUB)
zmq_socket.connect("tcp://172.31.6.86:8000")
ntv_msg = {'stream':'test', 'message': 'Hi its Eben', 'username':'testuser2'}
zmq_socket.send(json.dumps(ntv_msg))

