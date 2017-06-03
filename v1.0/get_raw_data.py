import urllib2
import json
import time
import os

url = 'https://api.mirrormedia.mg/posts'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

req = urllib2.Request(url, headers=hdr)

try:
    page = urllib2.urlopen(req)
except urllib2.HTTPError, e:
    print e.fp.read()

data = page.read()
jsondata = json.loads(data)
total = jsondata['_meta']['total']
page_num = total/50+1

for i in range(1,page_num):
    target_url = url + "?max_results=50&page=" + str(i)
    #print target_url
    if i%10==0 and i>0:
        print "Get "+str(i*50)+" news"
    try:
        req = urllib2.Request(target_url, headers=hdr)
        page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.fp.read()
    data = page.read()
    g = open('data/news-page-'+str(i),'w')
    g.write(data)
print "Total: around "+str(i*50)+" news"
g.close()

