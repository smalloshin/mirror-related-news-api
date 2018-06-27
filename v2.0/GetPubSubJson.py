import os
from google.cloud import pubsub
import json
import ConfigParser

# read the config for redis connection
config = ConfigParser.ConfigParser()
config.read('related-news-engine.conf')
credential = config.get('PUBSUB','GOOGLE_APPLICATION_CREDENTIALS')
project_id = config.get('PUBSUB','PROJECT_ID')
topic = config.get('PUBSUB','TOPIC')
sub = 'sub_test142'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential

subscriber = pubsub.SubscriberClient()
topic_name = 'projects/{project_id}/topics/{topic}'.format(project_id=project_id,topic=topic)
subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(project_id=project_id,sub=sub)

try:
    subscriber.create_subscription(subscription_name, topic_name)
except Exception as e:
    if "409" in str(e):
        print("[Warning] The subscriber exists!")
        pass
    else:
        print(e)
        exit()


def callback(message):
    if message.attributes:
        if 'operation' in message.arrtibute:
            value = message.arrtibutes.get('operation')
            if value=="delete":
                facet = json.loads(message.data)
                if '_id' in facet:
                    print(message.data)
                    # start to do something
    message.ack()


subscriber.subscribe('projects/{project_id}/subscriptions/{sub}'.format(project_id=project_id,sub=sub),callback)

while True:
    import time
    time.sleep(10)
    print("I'm awake!")


