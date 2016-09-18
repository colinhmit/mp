# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""
import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/colinh/Repositories/mp')

from stream.lib import irc as irc_
from stream.lib.functions_general import *
from stream.lib.functions_matching import *

class TwitchReader:

    def __init__(self, config, channel):
        self.config = config
        self.channel = channel
        self.chat = {}
        self.trending = {}
        
    def process_message(self, msg, msgtime):
        if len(self.trending)>0:
            (matched_msg, score) = fweo_compare(msg,self.trending.keys())
        
            if score > self.config['fw_eo_threshold']:
                if self.config['debug']:
                    pp("!!! "+matched_msg+" + "+msg+" = "+str(score)+" !!!")
                self.trending[matched_msg] = ((self.trending[matched_msg][0]+self.config['matched_add_base']), msgtime)
                
            else:
                if self.config['debug']:
                    pp("??? "+matched_msg+" + "+msg+" = "+str(score)+" ???")
                self.trending[msg] = (self.config['matched_init_base'], msgtime)
        else:
            if self.config['debug']:
                    pp("Init trending")
            self.trending[msg] = (self.config['matched_init_base'], msgtime)
        
        for key in self.trending.keys():
            curr_score, last_rcv_time = self.trending[key]
            curr_score -= self.config['decay_msg_base']
            curr_score -= round(msgtime - last_rcv_time,0) * self.config['decay_time_base']
                        
            if curr_score<1:
                del self.trending[key]
            else:
                self.trending[key] = (curr_score, last_rcv_time)

    def run(self):
        config = self.config
        f = open(config['log_path']+self.channel+'_stream.txt', 'r')
        
        strmdict = {}
        for line in f:
            pp(line)
            mssg = line.split("_")
            strmdict[float(mssg[0])] = (mssg[1],mssg[2].decode('utf-8'))
            
        ts_start = time.time()
        timekeys = sorted(strmdict.iterkeys())

        last_printed = 0
        while len(timekeys) > 0:
            
            mod_time, extra = divmod(time.time()-ts_start,config['output_freq'])
            if mod_time>last_printed:
                pp("****************************")
                for key in self.trending.keys():
                    pp(key+" : "+str(self.trending[key][0]))
                pp("****************************")
                
                last_printed = mod_time
            
            timekey = timekeys[0]
            #pp("~~~ "+str(timekey)+" | "+str(time.time() - ts_start))
            if (time.time() - ts_start) > timekey:
                self.chat[timekey] = {'channel': self.channel, 'message':strmdict[timekey][1], 'username': strmdict[timekey][0]}
            
                self.process_message(strmdict[timekey][1], timekey)   
            
                timekeys.pop(0)



    
 