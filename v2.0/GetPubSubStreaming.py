import os
from google.cloud import pubsub_v1
import json
import ConfigParser
import time
import datetime
from ProcessStreamingData import *

def GenerateStreamingJson(stream_jsons,dest_dir="streaming/"):
    time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = "streaming-"+time_stamp                  
    f = open(dest_dir+output_filename,'w')
    output_dict = dict()
    output_dict['_items']=dict()

    for i in len(stream_jsons):
        key = str(i)
        output_dict[key]=dict()
        output_dict[key]=stream_json[i]

    print("total:"+str(len(output_dict)))
    output_json = json.dumps(output_dict)
    f.write(output_json)
    print("output file:"+dest_dir+output_filename)
    f.close()

def GetPubSubStreaming(dest_dir="streaming/"):
    print("[START] Getting Pubsub Streaming...")
    # read the config for redis connection
    config = ConfigParser.ConfigParser()
    config.read('related-news-engine.conf')
    credential = config.get('PUBSUB','GOOGLE_APPLICATION_CREDENTIALS')
    project_id = config.get('PUBSUB','PROJECT_ID')
    topic_id = config.get('PUBSUB','TOPIC_ID')
    sub_id = 'sub_test9527'

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
   
    today_stream_jsons=[]
    slice_stream_jsons=[]

    # define the callback function
    def callback(message):
        json_dict = json.loads(message.data)
        if '_id' in json_dict:
            print(json_dict['_id'])    
            slice_stream_jsons.append(json_dict)
        message.ack()
    # subscriber
    subscriber.subscribe(subscription_path,callback)

    # what will we do when describing
    
    while True:
        time.sleep(10)
        if slice_stream_jsons!=[]:
            print("Ready to output:"+str(len(stream_jsons)))
            GenerateStreamingJson(today_stream_jsons,dest_dir)
            ProcessStreamingData()
            today_stream_jsons += slice_stream_jsons
            slice_stream_jsons=[]
            print("Clean the queue!")
        print("I'm sleep!")

if __name__=="__main__":
    GetPubSubStreaming()
