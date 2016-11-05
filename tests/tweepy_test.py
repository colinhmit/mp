#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

#Variables that contains the user credentials to access Twitter API 
consumer_token = 'b4pRX7KQPnNQpdyOrC4FTT9Wn'
consumer_secret = 'GYgrnWSQYzRhD2rCHCXkLLba2bTa0qQ7OCqOGCRB3XShEc4f2d'

access_token = '784870359241809920-pSQiIXkQXn8miVsqnL6LQrOfzTY7Tix'
access_secret = 'Olqq3CSWZ5ozLSqRubTIl3AgsCg27tkbfTGLhYAr4lXpd'
 
#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        jsondata = json.loads(data)
        if 'text' in jsondata.keys():
            print jsondata
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_token, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    stream = Stream(auth, l)

    stream.disconnect()
    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    #stream.filter(track=['#Game7'], async=1)
    #stream.filter(track=['#WorldSeries'], async=1)
