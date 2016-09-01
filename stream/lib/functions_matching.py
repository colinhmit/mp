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