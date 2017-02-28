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
        multiprocessing.Process(target=self.cluster_subjs).start()

    def cluster_subjs(self):
        context = zmq.Context()
        recvr = context.socket(zmq.SUB)
        recvr.connect("tcp://127.0.0.1:"+str(self.config['zmq_subj_port']))
        recvr.setsockopt(zmq.SUBSCRIBE, "")

        sendr = context.socket(zmq.PUB)
        sendr.connect("tcp://127.0.0.1:"+str(self.config['zmq_cluster_port']))

        for data in iter(recvr.recv, 'STOP'):
            try:
                src, stream, subjs = pickle.loads(data)
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
                        enriched_clusters = {}
                        for k in clusters:
                            enriched_clusters[stream + "_" + str(k)] = {
                                'avgscore': numpy.mean([subjs[subj]['score'] for subj in clusters[k]]),
                                'subjects': clusters[k],
                                'adjs': [item for sublist in (subjs[subj]['adjs'] for subj in clusters[k]) for item in sublist]
                            }
                        pickled_data = pickle.dumps((src, stream, enriched_clusters))
                        sendr.send(pickled_data)
                        gc.collect()
            except Exception, e:
                pp(e)
