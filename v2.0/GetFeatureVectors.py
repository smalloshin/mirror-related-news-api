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

# get the feature vectors from the whole data
def GetFeatureVectors(source_dir = 'intermediate-results/', pkl_dir='intermediate-results/', mode = "batch", pubsub_hson={}):
    if mode!="batch" and mode!="pubsub":
        print "Mode is wrong!"
        exit()

   
    msg_filename="news-id-tfidf50-topic-category.msg"
    if mode=='pubsub':
        msg_filename='pubsub-'+msg_filename

    print("*. Mode:"+mode)

    if not os.path.exists(source_dir+msg_filename):
        print "[Error] No features available! Execute GetFeatureVectorss.py first!"
        exit()
    else:
        df = pd.read_msgpack(source_dir+msg_filename)
        print "msg_filename: "+source_dir+msg_filename
    fenci_str=[]
    
    print "number of rows:",len(df)
    for x in df['tags_text']:
        keys = ""
        for i in range(len(x)):
            keys = keys + str(x[i][0])
            if i!=len(x)-1:
                keys = keys + " "
        fenci_str.append(keys)
        id_list = df['id'].tolist()

    #standard way to use TFIDF in scikit-learn
    print("Making Document Vectors...")
    
    transformer = TfidfTransformer()

    if mode=="batch":    
        cv = CountVectorizer()
        # get the vectorizer which fit 'fenci_str'
        term_doc = cv.fit_transform(fenci_str)
    else:
        # load countvectorizer
        with open(pkl_dir+"cv.pkl","r") as f_pkl:
            cv = Pickle.load(f_pkl)    
        term_doc = cv.transform(fenci_str)    

    tfidf = transformer.fit_transform(term_doc)
    fv = tfidf.toarray()
    print("Feature dimension:"+str(len(fv)))

    # save id_list and countvectorizer 
    if mode=="batch":
        f_pkl = open(pkl_dir+"cv.pkl",'w') 
        Pickle.dump(cv,f_pkl,True)
        f_pkl.close()
        f_id_list = open(pkl_dir+"id_list_all.pkl",'w')
        Pickle.dump(id_list, f_id_list, True)
        f_id_list.close()

    print("Done!")
    print "There are "+str(len(fv))+" feature vectors"   
    return fv, id_list

if __name__=="__main__":
    #get related news from all data
    fv,id_list =  GetFeatureVectors(mode="batch")
    print(id_list[0])
