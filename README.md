# mp
If you don't know, now you know

#instructions
Start the server by calling:
    python stream_server.py

Server runs on (localhost,4808), see configs

Start a client by calling in a different terminal shell:
    python stream_client.py

Enter the streamid of a stream (eg: sodapoppin or riotgames). See twitch.tv for examples.

Currently client_config (in configs) is set to demo_mode, meaning it will call for the chat from the server every 3 seconds.

Create multiple clients of the same stream, and different streams to see multithreading functionality.


