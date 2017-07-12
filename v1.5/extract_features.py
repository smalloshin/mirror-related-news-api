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

def extract_from_raw(data_dir, attr_list):
    json_dir = glob(data_dir)
    
    reChinese = re.compile('[\x80-\xff]+')
    word_list = list()
    for attr in attr_list:
        if attr == 'title':
            title_list = list()
        elif attr == 'category':
            category_list = list()
        elif attr == 'id':
            id_list = list()
    for json_file_name in json_dir:
        with open(json_file_name) as json_file: 
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
            
    record_dict = {'id': id_list, 'text': word_list, 'title': title_list, 'category': category_list}
    df = pd.DataFrame.from_dict(record_dict)
    nullIndex = pd.isnull(df).any(1).nonzero()[0]
    df.drop(nullIndex, inplace=True)
    #df.to_msgpack('news_id_tfidf50_topic_category.msg')
    return df

def extract_tfidf(source_dir="data/",msg_dir="output/",mode="batch"):
    if not mode in ["batch","recent"]:
        print "[Error] unknown mode!"
        exit()

    msg_name="news-id-tfidf50-topic-category.msg"
    if mode=="recent":
        msg_name="recent-"+msg_name

    if os.path.isdir(source_dir)==False:
        print "The source folder: '"+source_dir+"' does not exist. You may want to run get_raw_data.py first."    
        exit()
    if os.path.isdir(msg_dir)==False:
        print "The folder to store msg file: '"+msg_dir+"' does not exist."
        print "Creating...."
        os.makedirs(msg_dir)
        print "Done!"
    

    my_attr = ['title', 'id', 'category']
    new_df = extract_from_raw(source_dir+'*', my_attr)
    jieba.load_userdict('dict/moe.dict')
    jieba.analyse.set_stop_words('dict/stopping_words.dict')
    tfidf_50 = partial(jieba.analyse.extract_tags, topK=50, withWeight=True)
    new_df['tags_50_text'] = new_df['text'].apply(tfidf_50)
    #print(new_df.head())
    print("number of rows:",len(new_df))
    print new_df.head()
    new_df.to_msgpack(msg_dir+msg_name)

if __name__=="__main__":
   extract_tfidf(mode="batch")
   extract_tfidf(source_dir="recent/",mode="recent")
