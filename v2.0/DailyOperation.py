from CrawlRawJson import * 
from ExtractTFIDF import *
from GetFeatureVectors import *
from BuildIndexTreeV2 import *
from FeedToRedisV2 import *
import time
import os


t = time.time()
print("######## Related News Engine V2 ########")
print("Daily Operation Starts...")
print("**** Step 0: Preparing directories ****")
dirs = ['streaming-data/','intermediate-results','data/']

for x in dirs:
    if os.path.isdir(x)==False:
        os.makedirs(x)
    else:
        import glob
        filelist=glob.glob(os.path.join(x, "*"))
        for f in filelist:
            os.remove(f)
print("**** Step 1: Crawling json files for all news articles ****")
CrawlRawJson()
print("\n **** Step 2: Extract TF-IDF from articles ****")
ExtractTFIDF()
print("\n ****  Step 3: Generate Feature Vectors for articles ****")
fv, id_list = GetFeatureVectors()
print("\n **** Step 4: Build index tree for related news ****")
BuildIndexTree(fv,id_list)
print("\n **** Step 5: Feed related news articles into Redis ****")
FeedToRedis()
print(" ######## Done! Spent: "+str(time.time()-t)+"(s) ########")
