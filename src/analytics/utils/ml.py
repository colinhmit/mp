from sklearn.cluster import KMeans 
from hdbscan import HDBSCAN
import numpy

from functions_general import *

class autovivify(dict):
        '''Pickleable class to replicate the functionality of collections.defaultdict'''
        def __missing__(self, key):
                value = self[key] = []
                return value

        def __add__(self, x):
                '''Override addition for numeric types when self is empty'''
                if not self and isinstance(x, Number):
                        return x
                raise ValueError

        def __sub__(self, x):
                '''Also provide subtraction method'''
                if not self and isinstance(x, Number):
                        return -1 * x
                raise ValueError

class mlCluster:
        def __init__(self, ml_typ, val):
                self.model = None
                if ml_typ == "hdb":
                        self.model = HDBSCAN(min_cluster_size=val)
                elif ml_typ == "kmeans":
                        self.model = KMeans(init='k-means++', n_clusters=val, n_init=10)
                self.autovivify = autovivify()

        def cluster(self, labels, vectors):
                self.model.fit(numpy.array(vectors))
                cluster_labels = self.model.labels_
                self.find_subj_clusters(labels, cluster_labels)
                return self.autovivify

        def find_subj_clusters(self, labels_array, cluster_labels):
                '''Read the labels array and clusters label and return the set of words in each cluster'''
                for c, i in enumerate(cluster_labels):
                        self.autovivify[i].append(labels_array[c])