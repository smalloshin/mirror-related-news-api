import sys
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
import re
from functools import partial
import cPickle as pickle
from sklearn.feature_extraction import DictVectorizer
import os
import time

def extract_from_raw(data_dir, attr_list, page_limit,mode='batch'):
    reChinese = re.compile('[\x80-\xff]+')
    word_list = list()
    for attr in attr_list:
        if attr == 'title':
            title_list = list()
        elif attr == 'category':
            category_list = list()
        elif attr == 'id':
            id_list = list()
        elif attr == 'slug':
            slug_list = list()
        elif attr == 'heroImage':
            heroImage_list = list()
        elif attr == 'style':
            style_list = list()
        elif attr == 'sections':
            sections_list = list()

    json_dir = glob(data_dir)
    if mode=='batch':
        json_files=glob(data_dir+"news-page-*")
    elif mode=="pubsub":
        json_files=glob(data_dir+"*")

    temp_json_files = []
    for json_file_name in json_files:
        index = int(json_file_name.split('news-page-')[1])
        if index<=page_limit:
            temp_json_files.append(json_file_name)
    json_files=temp_json_files


    for json_file_name in json_files:
        with open(json_file_name) as json_file:
            #print("open:",json_file_name)
            data = json.load(json_file)
            items = data['_items']
            df = pd.DataFrame.from_dict(items)
            if 'title' in attr_list:
                title_temp_list = [x.encode('utf-8') for x in df['title']]
                title_list.extend(title_temp_list)
            if 'category' in attr_list:
                category_list.extend(df['categories'].tolist())
            if 'id' in attr_list:
                id_list.extend(df['_id'].tolist())
            if 'sections' in attr_list:
                sections_list.extend(df['sections'].tolist())
            if 'slug' in attr_list:
                slug_list.extend(df['slug'].tolist())
            if 'heroImage' in attr_list:
                heroImage_list.extend(df['heroImage'].tolist())
            if 'style' in attr_list:
                style_list.extend(df['style'].tolist())


            for content in df['content']:
                if pd.isnull(content):
                    word_list.append(content)                    
                else:
                    soup = BeautifulSoup(content['html'], 'html.parser')                                                
                    text = soup.get_text(strip=True)                      
                    
                    text = text.strip(' \t\n\r')
                    text = ' '.join(text.split())
                    text = text.encode('utf-8')
                    chlist = reChinese.findall(text)
                    sentences = " ".join(chlist)                
                    word_list.append(sentences)
            
    record_dict = {'id': id_list, 'text': word_list, 'title': title_list, 'category': category_list,'slug': slug_list, 'heroImage': heroImage_list, 'sections': sections_list,'style': style_list}
    df = pd.DataFrame.from_dict(record_dict)
    nullIndex = pd.isnull(df).any(1).nonzero()[0]
    df.drop(nullIndex, inplace=True)
    return df

def ExtractTFIDF(source_dir="data/",msg_dir="intermediate-results/",mode='batch',page_limit=2000):
    msg_name="news-id-tfidf50-topic-category.msg"


    if mode=='batch':
        if os.path.isdir(source_dir)==False:
            print "The source folder: '"+source_dir+"' does not exist. You may want to run get_raw_data.py first."    
            exit()
        if os.path.isdir(msg_dir)==False:
            print "The folder to store msg file: '"+msg_dir+"' does not exist."
            print "Creating...."
            os.makedirs(msg_dir)
            print "Done!"
    elif mode=='pubsub':
        msg_name = 'pubsub-'+msg_name
    
    my_attr = ['title', 'id', 'category','slug','sections','heroImage','style']
    print("msg file:"+str(source_dir+msg_name))
    t = time.time()
    print("Making DataFrame...")
    new_df = extract_from_raw(source_dir+'*', my_attr,page_limit)
    print(time.time()-t)

    jieba.load_userdict('dict/moe.dict')
    jieba.analyse.set_stop_words('dict/stopping_words.dict')
    tfidf_20 = partial(jieba.analyse.extract_tags, topK=10, withWeight=True)

    print("Derive TFIDF...")
    t = time.time()
    new_df['tags_text'] = new_df['text'].apply(tfidf_20)
    print(time.time()-t)
    print("number of rows:",len(new_df))
    print("number of unique id:",len(new_df['id'].unique()))
    new_df.to_msgpack(msg_dir+msg_name)
    print("output file: "+msg_dir+msg_name)

if __name__=="__main__":
   ExtractTFIDF(page_limit=3000)
