import urllib2
import urllib
import json
import time
import os


# dest: the folder to place the file; params: the params for url
def get_raw_news(dest='data/',params={}):
    if os.path.isdir(dest)==False:
        os.makedirs(dest)

    url = 'https://api.mirrormedia.mg/posts'

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

    url_params = urllib.urlencode(params)
    req = urllib2.Request(url+"?"+url_params, headers=hdr)

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
        g = open(dest+'news-page-'+str(i),'w')
        g.write(data)
    print "Created "+str(i)+" files (each of them contains 50 news except the last one.)"
    g.close()

if __name__=="__main__":
    get_raw_news()
