import time
import zmq

def producer():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUB)
    zmq_socket.connect("tcp://172.31.6.86:8000")
    #zmq_socket.connect("tcp://127.0.0.1:8000")
    # Start your result manager and workers before you start your producers
    for num in xrange(20000):
        work_message = unicode(num)
        zmq_socket.send_string(work_message)
    print 'done'

producer()
