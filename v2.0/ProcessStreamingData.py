from ExtractTFIDF import *
from GetFeatureVectors import *
from BuildIndexTreeV2 import *
from FeedToRedisV2 import * 

import time


def ProcessStreamingData():
    ExtractTFIDF(mode='pubsub')
    fv,id_list = GetFeatureVectors(mode="pubsub")
    BuildIndexTree(fv,id_list,mode="pubsub")
    FeedToRedis(mode="pubsub")
    print("DONE!")

if __name__=="__main__":
    ProcessStreamingData()
