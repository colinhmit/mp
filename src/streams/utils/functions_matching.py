# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 20:04:26 2016

@author: colinh
"""

import socket, re, time, sys
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def fwts_compare(msg1, msg2):
    return fuzz.token_set_ratio(msg1,msg2)

def fweo_compare(msg, msgs):
    return process.extractOne(msg, msgs, scorer=fuzz.token_set_ratio)

def fweo_compare_all(msg, msgs):
    return process.extract(msg, msgs, scorer=fuzz.token_set_ratio)

def fweb_compare(msg, msgs, threshold):
    return process.extractBests(msg, msgs, score_cutoff=threshold, limit=5)

def fweo_tsort_compare(msg, msgs):
    return process.extractOne(msg, msgs, scorer=fuzz.token_sort_ratio)

def fweo_check(msg, msgs):
	return process.extract(msg, msgs, scorer=fuzz.token_set_ratio, limit=1)

def fweo_threshold(msg, msgs, threshold):
	return process.extractOne(msg, msgs, scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
