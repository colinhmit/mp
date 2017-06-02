from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import numpy as np
np.seterr(divide='ignore', invalid='ignore')

cosine = lambda v1, v2: np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

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