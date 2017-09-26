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
    'funnel_host': DB_HOST,
    'funnel_ports': {
        'input_chat':     DB_PORT_INPUT_CHAT,
        'stream_chat':    DB_PORT_STREAM_CHAT
    }
}

##############################################################################
# Funnels
##############################################################################

input_chat_funnel_config = {
    # messaging
    'input_host': STREAM_HOST,
    'input_ports': {
        'internal':     STREAM_PORT_INTERNAL,
        'twitch':       STREAM_PORT_TWITCH,
        'twitter':      STREAM_PORT_TWITTER,
        'reddit':       STREAM_PORT_REDDIT
    },
    'funnel_host': DB_HOST,
    'funnel_port': DB_PORT_INPUT_CHAT
}

stream_chat_funnel_config = {
    # messaging
    'input_host': FWD_HOST,
    'input_ports': {
        'forwarder':     FWD_PORT_OUTPUT
    },
    'funnel_host': DB_HOST,
    'funnel_port': DB_PORT_STREAM_CHAT
}

##############################################################################
# Server
##############################################################################

input_db_config = {
    # worker setup
    'num_workers': 10,
    'worker_config': worker_config,

    # distributor setup
    'input_chat_funnel_config': input_chat_funnel_config,
    'stream_chat_funnel_config': stream_chat_funnel_config
}