fb_secret = '2308d641afe689cbf895f39afce6e8d2'
fb_id = '372161859804246'

import facebook

token = fb_id+'|'+fb_secret

graph = facebook.GraphAPI(token)

path = "/v2.8/10154824673843844/"
args = ["comments"]

'https://developers.facebook.com/tools/explorer?method=GET&path=10154824673843844%3Ffields%3Dcomments&version=v2.8'

#https://www.facebook.com/635366226645354/videos/649620661886577/
# profile = graph.get_object("me")
# friends = graph.get_connections("me", "friends")

# friend_list = [friend['name'] for friend in friends['data']]

# print friend_list