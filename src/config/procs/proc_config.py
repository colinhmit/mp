##############################################################################
# Chat Input
##############################################################################

from src.config.procs.input_chat_config import input_chat_config

##############################################################################
# Stream Forwarder
##############################################################################

from src.config.procs.forwarder_config import forwarder_config

##############################################################################
# Stream Forwarder
##############################################################################

from src.config.procs.input_db_config import input_db_config

##############################################################################
# Server
##############################################################################

proc_config = {
    'input_chat_config': input_chat_config,
    'forwarder_config': forwarder_config,
    'input_db_config': input_db_config
}