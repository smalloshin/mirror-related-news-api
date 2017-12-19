import urllib2
import urllib
import json
import time
import os
import datetime
import glob


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


def get_recent_data(dest_dir='recent/',params={},date=datetime.datetime.today(),date_num=1):
    if os.path.isdir(dest_dir)==False:
        os.makedirs(dest_dir)
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
        g = open(dest_dir+'news-page-'+str(i),'w')
        g.write(data) 

        for x in jsondata['_items']:
            #Time format: Wed, 05 Jul 2017 09:03:00 GMT
            d_nth = datetime.datetime.strptime(x['publishedDate'],"%a, %d %b %Y %X GMT").strftime("%j")        
            if d_nth<date_nth:
                next_flag=False
                break        
        
        if next_flag==False:
            break
        i=i-1
     

# dest_dir: the folder to place the file; params: the params for url
def get_raw_data(dest_dir='data/',params={}):    
    last_index = 1

    if os.path.isdir(dest_dir)==False:
        os.makedirs(dest_dir)
    else:
        filenames = glob.glob(dest_dir+"news-page-*")
        for x in filenames:
            current_index = int(x.split('news-page-')[1])
            if last_index < current_index:
                last_index = current_index

    url = 'https://api.mirrormedia.mg/posts?where={"style":{"$nin":["campaign"]},"isAdvertised":false,"isAdult":false,"state":{"$nin":["invisible"]},"categories":{"$nin":["57fca2f5c9b7a70e004e6df9","57f37a92a89ee20d00cc4a83"]}}&sort=-publishedDate'
    _,page_num = get_meta_data(url,params)


    print("*** Start crawling news pages ***")
    for i in range(last_index - 1, page_num + 1):
        print("*** Start crawling news pages", i, " ***")
        target_url = url + '&max_results&page=' + str(i)
        #print target_url
        if i%10==0 and i>0:
            print "Get page #"+str(i)+"..."
        try:
            req = urllib2.Request(target_url, headers=hdr)
            page = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.fp.read()
        data = page.read()
        g = open(dest_dir+'news-page-'+str(i),'w')
        g.write(data)
    print "Created "+str(i)+" files (each of them contains 50 news except the last one.)"
    g.close()

if __name__=="__main__":
    # get all data
    get_raw_data()
    # get recet data
    # get_recent_data()
