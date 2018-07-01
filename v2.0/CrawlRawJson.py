import urllib2
import urllib
import json
import time
import os
import datetime
import glob
import multiprocessing.pool

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def get_meta_data(url):
    req = urllib2.Request(url, headers=hdr)
    try:
        page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.fp.read()
        exit()

    data = page.read()
    jsondata = json.loads(data)
    total = jsondata['_meta']['total']
    max_results = jsondata['_meta']['max_results']
    page_num = total/max_results+1
    return page_num

# dest_dir: the folder to place the file; params: the params for url
def CrawlRawJson(dest_dir='data/',page_limit=float('inf')):    
    if os.path.isdir(dest_dir)==False:
        print("Build directory "+dest_dir)
        os.makedirs(dest_dir)
    else:
        print("Clean directory "+dest_dir)
        import glob
        filelist=glob.glob(os.path.join(dest_dir, "*"))
        for f in filelist:
            os.remove(f)

    url = 'https://api.mirrormedia.mg/posts?where={"style":{"$nin":["campaign"]},"isAdvertised":false,"isAdult":false,"state":{"$nin":["invisible"]},"categories":{"$nin":["57fca2f5c9b7a70e004e6df9","57f37a92a89ee20d00cc4a83"]}}&sort=-publishedDate'
    page_num = min(get_meta_data(url),page_limit)

    print("*** Start crawling news pages ***")
    print("*. Target: "+str(page_num)+" pages")

    jobinfo = {"time": time.time(), "count": 0}

    def crawling_job(i):
    #for i in range(page_num):
        target_url = url + '&page=' + str(i)
        #print("getting page #:"+str(i))
        try:
            req = urllib2.Request(target_url, headers=hdr)
            page = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.fp.read()
            exit()
        data = page.read()
        g = open(dest_dir+'news-page-'+str(i),'w')
        g.write(data)
        g.close()
        jobinfo["count"] += 1
        if jobinfo["count"]%50==0:
            print("Processed:"+str(jobinfo["count"])+", time passed:"+str(time.time()-jobinfo["time"])+"(s)")
            jobinfo["time"] = time.time()

    pool = multiprocessing.pool.ThreadPool()
    pool.map(crawling_job, range(1,page_num))
    pool.close()
    pool.join()
    print "Total: " + str(page_num) + " pages. The related news are in: "+dest_dir

if __name__=="__main__":
    CrawlRawJson()
