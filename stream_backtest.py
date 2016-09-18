# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 17:39:04 2016

@author: colinh
"""

import json, sys,time
from stream.backtest.readers.twitch_reader_template import *
import socket

test_twitch_config = {
	
	# details required to read Twitch log
	'log_path': '/Users/colinh/Repositories/mp/stream/backtest/logs/',
 
	# if set to true will display any data received
	'debug': False,

	# if set to true will log all messages from all channels
	# TODO
	'log_messages': False,

      #fw_eo output from funcions_matching threshold 
      'fw_eo_threshold': 65,
      
      #twitch_stream trending params
      'matched_init_base': 20,
      'matched_add_base': 20,
      
      'decay_msg_base': 1,
      'decay_time_base': 1,
      
      #output frequency
      'output_freq': 1
                       
}


if __name__ == '__main__':
    stream = raw_input('Enter the stream ID: ')
    reader = TwitchReader(test_twitch_config,stream)
    reader.run()