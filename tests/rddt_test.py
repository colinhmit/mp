
import praw
from functions_general import *

rddt_config = {
    # Reddit API Login
    'client_token': 'bx_HkZiUhuYJCw',
    'client_secret': '5l9swqgf2tAY2je0i61pNklgOCg',
    'user_agent': 'ISS:staycurrents.com:v0.1.9 (by /u/staycurrents)'
}

reddit = praw.Reddit(client_id=rddt_config['client_token'],
                     client_secret=rddt_config['client_secret'],
                     user_agent=rddt_config['user_agent'])

subreddit = reddit.subreddit('soccer')

subcontent = {}

while True:
	pp('iterating')
	# assume you have a Subreddit instance bound to variable `subreddit`
	for submission in subreddit.hot(limit=100):
		if submission.id not in subcontent:
			subcontent[submission.id] = {
				'title': submission.title,
				'score': submission.score,
				'url': submission.url
			}
		else:
			pp('//////')
			pp(submission.title)
			pp(submission.score - subcontent[submission.id]['score'])
			pp(vars(submission.author.name))
			subcontent[submission.id]['score'] = submission.score
