from hostport_config import *

##############################################################################
# Inputs
##############################################################################

internal_config = {
    # attributes
    'src': 'internal',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_INTERNAL,

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_INTERNAL,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_INTERNAL,

    # prod creds
    'host': INTERNAL_HOST,
    'port': INTERNAL_PORT
}

twitch_config = {
    # attributes
    'src': 'twitch',
    'socket_buffer_size': 4096,

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_TWITCH,

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_TWITCH,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_TWITCH,

    # prod creds   
    'server': 'irc.twitch.tv',
    'port': 6667,
    'username': 'chrendin',
    'client_id': 'r4jy4y7lwnzoez92z29zlgjlqggdyz',
    'oauth_password': 'oauth:1a6qgh8wz0b0lb2ue5zenht2lrkcdx'
}

twitter_config = {
    # attributes
    'src': 'twitter',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_TWITTER,

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_TWITTER,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_TWITTER,

    # prod creds
    # 'consumer_token': 'b4pRX7KQPnNQpdyOrC4FTT9Wn',
    # 'consumer_secret': 'GYgrnWSQYzRhD2rCHCXkLLba2bTa0qQ7OCqOGCRB3XShEc4f2d',
    # 'access_token': '784870359241809920-pSQiIXkQXn8miVsqnL6LQrOfzTY7Tix',
    # 'access_secret': 'Olqq3CSWZ5ozLSqRubTIl3AgsCg27tkbfTGLhYAr4lXpd'
                    
    # dev creds #1
    # 'consumer_token': 'lTImlMFo1GZzqJ5dynMHoOkEK',
    # 'consumer_secret': 'hkAYOdEN1nqmTtJBszgrC5VZE7gSFtN2nqgFsHxZbl8v8QVR0G',
    # 'access_token': '805548030816645120-aNstjukeFNVparl3x8lb8dyfUgIQzbf',
    # 'access_secret': 'QHpVzvSBDPTlQrY4k65ip0k3JFrQRIfKHv8JLUM43QTQw'

    # dev creds #2
    # 'consumer_token': 'brULNlsL5AI80FsiMAeH3us42',
    # 'consumer_secret': 'kdPYjOkOIR8NqnXqr7MZvTlR4mPwdMwF80KTytaeHUKFmNCCu5',
    # 'access_token': '178112532-kQ62pLaDjRrPEEn3W7zqsI0tLJgDPMkZgzR0U5iG',
    # 'access_secret': 'eik2jjyu0kLhkr2xNz53182Xa7ayktE646R7XrwQSGuCt'

    # dev creds #3
    'consumer_token': 'cPOClxrPAOdQhgfQfLdcXZL4D',
    'consumer_secret': 'uGByGCcB91FlNizE5edHPuVVmXInXcPIcHKE68n6drh6Achlaq',
    'access_token': '815322092627333121-W3OnWqcm8Mh4SGWJJc7OnmChwWump9m',
    'access_secret': 'MOMWd6pXkqlKxQQuSosa2fKK4sXqx58w2MhgA9G7OWGUq'
}

reddit_config = {
    # attributes
    'src': 'reddit',

    # messaging
    'input_host': INPUT_HOST,
    'input_port': INPUT_PORT_REDDIT,

    # distributor settings
    'dist_host': DIST_HOST,
    'dist_port': DIST_PORT_REDDIT,
    'stream_host': STREAM_HOST,
    'stream_port': STREAM_PORT_REDDIT,

    # prod creds
    'client_token': 'bx_HkZiUhuYJCw',
    'client_secret': '5l9swqgf2tAY2je0i61pNklgOCg',
    'user_agent': 'ISS:staycurrents.com:v0.1.9 (by /u/staycurrents)'
}

##############################################################################
# Components
##############################################################################

worker_config = {
    # messaging
    'input_host': INPUT_HOST,
    'input_ports': {
        'internal':     INPUT_PORT_INTERNAL,
        'twitch':       INPUT_PORT_TWITCH,
        'twitter':      INPUT_PORT_TWITTER,
        'reddit':       INPUT_PORT_REDDIT
    },
    'dist_host': DIST_HOST,
    'dist_ports': {
        'internal':     DIST_PORT_INTERNAL,
        'twitch':       DIST_PORT_TWITCH,
        'twitter':      DIST_PORT_TWITTER,
        'reddit':       DIST_PORT_REDDIT
    },

    # parsers
    'modules': {
        'internal':     'inputs.input_internal',
        'twitch':       'inputs.input_twitch',
        'twitter':      'inputs.input_twitter',
        'reddit':       'inputs.input_reddit'
    }
}

##############################################################################
# Master
##############################################################################

input_config = {
    # input decisions
    'inputs': ['internal', 'twitch', 'twitter', 'reddit'],
    'on': {
        'internal':     True,
        'twitch':       True,
        'twitter':      True,
        'reddit':       True,
    },
    'modules': {
        'internal':     'inputs.input_internal',
        'twitch':       'inputs.input_twitch',
        'twitter':      'inputs.input_twitter',
        'reddit':       'inputs.input_reddit'
    },
    'input_configs': {
        'internal':  internal_config,
        'twitch':    twitch_config,
        'twitter':   twitter_config,
        'reddit':    reddit_config
    },

    # worker setup
    'num_workers': 2,
    'worker_config': worker_config
}