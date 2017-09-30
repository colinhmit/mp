import praw

from src.utils._functions_general import *

client_token= 'bx_HkZiUhuYJCw'
client_secret= '5l9swqgf2tAY2je0i61pNklgOCg'
user_agent = 'ISS:staycurrents.com:v0.1.9 (by /u/staycurrents)'

api = praw.Reddit(client_id=client_token, client_secret=client_secret, user_agent=user_agent)

s = api.submission(id='58pj7j')

a = []

s.comments.replace_more()
for top_level_comment in s.comments:
    a.append(top_level_comment)