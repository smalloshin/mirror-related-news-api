# necessary libraries
import re,urllib2
from bs4 import BeautifulSoup
from urllib import urlopen
import requests
import json
import pandas as pd
import math
import cgi
import jieba
import jieba.analyse
from glob import glob
import fileinput
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
import re
from functools import partial
import cPickle
from annoy import AnnoyIndex
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import cPickle as Pickle
import multiprocessing.pool

# weight: the feature vectors; id_list: the mapping between index and real id; dest: the output path
def BuildIndexTree(fv,id_list,pkl_dir = 'intermediate-results/', dest_dir='intermediate-results/', mode="batch"):
    #start ann
    if not mode in ["batch","recent"]:
        print "[Error] Mode error!"
        exit()

    print("["+mode+"] Derive related news....")
    n = len(fv)
    f = len(fv[0])
    print("n="+str(n)+", f="+str(f)+"\n")

    print("Making Indexing Trees...")
    t = AnnoyIndex(f)  # Length of item vector that will be indexed
    for i in range(n):
        v = fv[i] 
        t.add_item(i,v)
        if i>=500 and i%500==0:
            print("Added...."+str(i))
    print("Build Indexing Trees....")
    t.build(5)

    # store the indexing tree
    tree_name = 'news-indexing-tree.ann'
    if mode=='recent':
        tree_name = 'recent-'+tree_name
    t.save(dest_dir + tree_name)
    print("Save indexing tree: "+ dest_dir + tree_name)
 
    # default generate 20 related news for each article
    # the result will be put into "output_filename"
    k=20
    output_filename='mirror-news-ann-distance-20.result'

    # t: the indexing tree for all data, t: the current indexing tree 
    if mode=="batch":
        pass
    elif mode=="recent":
        # 1. setting the output name 
        output_filename= 'recent-'+output_filename

        # 2. loading the indexing tree and id list of all data
        u = AnnoyIndex(f)
        # 2.1. Load indexing tree from all data
        if os.path.exists(dest_dir+"news-indexing-tree.ann"):
            print "Get the indexing tree: "+dest_dir+"news-indexing-tree.ann"
            u.load(dest_dir+"news-indexing-tree.ann")
        else:
            print "[Error] File does not exist:"+dest_dir+"news-indexing-tree.ann"
            print "Run ANN with batch mode first"
            exit()
        # 2.2. Load id list from all data
        if os.path.exists(pkl_dir+"id_list_all.pkl"):
            f_pkl = open(pkl_dir+"id_list_all.pkl",'r')
            id_list_all = Pickle.load(f_pkl)
        else:
            print "Failed to load: "+pkl_dir+"id_list_all.pkl"
            print "Load fallback id list"
            f_pkl = open("fallback/fallback-id-list-all.pkl","r")
            id_list_all = Pickle.load(f_pkl)

    g = open(dest_dir+output_filename,'w')
    jobinfo = {"time": time.time(), "count": 0}

    # generate a list for related news

    def ann_job(i):
        knn_news = t.get_nns_by_item(i, k+1, include_distances=True)
        knn_list =  knn_news[0]
        dist_list = knn_news[1]
        del(knn_list[0])        
        del(dist_list[0])
        related_news = [(id_list[knn_list[j]],dist_list[j]) for j in range(len(knn_list))]

        if mode == "recent":
            vi = t.get_item_vector(i)
            knn_news_all = u.get_nns_by_vector(v, k, include_distances=True) 
            knn_list_all = knn_news_all[0]
            dist_list_all = knn_news_all[1]
            related_news_all = [(id_list_all[knn_list[j]],dist_list[j]) for j in range(len(knn_list))]
            # overwrite related_news
            
            for x in related_news_all:
                if not x[0] in knn_list:
                    related_news.append(x)
            # sort according to score
            related_news = sorted(related_news,key=lambda x:x[1])[0:k]

        related_news_json = json.dumps(related_news)

        news_id = id_list[i]
        g.write(news_id+"\t"+related_news_json+"\n")

        jobinfo["count"] += 1
        if jobinfo["count"]%100==0:
            print("Processed:"+str(jobinfo["count"])+", time passed:"+str(time.time()-jobinfo["time"])+"(s)")
            jobinfo["time"] = time.time()

    pool = multiprocessing.pool.ThreadPool()
    pool.map(ann_job, range(n))
    print "The related news are in: "+dest_dir+output_filename

    g.close() 

if __name__=="__main__":
    from GetFeatureVectors import *
    fv,id_list =  GetFeatureVectors()
    BuildIndexTree(fv,id_list)

    # get related_news from recent data
    #fv,id_list =  get_feature_vectors(mode="recent")
    #ANN(fv,id_list,mode="recent")

