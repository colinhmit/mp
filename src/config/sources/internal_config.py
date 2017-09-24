from src.config.socket_config import *

##############################################################################
# Chat
##############################################################################

chat_conn_config = {
    # attributes
    'src': 'internal',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_INTERNAL,

    # connection creds
    'host': INTERNAL_HOST,
    'port': INTERNAL_PORT
}

chat_dist_config = {
    # attributes
    'src': 'internal',

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_INTERNAL,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_INTERNAL
}

##############################################################################
# Master
##############################################################################

internal_config = {
    # attributes
    'src': 'internal',

    # api

    # components
    'chat_conn_config': chat_conn_config,
    'chat_dist_config': chat_dist_config
}
