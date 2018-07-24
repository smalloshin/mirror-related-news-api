import pandas as pd
import sys
import datetime
import cPickle

if __name__=="__main__":
    if len(sys.argv)!=3: 
        print("Usage: python debug_tool.py {news_id} {mode}")
        print("Example: python debug_tool.py e12f2s pubsub")
        exit()
    
    _id=str(sys.argv[1])
    mode=str(sys.argv[2])

    print("Mode:"+mode)
    print("Checking:"+_id)

    msgname = "news-id-tfidf50-topic-category.msg"
    resultname = "related-news-pysparnn-"+"20180720.result"   #datetime.date.today().strftime("%Y%m%d")+".result"

    if mode=="pubsub":
        msgname="pubsub-"+msgname
        resultname="pubsub-"+resultname

    print("*. check: "+msgname)
    df = pd.read_msgpack(msgname)
    row = df[df.id==_id]
    print(" tf-idf terms/score:",row.tags_text,"\n")


    print("*. check: "+resultname)
    f = open(resultname,'r')

    for l in f:
        news_id, related_news = l.split("\t")
        if news_id==_id:
            print("related news:",related_news)
            break

    


    

