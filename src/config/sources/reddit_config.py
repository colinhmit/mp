from src.config.socket_config import *

##############################################################################
# Chat
##############################################################################

chat_conn_config = {
    # attributes
    'src': 'reddit',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_REDDIT
}

chat_dist_config = {
    # attributes
    'src': 'reddit',

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_REDDIT,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_REDDIT
}

##############################################################################
# Master
##############################################################################

reddit_config = {
    # attributes
    'src': 'reddit',

    # api
    # prod creds
    'client_token': 'bx_HkZiUhuYJCw',
    'client_secret': '5l9swqgf2tAY2je0i61pNklgOCg',
    'user_agent': 'ISS:staycurrents.com:v0.1.9 (by /u/staycurrents)',

    # components
    'chat_conn_config': chat_conn_config,
    'chat_dist_config': chat_dist_config
}
