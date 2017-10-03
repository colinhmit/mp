from src.config.socket_config import *

##############################################################################
# Chat Input
##############################################################################

chat_conn_config = {
    # attributes
    'src': 'twitch',
    'socket_buffer_size': 4096,

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_TWITCH,

    # connection creds   
    'server': 'irc.twitch.tv',
    'port': 6667,
    'username': 'chrendin',
    'oauth_password': 'oauth:1a6qgh8wz0b0lb2ue5zenht2lrkcdx'
}

chat_dist_config = {
    # attributes
    'src': 'twitch',

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_TWITCH,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_TWITCH
}

##############################################################################
# Stream
##############################################################################

trending_config = {
    # attributes
    'src': 'twitch',

    # matching logic
    'base_svo_match': False
}

nlp_config = {
    # attributes
    'src': 'twitch'
}

stream_chat_config = {
    # attributes
    'src': 'twitch',
    'trending': True,
    'nlp': True,

    # module
    'module': 'src.sources.twitch._functions_chat',

    # messaging
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_TWITCH
}

##############################################################################
# Master
##############################################################################

twitch_config = {
    # attributes
    'src': 'twitch',

    # api
    # prod creds
    'client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',

    # input components
    'chat_conn_config': chat_conn_config,
    'chat_dist_config': chat_dist_config,

    # stream chat components
    'trending_config': trending_config,
    'nlp_config': nlp_config,
    'stream_chat_config': stream_chat_config
}