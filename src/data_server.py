# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""
import threading
import json
import gc
import time
import zmq
import pickle
import datetime
import multiprocessing
import numpy

from streams.utils.ml import mlCluster, autovivify
from streams.utils.functions_general import *

class DataServer():
    def __init__(self, config):
        pp('Initializing Data Server...')
        self.config = config
        self.init_threads()

    def init_threads(self):
        multiprocessing.Process(target=self.handle_subjs).start()

        for _ in xrange(self.config['num_cluster_procs']):
            multiprocessing.Process(target=self.cluster_subjs).start()

    def handle_subjs(self):
        context = zmq.Context()
        recvr = context.socket(zmq.SUB)
        recvr.bind('tcp://'+self.config['zmq_data_host']+':'+str(self.config['zmq_data_port']))
        recvr.setsockopt(zmq.SUBSCRIBE, "")

        sendr = context.socket(zmq.PUSH)
        sendr.bind('tcp://'+self.config['zmq_proc_host']+':'+str(self.config['zmq_proc_port']))
        
        handling = True
        for data in iter(recvr.recv, 'STOP'):
            sendr.send(data)

    def cluster_subjs(self):
        context = zmq.Context()
        recvr = context.socket(zmq.PULL)
        recvr.connect('tcp://'+self.config['zmq_proc_host']+':'+str(self.config['zmq_proc_port']))

        sendr = context.socket(zmq.PUSH)
        sendr.connect('tcp://'+self.config['zmq_http_host']+':'+str(self.config['zmq_http_port']))
        
        for data in iter(recvr.recv, 'STOP'):
            try:
                pickledata = pickle.loads(data)
                stream = pickledata['stream']
                pp('processing... '+stream)
                if pickledata['type'] == 'subjects':
                    subjs = pickledata['data']
                    if len(subjs) > 0:
                        subj_scores = [subjs[x]['score'] for x in subjs]
                        pctile = numpy.percentile(numpy.array(subj_scores), self.config['subj_pctile'])

                        labels = []
                        vectors = []
                        for subj in subjs:
                            if subjs[subj]['score'] > pctile:
                                labels.append(subj)
                                vectors.append(subjs[subj]['vector'])

                        if len(labels) > 1:
                            model = mlCluster('hdb', self.config['hdb_min_cluster_size'])
                            clusters = model.cluster(labels,vectors)
                            pp('done ml... '+stream)
                            enriched_clusters = {}
                            for k in clusters:
                                enriched_clusters[stream + "_" + str(k)] = {
                                    'avgscore': numpy.mean([subjs[subj]['score'] for subj in clusters[k]]),
                                    'subjects': clusters[k],
                                    'adjs': [item for sublist in (subjs[subj]['adjs'] for subj in clusters[k]) for item in sublist]
                                }
                            data = {
                                'type': 'clusters',
                                'src': pickledata['src'],
                                'stream': stream,
                                'data': {'clusters': enriched_clusters}
                            }
                            pickled_data = pickle.dumps(data)
                            sendr.send(pickled_data)
                            gc.collect()
                            pp('finshed... '+stream)
            except Exception, e:
                pass
