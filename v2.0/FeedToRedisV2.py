from redis import Redis
import os
import pandas as pd
import json
import ConfigParser
import datetime
import time

# read the config for redis connection
config = ConfigParser.ConfigParser()
config.read('related-news-engine.conf')
host = config.get('REDIS','HOST')
port = config.get('REDIS','PORT')
password = config.get('REDIS','PASSWORD')
r = Redis(host=host,port=port,db=0,password=password)

DF_CACHE = dict()
def get_facets(r_id,df):
    """
    goal: get the data of r_id in dataframe df
    parameters:
        1. df: target dataframe
        2. r_id: target id
    """
    r_dict = dict()
    if not r_id in DF_CACHE:
        DF_CACHE[r_id] = df[df.id==r_id]
    that_df = DF_CACHE[r_id]
    if len(that_df)!=0:
        r_dict['_id'] = r_id
        r_dict['categories'] = (that_df.category).tolist()[0]
        r_dict['title'] = (that_df.title).tolist()[0]
        r_dict['features'] = (that_df.tags_text).tolist()[0]
        r_dict['slug'] = (that_df.slug).tolist()[0]
        r_dict['heroImage'] = (that_df.heroImage).tolist()[0]
        r_dict['sections'] = (that_df.sections).tolist()[0]
        r_dict['style'] = (that_df['style']).tolist()[0]
        r_dict['href'] = "posts/"+r_id
    else:
        print("bad:",r_id)
    
    return r_dict

def FeedToRedis(r=r,source_dir = "intermediate-results/", input_prefix="related-news-pysparnn",mode="batch"):
    if not mode in ["batch","pubsub"]:
        print "[Error] the mode is not correct!"
        exit()

    if TestConnection(r)==False:
        exit()

    t=time.time() 
    today_stamp=datetime.date.today().strftime("%Y%m%d")
    result_filename = input_prefix+"-"+today_stamp+".result"
    msg_filename = "news-id-tfidf50-topic-category.msg"

    print("*. mode:"+mode)

    if os.path.exists(source_dir+msg_filename)==True:
        df = pd.read_msgpack(source_dir+msg_filename)
        print("loading:"+source_dir+msg_filename)
    else:
        print("[Error] Cannot find:"+source_dir+msg_filename)
        exit()

    # add prefix when pubsubv
    if mode == "pubsub":
        result_filename = "pubsub-"+result_filename
        msg_filename = "pubsub-"+msg_filename
        if os.path.exists(source_dir+msg_filename)==True:
            pubsub_df = pd.read_msgpack(source_dir+msg_filename)
            print("loading:"+source_dir+msg_filename)
            print(len(pubsub_df),len(df))
            df = df.append(pubsub_df,ignore_index=True)
            print("merge dataframe in batch and pubsub modes")
            print(len(df))
        else:
            print("[Error] Cannot find:"+source_dir+msg_filename)
            exit()

    if os.path.exists(source_dir+result_filename)==True:
        f = open(source_dir+result_filename,'r')
    else:
        print("[Error] Cannot find:"+source_dir+result_filename)
        exit()

    c = 0
    news_dict = dict()
    for line in f:
        news_id,knn_json = line.replace("\n","").split("\t")
        knn_list = json.loads(knn_json)
       
        c+=1
        if c%500==0:
            print(c)
        
        r_news = []
        for (_,r_id) in knn_list:
            r_dict = get_facets(r_id,df)
            r_news.append(r_dict)

        n_dict = get_facets(news_id,df)
        n_dict['knn_list']=knn_list
        n_dict['related_news']=r_news

        news_dict["related-news-v2-"+news_id]= json.dumps(n_dict)

    """
    if you find error msg: MISCONF Redis is configured to save RDB snapshots, 
    try this on redis-cli: config set stop-writes-on-bgsave-error no
    """
    print "Total: "+str(len(news_dict))
    print "Feed all to Redis..."
    r.mset(news_dict)
    print "Done!"
    print(time.time()-t)

def TestConnection(r=r):
    ok=False
    try:
        response = r.client_list()
        print("Redis Connection OK!")
        ok=True
    except redis.ConnectionError:
        print("Redis Connection Error!")
    return ok

if __name__=="__main__":
    import time
    t = time.time()
    FeedToRedis(mode="batch")
    print("spent:"+str(time.time()-t)+"(s)")

