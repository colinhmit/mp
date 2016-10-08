# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 19:22:30 2016

@author: colinh
"""

from sys import argv
import json
from stream.twitch_stream import *
from stream.config.universal_config import *
import socket, threading
import logging
import boto3

logging.basicConfig()

class StreamServer:

    def __init__(self, config):

        #self.config must be set before calling create_socket!
        self.config = config
        self.init_socket()

        self.streams = {}
        self.threads = {}
        self.urls = {}

    #for python client testing
    def init_socket(self):
        if self.config['mode'] == 'python':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.bind((self.config['host'], self.config['port']))
            sock.listen(self.config['listeners'])
            self.socket = sock

        if self.config['mode'] == 'sqs':
            session = boto3.Session(
                aws_access_key_id='AKIAJJYQ67ESV5S4YVHQ',
                aws_secret_access_key='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',
                region_name='us-west-2',
            )
            self.client = session.client('sqs')

    #stream control
    def create_stream(self, stream):
        self.threads[stream] = threading.Thread(target=self.add_stream, args=(stream,))
        self.threads[stream].start()

    def add_stream(self, stream):
        self.streams[stream] = TwitchStream(twitch_config,stream)

        if self.config['mode'] == 'sqs':
            queue_name = 'mpq-' + stream
            response = self.client.create_queue(QueueName=queue_name)
            self.urls[stream] = response['QueueUrl']

        self.streams[stream].run()

    #nodejs invoked stream call
    #DECO////////////////////////////
    def get_stream_trending(self, stream):
        if stream in self.streams.keys():
            if self.config['debug']:
                pp('Found stream!')
            return self.streams[stream].get_trending()

        else:
            if self.config['debug']:
                pp('Stream not found.')
            self.create_stream(stream)
            stream_exists = False

            while not stream_exists:
                stream_exists = stream in self.streams.keys()

            if self.config['debug']:
                pp('Stream created!')

            return self.streams[stream].get_trending()
    #////////////////////////////

    #python client testing
    #DECO////////////////////
    def check_for_roger(self, data):
        if data[:5] == 'roger':
            return True

    def check_for_stream(self, data):
       if data[:6] == 'stream':
            return True

    def get_stream(self, data):
        return data[7:]

    def roger(self, message):
        return "roger" + message

    def listen_to_client(self, client_sock, client_address):
        config = self.config
        connected = True
        while connected:
            data = client_sock.recv(config['socket_buffer_size']).rstrip()

            if len(data) == 0:
                pp(('Connection lost by: ' + str(client_address)))
                connected = False

            if config['debug']:
                pp(data)

            if self.check_for_roger(data):
                client_sock.send('Roger')

            if self.check_for_stream(data):

                stream_id = self.get_stream(data)

                if stream_id in self.streams.keys():
                    if config['debug']:
                        pp('Found stream!')

                    #output = json.dumps(self.streams[stream_id].get_chat())
                    output = json.dumps(self.streams[stream_id].get_trending())

                    if config['debug']:
                        pp('Sending: '+ output+config['end_of_data'])

                    client_sock.sendall(output+config['end_of_data'])

                else:
                    if config['debug']:
                        pp('Stream not found.')
                    self.create_stream(stream_id)

                    stream_exists = False
                    while not stream_exists:
                        stream_exists = stream_id in self.streams.keys()

                    if config['debug']:
                        pp('Stream created!')

                    #output = json.dumps(self.streams[stream_id].get_chat())
                    output = json.dumps(self.streams[stream_id].get_trending())
                    if config['debug']:
                        pp('Sending: '+ output+config['end_of_data'])

                    client_sock.sendall(output+config['end_of_data'])

    def oldrun(self):
        sock = self.socket
        config = self.config
        pp(('Server initialized'))

        while True:
            (client_sock, client_address) = sock.accept()
            pp(('Connection initiated by: ' + str(client_address)))
            client_sock.settimeout(60)
            threading.Thread(target = self.listen_to_client,args = (client_sock,client_address)).start()
    #////////////////////

    #SQS messaging
    def listen_to_reqs(self, queuename):
        response = self.client.get_queue_url(QueueName=queuename)
        url = response['QueueUrl']

        while True:
            messages = self.client.receive_message(
                QueueUrl=url,
                AttributeNames=['All'],
                MaxNumberOfMessages=1,
                VisibilityTimeout=60,
                WaitTimeSeconds=5
            )

            if messages.get('Messages'):
                m = messages.get('Messages')[0]
                body = json.loads(m['Body'])
                receipt_handle = m['ReceiptHandle']

                stream_id = body['stream']

                if stream_id in self.streams.keys():
                    if self.config['debug']:
                        pp('Found stream already.')
                    pass
                else:
                    if self.config['debug']:
                        pp('Creating stream...')
                    self.create_stream(stream_id)

                response = self.client.delete_message(
                    QueueUrl=url,
                    ReceiptHandle=receipt_handle
                )

    def multicast_trending(self):
        while True:
            if len(self.urls.keys()) > 0:
                for stream_key in self.urls.keys():
                    stream_url = self.urls[stream_key]
                    stream_dict = json.dumps(self.streams[stream_key].get_trending())
                    if self.config['debug']:
                        pp(stream_dict)
                    response = self.client.send_message(
                        QueueUrl=stream_url,
                        MessageBody=stream_dict,
                        DelaySeconds=0,
                    )
            else:
                pass

            time.sleep(0.5)


if __name__ == '__main__':
    server = StreamServer(server_config)
    listen_thread = threading.Thread(target = server.listen_to_reqs, args = ('mpq',)).start()
    multicast_thread = threading.Thread(target = server.multicast_trending).start()

    # client = boto3.client('sqs')
    # response = client.get_queue_url(QueueName='mpq')
    # url = response['QueueUrl']


    # messages = client.receive_message(
    # QueueUrl=url,
    # AttributeNames=['All'],
    # MaxNumberOfMessages=1,
    # VisibilityTimeout=60,
    # WaitTimeSeconds=5
    # )
    # if messages.get('Messages'):
    #     m = messages.get('Messages')[0]
    #     body = m['Body']
    #     receipt_handle = m['ReceiptHandle']
    #     pp(body)
    #s = zerorpc.Server(server)
    #s.bind('tcp://0.0.0.0:4242')
    #s.run()

