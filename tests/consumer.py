import time
import zmq
import random

def consumer():
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.SUB)
    consumer_receiver.bind("tcp://127.0.0.1:8000")
    for work in iter(consumer_receiver.recv, 'STOP'):
        print work

consumer()
