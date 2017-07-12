import time
import get_raw_data as grd
import extract_features as ef
import get_related_news as grn
import feed_to_redis as ftr

from datetime import datetime


def micro_batch():
    grd.get_recent_data()
    ef.extract_features(source_dir="recent/",mode="recent")
    fv,id_list =  grn.get_feature_vectors(mode="recent")
    grn.ANN(fv,id_list,mode="recent")
    ftr.load_data(mode="recent")

def daily_batch():
    grd.get_raw_data()
    ef.extract_features(mode="batch")
    fv,id_list =  grn.get_feature_vectors(mode="batch")
    grn.ANN(fv,id_list)
    ftr.load_data(mode="batch")

if __name__=="__main__":
    micro_batch_period = 180
    daily_batch_hour = 3
   
    while True:
        print "[Wake-up] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " -- Executing micro batch!"
        micro_batch()
        h = int(datetime.now().strftime("%H"))
        if h==daily_batch_hour:
            print "Executing daily batch!"
            daily_batch()    
        print "Sleep for "+str(micro_batch_period)+" (s)...."
        time.sleep(micro_batch_period)
        
 



