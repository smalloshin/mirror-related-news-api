import time
import get_raw_data as grd
import extract_features as ef
import get_related_news as grn
import feed_to_redis as ftr

from datetime import datetime
import shutil
import os

def micro_batch():
    print "**** [Step 1] Clean old data and prepare directories ****"
    try:
        shutil.rmtree('recent/')
        os.makedirs('recent/')
        os.makedirs('output/')
    except:
        pass
    print "**** [Step 2] Crawl news articles ****"
    grd.get_recent_data()
    print "**** [Step 3] Compute features for each news articles ****"
    ef.extract_features(source_dir="recent/",mode="recent")
    print "**** [Step 4] Compute the related news ****"
    print "(may take long time)"
    fv,id_list =  grn.get_feature_vectors(mode="recent")
    grn.ANN(fv,id_list,mode="recent")
    print "**** [Step 5] Loading data to Redis ****"
    ftr.load_data(mode="recent")
    print "DONE!"

def daily_batch():
    print "**** [Step 1] Clean old data and prepare directories ****"
    try:
        shutil.rmtree('data/')
        os.makedirs('data/')
        os.makedirs('output/') 
    except:
        pass
    print "**** [Step 2] Crawl news articles ****"
    grd.get_raw_data()
    print "**** [Step 3] Compute features for each news articles ****"
    ef.extract_features(mode="batch")
    print "**** [Step 4] Compute the related news ****"
    print "(may take long time)"
    fv,id_list =  grn.get_feature_vectors(mode="batch")
    grn.ANN(fv,id_list)
    print "**** [Step 5] Loading data to Redis ****"
    ftr.load_data(mode="batch")
    print "DONE!"

if __name__=="__main__":
    micro_batch_period = 180
    daily_batch_hour = 19
   
    while True:
        f = open('operation.log','a')
        f.write("[Micro Batch] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " -- Executing micro batch!\n")
        print "[Wake-up] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " -- Executing micro batch!"
        try:
            micro_batch()
        except Exception as e:
            f.write("[Exception] "+str(e)+"\n")
            pass
        f.write("[Micro Batch] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " -- Micro batch is done!\n")
        h = int(datetime.now().strftime("%H"))
        if h==daily_batch_hour:
            print "Executing daily batch!"
            f.write("[Daily Batch] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " -- Executing daily batch!\n")
            try:
                daily_batch()    
            except Exception as e:
                f.write("[Exception] "+str(e)+"\n")
                pass
            f.write("[Daily Batch] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " -- Daily batch is done!\n")
        f.close() 
        time.sleep(30) 



