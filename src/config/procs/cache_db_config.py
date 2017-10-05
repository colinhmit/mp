from src.config.socket_config import *

##############################################################################
# Worker
##############################################################################

worker_config = {
    # db connect
    'db_str': 'testdb',
    'host_str': 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com',
    'port_str': '5432',
    'user_str': 'currentsdev',
    'pw_str': 'AndrewColinEben!',

    # messaging
    'worker_host': CACHE_HOST,
    'worker_port': CACHE_PORT
}

##############################################################################
# Server
##############################################################################

cache_db_config = {   
    # init cache
    'init_cache': [
        {
            'table': 'stream_chat',
            'src': 'internal',
            'stream': 'skt_rox',
            'start_num': 5,
            'end_num': 4000,
            'columns': ['time', 'src', 'stream', 'num', 'username', 'score', 'message', 'first_rcv_time']
        },

        {
            'table': 'stream_chat',
            'src': 'reddit',
            'stream': 'skt_rox',
            'start_num': 38,
            'end_num': 4000,
            'columns': ['time', 'src', 'stream', 'num', 'username', 'score', 'message', 'first_rcv_time']
        }
    ],

    # worker setup
    'num_workers': 10,
    'worker_config': worker_config
}