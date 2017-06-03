import requests

api_url = "http://localhost:5000/related_news"

params = {'k':5,'ids':'586b6e883c1f950d00ce2d31,58cfb1184dab280e005293b4'}

r = requests.get(api_url,params=params)
#print "1. hit:"+r.url
print r.text

