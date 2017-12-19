from redis import Redis
import os
import pandas as pd
import json

# redis connect string
r = Redis(host='localhost',port=6379)

DF_CACHE = dict()

def get_facets(df,r_id,fields = ['_id','features','category','title']):
    """
    goal: get the data of r_id in dataframe df
    parameters:
        1. df: target dataframe
        2. r_id: target id
        3. fields: target fields
    """
    r_dict = dict()
    if not r_id in DF_CACHE:
        DF_CACHE[r_id] = df[df.id==r_id]
    that_df = DF_CACHE[r_id]
    r_dict['_id'] = r_id
    r_dict['categories'] = (that_df.category).tolist()[0]
    r_dict['title'] = (that_df.title).tolist()[0]
    r_dict['features'] = (that_df.tags_text).tolist()[0]
    r_dict['slug'] = (that_df.slug).tolist()[0]
    r_dict['heroImage'] = (that_df.heroImage).tolist()[0]
    r_dict['sections'] = (that_df.sections).tolist()[0]
    r_dict['style'] = (that_df['style']).tolist()[0]
    r_dict['href'] = "posts/"+r_id
    return r_dict

def load_data(r=r,source_dir = "output/", mode="batch"):
    if not mode in ["batch","recent"]:
        print "[Error] the mode is not correct!"
        exit()

    result_filename = "mirror-news-ann-distance-20.result"
    msg_filename = "news-id-tfidf50-topic-category.msg"
    if mode == "recent":
        result_filename = "recent-"+result_filename
        msg_filename = "recent-"+msg_filename

    if os.path.exists(source_dir+result_filename)==True:
        f = open(source_dir+result_filename,'r')
    else:
        print("[Warning] Cannot find the latest list of related news. Use the fallback list now. Please run daily_batch.sh to get the latest related news")
        f = open('fallback/fallback.result','r')
    
    if os.path.exists(source_dir+msg_filename)==True:
        df = pd.read_msgpack(source_dir+msg_filename)
    else:
        print("[Warning] Cannot find the latest metadata of related news. Use the fallback metadata now. Please run daily_batch.sh to get the latest metadata")
        df = pd.read_msgpack('fallback/fallback.msg')

    print("Loading the KNN list...")
    
    news_dict = dict()
    for line in f:
        news_id, knn_raw = line.replace("\n","").split("\t")
        knn_list = json.loads(knn_raw)
       
        r_news = []
        for (r_id,_) in knn_list:
            r_dict = get_facets(df,r_id)
            r_news.append(r_dict)

        n_dict = get_facets(df,news_id)
        n_dict['knn_list']=knn_list
        n_dict['related_news']=r_news

        news_dict[news_id]= json.dumps(n_dict)

    """
    if you find error msg: MISCONF Redis is configured to save RDB snapshots, 
    try this on redis-cli: config set stop-writes-on-bgsave-error no
    """
    print "Total: "+str(len(news_dict))
    print "Feed all to Redis..."
    r.hmset('news_dict',news_dict)
    print "Done!" 

if __name__=="__main__":
    load_data(mode="batch")
    #load_data(r,mode="recent")

