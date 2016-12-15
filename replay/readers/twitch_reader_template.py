# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:42:42 2016

@author: colinh
"""
import sys

# Add the mp folder path to the sys.path list
sys.path.append('/Users/colinh/Repositories/mp')

from src.streams.utils import irc as irc_
from src.streams.utils.functions_general import *
from src.streams.utils.functions_matching import *

class TwitchReader:

    def __init__(self, config, channel):
        self.config = config
        self.channel = channel

        self.trending = {}
        self.last_rcv_time = None
        self.clean_trending = {}
        self.stop = False
    
    def get_trending(self):
        return self.clean_trending 

    def render_trending(self):
        if len(self.trending)>0:
            self.clean_trending = {msg_k: {'score':msg_v['score'], 'first_rcv_time': msg_v['first_rcv_time'] } for msg_k, msg_v in self.trending.items() if msg_v['visible']==1}

    def filter_trending(self):
        if len(self.trending)>0:
            temp_trending = dict(self.trending)
            max_key = max(temp_trending, key=lambda x: temp_trending[x]['score'] if temp_trending[x]['visible']==0 else 0)
            if self.trending[max_key]['visible'] == 0:
                self.trending[max_key]['visible'] = 1
                self.trending[max_key]['first_rcv_time'] = self.last_rcv_time

    def handle_match(self, matched_msg, msg, msgtime, user):
        if user in self.trending[matched_msg]['users']:
            if self.config['debug']:
                pp("&&& DUPLICATE"+matched_msg+" + "+msg+" &&&")
        else:
            if self.config['debug']:
                pp("!!! "+matched_msg+" + "+msg+" !!!")

            #check transformation
            match_subs = fweo_threshold(msg, self.trending[matched_msg]['msgs'].keys(), self.config['so_compare_threshold'])

            #if no substring match
            if match_subs == None:
                self.trending[matched_msg]['score'] += max(0.1,1-((len(self.trending[matched_msg]['users'])**2)/self.config['matched_add_user_base']))*self.config['matched_add_base']
                self.trending[matched_msg]['last_mtch_time'] = msgtime
                self.trending[matched_msg]['users'].append(user)
                self.trending[matched_msg]['msgs'][msg] = 1.0

            #if substring match
            else:
                submatched_msg = match_subs[0]
                self.trending[matched_msg]['msgs'][submatched_msg] += 1

                #if enough to branch
                if self.trending[matched_msg]['msgs'][submatched_msg] > self.trending[matched_msg]['msgs'][matched_msg]:
                    self.trending[submatched_msg] = {
                        'score': (self.trending[matched_msg]['score'] * self.trending[matched_msg]['msgs'][submatched_msg] / sum(self.trending[matched_msg]['msgs'].values())) + self.config['matched_add_base'], 
                        'last_mtch_time': msgtime,
                        'first_rcv_time': msgtime,
                        'users' : [user],
                        'msgs' : dict(self.trending[matched_msg]['msgs']),
                        'visible' : 1
                    }
                    self.trending[matched_msg]['score'] *= ((sum(self.trending[matched_msg]['msgs'].values())-self.trending[matched_msg]['msgs'][submatched_msg]) / sum(self.trending[matched_msg]['msgs'].values()))
                    del self.trending[matched_msg]['msgs'][submatched_msg]
                    del self.trending[submatched_msg]['msgs'][matched_msg]

                else:
                    self.trending[matched_msg]['score'] += max(0.1,1-((len(self.trending[matched_msg]['users'])**2)/self.config['matched_add_user_base']))*self.config['matched_add_base']
                    self.trending[matched_msg]['last_mtch_time'] = msgtime
                    self.trending[matched_msg]['users'].append(user)

    def handle_new(self, msg, msgtime, user):
        if len(msg) > 0:
            if self.config['debug']:
                pp("??? "+msg+" ???")
            self.trending[msg] = { 
                'score':  self.config['matched_init_base'],
                'last_mtch_time': msgtime,
                'first_rcv_time': msgtime,
                'users' : [user],
                'msgs' : {msg: 1.0},
                'visible' : 0
            }

    def decay(self, msg, msgtime):
        if (self.last_rcv_time!=None):
            prev_msgtime = self.last_rcv_time
            
            for key in self.trending.keys():
                if key == msg:
                    pass
                else:
                    curr_score = self.trending[key]['score']

                    msgtime_secs = (msgtime - prev_msgtime)
                    rcvtime_secs = (msgtime - self.trending[key]['first_rcv_time'])
                    lastmtch_secs = (msgtime - self.trending[key]['last_mtch_time'])

                    buffer_constant = min(msgtime_secs*self.config['buffer_mult'],1)
                    #msg event decay
                    curr_score -= buffer_constant*(1/max(self.config['decay_msg_min_limit'],rcvtime_secs))*self.config['decay_msg_base']
                    #time decay
                    curr_score -=  buffer_constant*max(rcvtime_secs,(lastmtch_secs**2)/self.config['decay_time_mtch_base']) * self.config['decay_time_base']
                                                  
                    if curr_score<=0.0:
                        del self.trending[key]
                    else:
                        self.trending[key]['score'] = curr_score

    def process_message(self, msg, msgtime, user):
        if len(self.trending)>0:
            matched = fweb_compare(msg, self.trending.keys(), self.config['fo_compare_threshold'])

            if (len(matched) == 0):
                self.handle_new(msg, msgtime, user)

            elif len(matched) == 1:
                matched_msg = matched[0][0]
                self.handle_match(matched_msg, msg, msgtime, user)

            else:
                matched_msgs = [x[0] for x in matched]
                (matched_msg, score) = fweo_tsort_compare(msg, matched_msgs)
                self.handle_match(matched_msg, msg, msgtime, user)

        else:
            if self.config['debug']:
                    pp("Init trending")
            self.handle_new(msg, msgtime, user)

        self.decay(msg, msgtime)

    def run(self, timestart):
        config = self.config

        self.trending = {}
        self.last_rcv_time = None
        self.clean_trending = {}
        self.stop = False

        f = open(config['log_path']+self.channel+'_stream.txt', 'r')
        
        strmdict = {}
        for line in f:
            pp(line)
            mssg = line.split("_")
            strmdict[float(mssg[0])] = (mssg[1],mssg[2].decode('utf-8'))
            
        timekeys = sorted(strmdict.iterkeys())

        last_printed = 0
        init = True

        while init:
            timekey = timekeys[0]
            if timestart > timekey:
                
                self.process_message(strmdict[timekey][1], timekey, strmdict[timekey][0])   
                #print (datetime.now()-timecheck)

                self.last_rcv_time = timekey
                #self.chat[timekey] = {'channel': self.channel, 'message':strmdict[timekey][1], 'username': strmdict[timekey][0]}


                timekeys.pop(0)
            else:
                init = False

        print self.trending

        ts_start = time.time()

        while (len(timekeys) > 0) & (not self.stop):
            
            # mod_time, extra = divmod(time.time()-ts_start,config['output_freq'])
            # if mod_time>last_printed:
            #     pp("****************************")
            #     for key in self.trending.keys():
            #         pp(key+" : "+str(self.trending[key]['score']))
            #     pp("****************************")
                
            #     last_printed = mod_time
             
            timekey = timekeys[0]
            if (time.time() - ts_start) > (timekey-timestart):
                
                #timecheck = datetime.now()
                self.process_message(strmdict[timekey][1], timekey, strmdict[timekey][0])   
                #print (datetime.now()-timecheck)

                self.last_rcv_time = timekey
                #self.chat[timekey] = {'channel': self.channel, 'message':strmdict[timekey][1], 'username': strmdict[timekey][0]}
            
                timekeys.pop(0)




    
 