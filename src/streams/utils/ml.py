# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:55:12 2016

@author: colinh
"""
from sklearn.cluster import KMeans 
from numbers import Number
from pandas import DataFrame
import sys, codecs, numpy

from functions_general import *

class autovivify_list(dict):
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

def find_word_clusters(labels_array, cluster_labels):
        '''Read the labels array and clusters label and return the set of words in each cluster'''
        cluster_to_words = autovivify_list()
        for c, i in enumerate(cluster_labels):
                cluster_to_words[ i ].append( labels_array[c] )
        return cluster_to_words