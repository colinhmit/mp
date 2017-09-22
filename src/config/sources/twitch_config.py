from src.config.socket_config import *

##############################################################################
# Chat
##############################################################################

twitch_chat_conn_config = {
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

twitch_chat_dist_config = {
    # attributes
    'src': 'twitch',

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_TWITCH,
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

    # components
    'chat_conn_config': twitch_chat_conn_config,
    'chat_dist_config': twitch_chat_dist_config
}