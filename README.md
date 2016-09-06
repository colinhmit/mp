# mp
If you don't know, now you know

## Setup

It is recommended that you use [virtualenv](https://virtualenv.pypa.io/en/stable/) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) to ensure consistency of dependencies. This is most easily accomplished with the following steps:

```
[sudo] pip install virtualenvwrapper
export WORKON_HOME=~/Envs
mkdir -p $WORKON_HOME

# add the following to ~/.profile || ~/.bash_profile || ~/.bashrc || ~/.zshrc
# source /usr/local/bin/virtualenvwrapper.sh

source ~/{profile file above}

mkvirtualenv mp
cd path/to/mp
pip install -r requirements.txt
```

Boom. You are now using a separate version of python and pip that are installed within the mp virtualenv along with all of the dependencies listed within `requirements.txt`.

To get out of the mp virtual env, simply run `deactivate`

To install a new dependency, just install as normal with `pip install <dependency>` and save by running `pip freeze > requirements.txt`

## Instructions
Start the server by calling:

```
python stream_server.py
```

Server runs on `localhost:4808` - see configs

Start a client by calling in a different terminal shell:
```
python stream_client.py
```

Enter the hostname (localhost for local development).
Enter the streamid of a stream (eg: sodapoppin or riotgames). See twitch.tv for examples.

Currently client_config (in configs) is set to demo_mode, meaning it will call for the chat from the server every 3 seconds.

Create multiple clients of the same stream, and different streams to see multithreading functionality.
