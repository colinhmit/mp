import time
import zmq
import random

def consumer():
    consumer_id = random.randrange(1,10005)
    print "I am consumer #%s" % (consumer_id)
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:5557")

    for work in iter(consumer_receiver.recv_string, 'STOP'):
        data = int(work)
        result = { 'consumer' : consumer_id, 'num' : int(data)}
        if data%2 == 0: 
            print result

consumer()
