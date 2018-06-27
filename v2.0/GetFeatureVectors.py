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
def GetFeatureVectors(source_dir = 'intermediate-results/', pkl_dir='intermediate-results/', mode = "batch"):
    if mode!="batch" and mode!="recent":
        print "Mode is wrong!"
        exit()

    msg_filename="news-id-tfidf50-topic-category.msg"
    
    if mode=="recent":
        msg_filename='recent-'+msg_filename
    
    if not os.path.exists(source_dir+msg_filename):
        print "[Error] No features available! Execute get_features.py first!"
        print "[Fallback] Get features from fallback.msg!"
        df = pd.read_msgpack('fallback/fallback.msg')
    else:
        df = pd.read_msgpack(source_dir+msg_filename)

    print "msg_filename: "+msg_filename
    fenci_str=[]
    print "number of rows:",len(df)
    
    for x in df['tags_text']:
        keys = ""
        for i in range(len(x)):
            keys = keys + str(x[i][0])
            if i!=len(x)-1:
                keys = keys + " "
        fenci_str.append(keys)
    #fenci_str=df['fenci_str'].tolist() 
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
        if os.path.exists(pkl_dir+"cv.pkl"):
            f_pkl = open(pkl_dir+"cv.pkl","r")
        else:
            f_pkl = open("fallback/fallback-cv.pkl","r")
        cv = Pickle.load(f_pkl)    
        term_doc = cv.transform(fenci_str)    

    tfidf = transformer.fit_transform(term_doc)
    fv = tfidf.toarray()
    print len(fv[0])
 
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
