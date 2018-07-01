# necessary libraries
import json
import pandas as pd
import math
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import cPickle as Pickle
import multiprocessing.pool
"""
Facebook ANN package
See: https://github.com/facebookresearch/pysparnn
"""
import pysparnn.cluster_index as ci
import datetime



"""
Parameters:
fv: the feature vectors; id_list: the list of ids; cp: existing index (only in recent mode) 
pkl_dir: the path where the existing model is
dest_dir: the path of the output model; output_prefix: the output file name prefix
"""
def BuildIndexTree(fv,id_list,k=20,cp=None,mode="batch",pkl_dir = 'intermediate-results/', dest_dir='intermediate-results/', output_prefix="related-news-pysparnn"):
    if not mode in ["batch","pubsub"]:
        print "[Error] Mode error!"
        exit()

    print("["+mode+"] Derive related  news....")
    n = len(fv)
    f = len(fv[0])
    print("n="+str(n)+", f="+str(f)+"\n")

    if mode=='batch':
        print("Bullding index (by pysparnn) ...")
        t=time.time()
        cp = ci.MultiClusterIndex(fv,id_list) 
        print(time.time()-t) 
        # store the index
        t = time.time()
        print("Store index into disk....")
        Pickle.dump(cp,open(dest_dir+'pysparnn-index.pkl','w'))
        print(time.time()-t)
    elif mode=="poubsub":
        t=time.time()
        # if first time: load batch model!
        if cp==None:
            cp = Pickle.load(open(pkl_dir+'pysparnn-index.pkl','r'))
        print(time.time()-t)
        # add vectors into the index
        for i in range(len(fv)):
            cp.insert(fv[i],id_list[i])

    # create output file if not exists. otherwise, append the result.
    today_stamp=datetime.date.today().strftime("%Y%m%d")
    output_filename=output_prefix+"-"+today_stamp+".result"

    if mode=='batch':
        g = open(dest_dir+output_filename,'w')
    elif mode=='pubsub':
        g = open(dest_dir+output_filename,'a+')
        
   
    print("Generate related news list...")
    t = time.time()
    # generate a list for related news
    # [[(dist_11,id_11),(dist_12,id_12),...],[(dist_21,id_21),(dist_22,id_22)...],...   ]
    knn_news = cp.search(fv,k=k+1,return_distance=True)
    for x in knn_news:
        news_id = x[0][1]
        related_news_json = json.dumps(x[1:-1])
        g.write(news_id+"\t"+related_news_json+"\n")
    print(time.time()-t)

    print "The related news are in: "+dest_dir+output_filename
    g.close()
    return cp

if __name__=="__main__":
    from GetFeatureVectors import *
    fv,id_list =  GetFeatureVectors()
    BuildIndexTree(fv,id_list)

