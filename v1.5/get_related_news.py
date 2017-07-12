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

# get the feature vectors from the whole data
def get_feature_vectors(source_path = 'output/', pkl_path='output/', mode = "batch"):
    if mode!="batch" and mode!="recent":
        print "Mode is wrong!"
        exit()

    msg_filename="news-id-tfidf50-topic-category.msg"
    
    if mode=="recent":
        msg_filename='recent-'+msg_filename
    
    if not os.path.exists(source_path+msg_filename):
            print "[Error] No features available! Execute get_features.py first!"
            print "[Fallback] Get features from fallback.msg!"
            df = pd.read_msgpack('fallback.msg')
        else:
            df = pd.read_msgpack(source_path+msg_filename)

    fenci_str=[]
    print "number of rows:",len(df)
    
    for x in df['tags_50_text']:
        keys = ""
        for i in range(len(x)):
            keys = keys + str(x[i][0])
            if i!=len(x)-1:
                keys = keys + " "
        fenci_str.append(keys)
    #fenci_str=df['fenci_str'].tolist() 
    id_list = df['id'].tolist()
    print fenci_str[0]

    #standard way to use TFIDF in scikit-learn
    print("Making Document Vectors...")
    
    if mode=="batch":    
        cv = CountVectorizer()
    else:
        # load countvectorizer
        f_pkl = open(pkl_path+"cv.pkl","r")
        cv = Pickle.load(f_pkl)    
    
    transformer = TfidfTransformer()
    # get the vectorizer which fit 'fenci_str'
    term_doc = cv.fit_transform(fenci_str)    
    tfidf = transformer.fit_transform(term_doc)
    fv = tfidf.toarray()
    
    # save countvectorizer 
    if mode=="batch":
        f_pkl = open(pkl_path+"cv.pkl",'w') 
        Pickle.dump(cv,f_pkl,True)
        f_pkl.close()
    print("Done!")   
    return fv, id_list

# weight: the feature vectors; id_list: the mapping between index and real id; dest: the output path
def ANN(fv,id_list,dest_dir='output/', mode="batch"):
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

    if mode=='batch':
        t.save(dest_dir+'mirror-news.ann')
    else:
        t.save(dest_dir+'recent-mirror-news.ann')
    print("Done!")

    # in case we need to get ann
    # u = AnnoyIndex(f)
    # u.load(dest+'mirror-news.ann')
    u=t
    k=20
 
    output_filename='mirror-news-ann-distance-20.result'
    if mode=="recent":
        output_filename= 'recent-'+output_filename

    g = open(dest_dit+output_filename,'w')
    pre_t = time.time()
    for i in range(n):
        news_id = id_list[i]
        knn_news = u.get_nns_by_item(i, k+1, include_distances=True)
        knn_list =  knn_news[0]
        dist_list = knn_news[1]
        del(knn_list[0])        
        del(dist_list[0])
        related_news = [(id_list[knn_list[j]],dist_list[j]) for j in range(len(knn_list))]
        related_news_json = json.dumps(related_news)
        g.write(news_id+"\t"+related_news_json+"\n")
        if i%100==0:
            print("Processed:"+str(i)+", time passed:"+str(time.time()-pre_t)+"(s)")
            pre_t=time.time()
    print "The related news are in: "+dest+output_filename
    g.close() 

if __name__=="__main__":
    fv,id_list =  get_feature_vectors(mode="batch")
    #ANN(fv,id_list)
