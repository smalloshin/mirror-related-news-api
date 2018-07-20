import os
from google.cloud import pubsub_v1
import json
import ConfigParser
import time
import datetime
# for pubsub mode
from ExtractTFIDF import *
from GetFeatureVectors import *
from BuildIndexTreeV2 import *
from FeedToRedisV2 import * 
from multiprocessing import Queue

def ProcessStreamingData():
    ExtractTFIDF(mode='pubsub')
    fv,id_list = GetFeatureVectors(mode="pubsub")
    BuildIndexTree(fv,id_list,mode="pubsub")
    FeedToRedis(mode="pubsub")
    print("DONE!")

def GenerateStreamingJson(stream_jsons,dest_dir="streaming-data/"):
    time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = "streaming-"+time_stamp                  
    f = open(dest_dir+output_filename,'w')
    output_dict = dict()
    output_dict['_items']=stream_jsons

    print("total:"+str(len(stream_jsons)))
    output_json = json.dumps(output_dict)
    f.write(output_json)
    print("output file:"+dest_dir+output_filename)
    f.close()

def GetPubSubStreaming(dest_dir="streaming-data/"):
    print("[START] Getting Pubsub Streaming...")
    # read the config for redis connection
    config = ConfigParser.ConfigParser()
    config.read('related-news-engine.conf')
    credential = config.get('PUBSUB','GOOGLE_APPLICATION_CREDENTIALS')
    project_id = config.get('PUBSUB','PROJECT_ID')
    topic_id = config.get('PUBSUB','TOPIC_ID')
    sub_id = config.get('PUBSUB','SUB_ID')

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential

    project_path = 'projects/'+project_id
    topic_path = project_path+'/topics/'+topic_id
    subscription_path = project_path+'/subscriptions/'+sub_id
    full_subscription_path = topic_path+'/subscriptions/'+sub_id
   

    print('subscription_path:'+subscription_path)
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()    
    
    existing_subscriber=False
    for subinfo in subscriber.list_subscriptions(project_path):
        if subscription_path==subinfo.name:
            existing_subscriber=True
            break

    if existing_subscriber==False:
        subscriber.create_subscription(subscription_path,topic_path)
   
    q = Queue()

    # define the callback function
    def callback(message):
        json_dict = json.loads(message.data)
        if '_id' in json_dict:
            print(json_dict['_id']) 
            q.put(json_dict)
        message.ack()
    # subscriber
    subscriber.subscribe(subscription_path,callback)

    # what will we do when describing
    sleep_count = 0
    while True:
        time.sleep(10)
        while q.empty()!=True:
            print("Ready to output:"+str(q.qsize()))
            
            # get all jsons in queue
            target_jsons = []        
            while q.empty()!=True:
                target_jsons.append(q.get())

            # process jsons in the target_jsons
            GenerateStreamingJson(target_jsons,dest_dir)
            ProcessStreamingData()

            #logging
            time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            print("["+time_stamp+"] finished:"+str(len(target_jsons))+"; new-comers:"+str(q.qsize()))
            sleep_count=0

        sleep_count+=1
        if sleep_count%10==0:
            print("Sleep "+str(sleep_count*10)+" times...")

if __name__=="__main__":
    GetPubSubStreaming()
