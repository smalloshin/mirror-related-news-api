import urllib2
import urllib
import json
import time
import os
import datetime

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def get_meta_data(url,params):
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
    return total,page_num


def get_recent_data(dest='data/recent/',params={},date=datetime.datetime.today(),date_num=1):
    if os.path.isdir(dest)==False:
        os.makedirs(dest)
    date_nth = date.strftime("%j") 
    url = 'https://api.mirrormedia.mg/posts'
    _,page_num = get_meta_data(url,params)
   
    i = page_num
    while i>0:
        next_flag=True
        target_url = url + "?max_results=50&page=" + str(i)
        #print target_url
        print "Get news in page "+str(i)
        try:
            req = urllib2.Request(target_url, headers=hdr)
            page = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.fp.read()

        data = page.read()
        jsondata = json.loads(data)
        g = open(dest+'news-page-'+str(i),'w')
        g.write(data) 

        for x in jsondata['_items']:
            #Time format: Wed, 05 Jul 2017 09:03:00 GMT
            d_nth = datetime.datetime.strptime(x['publishedDate'],"%a, %d %b %Y %X GMT").strftime("%j")        
            print d_nth, date_nth
            if d_nth<date_nth:
                print x['publishedDate']
                next_flag=False
                break        
        
        if next_flag==False:
            break
        i=i-1
        #g = open(dest+'news-page-'+str(i),'w')
        #g.write(data)            
     

# dest: the folder to place the file; params: the params for url
def get_raw_data(dest='data/',params={}):
    if os.path.isdir(dest)==False:
        os.makedirs(dest)

    url = 'https://api.mirrormedia.mg/posts'
    _,page_num = get_meta_data(url,params)

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
    get_raw_data()
