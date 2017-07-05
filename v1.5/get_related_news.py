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

    if mode=="batch":
        if not os.path.exists(source_path+"news_id_tfidf50_topic_category.msg"):
            print "[Error] No features available! Execute get_features.py first!"
            print "[Fallback] Get features from fallback.msg!"
            df = pd.read_msgpack('fallback.msg')
        else:
            df = pd.read_msgpack(source_path+'news_id_tfidf50_topic_category.msg')
    else:
        # load dataframe
        if not os.path.exists(source_path+'recent_tfidf_topic_category.msg'):
            print "[Error] "+source_path+'recent_tfidf_topic_category.msg does not exist!'
            exit()
        df = pd.read_msgpack(source_path+'recent_tfidf_topic_category.msg')        
  


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
    weight = tfidf.toarray()
    
    # save countvectorizer 
    if mode=="batch":
        f_pkl = open(pkl_path+"cv.pkl",'w') 
        Pickle.dump(cv,f_pkl,True)
        f_pkl.close()
    print("Done!")   
    return weight, id_list

# weight: the feature vectors; id_list: the mapping between index and real id; dest: the output path
def ANN(weight,id_list,dest='output/'):
    #start ann
    print("Doing ANN...")
    n = len(weight)
    f = len(weight[0])
    print("n="+str(n)+", f="+str(f)+"\n")

    print("Making Indexing Trees...")
    t = AnnoyIndex(f)  # Length of item vector that will be indexed
    for i in range(n):
        v = weight[i] 
        t.add_item(i,v)
        if i>=500 and i%500==0:
            print("Added...."+str(i))
    print("Build Indexing Trees....")
    t.build(5)
    t.save(dest+'mirror-news.ann')
    print("Done!")

    #get ann
    u = AnnoyIndex(f)
    u.load(dest+'mirror-news.ann')
    u=t
    k=20
    g = open(dest+'mirror-news-ann-distance-20.result','w')
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
    print "The related news are in: "+dest+ "mirror-news-ann-distance-20.result"
    g.close() 

if __name__=="__main__":
    weight,id_list =  get_feature_vectors(mode="batch")
    ANN(weight,id_list)
