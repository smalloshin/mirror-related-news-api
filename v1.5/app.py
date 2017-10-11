from flask import Flask,request, jsonify, json
import json
import time
import os
import requests
import pandas as pd
from redis import Redis
from feed_to_redis import load_data
import ast

max_k=20
app = Flask(__name__)
# this is for docker
r = Redis(host='redis',port=6379)

@app.route('/related_news')
def get_knn():
    k = int(request.args.get('k'))
    news_id = request.args.get('id')
    news_ids = request.args.get('ids')
    debug = request.args.get('debug')    
 
    if k==None:
        k=5
    if debug==None:
        debug="off"

    if r.hgetall('news_dict')==None:
        load_data(r)    
    
    # if id is set, ids is useless
    news_ids_list=[]
    if news_id!=None:
        news_ids_list.append(news_id)
    elif news_ids!=None:
        news_ids_list=news_ids.split(",")        

    return jsonify(make_dict(news_ids_list,k,debug))


def make_dict(news_ids_list,k,debug):
    json_dict = dict()
    json_dict['result']=[]

    target_articles = r.hmget('news_dict',news_ids_list)
    # all news related to news)ids_list
    # news_dict: news_id --> json dictionary of news_id
    news_dict = dict()
    
    all_knns = dict()
    for target_article in target_articles:
         target_dict = ast.literal_eval(target_article)
         target_id = target_dict['_id']
         news_dict[target_id] = target_dict
         all_knns[target_id] = [x[0] for x in target_dict['knn_list']]

    # all_knns.values() ==> [[knn_list1],...]
    knn_keys = []
    for x in all_knns.values():
        knn_keys+=x

    knn_articles = r.hmget('news_dict',knn_keys)

    for knn_article in knn_articles:
         knn_dict = ast.literal_eval(knn_article)
         knn_id = knn_dict['_id']
         news_dict[knn_id] = knn_dict
    ## now local news_dict is build (to be tested)
 
    for nid in news_ids_list:
         this_dict = news_dict[nid]
         n_id = this_dict['_id']
         n_cat = this_dict['category']
         n_title = this_dict['title']
         n_features = this_dict['features']    
    
 
         n_dict=dict()
         n_dict['title']=n_title
         n_dict['_id']=nid
         if debug=="on":
             n_dict['features']= n_features
             
         n_dict['related_news']=[]         
         n_dict['category']=n_cat
         n_dict['url']="https://api.mirrormedia.mg/posts/"+nid
         #n_dict['title']=df[df.id==nid].title
         # dump related news
         knn_list = this_dict['knn_list']
         i=0
         for npair in knn_list:
             rid = npair[0]
             dist = float(npair[1])
             that_dict = news_dict[rid]

             r_dict=dict()
             r_dict['_id']=rid
             r_dict['dist']=dist
             r_dict['title']= that_dict['title']
             r_dict['category']=that_dict['category']
             r_dict['url']="https://api.mirrormedia.mg/posts/"+rid
             if debug=="on":
                 r_dict['features'] = that_dict['features']

             n_dict['related_news'].append(r_dict)

             i=i+1
             if i>=k:
                 break                          

         json_dict['result'].append(n_dict)
    
    count = len(json_dict['result'])
    print count
    json_dict['count']=count
    return json_dict    
             
   
if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
	port=8080,
        debug=True
    )

