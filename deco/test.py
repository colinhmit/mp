import multiprocessing

class Worker:
    def __init__(self, num):
        for i in xrange(num):
        	print i

for _ in xrange(3):
    multiprocessing.Process(target=Worker, args=(10,)).start()
   