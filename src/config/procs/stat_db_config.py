##############################################################################
# INPUT CHAT Worker
##############################################################################

input_chat_stats_config = {
    # db connect
    'db_str': 'testdb',
    'host_str': 'currentsdb.clocpkfrofip.us-west-2.rds.amazonaws.com',
    'port_str': '5432',
    'user_str': 'currentsdev',
    'pw_str': 'AndrewColinEben!',

    #settings
    'interval': 5,
    'lookback': 60
}

##############################################################################
# Server
##############################################################################

stat_db_config = {
    # worker setup
    'input_chat_stats_config': input_chat_stats_config
}