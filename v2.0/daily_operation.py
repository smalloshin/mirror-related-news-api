from CrawlRawJson import * 
from ExtractTFIDF import *
from GetFeatureVectors import *
from BuildIndexTree import *
from FeedToRedis import *
import time
import os


t = time.time()
print("######## Related News Engine V2 ########")
print("Daily Operation Starts...")
print("**** Step 0: Preparing directories ****")
if os.path.isdir('streaming-data/')==False:
    os.makedirs('streaming-data/')
else:
    import glob
    filelist=glob.glob(os.path.join('streaming-data/', "*"))
    for f in filelist:
        os.remove(f)
print("**** Step 1: Crawling json files for all news articles ****")
CrawlRawJson()
print("\n **** Step 2: Extract TF-IDF from articles ****")
ExtractTFIDF()
print("\n ****  Step 3: Generate Feature Vectors for articles ****")
fv, id_list = GetFeatureVectors()
print("\n **** Step 4: Build index tree for related news ****")
BuildIndexTreeV2(fv,id_list)
print("\n **** Step 5: Feed related news articles into Redis ****")
FeedToRedisV2()
print(" ######## Done! Spent: "+str(time.time()-t)+"(s) ########")
